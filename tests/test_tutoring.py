"""The tutoring turn: answer matching, hint ladder, leak guard, escalation and model outages."""
import pytest
from fastapi.testclient import TestClient

from tests.conftest import TEACHER, sign_in

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
    sign_in(client, sid)
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
    feed = sign_in(client, TEACHER).get("/api/escalations", params={"student_id": sid}).json()["escalations"]
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
    profile = client.get("/api/profile").json()["profile"]                 # no id needed: it is your own
    assert "Fractions" not in profile["concept_mastery"] and profile["recent_attempts"] == []
    assert _chat(client, sid, "   ").status_code == 400


def test_explain_only_never_opens_a_problem(client):
    sid = "freequest@example.com"
    sign_in(client, sid)
    r = client.post("/api/chat", json={"concept": "Fractions", "message": "What is a fraction?", "explain_only": True}).json()
    assert r["active_question"] is None and "Try this" not in r["reply"]
    again = client.post("/api/chat", json={"concept": "Fractions", "message": "2/6", "explain_only": True}).json()
    assert again["hint_ladder"] == {"kind": "none"} and again["active_question"] is None      # explained, not graded


@pytest.mark.parametrize(
    "question, answer, key, model_label, expected",
    [
        ("What is 1/2 + 1/4?", "2/6", "3/4", "careless", "conceptual"),       # far off: a wrong method
        ("Solve for x: 5x - 7 = 18", "6", "5", "none", "careless"),           # within 25%: a slip
        ("Solve for x: 4 - x = 9", "5", "-5", "conceptual", "careless"),      # sign slip
        ("Which is greater: 2/5 or 3/10?", "3/10", "2/5", "careless", "conceptual"),  # picked the other option
        ("Convert 0.75 to a percentage.", "7.5%", "75%", "careless", "conceptual"),
        ("Solve for x: 2x + 3 = 11", "x is about 4ish?", "4", "careless", "careless"),  # not a bare number: model decides
        ("Solve for x: 2x + 3 = 11", "dunno", "4", "none", "conceptual"),
        ("What is 1/2 + 1/4?", "2/6", "3/4", "prerequisite", "prerequisite"),
    ],
)
def test_error_type_rules(question, answer, key, model_label, expected):
    from backend.agents.evaluator_agent import classify_error

    assert classify_error(question, answer, key, model_label) == expected


@pytest.mark.parametrize(
    "message, expected",
    [
        ("Can you explain fractions?", True), ("why do we need a common denominator", True),
        ("what is the capital of france", True), ("2/6", False), ("is it 5/6?", False),
        ("I don't know", False), ("no idea", False), ("idk", False),
        ("Teach me probability", True), ("show me an example", True), ("please explain again", True),
        ("I want to learn algebra", True), ("lets do geometry", True), ("bananas are yellow", False),
    ],
)
def test_question_or_answer(message, expected):
    from backend.api.server import looks_like_question

    assert looks_like_question(message) is expected


def test_mentions_key():
    from backend.agents.evaluator_agent import mentions_key

    assert mentions_key("is it 5/6?", "5/6") and mentions_key("I got 10/12", "5/6") and mentions_key("0.75", "75%")
    assert not mentions_key("the capital of France is Paris", "5/6") and not mentions_key("it is 4/6", "5/6")
    assert mentions_key("anything", "a right angle")          # word keys are left to the model


def test_question_while_a_problem_is_open_is_not_graded(client):
    sid = "asks-questions@example.com"
    _chat(client, sid, "Teach me probability", concept="Probability")
    before = client.get("/api/profile").json()["profile"]["concept_mastery"]
    r = _chat(client, sid, "Can you explain fractions instead?", concept="Probability").json()
    assert "back to your problem" in r["reply"] and r["active_question"] and r["hint_ladder"] == {"kind": "none"}
    assert client.get("/api/profile").json()["profile"]["concept_mastery"] == before       # nothing recorded


def test_model_cannot_call_an_unrelated_reply_correct(client, monkeypatch):
    sid = "random-reply@example.com"
    _chat(client, sid, "Teach me fractions")
    real_call = llm._call

    def says_correct(task, user, schema, *a, **k):
        if task == "assess":
            return '{"verdict": "correct", "error_type": "none", "misconception": "", "missing_prerequisite": "none", "confidence": 0.9, "distress": false}'
        return real_call(task, user, schema, *a, **k)

    monkeypatch.setattr(llm, "_call", says_correct)
    r = _chat(client, sid, "bananas are yellow").json()
    assert not r["reply"].startswith(("That's right", "Correct", "Spot on", "Yes, that's it")) and r["hint_ladder"]["kind"] == "steps"
