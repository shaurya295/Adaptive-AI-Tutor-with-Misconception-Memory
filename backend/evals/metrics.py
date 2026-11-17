"""
metrics.py
----------
The six evaluation metrics on the teacher's "Eval metrics" screen, each
computed exactly as the screen describes it. Pure functions over the turn log
(backend/memory/eval_store.interaction_log) and the quiz attempts
(backend/memory/quiz_store); no model calls.

Each returns {"value": float | None, "sample_size": int, "label": str}.
value is None when there is not enough data yet.

1. Learning gain          mean (post-test % - pre-test %) over finished rounds
2. Misconception recall   of turns that flagged a prerequisite gap, the share where
                          that gap was already on the student's record
3. Adaptation quality     of hint turns that follow a hint turn on the same concept,
                          the share whose hint strength held steady or rose
4. Escalation precision   of escalations a teacher has reviewed, the share marked warranted
5. Memory usefulness      per concept with 4+ graded turns: correct rate in the later
                          half minus the earlier half, averaged over concepts
6. Hint quality           of hint turns, the share written without the answer-leak
                          guard stepping in
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Optional

from backend.memory.eval_store import get_interactions
from backend.memory.quiz_store import get_all_rounds


def _metric(value: Optional[float], sample_size: int, label: str) -> dict[str, Any]:
    return {"value": value, "sample_size": sample_size, "label": label}


def learning_gain(student_id: Optional[str] = None) -> dict[str, Any]:
    gains = [
        r["post_score"] - r["pre_score"]
        for r in get_all_rounds(student_id)
        if r.get("pre_score") is not None and r.get("post_score") is not None
    ]
    value = sum(gains) / len(gains) if gains else None
    return _metric(value, len(gains), "Avg. post-test minus pre-test score per finished round")


def misconception_recall(student_id: Optional[str] = None, rows: Optional[list] = None) -> dict[str, Any]:
    rows = rows if rows is not None else get_interactions(student_id)
    flagged = [r for r in rows if r.get("missing_prerequisite") and r.get("prereq_known_before") is not None]
    value = sum(1 for r in flagged if r["prereq_known_before"]) / len(flagged) if flagged else None
    return _metric(value, len(flagged), "Flagged prerequisite gaps already on record")


def adaptation_quality(student_id: Optional[str] = None, rows: Optional[list] = None) -> dict[str, Any]:
    rows = rows if rows is not None else get_interactions(student_id)
    last_level: dict[tuple, int] = {}
    held = total = 0
    for r in rows:                                   # oldest first
        key = (r["student_id"], r["concept"])
        if r["path"] != "hint" or r.get("hint_level") is None:
            if r["path"] != "hint":
                last_level.pop(key, None)            # a correct answer or a hand-off ends the run of hints
            continue
        if key in last_level:
            total += 1
            held += r["hint_level"] >= last_level[key]
        last_level[key] = r["hint_level"]
    return _metric(held / total if total else None, total, "Post-miss hints that held or raised their strength")


def escalation_precision(student_id: Optional[str] = None, rows: Optional[list] = None) -> dict[str, Any]:
    rows = rows if rows is not None else get_interactions(student_id)
    reviewed = [r for r in rows if r["escalated"] and r.get("warranted") is not None]
    value = sum(1 for r in reviewed if r["warranted"]) / len(reviewed) if reviewed else None
    return _metric(value, len(reviewed), "Teacher-reviewed escalations marked warranted")


def memory_usefulness(student_id: Optional[str] = None, rows: Optional[list] = None) -> dict[str, Any]:
    rows = rows if rows is not None else get_interactions(student_id)
    by_concept: dict[tuple, list[bool]] = defaultdict(list)
    for r in rows:
        if r.get("answer_correct") is not None:
            by_concept[(r["student_id"], r["concept"])].append(bool(r["answer_correct"]))
    changes = []
    for results in by_concept.values():
        if len(results) >= 4:
            half = len(results) // 2
            early, late = results[:half], results[-half:]
            changes.append(sum(late) / len(late) - sum(early) / len(early))
    value = sum(changes) / len(changes) if changes else None
    return _metric(value, len(changes), "Correct-rate change, later vs earlier attempts per concept")


def hint_quality(student_id: Optional[str] = None, rows: Optional[list] = None) -> dict[str, Any]:
    rows = rows if rows is not None else get_interactions(student_id)
    hints = [r for r in rows if r["path"] == "hint" and r.get("leak_guard_triggered") is not None]
    value = sum(1 for r in hints if not r["leak_guard_triggered"]) / len(hints) if hints else None
    return _metric(value, len(hints), "Hints written without the answer-leak guard intervening")


def compute_all_metrics(student_id: Optional[str] = None) -> dict[str, dict[str, Any]]:
    rows = get_interactions(student_id)
    return {
        "learning_gain": learning_gain(student_id),
        "misconception_recall": misconception_recall(rows=rows),
        "adaptation_quality": adaptation_quality(rows=rows),
        "escalation_precision": escalation_precision(rows=rows),
        "memory_usefulness": memory_usefulness(rows=rows),
        "hint_quality": hint_quality(rows=rows),
    }
