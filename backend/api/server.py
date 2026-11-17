"""
server.py
---------
FastAPI backend for the web dashboards (frontend_web/simple,
frontend_web/gamified), replacing Streamlit as the primary UI. Every
endpoint below is a thin wrapper around existing backend functions -- no new
tutoring/grading/escalation logic lives here, only request/response shaping
and the small bit of per-student session state in sessions.py.

Run: uvicorn backend.api.server:app --reload --port 8000
"""

from __future__ import annotations

import logging
import time
from datetime import timezone
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from backend.agents.orchestrator import tutor_app
from backend.agents.tutor_planner import run_explain
from backend.api.auth import infer_role, is_valid_email
from backend.api.sessions import get_session
from backend.content import VARIANTS, get_quiz, grade_quiz, next_practice_question
from backend.llm import LLMError
from backend.evals.metrics import compute_all_metrics
from backend.memory.conversation_store import get_recent_messages, save_message
from backend.memory.eval_store import get_interactions, set_escalation_warranted
from backend.memory.graph_viz import build_prerequisite_graph_json
from backend.memory.quiz_store import (
    get_round_summary,
    next_round_number,
    record_attempt,
)
from backend.memory.spaced_repetition import get_due_reviews, get_schedule, schedule_next_review
from backend.memory.student_graph_store import load_student_profile, save_student_profile

app = FastAPI(title="Adaptive AI Tutor API")
logger = logging.getLogger("api")

# How far up the hint ladder each teaching strategy sits (0 = no ladder shown).
_LADDER_LEVELS = {"retry_prompt": 1, "small_clue": 1, "stronger_hint": 2, "worked_example": 3, "prerequisite_review": 3}

_REPO_ROOT = Path(__file__).resolve().parents[2]


# --------------------------------------------------------------------------- #
# Request bodies
# --------------------------------------------------------------------------- #

class LoginBody(BaseModel):
    email: str


class ChatBody(BaseModel):
    student_id: str
    concept: str
    message: str


class QuizStartBody(BaseModel):
    student_id: str
    concept: str
    variant: str  # "pre" | "post"


class QuizSkipBody(BaseModel):
    student_id: str
    concept: str
    variant: str


class QuizSubmitBody(BaseModel):
    student_id: str
    concept: str
    variant: str
    selected_indices: list[Optional[int]]


class EscalationReviewBody(BaseModel):
    student_id: str
    id: int
    warranted: bool


# --------------------------------------------------------------------------- #
# Shared helpers
# --------------------------------------------------------------------------- #

def _hint_ladder_payload(final_state: dict[str, Any]) -> dict[str, Any]:
    if "escalation_result" in final_state:
        return {"kind": "note", "text": "Escalated to teacher — this has been flagged for follow-up."}
    strategy = (final_state.get("tutor_plan_result") or {}).get("applied_strategy") or final_state.get(
        "recommended_strategy"
    )
    level = _LADDER_LEVELS.get(strategy or "", 0)
    if level == 0:
        return {"kind": "none"}
    return {
        "kind": "steps",
        "current_index": level - 1,
        "labels": ["Small clue", "Stronger hint", "Worked example"],
    }


def _check_variant(variant: str) -> None:
    if variant not in VARIANTS:
        raise HTTPException(status_code=400, detail="variant must be 'pre' or 'post'.")


def _with_schedule(profile: dict[str, Any], student_id: str) -> dict[str, Any]:
    """Adds next_review / last_practiced (YYYY-MM-DD) to each mastery entry, as the UI expects."""
    for row in get_schedule(student_id):
        entry = (profile.get("concept_mastery") or {}).get(row["concept"])
        if entry is not None:
            entry["next_review"] = str(row["next_review_at"])[:10]
            entry["last_practiced"] = str(row["last_reviewed_at"])[:10]
    return profile


