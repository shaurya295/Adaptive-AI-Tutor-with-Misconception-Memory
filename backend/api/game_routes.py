"""
game_routes.py
--------------
API for the gamified dashboard (PixelTutor). Mounted by server.py under /api.

Every multiple-choice answer is graded here, instantly, against the content bank (no AI
call), and it updates the same student record the Simple dashboard and the teacher screens
use: topic mastery, review schedule and the turn log behind the teacher's metrics. Three
wrong answers in a row on a topic (the hearts) notify the teacher.
"""

from __future__ import annotations

import re
import secrets
from collections import defaultdict
from datetime import timedelta
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, Field

from backend import content, game
from backend.api.auth import Caller, current_caller, start_session as start_auth_session
from backend.memory import game_store as store
from backend.memory.eval_store import get_interactions, record_interaction
from backend.memory.spaced_repetition import get_due_reviews, schedule_next_review
from backend.memory.student_graph_store import load_student_profile, save_student_profile
from backend.memory.student_profile import DEFAULT_MASTERY, MASTERY_DECREMENT, MASTERY_INCREMENT, MAX_RECENT_ATTEMPTS

router = APIRouter(prefix="/api")
WHO = Depends(current_caller)
KINDS = ("pretest", "lesson", "posttest")


# ---------------------------------------------------------------------------- helpers

def _misses(student_id: str, concept: Optional[str]) -> int:
    if not concept:
        return 0
    entry = (load_student_profile(student_id).get("concept_mastery") or {}).get(concept) or {}
    return entry.get("consecutive_misses", 0)


def hud(student_id: str, concept: Optional[str] = None) -> dict[str, Any]:
    rows = store.attempts(student_id)
    xp = game.total_xp(r["correct"] for r in rows)
    level, pct = game.level_of(xp)
    return {
        "level": level,
        "xp": xp,
        "xp_pct": pct,
        "coins": game.coins_balance(sum(r["correct"] for r in rows), store.finished_session_count(student_id), store.hints_bought(student_id)),
        "streak": game.streak_days({store.local_date(r["created_at"]) for r in rows}, store.local_date(store.utcnow())),
        "hearts": game.hearts_left(_misses(student_id, concept)),
        "max_hearts": game.MAX_HEARTS,
        "badges": store.badges(student_id),
    }


def _display_name(student_id: str) -> str:
    return store.get_player(student_id).get("display_name") or student_id.split("@")[0]


def _choose_topic(student_id: str) -> tuple[str, str]:
    """Due for review first, otherwise the weakest (or untried) topic."""
    topics = content.topics()
    due = [r["concept"] for r in get_due_reviews(student_id) if r["concept"] in topics]
    if due:
        return due[0], "due for review"
    mastery = load_student_profile(student_id).get("concept_mastery") or {}
    weakest = min(topics, key=lambda t: (mastery.get(t) or {}).get("mastery", -1))
    return weakest, "new topic" if weakest not in mastery else "your weakest topic"


# ---------------------------------------------------------------------------- identity

class GuestBody(BaseModel):
    name: str = Field(min_length=1, max_length=20)


@router.post("/auth/guest")
def guest_sign_in(body: GuestBody, response: Response) -> dict[str, Any]:
    """The game's own sign-in screen: a hero name, no email. Creates a guest student."""
    name = " ".join(body.name.split())[:20]
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "hero"
    student_id = f"{slug}-{secrets.token_hex(3)}@guest.pixeltutor"
    store.save_player(student_id, display_name=name)
    start_auth_session(response, student_id, "student")
    return {"student_id": student_id, "role": "student", "display_name": name}


class MeBody(BaseModel):
    display_name: Optional[str] = Field(default=None, max_length=20)
    companion_id: Optional[str] = Field(default=None, max_length=32)


@router.get("/me")
def me(concept: Optional[str] = None, caller: Caller = WHO) -> dict[str, Any]:
    player = store.get_player(caller.email)
    return {
        "student_id": caller.email,
        "role": caller.role,
        "display_name": _display_name(caller.email),
        "companion_id": player.get("companion_id"),
        "hud": hud(caller.email, concept),
        "due_count": len(get_due_reviews(caller.email)),
    }


