"""
escalation_agent.py
-------------------
Escalation Agent: hands a struggling or distressed student over to a teacher.

It runs when the student has missed the same concept too many times in a
row, sounds upset, or the reply looks copied. It writes two things, both from
facts already in the turn (no model call, so the student is never left
waiting at the moment they most need a reply):

    teacher_summary   what the teacher needs: trigger, question, the
                      student's answer and the diagnosis
    student_message   a short, kind note that a teacher will follow up
"""

from __future__ import annotations

import logging

from pydantic import BaseModel

logger = logging.getLogger("escalation_agent")


class EscalationResult(BaseModel):
    teacher_summary: str
    student_message: str
    escalation_flag: bool = True
    trigger_type: str = "Repeated failure"      # "Repeated failure" | "Distress" | "Cheating risk"


_STUDENT_MESSAGES = {
    "Distress": (
        "This one has been frustrating, and that's okay. I've asked your teacher to go through it "
        "with you. Take a short break; you've put in real effort."
    ),
    "Cheating risk": (
        "I'd like your teacher to look at this one with you, so we can be sure the steps make sense "
        "to you. They'll follow up soon."
    ),
    "Repeated failure": (
        "We've tried this a few ways and it still isn't clicking, which happens to everyone. "
        "I've asked your teacher to walk through it with you."
    ),
}


def run_escalation(state: dict) -> dict:
    """
    LangGraph node. Reads the turn's facts and writes escalation_result, teacher_summary,
    hint_text (the message the student sees) and escalation_flag.
    """
    concept = state.get("current_concept") or "this topic"
    profile = state.get("student_memory_profile") or {}
    misses = ((profile.get("concept_mastery") or {}).get(concept) or {}).get("consecutive_misses", 0)
    diagnostic = state.get("diagnostic_result") or {}
    evaluator = state.get("evaluator_result") or {}

    if state.get("cheating_risk_detected"):
        trigger_type = "Cheating risk"
        trigger = "Reply typed faster than it could be composed: " + (evaluator.get("cheating_risk_reasoning") or "timing check")
    elif state.get("distress_detected"):
        trigger_type = "Distress"
        trigger = f"Student sounds upset or ready to give up, after {misses} consecutive miss(es)"
    else:
        trigger_type = "Repeated failure"
        trigger = f"Still stuck on {concept} after {misses} consecutive misses"

    answer = " ".join((state.get("student_response") or "").split())[:120]
    parts = [f"{trigger}.", f'Question: {state.get("current_question") or "(none)"}', f'Last answer: "{answer}".']
    if diagnostic.get("identified_misconception"):
        parts.append(f"Likely misconception: {diagnostic['identified_misconception']}.")
    if diagnostic.get("missing_prerequisite"):
        parts.append(f"Possible gap in: {diagnostic['missing_prerequisite']}.")

    result = EscalationResult(
        teacher_summary=" ".join(parts), student_message=_STUDENT_MESSAGES[trigger_type], trigger_type=trigger_type
    )
    logger.info("ESCALATION (%s) | %s", trigger_type, result.teacher_summary)
    state["escalation_result"] = result.model_dump(mode="json")
    state["teacher_summary"] = result.teacher_summary
    state["hint_text"] = result.student_message
    state["escalation_flag"] = True
    return state
