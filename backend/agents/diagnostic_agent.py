"""
diagnostic_agent.py
-------------------
Diagnostic Agent: turns the assessment of a wrong answer into a diagnosis and
chooses how strongly the tutor should help.

The error type, misconception and missing prerequisite come from the single
assessment call the Evaluator already made (state["assessment"]); if a turn
reaches this node without one, the node makes that call itself.

The teaching strategy is a rule, not a model opinion, so the hint ladder
always climbs the same way:

    careless slip          -> retry_prompt
    missing prerequisite   -> prerequisite_review
    conceptual, 0 misses   -> small_clue
    conceptual, 1 miss     -> stronger_hint
    conceptual, 2+ misses  -> worked_example

"misses" is the student's run of consecutive misses on this concept before
this turn.
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from backend.agents.evaluator_agent import assess

logger = logging.getLogger("diagnostic_agent")


class ErrorType(str, Enum):
    NONE = "None"
    CARELESS = "Careless"
    CONCEPTUAL = "Conceptual"
    PREREQUISITE = "Prerequisite"


class InstructionalStrategy(str, Enum):
    NONE = "none"
    RETRY_PROMPT = "retry_prompt"
    SMALL_CLUE = "small_clue"
    STRONGER_HINT = "stronger_hint"
    WORKED_EXAMPLE = "worked_example"
    PREREQUISITE_REVIEW = "prerequisite_review"
    ESCALATE_TO_TEACHER = "escalate_to_teacher"


class DiagnosticResult(BaseModel):
    is_correct: bool = False
    error_type: ErrorType = ErrorType.CONCEPTUAL
    identified_misconception: Optional[str] = None
    missing_prerequisite: Optional[str] = None
    confidence: float = Field(0.5, ge=0.0, le=1.0)
    reasoning: str = ""
    recommended_strategy: InstructionalStrategy = InstructionalStrategy.SMALL_CLUE


_ERROR_TYPES = {
    "careless": ErrorType.CARELESS,
    "conceptual": ErrorType.CONCEPTUAL,
    "prerequisite": ErrorType.PREREQUISITE,
    "none": ErrorType.NONE,
}


def choose_strategy(error_type: ErrorType, consecutive_misses: int) -> InstructionalStrategy:
    if error_type == ErrorType.NONE:
        return InstructionalStrategy.NONE
    if error_type == ErrorType.CARELESS and consecutive_misses == 0:
        return InstructionalStrategy.RETRY_PROMPT
    if error_type == ErrorType.PREREQUISITE:
        return InstructionalStrategy.PREREQUISITE_REVIEW
    if consecutive_misses <= 0:
        return InstructionalStrategy.SMALL_CLUE
    if consecutive_misses == 1:
        return InstructionalStrategy.STRONGER_HINT
    return InstructionalStrategy.WORKED_EXAMPLE


def run_diagnostic(state: dict) -> dict:
    """
    LangGraph node, on the branch where the answer was not a confident correct one.
    Reads student_response, current_concept, current_question, student_memory_profile and the
    Evaluator's "assessment". Writes diagnostic_result, error_type and recommended_strategy.
    """
    student_response = state.get("student_response")
    current_concept = state.get("current_concept")
    if not student_response or not current_concept:
        raise ValueError("run_diagnostic requires 'student_response' and 'current_concept' in state.")

    assessment = state.get("assessment") or assess(
        state.get("current_question") or "", student_response, current_concept, state.get("reference_answer")
    )
    profile = state.get("student_memory_profile") or {}
    misses = ((profile.get("concept_mastery") or {}).get(current_concept) or {}).get("consecutive_misses", 0)
    is_correct = state.get("answer_quality") == "correct"
    error_type = ErrorType.NONE if is_correct else _ERROR_TYPES.get(assessment["error_type"], ErrorType.CONCEPTUAL)
    if not is_correct and error_type == ErrorType.NONE:
        error_type = ErrorType.CONCEPTUAL

    result = DiagnosticResult(
        is_correct=is_correct,
        error_type=error_type,
        identified_misconception=assessment["misconception"] or None,
        missing_prerequisite=assessment["missing_prerequisite"] if error_type == ErrorType.PREREQUISITE else None,
        confidence=assessment["confidence"],
        reasoning=f"{error_type.value} error after {misses} consecutive miss(es) on {current_concept}.",
        recommended_strategy=choose_strategy(error_type, misses),
    )
    logger.info("Diagnosis for %r -> %s, strategy=%s", current_concept, result.error_type.value, result.recommended_strategy.value)
    state["diagnostic_result"] = result.model_dump(mode="json")
    state["error_type"] = result.error_type.value
    state["recommended_strategy"] = result.recommended_strategy.value
    return state