@router.patch("/me")
def update_me(body: MeBody, caller: Caller = WHO) -> dict[str, Any]:
    name = " ".join(body.display_name.split()) if body.display_name else None
    store.save_player(caller.email, display_name=name or None, companion_id=body.companion_id)
    return me(caller=caller)


# ---------------------------------------------------------------------------- questions

@router.get("/game/quiz")
def game_quiz(variant: str, caller: Caller = WHO) -> dict[str, Any]:
    if variant not in content.VARIANTS:
        raise HTTPException(status_code=400, detail="variant must be 'pre' or 'post'.")
    return {"questions": [content.public_question(q) for q in content.game_quiz(variant)]}


@router.get("/game/lesson")
def game_lesson(concept: Optional[str] = None, caller: Caller = WHO) -> dict[str, Any]:
    topics = content.topics()
    if concept and concept not in topics:
        raise HTTPException(status_code=404, detail="Unknown topic.")
    reason = "your choice"
    if not concept:
        concept, reason = _choose_topic(caller.email)
    lesson = content.lessons().get(concept)
    if not lesson:
        raise HTTPException(status_code=404, detail="No lesson for this topic yet.")
    answered = {r["question_id"] for r in store.attempts(caller.email) if r["correct"]}
    questions = [content.find_question(q["id"]) for q in lesson["questions"]]
    questions.sort(key=lambda q: q["id"] in answered)          # unanswered first
    return {
        "concept": concept,
        "reason": reason,
        "lesson_index": topics.index(concept) + 1,
        "lesson_total": len(topics),
        "dialog": lesson["dialog"],
        "questions": [content.public_question(q) for q in questions],
    }


# ---------------------------------------------------------------------------- sessions

class SessionBody(BaseModel):
    kind: str
    concept: Optional[str] = None


@router.post("/game/sessions")
def start_game_session(body: SessionBody, caller: Caller = WHO) -> dict[str, Any]:
    if body.kind not in KINDS:
        raise HTTPException(status_code=400, detail=f"kind must be one of {KINDS}.")
    return {"session_id": store.start_session(caller.email, body.kind, body.concept)}


def _own_session(session_id: int, caller: Caller) -> dict[str, Any]:
    s = store.get_session(session_id)
    if not s or s["student_id"] != caller.email:
        raise HTTPException(status_code=404, detail="Session not found.")
    return s


@router.post("/game/sessions/{session_id}/finish")
def finish_game_session(session_id: int, caller: Caller = WHO) -> dict[str, Any]:
    _own_session(session_id, caller)
    store.finish_session(session_id)          # finishing twice changes nothing; the bonus is counted once
    rows = store.attempts(caller.email, session_id=session_id)
    correct = sum(r["correct"] for r in rows)
    s = store.get_session(session_id)
    return {
        "questions": len(rows),
        "correct": correct,
        "xp_earned": game.total_xp(r["correct"] for r in rows),
        "coins_earned": game.COINS_CORRECT * correct + game.COINS_SESSION,
        "duration_s": int((s["finished_at"] - s["started_at"]).total_seconds()),
        "hud": hud(caller.email, s["concept"]),
    }


# ---------------------------------------------------------------------------- answering

class AnswerBody(BaseModel):
    question_id: int
    selected_index: Optional[int] = None          # None = time ran out
    time_taken_ms: Optional[int] = Field(default=None, ge=0)
    session_id: Optional[int] = None