def _round_scores(student_id: str, concept: str, round_number: Optional[int]) -> tuple[Optional[list[int]], Optional[list[int]]]:
    """Returns ([correct, total], [correct, total]) for pre/post of a round, or (None, None) entries not yet attempted."""
    if round_number is None:
        return None, None
    summary = get_round_summary(student_id, concept, round_number)
    pre = None
    if summary["pre_count"]:
        pre = [round(summary["pre_score"] * summary["pre_count"]), summary["pre_count"]]
    post = None
    if summary["post_count"]:
        post = [round(summary["post_score"] * summary["post_count"]), summary["post_count"]]
    return pre, post


_PCT_METRIC_KEYS = {"misconception_recall", "adaptation_quality", "escalation_precision", "hint_quality"}
_DELTA_METRIC_KEYS = {"learning_gain", "memory_usefulness"}

_METRIC_LABELS = {
    "learning_gain": "Learning gain",
    "misconception_recall": "Misconception recall",
    "adaptation_quality": "Adaptation quality",
    "escalation_precision": "Escalation precision",
    "memory_usefulness": "Memory usefulness",
    "hint_quality": "Hint quality",
}
_METRIC_DESCRIPTIONS = {   # worded exactly as on the reference's Eval metrics screen
    "learning_gain": "Avg. pre-test → post-test percentage-point change this session.",
    "misconception_recall": "Share of flagged prerequisite gaps the system correctly recognized as already-known.",
    "adaptation_quality": "Share of post-miss turns where hint strength held steady or escalated, never regressed.",
    "escalation_precision": "Share of teacher-reviewed escalations confirmed as warranted.",
    "memory_usefulness": "Correctness-rate change, second half vs. first half of each concept's attempts this session.",
    "hint_quality": "Share of hint-ladder turns generated cleanly, without the answer-leak guard intervening.",
}


def _fmt_metric(key: str, metric: dict[str, Any]) -> dict[str, Any]:
    value = metric["value"]
    if key in _PCT_METRIC_KEYS:
        display = f"{value * 100:.0f}%" if value is not None else "—"
        status = "unknown" if value is None else ("good" if value >= 0.7 else "warn" if value >= 0.4 else "critical")
    else:
        display = (f"{'+' if value >= 0 else ''}{value * 100:.0f} pts") if value is not None else "—"
        status = "unknown" if value is None else ("good" if value >= 0.1 else "warn" if value >= 0 else "critical")
    return {
        "label": _METRIC_LABELS[key],
        "display": display,
        "status": status,
        "description": _METRIC_DESCRIPTIONS[key],
    }


def _escalation_row(row: dict[str, Any]) -> dict[str, Any]:
    trigger_type = row.get("trigger_type")
    if not trigger_type:   # rows logged before trigger_type existed
        trigger_type = (
            "Cheating risk" if row.get("cheating_risk_detected")
            else "Distress" if row.get("distress_detected")
            else "Repeated failure"
        )
    created = row["created_at"]
    if created.tzinfo is None:
        created = created.replace(tzinfo=timezone.utc)
    return {
        "id": row["id"],
        "time": created.astimezone().strftime("%d %b %H:%M"),
        "topic": row["concept"],
        "trigger": (row.get("teacher_summary") or f"{trigger_type} on {row['concept']}")[:300],
        "misses": row.get("consecutive_misses_before", 0),
        "trigger_type": trigger_type,
        "warranted": row.get("warranted"),
    }


# --------------------------------------------------------------------------- #
# Auth
# --------------------------------------------------------------------------- #

@app.post("/api/login")
def login(body: LoginBody) -> dict[str, Any]:
    email = body.email.strip().lower()
    if not is_valid_email(email):
        raise HTTPException(status_code=400, detail="Enter a valid email address.")
    return {"student_id": email, "role": infer_role(email)}


# --------------------------------------------------------------------------- #
# Student: state + chat
# --------------------------------------------------------------------------- #

