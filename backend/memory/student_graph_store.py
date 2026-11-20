"""
student_graph_store.py
----------------------
Loads and saves each student's memory profile.

Every agent and the LangGraph pipeline see one dict shape:

    {"student_id", "concept_mastery": {concept: {"mastery", "consecutive_misses"}},
     "weak_prerequisites": [...], "recent_attempts": [{"concept", "correct"}]}

This module is the only place that knows where that dict is stored. It lives
in the same SQL database as the rest of the tutor's memory (SQLite by
default), so a student's progress survives restarts with nothing else to
install. Two tables:

    concept_state    one row per (student, concept): mastery, consecutive_misses
    student_profile  one row per student: weak prerequisites and recent attempts (JSON)
"""

from __future__ import annotations

import json
import logging
from typing import Any

from sqlalchemy import Column, Float, Integer, MetaData, String, Table, Text, UniqueConstraint, delete, select

from backend.memory.db import get_engine

logger = logging.getLogger("student_graph_store")

DEFAULT_MASTERY = 0.3

_engine = get_engine()
_metadata = MetaData()

concept_state = Table(
    "concept_state",
    _metadata,
    Column("id", Integer, primary_key=True),
    Column("student_id", String(128), nullable=False, index=True),
    Column("concept", String(256), nullable=False),
    Column("mastery", Float, nullable=False, default=DEFAULT_MASTERY),
    Column("consecutive_misses", Integer, nullable=False, default=0),
    UniqueConstraint("student_id", "concept", name="uq_concept_state_student_concept"),
)

student_profile = Table(
    "student_profile",
    _metadata,
    Column("student_id", String(128), primary_key=True),
    Column("weak_prerequisites_json", Text, nullable=False, default="[]"),
    Column("recent_attempts_json", Text, nullable=False, default="[]"),
)

_metadata.create_all(_engine)


def _empty_profile(student_id: str) -> dict:
    return {
        "student_id": student_id,
        "concept_mastery": {},
        "weak_prerequisites": [],
        "recent_attempts": [],
    }


def load_student_profile(student_id: str) -> dict:
    """The student's profile, or a fresh empty one if they have no history yet."""
    profile = _empty_profile(student_id)
    try:
        with _engine.connect() as conn:
            for row in conn.execute(select(concept_state).where(concept_state.c.student_id == student_id)).mappings():
                profile["concept_mastery"][row["concept"]] = {
                    "mastery": row["mastery"],
                    "consecutive_misses": row["consecutive_misses"],
                }
            extra = conn.execute(select(student_profile).where(student_profile.c.student_id == student_id)).mappings().first()
            if extra:
                profile["weak_prerequisites"] = json.loads(extra["weak_prerequisites_json"] or "[]")
                profile["recent_attempts"] = json.loads(extra["recent_attempts_json"] or "[]")
    except Exception as exc:  # noqa: BLE001 - a read failure returns a safe empty profile, never crashes a turn
        logger.warning("load_student_profile(%r) failed: %s", student_id, exc)
        return _empty_profile(student_id)
    return profile


def save_student_profile(student_id: str, profile: dict[str, Any]) -> None:
    """Replaces the stored profile with this one, in a single transaction."""
    try:
        with _engine.begin() as conn:
            conn.execute(delete(concept_state).where(concept_state.c.student_id == student_id))
            rows = [
                {
                    "student_id": student_id,
                    "concept": concept,
                    "mastery": float(data.get("mastery", DEFAULT_MASTERY)),
                    "consecutive_misses": int(data.get("consecutive_misses", 0)),
                }
                for concept, data in (profile.get("concept_mastery") or {}).items()
            ]
            if rows:
                conn.execute(concept_state.insert(), rows)
            conn.execute(delete(student_profile).where(student_profile.c.student_id == student_id))
            conn.execute(
                student_profile.insert(),
                {
                    "student_id": student_id,
                    "weak_prerequisites_json": json.dumps(profile.get("weak_prerequisites") or []),
                    "recent_attempts_json": json.dumps(profile.get("recent_attempts") or []),
                },
            )
    except Exception as exc:  # noqa: BLE001 - a failed save must not break the tutoring turn
        logger.warning("save_student_profile(%r) failed: %s", student_id, exc)


if __name__ == "__main__":
    demo = {
        "student_id": "stu_test_1024",
        "concept_mastery": {"Fractions": {"mastery": 0.42, "consecutive_misses": 1}},
        "weak_prerequisites": ["Common Denominators"],
        "recent_attempts": [{"concept": "Fractions", "correct": False}],
    }
    save_student_profile(demo["student_id"], demo)
    print(json.dumps(load_student_profile(demo["student_id"]), indent=2))
