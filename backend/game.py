"""
game.py
-------
The rules of the gamified dashboard (PixelTutor), as pure functions so they are easy to
test and change in one place. Everything is derived from the student's real answers.

XP        10 per correct answer, 2 per wrong answer (effort counts)
Level     a new level every 100 XP; the HUD bar shows progress through the current level
Coins     start with 20; +5 per correct answer; +10 per finished session; an extra hint
          before answering costs 5 (the hint after a wrong answer is always free)
Streak    days in a row (ending today or yesterday) with at least one answer
Hearts    3 per topic; each wrong answer in a row costs one. When they run out the tutor
          tells the teacher, and the hearts refill. Nothing is ever locked.
Badges    "<TOPIC> MASTER" when mastery of a topic reaches 70%
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Iterable

XP_CORRECT = 10
XP_WRONG = 2
XP_PER_LEVEL = 100
COINS_START = 20
COINS_CORRECT = 5
COINS_SESSION = 10
HINT_COST = 5
MAX_HEARTS = 3
BADGE_MASTERY = 0.7


def xp_for(correct: bool) -> int:
    return XP_CORRECT if correct else XP_WRONG


def total_xp(results: Iterable[bool]) -> int:
    return sum(xp_for(c) for c in results)


def level_of(xp: int) -> tuple[int, int]:
    """(level, percent of the way to the next level)."""
    return 1 + xp // XP_PER_LEVEL, (xp % XP_PER_LEVEL) * 100 // XP_PER_LEVEL


def coins_balance(correct_answers: int, finished_sessions: int, hints_bought: int) -> int:
    return COINS_START + COINS_CORRECT * correct_answers + COINS_SESSION * finished_sessions - HINT_COST * hints_bought


def streak_days(active_days: Iterable[date], today: date) -> int:
    days = set(active_days)
    start = today if today in days else today - timedelta(days=1)
    n = 0
    while start - timedelta(days=n) in days:
        n += 1
    return n


def hearts_left(consecutive_misses: int) -> int:
    return max(0, MAX_HEARTS - consecutive_misses)


def badge_for(concept: str) -> str:
    return f"{concept.upper()} MASTER"
