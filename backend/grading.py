"""
grading.py
----------
Checks a typed answer against a known answer key without asking the AI.

    match_answer("0.75", "3/4")            -> True   (same value)
    match_answer("x = 4", "4")             -> True
    match_answer("2/6", "3/4")             -> False
    match_answer("I think it's 3/4", "3/4")-> None   (not a bare answer: let the model judge)

Returns True or False only when the reply is a bare answer; anything with
reasoning or several numbers returns None, so the model reads it instead.
"""

from __future__ import annotations

import re
from fractions import Fraction
from typing import Optional

_UNITS = re.compile(
    r"°|\bdegrees?\b|\bsquare\s+(centi)?met(re|er)s?\b|\bsq\.?\s*cm\b|cm\s*\^?\s*2\b|cm²|\bcentimet(re|er)s?\b|\bcm\b|\bunits?\b",
    re.I,
)
_LEAD_IN = re.compile(r"^(the\s+)?(answer|result|it)\s*(is|=|:)?\s*|^[a-z]\s*=\s*|^=\s*", re.I)
_MIXED = re.compile(r"^(-?\d+)\s+(\d+)\s*/\s*(\d+)$")
_FRACTION = re.compile(r"^(-?\d+)\s*/\s*(\d+)$")
_DECIMAL = re.compile(r"^-?(\d+\.?\d*|\.\d+)$")


def _clean(text: str) -> str:
    t = text.strip().lower().replace("−", "-").replace("–", "-").replace("percent", "%").replace("per cent", "%")
    t = _UNITS.sub("", t).strip().rstrip(".!").strip()
    t = _LEAD_IN.sub("", t).strip()
    return t


def parse_value(text: str) -> Optional[Fraction]:
    """The single number a bare answer stands for, or None if it is not one bare number."""
    t = _clean(text)
    percent = t.endswith("%")
    if percent:
        t = t[:-1].strip()
    try:
        if m := _MIXED.match(t):
            whole, num, den = int(m[1]), int(m[2]), int(m[3])
            value = Fraction(abs(whole) * den + num, den) * (-1 if whole < 0 else 1)
        elif m := _FRACTION.match(t):
            value = Fraction(int(m[1]), int(m[2]))
        elif _DECIMAL.match(t):
            value = Fraction(t)
        else:
            return None
    except (ZeroDivisionError, ValueError):
        return None
    return value / 100 if percent else value


def _form(text: str) -> str:
    t = _clean(text).replace(" ", "")
    if t.startswith("."):
        t = "0" + t
    return t


def match_answer(answer: str, key: str, exact_form: bool = False) -> Optional[bool]:
    """True / False for a bare answer, None when the reply needs reading."""
    if exact_form:
        if parse_value(answer) is None:
            return None
        return _form(answer) == _form(key)
    got, want = parse_value(answer), parse_value(key)
    if want is None:                      # the key is words, not a number
        a, k = _form(answer), _form(key)
        return True if a == k else None
    if got is None:
        return None
    if ("%" in key) != ("%" in _clean(answer)):
        return False                      # 0.5 is not an answer to "as a percentage"
    return got == want