@router.post("/game/answer")
def answer(body: AnswerBody, caller: Caller = WHO) -> dict[str, Any]:
    q = content.find_question(body.question_id)
    if not q:
        raise HTTPException(status_code=404, detail="Unknown question.")
    if body.session_id is not None:
        _own_session(body.session_id, caller)
    sid, concept = caller.email, q["concept"]
    picked = body.selected_index
    correct = picked == q["answer"]
    fb = (q.get("feedback") or {}).get(str(picked)) if picked is not None else None
    misconception_id = (fb or {}).get("misconception")
    seen_before = bool(misconception_id) and store.misconception_seen_before(sid, misconception_id)
    bought = store.hint_bought_for(sid, q["id"])

    # shared student record: mastery, misses, recent attempts
    profile = load_student_profile(sid)
    entry = profile.setdefault("concept_mastery", {}).setdefault(concept, {"mastery": DEFAULT_MASTERY, "consecutive_misses": 0})
    mastery_before, misses_before = entry["mastery"], entry["consecutive_misses"]
    if correct:
        entry["mastery"] = round(min(1.0, entry["mastery"] + MASTERY_INCREMENT), 4)
        entry["consecutive_misses"] = 0
    else:
        entry["mastery"] = round(max(0.0, entry["mastery"] - MASTERY_DECREMENT), 4)
        entry["consecutive_misses"] += 1
    escalated = entry["consecutive_misses"] >= game.MAX_HEARTS
    if escalated:
        entry["consecutive_misses"] = 0                      # the teacher takes it from here; hearts refill
    profile.setdefault("recent_attempts", []).append({"concept": concept, "correct": correct})
    profile["recent_attempts"] = profile["recent_attempts"][-MAX_RECENT_ATTEMPTS:]
    save_student_profile(sid, profile)
    schedule_next_review(sid, concept, entry["mastery"])

    store.record_attempt(
        student_id=sid, session_id=body.session_id, question_id=q["id"], concept=concept, source=q["source"],
        selected_index=picked, correct=correct, misconception_id=misconception_id,
        time_taken_ms=body.time_taken_ms, hint_bought=bought,
    )
    miscon_text = content.misconceptions().get(misconception_id, {}).get("text") if misconception_id else None
    summary = None
    if escalated:
        summary = (
            f"Still stuck on {concept} after {game.MAX_HEARTS} wrong answers in a row in PixelTutor. "
            f"Question: {q['question']} Last answer: \"{q['choices'][picked] if picked is not None else 'no answer (time ran out)'}\"."
            + (f" Likely misconception: {miscon_text}" if miscon_text else "")
        )
    record_interaction(
        student_id=sid, concept=concept, path="escalation" if escalated else "game",
        mastery_signal=correct, distress_detected=False, cheating_risk_detected=False, escalated=escalated,
        consecutive_misses_before=misses_before, mastery_before=mastery_before, mastery_after=entry["mastery"],
        answer_quality="correct" if correct else "incorrect", identified_misconception=miscon_text,
        teacher_summary=summary, answer_correct=correct, trigger_type="Repeated failure" if escalated else None,
    )
    new_badges = []
    if entry["mastery"] >= game.BADGE_MASTERY and store.award_badge(sid, game.badge_for(concept)):
        new_badges.append(game.badge_for(concept))

    return {
        "correct": correct,
        "correct_index": q["answer"],
        "feedback": None if correct else (fb or {}).get("text") or "Not quite. Look again at what the question asks.",
        "misconception_id": misconception_id,
        "misconception": miscon_text,
        "seen_before": seen_before,
        "xp_delta": game.xp_for(correct),
        "coins_delta": game.COINS_CORRECT if correct else 0,
        "escalated": escalated,
        "new_badges": new_badges,
        "mastery": entry["mastery"],
        "hud": hud(sid, concept),
    }


class HintBody(BaseModel):
    question_id: int


@router.post("/game/hint")
def buy_hint(body: HintBody, caller: Caller = WHO) -> dict[str, Any]:
    q = content.find_question(body.question_id)
    if not q:
        raise HTTPException(status_code=404, detail="Unknown question.")
    if not store.hint_bought_for(caller.email, q["id"]):          # buying the same clue twice is free
        if hud(caller.email)["coins"] < game.HINT_COST:
            raise HTTPException(status_code=402, detail=f"A hint costs {game.HINT_COST} coins. Answer questions to earn more!")
        store.spend_coins(caller.email, q["id"], game.HINT_COST)
    return {"clue": q.get("clue") or "Read the question slowly and rule out options that can't be right.", "hud": hud(caller.email, q["concept"])}