@app.get("/api/state")
def get_state(student_id: str, concept: Optional[str] = None) -> dict[str, Any]:
    session = get_session(student_id)
    history = get_recent_messages(student_id)
    messages = (
        [{"role": m["role"], "content": m["content"]} for m in history]
        if history
        else [{"role": "assistant", "content": "Hi! What would you like to learn today?"}]
    )
    profile = load_student_profile(student_id)
    due_for_review = [row["concept"] for row in get_due_reviews(student_id)]

    pre_test_scores: dict[str, Any] = {}
    post_test_scores: dict[str, Any] = {}
    if concept is not None:
        round_number = session.quiz_round.get(concept)
        pre, post = _round_scores(student_id, concept, round_number)
        if pre is not None:
            pre_test_scores[concept] = pre
        if post is not None:
            post_test_scores[concept] = post

    return {
        "messages": messages,
        "profile": _with_schedule(profile, student_id),
        "active_question": session.active_question(concept),
        "pre_test_scores": pre_test_scores,
        "post_test_scores": post_test_scores,
        "due_for_review": due_for_review,
        "hint_ladder": session.last_hint_ladder,
    }


def _start_practice(session, concept: str) -> Optional[str]:
    """Makes the next practice question for this topic the problem in progress; returns its text."""
    asked = session.asked.setdefault(concept, [])
    q = next_practice_question(concept, asked)
    if q is None:
        session.active.pop(concept, None)
        return None
    asked.append(q["id"])
    session.active[concept] = {"question": q["question"], "answer": q["answer"], "exact": bool(q.get("exact")), "id": q["id"]}
    return q["question"]


@app.post("/api/chat")
def chat(body: ChatBody) -> dict[str, Any]:
    message = body.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Type a message first.")
    session = get_session(body.student_id)
    response_time_seconds = (
        time.time() - session.last_tutor_message_at if session.last_tutor_message_at is not None else None
    )
    profile = load_student_profile(body.student_id)
    active = session.active.get(body.concept)
    escalated = False
    hint_ladder: dict[str, Any] = {"kind": "none"}

    try:
        if active is None:
            result = run_explain(current_concept=body.concept, student_question=message, student_memory_profile=profile)
            reply = result["hint_text"]
            question = _start_practice(session, body.concept)
            if question:
                reply += f"\n\n**Try this:** {question}"
        else:
            final_state = tutor_app.invoke(
                {
                    "student_id": body.student_id,
                    "current_question": active["question"],
                    "current_concept": body.concept,
                    "student_response": message,
                    "student_memory_profile": profile,
                    "response_time_seconds": response_time_seconds,
                    "reference_answer": active.get("answer"),
                    "exact_form": bool(active.get("exact")),
                }
            )
            reply = final_state.get("hint_text") or "I'm not sure how to respond to that. Could you rephrase?"
            profile = final_state.get("student_memory_profile") or profile
            escalated = "escalation_result" in final_state
            hint_ladder = _hint_ladder_payload(final_state)
            if escalated:
                session.active.pop(body.concept, None)      # the teacher takes it from here
            elif "diagnostic_result" not in final_state:    # correct: move on to a new problem
                question = _start_practice(session, body.concept)
                if question:
                    reply += f"\n\n**Try this:** {question}"
            # otherwise the same problem stays open, so the hint ladder can climb
    except LLMError as exc:
        # Nothing was graded or recorded, so an outage never counts against the student.
        logger.warning("Model unavailable during chat: %s", exc)
        raise HTTPException(
            status_code=503,
            detail="The tutor's AI model isn't responding right now. Your answer was not marked; please try again in a moment.",
        ) from exc

    save_message(body.student_id, "user", message, concept=body.concept)
    save_message(body.student_id, "assistant", reply, concept=body.concept)
    session.last_tutor_message_at = time.time()
    session.last_hint_ladder = hint_ladder

    return {
        "reply": reply,
        "active_question": session.active_question(body.concept),
        "hint_ladder": hint_ladder,
        "profile": _with_schedule(profile, body.student_id),
        "escalated": escalated,
    }


# --------------------------------------------------------------------------- #
# Student: pre/post-test quizzes (free-text, EvaluatorAgent-graded)
# --------------------------------------------------------------------------- #

