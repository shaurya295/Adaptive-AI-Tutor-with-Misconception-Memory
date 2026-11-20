"""
eval_errors.py
--------------
Checks how well the real model labels WHY an answer is wrong (careless slip vs
misunderstanding vs missing earlier skill), on a small hand-labelled set.

    .venv/bin/python -m backend.tools.eval_errors
"""
from __future__ import annotations

import time

from backend.agents.evaluator_agent import assess, classify_error

# (topic, question, answer key, student's answer, expected error type)
CASES = [
    ("Fractions", "What is 1/2 + 1/4?", "3/4", "2/6", "conceptual"),
    ("Fractions", "What is 2/3 + 1/6?", "5/6", "3/9", "conceptual"),
    ("Fractions", "Which is greater: 2/5 or 3/10?", "2/5", "3/10", "conceptual"),
    ("Fractions", "What is 3/4 - 1/8?", "5/8", "6/8", "careless"),
    ("Algebra", "Solve for x: 2x + 3 = 11", "4", "7", "conceptual"),
    ("Algebra", "Solve for x: 5x - 7 = 18", "5", "6", "careless"),
    ("Algebra", "Solve for x: 3(x + 2) = 21", "5", "6.33", "conceptual"),
    ("Geometry", "Two angles of a triangle are 50 degrees and 60 degrees. What is the third angle, in degrees?", "70", "250", "conceptual"),
    ("Decimals and Percentages", "Convert 0.75 to a percentage.", "75%", "7.5%", "conceptual"),
    ("Decimals and Percentages", "What is 0.4 + 0.35?", "0.75", "0.39", "conceptual"),
]


def main() -> None:
    right, started = 0, time.time()
    for topic, q, key, ans, want in CASES:
        got = assess(q, ans, topic, key)
        got["error_type"] = classify_error(q, ans, key, got["error_type"])   # as run_evaluator does
        ok = got["error_type"] == want
        right += ok
        print(f"{'ok ' if ok else 'BAD'} want={want:11} got={got['error_type']:11} | {ans:6} for {q[:48]}  ({got['misconception'][:60]})")
    print(f"\n{right}/{len(CASES)} error types right in {time.time() - started:.0f}s")


if __name__ == "__main__":
    main()
