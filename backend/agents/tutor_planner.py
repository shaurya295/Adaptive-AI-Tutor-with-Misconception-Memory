"""
tutor_planner.py
----------------
Tutor Planner: writes what the student sees.

    praise    correct answer: a short, fixed message (no model call)
    hint      wrong answer: one model call, strength set by the Diagnostic
              Agent's strategy (small clue -> stronger hint -> worked example),
              grounded in the curriculum notes
    explain   a fresh question from the student: one model call

Answer-leak guard: a hint must not hand over the answer. The hint is checked
against the question's answer key; if the key shows up, the hint is written
once more with a firmer instruction, and if it still leaks, a safe hint
written by hand is used. A leak never calls the teacher.

If the model is unavailable while writing a hint, the hand-written hint is
used and the turn carries on.
"""

from __future__ import annotations

import logging
import re
from typing import Optional

from pydantic import BaseModel

from backend import llm
from backend.agents.diagnostic_agent import InstructionalStrategy

logger = logging.getLogger("tutor_planner")

_PRAISE = [
    "That's right. Nicely done.",
    "Correct! You handled that well.",
    "Yes, that's it. Good work.",
    "Spot on. You're getting the hang of this.",
]

_LEVEL_INSTRUCTIONS = {
    "retry_prompt": "The student knows the method and slipped. Ask them to recheck one specific step. At most 30 words.",
    "small_clue": "Give a small clue that points at the first step, without doing it for them. At most 45 words.",
    "stronger_hint": "Give a stronger hint: name the rule to use and how to start, without finishing the calculation. At most 60 words.",
    "worked_example": (
        "Work through a SIMILAR example with DIFFERENT numbers, step by step, then ask the student to "
        "try the original question again. At most 110 words."
    ),
    "prerequisite_review": (
        "The student is missing an earlier skill. Briefly re-teach that skill with a tiny example, "
        "then link it back to this question. At most 80 words."
    ),
}
_FALLBACK_HINTS = {
    "retry_prompt": "You're close. Go back over your working one step at a time and check each calculation. What do you get this time?",
    "small_clue": "Look closely at what the question is asking before you calculate. What is the very first step?",
    "stronger_hint": "Think about the rule we use for this kind of problem and apply it one step at a time. Which rule fits here?",
    "worked_example": "Let's slow down. Write out each step of your working, and tell me the first step you would take and why.",
    "prerequisite_review": "Let's step back to the idea this question builds on. Can you explain that earlier idea in your own words first?",
}
_NUM_PREDICT = {"retry_prompt": 60, "small_clue": 90, "stronger_hint": 110, "worked_example": 190, "prerequisite_review": 150}


class TutorPlanResult(BaseModel):
    hint_text: str
    applied_strategy: InstructionalStrategy = InstructionalStrategy.NONE
    practice_question: Optional[str] = None
    escalation_flag: bool = False
    escalation_reason: Optional[str] = None
    leak_guard_triggered: bool = False
    written_by: str = "model"           # "model", "template" or "fallback"


def leaks_answer(hint_text: str, reference_answer: Optional[str], question: str = "") -> bool:
    """Does the hint state the answer key? Numbers that already appear in the question do not count."""
    if not reference_answer:
        return False
    key = reference_answer.strip().lower().rstrip("%")
    if not key:
        return False
    token = rf"(?<![\w/.]){re.escape(key)}(?![\w/]|\.\d)"
    hint = hint_text.lower()
    if not re.search(token, hint):
        return False
    if re.fullmatch(r"-?\d", key):
        # A lone digit turns up in ordinary sentences; only count it when presented as a result.
        return bool(re.search(rf"(=|\bis|\bequals|\banswer\b[^.]*?)\s*{re.escape(key)}(?![\w/]|\.\d)", hint))
    return not re.search(token, question.lower())


def praise_text(turn_number: int = 0) -> str:
    return _PRAISE[turn_number % len(_PRAISE)]


def _hint_prompt(question, answer, concept, strategy, misconception, times_missed, prerequisite, curriculum, firm) -> str:
    lines = [
        f"TASK: Write the tutor's reply to a wrong answer. {_LEVEL_INSTRUCTIONS[strategy]}",
        f"Topic: {concept}",
        f"Question: {question}",
        f'Student wrote: """{answer}"""',
    ]
    if misconception:
        lines.append(f"Likely misconception: {misconception}")
    if prerequisite:
        lines.append(f"Earlier skill to review: {prerequisite}")
    if times_missed:
        lines.append(f"The student has now missed this question {times_missed + 1} times; acknowledge that gently.")
    if curriculum:
        lines.append(f"Curriculum note: {curriculum}")
    lines.append("Speak to the student directly and end with a question that prompts their next step.")
    lines.append(
        "You MUST NOT write the final answer to the question in any form." if firm
        else "Do not state the final answer to the question."
    )
    return "\n".join(lines)


