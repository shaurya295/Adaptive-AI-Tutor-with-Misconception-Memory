"""
game_store.py
-------------
What the gamified dashboard remembers, in the shared SQL database:

    game_players   display name and chosen study companion
    game_sessions  one row per pre-test, lesson or post-test played (start, finish)
    game_attempts  every multiple-choice answer: question, choice, right or wrong,
                   misconception revealed, time taken, whether a hint was bought
    coin_spends    coins spent on hints
    game_badges    badges earned (each once)

XP, level, coins and streak are not stored: backend/game.py computes them from these rows,
so they can never drift out of step with what the student actually did.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any, Optional

from sqlalchemy import (
    Boolean, Column, DateTime, Integer, MetaData, String, Table, Text, UniqueConstraint, func, select,
)

from backend.memory.db import get_engine

_engine = get_engine()
_metadata = MetaData()

game_players = Table(
    "game_players", _metadata,
    Column("student_id", String(256), primary_key=True),
    Column("display_name", String(64), nullable=True),
    Column("companion_id", String(32), nullable=True),
    Column("created_at", DateTime, nullable=False),
)
game_sessions = Table(
    "game_sessions", _metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("student_id", String(256), nullable=False, index=True),
    Column("kind", String(16), nullable=False),            # pretest | lesson | posttest
    Column("concept", String(256), nullable=True),
    Column("started_at", DateTime, nullable=False),
    Column("finished_at", DateTime, nullable=True),
)
game_attempts = Table(
    "game_attempts", _metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("student_id", String(256), nullable=False, index=True),
    Column("session_id", Integer, nullable=True, index=True),
    Column("question_id", Integer, nullable=False),
    Column("concept", String(256), nullable=False),
    Column("source", String(16), nullable=False),          # pre | post | lesson
    Column("selected_index", Integer, nullable=True),
    Column("correct", Boolean, nullable=False),
    Column("misconception_id", String(64), nullable=True),
    Column("time_taken_ms", Integer, nullable=True),
    Column("hint_bought", Boolean, nullable=False, default=False),
    Column("created_at", DateTime, nullable=False),
)
coin_spends = Table(
    "coin_spends", _metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("student_id", String(256), nullable=False, index=True),
    Column("question_id", Integer, nullable=False),
    Column("amount", Integer, nullable=False),
    Column("created_at", DateTime, nullable=False),
)
game_badges = Table(
    "game_badges", _metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("student_id", String(256), nullable=False, index=True),
    Column("badge", String(64), nullable=False),
    Column("earned_at", DateTime, nullable=False),
    UniqueConstraint("student_id", "badge", name="uq_game_badge"),
)
_metadata.create_all(_engine)


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def local_date(stored: datetime) -> date:
    return stored.replace(tzinfo=timezone.utc).astimezone().date()


# ---- players ---------------------------------------------------------------------------

def get_player(student_id: str) -> dict[str, Any]:
    with _engine.connect() as c:
        row = c.execute(select(game_players).where(game_players.c.student_id == student_id)).mappings().first()
    return dict(row) if row else {"student_id": student_id, "display_name": None, "companion_id": None}


def save_player(student_id: str, display_name: Optional[str] = None, companion_id: Optional[str] = None) -> dict[str, Any]:
    current = get_player(student_id)
    values = {
        "display_name": display_name if display_name is not None else current.get("display_name"),
        "companion_id": companion_id if companion_id is not None else current.get("companion_id"),
    }
    with _engine.begin() as c:
        if current.get("created_at"):
            c.execute(game_players.update().where(game_players.c.student_id == student_id).values(**values))
        else:
            c.execute(game_players.insert().values(student_id=student_id, created_at=utcnow(), **values))
    return get_player(student_id)


# ---- sessions --------------------------------------------------------------------------

def start_session(student_id: str, kind: str, concept: Optional[str]) -> int:
    with _engine.begin() as c:
        return c.execute(
            game_sessions.insert().values(student_id=student_id, kind=kind, concept=concept, started_at=utcnow())
        ).inserted_primary_key[0]


def get_session(session_id: int) -> Optional[dict[str, Any]]:
    with _engine.connect() as c:
        row = c.execute(select(game_sessions).where(game_sessions.c.id == session_id)).mappings().first()
    return dict(row) if row else None


def finish_session(session_id: int) -> None:
    with _engine.begin() as c:
        c.execute(
            game_sessions.update()
            .where(game_sessions.c.id == session_id, game_sessions.c.finished_at.is_(None))
            .values(finished_at=utcnow())
        )


def finished_session_count(student_id: str) -> int:
    with _engine.connect() as c:
        return c.execute(
            select(func.count()).select_from(game_sessions)
            .where(game_sessions.c.student_id == student_id, game_sessions.c.finished_at.is_not(None))
        ).scalar_one()


# ---- attempts, coins, badges -----------------------------------------------------------

def record_attempt(**values: Any) -> int:
    with _engine.begin() as c:
        return c.execute(game_attempts.insert().values(created_at=utcnow(), **values)).inserted_primary_key[0]


def attempts(student_id: Optional[str] = None, session_id: Optional[int] = None) -> list[dict[str, Any]]:
    stmt = select(game_attempts).order_by(game_attempts.c.id)
    if student_id is not None:
        stmt = stmt.where(game_attempts.c.student_id == student_id)
    if session_id is not None:
        stmt = stmt.where(game_attempts.c.session_id == session_id)
    with _engine.connect() as c:
        return [dict(r) for r in c.execute(stmt).mappings()]


def misconception_seen_before(student_id: str, misconception_id: str) -> bool:
    with _engine.connect() as c:
        return c.execute(
            select(func.count()).select_from(game_attempts)
            .where(game_attempts.c.student_id == student_id, game_attempts.c.misconception_id == misconception_id)
        ).scalar_one() > 0


def spend_coins(student_id: str, question_id: int, amount: int) -> None:
    with _engine.begin() as c:
        c.execute(coin_spends.insert().values(student_id=student_id, question_id=question_id, amount=amount, created_at=utcnow()))


def hints_bought(student_id: str) -> int:
    with _engine.connect() as c:
        return c.execute(select(func.count()).select_from(coin_spends).where(coin_spends.c.student_id == student_id)).scalar_one()


def hint_bought_for(student_id: str, question_id: int) -> bool:
    with _engine.connect() as c:
        return c.execute(
            select(func.count()).select_from(coin_spends)
            .where(coin_spends.c.student_id == student_id, coin_spends.c.question_id == question_id)
        ).scalar_one() > 0


def badges(student_id: str) -> list[str]:
    with _engine.connect() as c:
        return [r[0] for r in c.execute(select(game_badges.c.badge).where(game_badges.c.student_id == student_id).order_by(game_badges.c.id))]


def award_badge(student_id: str, badge: str) -> bool:
    """True if this badge is new for the student."""
    if badge in badges(student_id):
        return False
    with _engine.begin() as c:
        c.execute(game_badges.insert().values(student_id=student_id, badge=badge, earned_at=utcnow()))
    return True


def all_player_ids() -> list[str]:
    with _engine.connect() as c:
        ids = {r[0] for r in c.execute(select(game_attempts.c.student_id).distinct())}
        ids |= {r[0] for r in c.execute(select(game_players.c.student_id))}
    return sorted(ids)
