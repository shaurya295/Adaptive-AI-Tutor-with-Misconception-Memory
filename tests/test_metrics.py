"""The six teacher metrics, each checked against a small hand-made turn log, plus the escalation review."""
import pytest
from fastapi.testclient import TestClient

from backend.evals import metrics as m


def turn(path="hint", sid="s", concept="Fractions", **kw):
    row = {"student_id": sid, "concept": concept, "path": path, "escalated": path == "escalation",
           "warranted": None, "answer_correct": path == "praise", "missing_prerequisite": None,
           "prereq_known_before": None, "leak_guard_triggered": None, "hint_level": None}
    row.update(kw)
    return row


def test_misconception_recall():
    rows = [turn(missing_prerequisite="Common Denominators", prereq_known_before=False),
            turn(missing_prerequisite="Common Denominators", prereq_known_before=True),
            turn(missing_prerequisite="Common Denominators", prereq_known_before=True),
            turn()]                                                    # no gap flagged: not counted
    r = m.misconception_recall(rows=rows)
    assert r["value"] == pytest.approx(2 / 3) and r["sample_size"] == 3


def test_adaptation_quality_counts_only_follow_up_hints():
    rows = [turn(hint_level=1), turn(hint_level=2), turn(hint_level=1),   # rose, then dropped
            turn("praise"),                                               # run of hints ends
            turn(hint_level=1), turn(hint_level=1),                       # held
            turn(concept="Algebra", hint_level=3)]                        # first hint on another concept
    r = m.adaptation_quality(rows=rows)
    assert r["value"] == pytest.approx(2 / 3) and r["sample_size"] == 3


def test_escalation_precision_uses_teacher_verdicts():
    rows = [turn("escalation", warranted=True), turn("escalation", warranted=False),
            turn("escalation", warranted=True), turn("escalation")]       # not reviewed yet
    r = m.escalation_precision(rows=rows)
    assert r["value"] == pytest.approx(2 / 3) and r["sample_size"] == 3
    assert m.escalation_precision(rows=[turn("escalation")])["value"] is None


def test_memory_usefulness_compares_halves():
    improving = [turn(answer_correct=c) for c in (False, False, True, True)]          # 0% -> 100%
    flat = [turn(concept="Algebra", answer_correct=c) for c in (True, False, True, False, True)]  # 50% -> 50%
    r = m.memory_usefulness(rows=improving + flat)
    assert r["value"] == pytest.approx(0.5) and r["sample_size"] == 2
    assert m.memory_usefulness(rows=improving[:3])["value"] is None      # too few attempts


def test_hint_quality():
    rows = [turn(leak_guard_triggered=False), turn(leak_guard_triggered=False), turn(leak_guard_triggered=True), turn("praise")]
    assert m.hint_quality(rows=rows)["value"] == pytest.approx(2 / 3)


@pytest.fixture(scope="module")
def client():
    from backend.api.server import app

    return TestClient(app)


def _chat(client, sid, message):
    return client.post("/api/chat", json={"student_id": sid, "concept": "Fractions", "message": message}).json()


def test_live_turns_feed_the_metrics_and_the_escalation_review(client):
    sid = "metrics-live@example.com"
    _chat(client, sid, "Teach me")
    for _ in range(5):
        _chat(client, sid, "2/6")                                       # four hints, then the teacher is called
    _chat(client, sid, "Teach me again")
    _chat(client, sid, "5/6")                                           # correct (key for 2/3 + 1/6)

    shown = {x["label"]: x for x in client.get("/api/eval-metrics", params={"student_id": sid}).json()["metrics"]}
    assert shown["Adaptation quality"]["display"] == "100%"            # 0 -> 1 -> 2 -> 2 never dropped
    assert shown["Hint quality"]["display"] == "100%"
    assert shown["Memory usefulness"]["display"] == "+33 pts"          # 6 graded answers: 0 of 3 early, 1 of 3 late
    assert shown["Escalation precision"]["display"] == "—"             # nothing reviewed yet
    assert shown["Learning gain"]["description"].startswith("Avg. pre-test")

    feed = client.get("/api/escalations", params={"student_id": sid}).json()["escalations"]
    assert len(feed) == 1 and feed[0]["warranted"] is None and "Question: What is 1/2 + 1/4?" in feed[0]["trigger"]
    assert client.post("/api/escalations/review", json={"student_id": sid, "id": feed[0]["id"], "warranted": True}).json() == {"ok": True}
    shown = {x["label"]: x for x in client.get("/api/eval-metrics", params={"student_id": sid}).json()["metrics"]}
    assert shown["Escalation precision"]["display"] == "100%"
    assert client.get("/api/escalations", params={"student_id": sid}).json()["escalations"][0]["warranted"] is True


def test_review_only_applies_to_escalations(client):
    assert client.post("/api/escalations/review", json={"student_id": "x", "id": 999999, "warranted": True}).status_code == 404
