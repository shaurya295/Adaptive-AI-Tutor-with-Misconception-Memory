"""The tutoring turn: answer matching, hint ladder, leak guard, escalation and model outages."""
import pytest
from fastapi.testclient import TestClient

from backend import llm
from backend.agents.diagnostic_agent import ErrorType, choose_strategy
from backend.agents.tutor_planner import leaks_answer, plan_hint
from backend.grading import match_answer


@pytest.mark.parametrize(
    "answer, key, expected",
    [
        ("3/4", "3/4", True), ("0.75", "3/4", True), ("6/8", "3/4", True), ("2/4", "1/2", True),
        ("2/6", "3/4", False), ("x = 4", "4", True), ("x=-5", "-5", True), ("The answer is 7.", "7", True),
        ("70 degrees", "70", True), ("70°", "70", True), ("28 cm²", "28", True), ("1 1/2", "3/2", True),
        ("75%", "75%", True), ("75 percent", "75%", True), ("0.75", "75%", False), (".7", "0.7", True),
        ("I think it's 3/4 because 2/4 + 1/4", "3/4", None), ("idk", "3/4", None), ("1/0", "3/4", None),
    ],
)
def test_answer_matcher(answer, key, expected):
    assert match_answer(answer, key) is expected


def test_exact_form_questions():
    assert match_answer("3/10", "3/10", exact_form=True) is True
    assert match_answer("6/20", "3/10", exact_form=True) is False      # right value, not lowest terms
    assert match_answer("3/5", "0.6", exact_form=True) is False        # asked for a decimal
    assert match_answer(".6", "0.6", exact_form=True) is True


def test_leak_guard_only_fires_on_the_answer():
    q = "What is 1/2 + 1/4?"
    assert leaks_answer("So the answer is 3/4.", "3/4", q)
    assert not leaks_answer("Rewrite 1/2 as 2/4, then add the numerators. What do you get?", "3/4", q)
    assert not leaks_answer("For example 1/3 + 1/6 = 3/6. Now try yours.", "3/4", q)       # a different worked example
    assert leaks_answer("Divide both sides, so x = 4.", "4", "Solve for x: 2x + 3 = 11")
    assert not leaks_answer("There are 2 steps: subtract 3, then divide by 2.", "4", "Solve for x: 2x + 3 = 11")
    assert not leaks_answer("Which is bigger, 2/5 or 3/10?", "2/5", "Which is greater: 2/5 or 3/10?")  # already in the question


def test_leaky_hint_is_replaced_not_escalated(monkeypatch):
    monkeypatch.setattr(llm, "_call", lambda *a, **k: "Easy: the answer is 3/4.")
    plan = plan_hint("What is 1/2 + 1/4?", "2/6", "Fractions", "small_clue", reference_answer="3/4")
    assert plan.leak_guard_triggered and plan.written_by == "fallback"
    assert "3/4" not in plan.hint_text and plan.escalation_flag is False


def test_hint_ladder_climbs():
    assert [choose_strategy(ErrorType.CONCEPTUAL, n).value for n in range(4)] == ["small_clue", "stronger_hint", "worked_example", "worked_example"]
    assert choose_strategy(ErrorType.CARELESS, 0).value == "retry_prompt"
    assert choose_strategy(ErrorType.PREREQUISITE, 1).value == "prerequisite_review"


@pytest.fixture(scope="module")
def client():
    from backend.api.server import app

    return TestClient(app)


def _chat(client, sid, message, concept="Fractions"):
    return client.post("/api/chat", json={"student_id": sid, "concept": concept, "message": message})


def test_full_session(client):
    sid = "session@example.com"
    first = _chat(client, sid, "How do I add fractions?").json()
    assert first["active_question"] == "What is 1/2 + 1/4?" and "**Try this:**" in first["reply"]

    ladder = []
    for _ in range(4):
        r = _chat(client, sid, "2/6").json()
        ladder.append(r["hint_ladder"].get("current_index"))
        assert r["active_question"] == "What is 1/2 + 1/4?" and not r["escalated"]      # same problem stays open
    assert ladder == [0, 1, 2, 2]
    entry = r["profile"]["concept_mastery"]["Fractions"]
    assert entry["consecutive_misses"] == 4 and entry["mastery"] < 0.3

    fifth = _chat(client, sid, "2/6").json()                                              # fifth miss: teacher is called
    assert fifth["escalated"] and fifth["hint_ladder"]["kind"] == "note" and fifth["active_question"] is None
    assert fifth["profile"]["concept_mastery"]["Fractions"]["consecutive_misses"] == 0   # not sticky
    feed = client.get("/api/escalations", params={"student_id": sid}).json()["escalations"]
    assert len(feed) == 1 and feed[0]["trigger_type"] == "Repeated failure" and feed[0]["misses"] == 4

    again = _chat(client, sid, "Can you explain once more?").json()
    assert again["active_question"] == "What is 2/3 + 1/6?" and not again["escalated"]


def test_correct_answer_needs_no_model_call(client):
    sid = "correct@example.com"
    _chat(client, sid, "Teach me fractions")
    before = llm.calls_made
    r = _chat(client, sid, "0.75").json()                         # equivalent to the key 3/4
    assert llm.calls_made == before
    assert r["active_question"] == "What is 2/3 + 1/6?" and r["hint_ladder"] == {"kind": "none"}
    entry = r["profile"]["concept_mastery"]["Fractions"]
    assert entry["mastery"] == pytest.approx(0.45) and entry["consecutive_misses"] == 0
    before = llm.calls_made
    _chat(client, sid, "1/3")                                     # wrong: one judging call + one hint call
    assert llm.calls_made - before == 2


def test_topics_keep_their_own_problem(client):
    sid = "topics@example.com"
    _chat(client, sid, "Start", concept="Fractions")
    _chat(client, sid, "Start", concept="Algebra")
    state = lambda c: client.get("/api/state", params={"student_id": sid, "concept": c}).json()["active_question"]
    assert state("Fractions") == "What is 1/2 + 1/4?" and state("Algebra") == "Solve for x: 2x + 3 = 11"


def test_model_outage_is_not_marked_against_the_student(client, monkeypatch):
    sid = "outage@example.com"
    _chat(client, sid, "Teach me fractions")

    def down(*a, **k):
        raise llm.LLMError("connection refused")

    monkeypatch.setattr(llm, "_call", down)
    r = _chat(client, sid, "I think it is maybe 2/6?")
    assert r.status_code == 503 and "not marked" in r.json()["detail"]
    profile = client.get("/api/profile", params={"student_id": sid}).json()["profile"]
    assert "Fractions" not in profile["concept_mastery"] and profile["recent_attempts"] == []
    assert _chat(client, sid, "   ").status_code == 400
