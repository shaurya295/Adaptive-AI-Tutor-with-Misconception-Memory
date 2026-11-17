"""
evaluator_agent.py
------------------
Evaluator Agent: the first node of every tutoring turn.

It decides how good the student's answer is, and it does the cheap, certain
checks before it spends time on the language model:

1. If the question has an answer key and the reply is a bare answer ("3/4",
   "0.75", "x = 4"), it is graded by backend.grading with no model call.
2. A reply typed faster than a person can compose it is flagged as a
   cheating risk by word count and elapsed time.
3. Everything else gets ONE short model call that returns the verdict
   together with the diagnosis (error type, misconception, missing
   prerequisite, distress). The Diagnostic Agent reuses that assessment, so
   a wrong answer costs one judging call, not two.

mastery_signal is computed here, never taken from the model: the answer is
correct and the confidence is at or above the routing threshold.
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field

from backend import llm
from backend.grading import match_answer
from backend.memory.misconception_graph import get_prerequisites

logger = logging.getLogger("evaluator_agent")

CONFIDENCE_FOR_MASTERY = 0.6
MAX_PLAUSIBLE_WORDS_PER_SECOND = 3.0
MIN_WORDS_FOR_SPEED_CHECK = 8


class AnswerQuality(str, Enum):
    CORRECT = "correct"
    PARTIALLY_CORRECT = "partially_correct"
    INCORRECT = "incorrect"


class EvaluatorResult(BaseModel):
    answer_quality: AnswerQuality
    quality_reasoning: str = ""
    confidence_score: float = Field(0.5, ge=0.0, le=1.0)
    mastery_signal: bool = False
    distress_detected: bool = False
    cheating_risk_detected: bool = False
    cheating_risk_reasoning: str = ""
    graded_by: str = "model"            # "answer_key" when no model call was needed


def _speed_check(student_response: str, response_time_seconds: Optional[float]) -> tuple[bool, str]:
    """Is this reply too long to have been composed and typed in the time it took?"""
    if not response_time_seconds or response_time_seconds <= 0:
        return False, ""
    words = len(student_response.split())
    if words < MIN_WORDS_FOR_SPEED_CHECK:
        return False, ""
    rate = words / response_time_seconds
    if rate > MAX_PLAUSIBLE_WORDS_PER_SECOND:
        return True, f"{words} words in {response_time_seconds:.1f}s (about {rate:.1f} words per second)"
    return False, ""


def _assess_schema(prerequisites: list[str]) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "verdict": {"type": "string", "enum": [q.value for q in AnswerQuality]},
            "error_type": {"type": "string", "enum": ["careless", "conceptual", "prerequisite", "none"]},
            "misconception": {"type": "string"},
            "missing_prerequisite": {"type": "string", "enum": [*prerequisites, "none"]},
            "confidence": {"type": "number"},
            "distress": {"type": "boolean"},
        },
        "required": ["verdict", "error_type", "misconception", "missing_prerequisite", "confidence", "distress"],
    }


def _assess_prompt(question: str, answer: str, concept: str, key: Optional[str], prerequisites: list[str]) -> str:
    key_line = f"Correct answer: {key}\nAn equivalent value counts as correct.\n" if key else ""
    prereq_line = ", ".join(prerequisites) if prerequisites else "none listed"
    return (
        "TASK: Judge the student's answer and say what went wrong.\n"
        f"Topic: {concept}\n"
        f"Question: {question}\n"
        f"{key_line}"
        f'Student wrote: """{answer}"""\n'
        "verdict: correct, partially_correct or incorrect.\n"
        "error_type: careless (knows the method, slipped), conceptual (misunderstands this topic), "
        "prerequisite (an earlier skill is missing), or none if the answer is correct.\n"
        "misconception: the wrong idea behind the answer, in at most 12 words; empty if correct.\n"
        f"missing_prerequisite: one of [{prereq_line}] if error_type is prerequisite, otherwise none.\n"
        "confidence: 0 to 1, how sure the student seems of a correct answer (hedging lowers it).\n"
        "distress: true only if the student sounds upset or wants to give up.\n"
        "Reply as JSON."
    )


def assess(question: str, answer: str, concept: str, key: Optional[str]) -> dict[str, Any]:
    """One model call: verdict plus diagnosis. Raises llm.LLMError if the model is unavailable."""
    prerequisites = get_prerequisites(concept)
    data = llm.chat_json("assess", _assess_prompt(question, answer, concept, key, prerequisites), _assess_schema(prerequisites))
    try:
        confidence = min(1.0, max(0.0, float(data.get("confidence", 0.5))))
    except (TypeError, ValueError):
        confidence = 0.5
    verdict = data.get("verdict") if data.get("verdict") in {q.value for q in AnswerQuality} else "incorrect"
    prereq = data.get("missing_prerequisite")
    return {
        "verdict": verdict,
        "error_type": data.get("error_type") if data.get("error_type") in ("careless", "conceptual", "prerequisite", "none") else "conceptual",
        "misconception": (data.get("misconception") or "").strip()[:160],
        "missing_prerequisite": prereq if prereq in prerequisites else None,
        "confidence": confidence,
        "distress": bool(data.get("distress")),
    }


def run_evaluator(state: dict) -> dict:
    """
    LangGraph node. Reads student_response, current_question, current_concept and, when present,
    reference_answer / exact_form / response_time_seconds. Writes evaluator_result, answer_quality,
    confidence_score, mastery_signal, distress_detected, cheating_risk_detected and, when the model
    was consulted, "assessment" for the Diagnostic Agent to reuse.
    """
    student_response = state.get("student_response")
    current_question = state.get("current_question")
    current_concept = state.get("current_concept")
    if not student_response or not current_question or not current_concept:
        raise ValueError("run_evaluator requires 'student_response', 'current_question' and 'current_concept' in state.")

    key = state.get("reference_answer")
    cheating, cheating_why = _speed_check(student_response, state.get("response_time_seconds"))
    matched = match_answer(student_response, key, bool(state.get("exact_form"))) if key else None

    if matched is True:
        result = EvaluatorResult(
            answer_quality=AnswerQuality.CORRECT,
            quality_reasoning="Matches the answer key.",
            confidence_score=0.9,
            graded_by="answer_key",
        )
    else:
        assessment = assess(current_question, student_response, current_concept, key)
        if matched is False:
            assessment["verdict"] = AnswerQuality.INCORRECT.value      # the key outranks the model's opinion
        if assessment["verdict"] != AnswerQuality.CORRECT.value and assessment["error_type"] == "none":
            assessment["error_type"] = "conceptual"
        state["assessment"] = assessment
        result = EvaluatorResult(
            answer_quality=AnswerQuality(assessment["verdict"]),
            quality_reasoning=assessment["misconception"] or "Judged by the model.",
            confidence_score=assessment["confidence"] if matched is None else 0.9,
            distress_detected=assessment["distress"],
            graded_by="answer_key" if matched is False else "model",
        )

    result.cheating_risk_detected = cheating
    result.cheating_risk_reasoning = cheating_why
    result.mastery_signal = (
        result.answer_quality == AnswerQuality.CORRECT and result.confidence_score >= CONFIDENCE_FOR_MASTERY and not cheating
    )
    logger.info(
        "Evaluation -> quality=%s confidence=%.2f mastery=%s distress=%s cheating=%s by=%s",
        result.answer_quality.value, result.confidence_score, result.mastery_signal,
        result.distress_detected, result.cheating_risk_detected, result.graded_by,
    )
    state["evaluator_result"] = result.model_dump(mode="json")
    state["answer_quality"] = result.answer_quality.value
    state["confidence_score"] = result.confidence_score
    state["mastery_signal"] = result.mastery_signal
    state["distress_detected"] = result.distress_detected
    state["cheating_risk_detected"] = result.cheating_risk_detected
    return state
