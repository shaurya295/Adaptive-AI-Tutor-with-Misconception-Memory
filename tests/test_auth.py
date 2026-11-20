"""Sign-in, sessions and who may see or change what."""
import pytest
from fastapi.testclient import TestClient

from backend.api.server import app
from tests.conftest import TEACHER, sign_in


@pytest.fixture
def client():
    return TestClient(app)


def test_everything_needs_a_session(client):
    for method, path, kw in [
        ("get", "/api/state", {}), ("get", "/api/profile", {}), ("get", "/api/schedule", {}),
        ("get", "/api/eval-metrics", {}), ("get", "/api/misconception-graph", {"params": {"concept": "Fractions"}}),
        ("get", "/api/escalations", {"params": {"student_id": "a@b.com"}}),
        ("post", "/api/chat", {"json": {"concept": "Fractions", "message": "hi"}}),
        ("post", "/api/quiz/start", {"json": {"concept": "Fractions", "variant": "pre"}}),
        ("post", "/api/escalations/review", {"json": {"id": 1, "warranted": True}}),
    ]:
        assert getattr(client, method)(path, **kw).status_code == 401, path


def test_login_sets_an_httponly_session_cookie(client):
    r = client.post("/api/login", json={"email": "  Riya@Gmail.com "})
    assert r.json() == {"student_id": "riya@gmail.com", "role": "student"}
    cookie = r.headers["set-cookie"].lower()
    assert "tutor_session=" in cookie and "httponly" in cookie and "samesite=lax" in cookie
    assert client.post("/api/login", json={"email": "not-an-email"}).status_code == 400


def test_students_only_see_their_own_data(client):
    sign_in(client, "victim@gmail.com")
    client.post("/api/quiz/start", json={"concept": "Fractions", "variant": "pre"})
    sign_in(client, "nosy@gmail.com")
    assert client.get("/api/profile", params={"student_id": "victim@gmail.com"}).status_code == 403
    assert client.get("/api/state", params={"student_id": "victim@gmail.com"}).status_code == 403
    assert client.get("/api/eval-metrics", params={"student_id": "victim@gmail.com"}).status_code == 403
    assert client.get("/api/schedule", params={"student_id": "victim@gmail.com"}).status_code == 403
    assert client.post("/api/chat", json={"student_id": "victim@gmail.com", "concept": "Fractions", "message": "hi"}).status_code == 403
    assert client.post("/api/quiz/submit", json={"student_id": "victim@gmail.com", "concept": "Fractions", "variant": "pre", "selected_indices": [0, 0, 0]}).status_code == 403
    assert client.get("/api/eval-metrics").status_code == 200          # their own
    assert client.get("/api/profile", params={"student_id": "NOSY@gmail.com"}).status_code == 200


def test_teacher_only_routes(client):
    sign_in(client, "student@gmail.com")
    assert client.get("/api/escalations", params={"student_id": "student@gmail.com"}).status_code == 403
    assert client.post("/api/escalations/review", json={"id": 1, "warranted": True}).status_code == 403
    sign_in(client, TEACHER)
    assert client.get("/api/escalations", params={"student_id": "victim@gmail.com"}).status_code == 200
    assert client.get("/api/profile", params={"student_id": "victim@gmail.com"}).status_code == 200
    assert client.get("/api/eval-metrics").status_code == 200          # whole class
    assert client.post("/api/chat", json={"student_id": "victim@gmail.com", "concept": "Fractions", "message": "hi"}).status_code == 403


def test_logout_ends_the_session(client):
    sign_in(client, "leaving@gmail.com")
    assert client.get("/api/profile").status_code == 200
    assert client.post("/api/logout").json() == {"ok": True}
    assert client.get("/api/profile").status_code == 401


def test_forged_cookie_is_rejected(client):
    client.cookies.set("tutor_session", "made-up-token")
    assert client.get("/api/profile").status_code == 401