@app.post("/api/quiz/start")
def quiz_start(body: QuizStartBody) -> dict[str, Any]:
    _check_variant(body.variant)
    session = get_session(body.student_id)
    if body.concept not in session.quiz_round:
        session.quiz_round[body.concept] = next_round_number(body.student_id, body.concept)
    return {
        "questions": [
            {"question_id": q["id"], "question": q["question"], "choices": q["choices"]}
            for q in get_quiz(body.concept, body.variant)
        ]
    }


@app.post("/api/quiz/skip")
def quiz_skip(body: QuizSkipBody) -> dict[str, Any]:
    session = get_session(body.student_id)
    if body.concept not in session.quiz_round:
        session.quiz_round[body.concept] = next_round_number(body.student_id, body.concept)
    return {"ok": True}


@app.post("/api/quiz/submit")
def quiz_submit(body: QuizSubmitBody) -> dict[str, Any]:
    _check_variant(body.variant)
    session = get_session(body.student_id)
    round_number = session.quiz_round.get(body.concept)
    if round_number is None:
        round_number = next_round_number(body.student_id, body.concept)
        session.quiz_round[body.concept] = round_number

    results = grade_quiz(body.concept, body.variant, body.selected_indices)
    if not results:
        raise HTTPException(status_code=404, detail="No quiz questions are available for this topic.")
    for r in results:
        record_attempt(
            body.student_id, body.concept, round_number, body.variant, r["question_id"], r["picked_text"], r["correct"]
        )
    correct_count = sum(1 for r in results if r["correct"])
    total = len(results)

    if body.variant == "pre":
        # The placement score seeds mastery only for a topic the student has not
        # practised yet, so retaking it never wipes progress earned in tutoring.
        profile = load_student_profile(body.student_id)
        mastery = profile.setdefault("concept_mastery", {})
        if body.concept not in mastery:
            score = correct_count / total
            mastery[body.concept] = {"mastery": score, "consecutive_misses": 0}
            save_student_profile(body.student_id, profile)
            schedule_next_review(body.student_id, body.concept, score)
    else:
        session.quiz_round.pop(body.concept, None)

    return {"correct": correct_count, "total": total}


# --------------------------------------------------------------------------- #
# Teacher (and profile/self-view): lookup, metrics, graph, escalations
# --------------------------------------------------------------------------- #

@app.get("/api/profile")
def get_profile(student_id: str) -> dict[str, Any]:
    return {
        "profile": _with_schedule(load_student_profile(student_id), student_id),
        "due_for_review": [row["concept"] for row in get_due_reviews(student_id)],
    }


@app.get("/api/eval-metrics")
def eval_metrics(student_id: Optional[str] = None) -> dict[str, Any]:
    metrics = compute_all_metrics(student_id)
    order = ["learning_gain", "misconception_recall", "adaptation_quality", "escalation_precision", "memory_usefulness", "hint_quality"]
    return {"metrics": [_fmt_metric(key, metrics[key]) for key in order]}


@app.get("/api/misconception-graph")
def misconception_graph(concept: str, student_id: Optional[str] = None) -> dict[str, Any]:
    profile = load_student_profile(student_id) if student_id else {}
    return build_prerequisite_graph_json(concept, profile)


@app.get("/api/schedule")
def schedule(student_id: str) -> dict[str, Any]:
    return {"schedule": get_schedule(student_id)}


@app.get("/api/escalations")
def escalations(student_id: str) -> dict[str, Any]:
    rows = [r for r in get_interactions(student_id) if r.get("escalated")]
    return {"escalations": [_escalation_row(r) for r in rows]}


@app.post("/api/escalations/review")
def escalations_review(body: EscalationReviewBody) -> dict[str, Any]:
    ok = set_escalation_warranted(body.id, body.warranted)
    if not ok:
        raise HTTPException(status_code=404, detail="Escalation not found.")
    return {"ok": True}


# --------------------------------------------------------------------------- #
# Static frontends (mounted last so /api/* routes above take precedence)
# --------------------------------------------------------------------------- #

app.mount("/gamified", StaticFiles(directory=_REPO_ROOT / "frontend_web" / "gamified", html=True), name="gamified")
app.mount("/", StaticFiles(directory=_REPO_ROOT / "frontend_web" / "simple", html=True), name="simple")
