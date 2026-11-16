"""The multiple-choice placement check and post-test: bank integrity and API behaviour."""
import pytest
from fastapi.testclient import TestClient

from backend import content


def test_bank_is_well_formed():
    ids = set()
    for topic in content.topics():
        for variant in content.VARIANTS:
            questions = content.get_quiz(topic, variant)
            assert len(questions) >= 3, (topic, variant)
            for q in questions:
                assert len(q["choices"]) == 4 and len(set(q["choices"])) == 4, q
                assert 0 <= q["answer"] < 4, q
                assert q["id"] not in ids, "duplicate question id"
                ids.add(q["id"])


def test_pre_and_post_use_different_questions():
    for topic in content.topics():
        pre = {q["question"] for q in content.get_quiz(topic, "pre")}
        post = {q["question"] for q in content.get_quiz(topic, "post")}
        assert not pre & post, topic


def test_grading_is_by_index():
    answers = [q["answer"] for q in content.get_quiz("Fractions", "pre")]
    assert all(r["correct"] for r in content.grade_quiz("Fractions", "pre", answers))
    wrong = [(a + 1) % 4 for a in answers]
    assert not any(r["correct"] for r in content.grade_quiz("Fractions", "pre", wrong))
    assert not any(r["correct"] for r in content.grade_quiz("Fractions", "pre", [None, 9, -1]))


@pytest.fixture(scope="module")
def client():
    from backend.api.server import app

    return TestClient(app)


def test_quiz_round_trip(client):
    who = {"student_id": "quiz-tester@example.com", "concept": "Fractions"}
    start = client.post("/api/quiz/start", json={**who, "variant": "pre"}).json()
    assert len(start["questions"]) == 3
    assert set(start["questions"][0]) == {"question_id", "question", "choices"}   # the answer key never leaves the server
    key = [q["answer"] for q in content.get_quiz("Fractions", "pre")]
    picked = [key[0], key[1], (key[2] + 1) % 4]
    assert client.post("/api/quiz/submit", json={**who, "variant": "pre", "selected_indices": picked}).json() == {"correct": 2, "total": 3}
    state = client.get("/api/state", params=who).json()
    assert state["pre_test_scores"]["Fractions"] == [2, 3]
    post_key = [q["answer"] for q in content.get_quiz("Fractions", "post")]
    assert client.post("/api/quiz/submit", json={**who, "variant": "post", "selected_indices": post_key}).json() == {"correct": 3, "total": 3}


def test_quiz_rejects_bad_input(client):
    who = {"student_id": "quiz-tester@example.com", "concept": "Fractions"}
    assert client.post("/api/quiz/start", json={**who, "variant": "final"}).status_code == 400
    unknown = {"student_id": "quiz-tester@example.com", "concept": "Knitting"}
    assert client.post("/api/quiz/start", json={**unknown, "variant": "pre"}).json() == {"questions": []}
    assert client.post("/api/quiz/submit", json={**unknown, "variant": "pre", "selected_indices": [0]}).status_code == 404