# ---------------------------------------------------------------------------- progress views

@router.get("/game/curve")
def learning_curve(granularity: str = "session", caller: Caller = WHO) -> dict[str, Any]:
    rows = store.attempts(caller.email)
    groups: dict[Any, list] = defaultdict(list)
    if granularity == "day":
        for r in rows:
            groups[store.local_date(r["created_at"]).isoformat()].append(r)
        labels = {k: k[5:] for k in groups}
    else:
        for r in rows:
            groups[r["session_id"] or f"free-{r['id'] // 5}"].append(r)
        labels = {k: f"S{i}" for i, k in enumerate(groups, 1)}
    points = []
    for key, items in groups.items():
        times = [r["time_taken_ms"] for r in items if r["time_taken_ms"]]
        points.append({
            "label": labels[key],
            "accuracy_pct": round(100 * sum(r["correct"] for r in items) / len(items), 1),
            "avg_time_ms": round(sum(times) / len(times)) if times else 0,
            "attempts": len(items),
        })
    return {"points": points[-12:]}


@router.get("/game/stats")
def stats(caller: Caller = WHO) -> dict[str, Any]:
    rows = store.attempts(caller.email)
    mastery = load_student_profile(caller.email).get("concept_mastery") or {}
    recent = rows[-20:]
    times = [r["time_taken_ms"] for r in recent if r["time_taken_ms"]]
    last_seen: dict[str, str] = {}
    for r in rows:                                   # a misconception is active until the topic's next correct answer
        if r["misconception_id"]:
            last_seen[r["misconception_id"]] = r["concept"]
        elif r["correct"]:
            for m, c in list(last_seen.items()):
                if c == r["concept"]:
                    del last_seen[m]
    logged = get_interactions(caller.email)
    escalations = sum(1 for r in logged if r.get("escalated"))
    confidences = [r["confidence_score"] for r in logged if r.get("confidence_score") is not None and r["path"] != "game"][-20:]
    previous = rows[-40:-20]
    trend = lambda part: (sum(r["correct"] for r in part) / len(part)) if part else None
    return {
        "attempts": len(rows),
        "rolling_accuracy": round(100 * trend(recent), 1) if recent else None,
        "previous_accuracy": round(100 * trend(previous), 1) if previous else None,
        "rolling_avg_time_ms": round(sum(times) / len(times)) if times else None,
        "hint_usage_pct": round(100 * sum(r["hint_bought"] for r in recent) / len(recent), 1) if recent else None,
        "active_misconceptions": len(last_seen),
        "escalations": escalations,
        "avg_confidence": round(100 * sum(confidences) / len(confidences), 1) if confidences else None,
        "streak": hud(caller.email)["streak"],
        "lesson_progress_pct": round(100 * sum(((mastery.get(t) or {}).get("mastery", 0.0)) for t in content.topics()) / len(content.topics()), 1),
    }


@router.get("/game/leaderboard")
def leaderboard(window: str = "all", caller: Caller = WHO) -> dict[str, Any]:
    since = store.utcnow() - timedelta(days=7) if window == "7d" else None
    entries = []
    for sid in store.all_player_ids():
        rows = [r for r in store.attempts(sid) if since is None or r["created_at"] >= since]
        if not rows and sid != caller.email:
            continue
        player = store.get_player(sid)
        entries.append({
            "student_id": sid if sid == caller.email or caller.is_teacher else None,
            "name": _display_name(sid).upper()[:12],
            "xp": game.total_xp(r["correct"] for r in rows),
            "streak": hud(sid)["streak"],
            "badge": "🏆" if store.badges(sid) else "",
            "avatar": player.get("companion_id"),
            "is_me": sid == caller.email,
        })
    entries.sort(key=lambda e: (-e["xp"], e["name"]))
    for i, e in enumerate(entries, 1):
        e["rank"] = i
    return {"entries": entries}
