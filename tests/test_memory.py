"""Student memory lives in SQL and the prerequisite graph in a content file: neither needs Neo4j."""
import pytest
from fastapi.testclient import TestClient

from tests.conftest import TEACHER, sign_in

from backend import content
from backend.memory import misconception_graph as graph
from backend.memory.student_graph_store import load_student_profile, save_student_profile


def test_profile_round_trip_and_overwrite():
    sid = "memory-tester@example.com"
    assert load_student_profile(sid)["concept_mastery"] == {}
    profile = {
        "student_id": sid,
        "concept_mastery": {"Fractions": {"mastery": 0.42, "consecutive_misses": 2}},
        "weak_prerequisites": ["Common Denominators"],
        "recent_attempts": [{"concept": "Fractions", "correct": False}],
    }
    save_student_profile(sid, profile)
    assert load_student_profile(sid) == profile
    profile["concept_mastery"]["Fractions"] = {"mastery": 0.57, "consecutive_misses": 0}
    profile["concept_mastery"]["Algebra"] = {"mastery": 0.3, "consecutive_misses": 1}
    save_student_profile(sid, profile)
    assert load_student_profile(sid) == profile


def test_students_are_isolated():
    save_student_profile("a@example.com", {"concept_mastery": {"Geometry": {"mastery": 0.9, "consecutive_misses": 0}}})
    assert load_student_profile("b@example.com")["concept_mastery"] == {}


def test_every_topic_is_in_the_graph_with_ui_names():
    concepts = graph.get_all_concepts()
    for topic in content.topics():
        assert topic in concepts
        assert graph.get_prerequisites(topic), f"{topic} has no prerequisites"
    assert graph.get_prerequisites("Fractions") == ["Comparing Unit Fractions", "Common Denominators"]
    assert "Part-Whole Division" in graph.get_deep_prerequisites("Algebra")
    assert graph.get_prerequisites("Knitting") == []


@pytest.fixture(scope="module")
def client():
    from backend.api.server import app

    return TestClient(app)


def test_placement_score_is_remembered(client):
    sign_in(client, "placement@example.com")
    who = {"student_id": "placement@example.com", "concept": "Algebra"}
    key = [q["answer"] for q in content.get_quiz("Algebra", "pre")]
    client.post("/api/quiz/start", json={**who, "variant": "pre"})
    client.post("/api/quiz/submit", json={**who, "variant": "pre", "selected_indices": [key[0], key[1], (key[2] + 1) % 4]})
    entry = client.get("/api/profile", params={"student_id": who["student_id"]}).json()["profile"]["concept_mastery"]["Algebra"]
    assert entry["mastery"] == pytest.approx(2 / 3)
    assert entry["next_review"] and entry["last_practiced"]
    # retaking the placement check must not overwrite it
    client.post("/api/quiz/submit", json={**who, "variant": "pre", "selected_indices": [None, None, None]})
    again = client.get("/api/profile", params={"student_id": who["student_id"]}).json()["profile"]["concept_mastery"]["Algebra"]
    assert again["mastery"] == pytest.approx(2 / 3)


def test_graph_endpoint_shows_prerequisites_with_mastery(client):
    sign_in(client, "graph@example.com")
    save_student_profile("graph@example.com", {"concept_mastery": {"Fractions": {"mastery": 0.45, "consecutive_misses": 0}, "Common Denominators": {"mastery": 0.28, "consecutive_misses": 1}}})
    data = client.get("/api/misconception-graph", params={"concept": "Fractions", "student_id": "graph@example.com"}).json()
    assert data["neo4j_available"] is True
    assert [n["name"] for n in data["nodes"]] == ["Fractions", "Comparing Unit Fractions", "Common Denominators"]
    assert data["nodes"][0]["is_focus"] and data["nodes"][2]["mastery"] == pytest.approx(0.28)
    assert {"from": "Fractions", "to": "Common Denominators"} in data["edges"]