def plan_hint(
    question: str,
    answer: str,
    concept: str,
    strategy: str,
    misconception: Optional[str] = None,
    times_missed: int = 0,
    prerequisite: Optional[str] = None,
    curriculum: str = "",
    reference_answer: Optional[str] = None,
) -> TutorPlanResult:
    if strategy not in _LEVEL_INSTRUCTIONS:
        strategy = "small_clue"
    applied = InstructionalStrategy(strategy)
    leaked = False
    for firm in (False, True):
        try:
            text = llm.chat_text(
                "hint",
                _hint_prompt(question, answer, concept, strategy, misconception, times_missed, prerequisite, curriculum, firm),
                num_predict=_NUM_PREDICT[strategy],
            )
        except llm.LLMError as exc:
            logger.warning("Hint generation failed (%s); using the hand-written hint.", exc)
            break
        if not leaks_answer(text, reference_answer, question):
            return TutorPlanResult(hint_text=text, applied_strategy=applied, leak_guard_triggered=leaked)
        leaked = True
        logger.warning("Answer leak caught in a %s hint; %s.", strategy, "retrying" if not firm else "using the hand-written hint")
    return TutorPlanResult(
        hint_text=_FALLBACK_HINTS[strategy], applied_strategy=applied, leak_guard_triggered=leaked, written_by="fallback"
    )


def run_tutor_planner(state: dict) -> dict:
    """
    LangGraph node. With no diagnostic_result in state the answer was a confident correct one
    (praise); otherwise it writes a hint. Writes tutor_plan_result, hint_text, practice_question
    and escalation_flag. The next practice question is chosen by the caller, from the bank.
    """
    student_response = state.get("student_response")
    current_question = state.get("current_question")
    current_concept = state.get("current_concept")
    if not student_response or not current_question or not current_concept:
        raise ValueError("run_tutor_planner requires 'student_response', 'current_question' and 'current_concept' in state.")

    diagnostic = state.get("diagnostic_result")
    profile = state.get("student_memory_profile") or {}
    if diagnostic is None:
        attempts = len(profile.get("recent_attempts") or [])
        result = TutorPlanResult(hint_text=praise_text(attempts), written_by="template")
    else:
        curriculum = ""
        try:
            if llm.is_fake():   # tests and demos: no embedding model to call
                raise LookupError
            from backend.rag.retriever import get_curriculum_context

            curriculum = (
                get_curriculum_context(
                    concept=current_concept,
                    error_type=state.get("error_type", ""),
                    misconception=diagnostic.get("identified_misconception") or "",
                )
                or ""
            )[:700]
        except LookupError:
            pass
        except Exception as exc:  # noqa: BLE001 - curriculum notes are a bonus, never a blocker
            logger.warning("Curriculum lookup failed: %s", exc)
        misses = ((profile.get("concept_mastery") or {}).get(current_concept) or {}).get("consecutive_misses", 0)
        result = plan_hint(
            question=current_question,
            answer=student_response,
            concept=current_concept,
            strategy=diagnostic.get("recommended_strategy") or "small_clue",
            misconception=diagnostic.get("identified_misconception"),
            times_missed=misses,
            prerequisite=diagnostic.get("missing_prerequisite"),
            curriculum=curriculum,
            reference_answer=state.get("reference_answer"),
        )
    logger.info("Tutor plan -> strategy=%s by=%s leak_guard=%s", result.applied_strategy.value, result.written_by, result.leak_guard_triggered)
    state["tutor_plan_result"] = result.model_dump(mode="json")
    state["hint_text"] = result.hint_text
    state["practice_question"] = result.practice_question
    state["escalation_flag"] = result.escalation_flag
    return state


def run_explain(current_concept: str, student_question: str, student_memory_profile: dict) -> dict:
    """
    Explain mode: the student asked something and no problem is in progress. One model call.
    Returns tutor_plan_result, hint_text and practice_question (None: the caller picks one from
    the bank). Raises llm.LLMError if the model is unavailable.
    """
    weak = ", ".join((student_memory_profile or {}).get("weak_prerequisites") or [])
    prompt = (
        "TASK: Answer the student's question in at most 90 words, with one tiny example.\n"
        f"The student is currently practising: {current_concept}\n"
        f'Student asked: """{student_question}"""\n'
        "Answer what they actually asked, even if it is about a different maths topic than the one they are practising. "
        "If the question is not about maths, say kindly in one sentence that you can only help with maths, and suggest a maths question about the topic they are practising.\n"
        + (f"The student has struggled with: {weak}. Connect to that if it helps.\n" if weak else "")
        + "Do not ask a question at the end; a practice problem follows your explanation."
    )
    text = llm.chat_text("explain", prompt, num_predict=170)
    result = TutorPlanResult(hint_text=text)
    return {"tutor_plan_result": result.model_dump(mode="json"), "hint_text": result.hint_text, "practice_question": None}
