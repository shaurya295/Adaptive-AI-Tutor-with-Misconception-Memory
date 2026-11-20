"""Content packages: misconception catalogue, game lessons, and the quiz bank's feedback fields.

The game grades multiple-choice answers instantly with no AI call, so every question needs:
a clue (bought with coins before answering) and, for each wrong option, feedback that names the
misconception it reveals. These tests define what valid content looks like.
"""
import json
import re
from pathlib import Path

import pytest

from backend import content
from backend.grading import parse_value

C = Path(__file__).resolve().parents[1] / "backend" / "content"
TOPICS = ["Fractions", "Probability", "Algebra", "Geometry", "Decimals and Percentages"]
ID_RE = re.compile(r"^[a-z]+(-[a-z0-9]+)+$")


def load(name):
    return json.loads((C / name).read_text(encoding="utf-8"))


def test_misconception_catalogue():
    cat = load("misconceptions.json")
    assert set(v["topic"] for v in cat.values()) == set(TOPICS)
    assert len(cat) >= 26
    for mid, m in cat.items():
        assert ID_RE.match(mid), mid
        assert m["topic"] in TOPICS and 10 <= len(m["text"]) <= 140, mid


def _check_mcq(q, topic, misconceptions):
    assert len(q["choices"]) == 4 and len(set(q["choices"])) == 4, q["id"]
    assert 0 <= q["answer"] < 4, q["id"]
    assert 15 <= len(q["clue"]) <= 200, q["id"]
    key = q["choices"][q["answer"]]
    assert key.lower() not in q["clue"].lower(), f"clue gives away the answer: {q['id']}"
    wrong = {str(i) for i in range(4) if i != q["answer"]}
    assert set(q["feedback"]) == wrong, f"feedback must cover exactly the wrong options: {q['id']}"
    for i, fb in q["feedback"].items():
        assert 15 <= len(fb["text"]) <= 260, (q["id"], i)
        mid = fb.get("misconception")
        assert mid is None or (mid in misconceptions and misconceptions[mid]["topic"] == topic), (q["id"], mid)
    # numeric keys must not collide with an equivalent wrong option (e.g. 1/2 and 0.5), except where the
    # question asks for a form ("simplify", "lowest terms"): there the unsimplified fraction is a real wrong answer
    values = [parse_value(c) for c in q["choices"]]
    asks_for_form = re.search(r"simplif|lowest terms|simplest form", q["question"], re.I)
    if values[q["answer"]] is not None and not asks_for_form:
        assert values.count(values[q["answer"]]) == 1, f"two options have the same value: {q['id']}"


def test_quiz_bank_has_game_feedback():
    cat = load("misconceptions.json")
    tagged = 0
    for topic in TOPICS:
        for variant in ("pre", "post"):
            for q in content.get_quiz(topic, variant):
                _check_mcq(q, topic, cat)
                tagged += sum(1 for f in q["feedback"].values() if f.get("misconception"))
    assert tagged >= 40, "most wrong options should name a misconception"


def test_lessons():
    cat = load("misconceptions.json")
    lessons = load("lessons.json")
    assert list(lessons) == TOPICS
    ids = {q["id"] for t in TOPICS for v in ("pre", "post") for q in content.get_quiz(t, v)}
    for topic, lesson in lessons.items():
        assert len(lesson["dialog"]) == 5 and all(20 <= len(line) <= 220 for line in lesson["dialog"]), topic
        assert len(lesson["questions"]) >= 6, topic
        for q in lesson["questions"]:
            assert q["id"] not in ids, f"duplicate question id {q['id']}"
            ids.add(q["id"])
            _check_mcq(q, topic, cat)
        used = {f.get("misconception") for q in lesson["questions"] for f in q["feedback"].values()} - {None}
        topic_ids = {m for m, v in cat.items() if v["topic"] == topic}
        assert len(used & topic_ids) >= 3, f"{topic} lessons should exercise at least 3 of its misconceptions"
