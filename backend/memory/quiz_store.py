"""
quiz_store.py
-------------
Caches quiz questions per concept and records every pre/post-test attempt —
the persistence behind the "pre-test to post-test learning gain" measurement
(judging metric #1). Every pretest/post-test cycle for a student+concept is
its own numbered "round", so learning gain is queryable across multiple
rounds over time (explicit wording in the problem statement), not just
within a single session.

Backed by the shared SQLAlchemy engine (backend/memory/db.py) — same
database as conversation_store.py.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    func,
    select,
)

from backend.memory.db import get_engine

logger = logging.getLogger("quiz_store")
logging.basicConfig(level=logging.INFO)

_engine = get_engine()
_metadata = MetaData()

quiz_attempts = Table(
    "quiz_attempts",
    _metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("student_id", String(128), nullable=False, index=True),
    Column("concept", String(256), nullable=False, index=True),
    Column("round_number", Integer, nullable=False),
    Column("phase", String(8), nullable=False),  # "pre" | "post"
    Column("question_id", Integer, nullable=False),
    Column("student_answer", Text, nullable=False),
    Column("is_correct", Boolean, nullable=False),
    Column("created_at", DateTime, nullable=False),
)


def init_db() -> None:
    """Creates the quiz tables if they don't already exist. Idempotent."""
    _metadata.create_all(_engine)


# Tables must exist before any read/write call.
init_db()


def record_attempt(
    student_id: str,
    concept: str,
    round_number: int,
    phase: str,
    question_id: int,
    student_answer: str,
    is_correct: bool,
) -> None:
    """Records one graded quiz answer. Failures are logged, not raised."""
    try:
        with _engine.begin() as conn:
            conn.execute(
                quiz_attempts.insert().values(
                    student_id=student_id,
                    concept=concept,
                    round_number=round_number,
                    phase=phase,
                    question_id=question_id,
                    student_answer=student_answer,
                    is_correct=is_correct,
                    created_at=datetime.now(timezone.utc),
                )
            )
    except Exception as exc:  # noqa: BLE001
        logger.warning("record_attempt failed for student_id=%r: %s", student_id, exc)


def next_round_number(student_id: str, concept: str) -> int:
    """Returns 1 + the highest round_number already recorded, or 1 if none exist."""
    try:
        with _engine.connect() as conn:
            stmt = select(func.max(quiz_attempts.c.round_number)).where(
                quiz_attempts.c.student_id == student_id,
                quiz_attempts.c.concept == concept,
            )
            current_max = conn.execute(stmt).scalar()
        return (current_max or 0) + 1
    except Exception as exc:  # noqa: BLE001
        logger.warning("next_round_number failed for student_id=%r: %s", student_id, exc)
        return 1


def get_all_rounds(student_id: Optional[str] = None) -> list[dict[str, Any]]:
    """
    Returns every (student_id, concept, round_number) group that has at
    least one recorded attempt, each with its pre/post scores — the raw
    material for the eval dashboard's learning-gain metric across every
    round, not just one lookup. student_id=None returns every student's
    rounds. Returns [] on failure rather than raising.
    """
    try:
        with _engine.connect() as conn:
            stmt = select(
                quiz_attempts.c.student_id,
                quiz_attempts.c.concept,
                quiz_attempts.c.round_number,
            ).distinct()
            if student_id is not None:
                stmt = stmt.where(quiz_attempts.c.student_id == student_id)
            groups = conn.execute(stmt).all()
    except Exception as exc:  # noqa: BLE001
        logger.warning("get_all_rounds failed for student_id=%r: %s", student_id, exc)
        return []

    rounds = []
    for sid, concept, round_number in groups:
        summary = get_round_summary(sid, concept, round_number)
        rounds.append(
            {
                "student_id": sid,
                "concept": concept,
                "round_number": round_number,
                **summary,
            }
        )
    return rounds


def get_round_summary(student_id: str, concept: str, round_number: int) -> dict[str, Any]:
    """
    Returns {"pre_score", "post_score", "pre_count", "post_count"} for a
    given round — pre_score/post_score are fractions correct (0.0-1.0) or
    None if that phase hasn't been attempted yet. Raw material for the
    reveal card, and later the eval dashboard's learning-gain chart.
    """
    summary: dict[str, Any] = {
        "pre_score": None,
        "post_score": None,
        "pre_count": 0,
        "post_count": 0,
    }
    try:
        with _engine.connect() as conn:
            for phase in ("pre", "post"):
                stmt = select(quiz_attempts.c.is_correct).where(
                    quiz_attempts.c.student_id == student_id,
                    quiz_attempts.c.concept == concept,
                    quiz_attempts.c.round_number == round_number,
                    quiz_attempts.c.phase == phase,
                )
                results = [row[0] for row in conn.execute(stmt).all()]
                if results:
                    summary[f"{phase}_score"] = sum(results) / len(results)
                    summary[f"{phase}_count"] = len(results)
    except Exception as exc:  # noqa: BLE001
        logger.warning("get_round_summary failed for student_id=%r: %s", student_id, exc)
    return summary


# --------------------------------------------------------------------------- #
# Standalone test
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    """
    $ ollama serve
    $ python -m backend.memory.quiz_store
    """
    import json

    test_student = "stu_quiz_test"
    test_concept = "Fractions"

    print("=" * 80)
    print("Fetching/generating questions (requires Ollama)...")
    questions = get_or_generate_questions(test_concept, n=3)
    print(json.dumps(questions, indent=2))

    round_num = next_round_number(test_student, test_concept)
    print(f"\nRound number: {round_num}")

    print("\nRecording a mock pre-test (2 correct, 1 wrong)...")
    for i, q in enumerate(questions):
        record_attempt(
            test_student,
            test_concept,
            round_num,
            "pre",
            q["id"],
            "mock answer",
            is_correct=(i != 0),
        )

    summary = get_round_summary(test_student, test_concept, round_num)
    print("\nRound summary:")
    print(json.dumps(summary, indent=2))
    print("=" * 80)
