"""
Curated content the tutor draws on. For now: the multiple-choice question bank
used by the placement check (pre) and the post-test.

Every question has a stable numeric id, four choices and the index of the
correct one, so grading is instant and never needs the AI model.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

_QUESTIONS_FILE = Path(__file__).with_name("questions.json")
VARIANTS = ("pre", "post")


@lru_cache(maxsize=1)
def _bank() -> dict[str, dict[str, list[dict[str, Any]]]]:
    return json.loads(_QUESTIONS_FILE.read_text(encoding="utf-8"))


def topics() -> list[str]:
    return list(_bank())


def get_quiz(concept: str, variant: str) -> list[dict[str, Any]]:
    """Questions for one topic and variant ("pre" or "post"); [] if the topic has no bank."""
    if variant not in VARIANTS:
        raise ValueError(f"variant must be one of {VARIANTS}, got {variant!r}")
    return list(_bank().get(concept, {}).get(variant, []))


def grade_quiz(concept: str, variant: str, selected_indices: list[int | None]) -> list[dict[str, Any]]:
    """One result per question: the question, what was picked and whether it was right."""
    results = []
    questions = get_quiz(concept, variant)
    for i, q in enumerate(questions):
        picked = selected_indices[i] if i < len(selected_indices) else None
        valid = isinstance(picked, int) and 0 <= picked < len(q["choices"])
        results.append(
            {
                "question_id": q["id"],
                "picked_text": q["choices"][picked] if valid else "",
                "correct": bool(valid and picked == q["answer"]),
            }
        )
    return results


# --------------------------------------------------------------------------- #
# Practice questions for the tutoring chat (separate from the quiz sets, so
# tutoring never rehearses the exact post-test questions)
# --------------------------------------------------------------------------- #

@lru_cache(maxsize=1)
def _practice() -> dict[str, list[dict[str, Any]]]:
    return json.loads(Path(__file__).with_name("practice.json").read_text(encoding="utf-8"))


def next_practice_question(concept: str, asked_ids: list[int]) -> dict[str, Any] | None:
    """The first practice question for this topic not asked yet; starts over once all were asked."""
    bank = _practice().get(concept) or []
    if not bank:
        return None
    for q in bank:
        if q["id"] not in asked_ids:
            return q
    return bank[len(asked_ids) % len(bank)]


# --------------------------------------------------------------------------- #
# Game content: misconception catalogue, lessons, and lookup of any multiple-
# choice question (quiz bank or lessons) by id
# --------------------------------------------------------------------------- #

def _load_optional(name: str) -> dict:
    path = Path(__file__).with_name(name)
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


@lru_cache(maxsize=1)
def misconceptions() -> dict[str, dict[str, str]]:
    return _load_optional("misconceptions.json")


@lru_cache(maxsize=1)
def lessons() -> dict[str, dict[str, Any]]:
    return _load_optional("lessons.json")


@lru_cache(maxsize=1)
def _mcq_index() -> dict[int, dict[str, Any]]:
    """Every multiple-choice question by id, with its topic and where it comes from."""
    index: dict[int, dict[str, Any]] = {}
    for topic, sets in _bank().items():
        for variant, questions in sets.items():
            for q in questions:
                index[q["id"]] = {**q, "concept": topic, "source": variant}
    for topic, lesson in lessons().items():
        for q in lesson.get("questions", []):
            index[q["id"]] = {**q, "concept": topic, "source": "lesson"}
    return index


def find_question(question_id: int) -> dict[str, Any] | None:
    return _mcq_index().get(question_id)


def public_question(q: dict[str, Any]) -> dict[str, Any]:
    """What the browser may see: never the answer, the clue or the feedback."""
    return {"question_id": q["id"], "concept": q["concept"], "question": q["question"], "choices": q["choices"]}


def game_quiz(variant: str) -> list[dict[str, Any]]:
    """The game's placement check / post-test: the first question of each topic for that variant."""
    if variant not in VARIANTS:
        raise ValueError(f"variant must be one of {VARIANTS}")
    out = []
    for topic in topics():
        questions = get_quiz(topic, variant)
        if questions:
            out.append(find_question(questions[0]["id"]))
    return out
