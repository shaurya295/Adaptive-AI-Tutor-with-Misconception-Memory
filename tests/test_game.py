"""PixelTutor game: rules, sign-in, answering, hints, hearts and teacher hand-off, progress views."""
from datetime import date

import pytest
from fastapi.testclient import TestClient

from backend import content, game
from backend.api.server import app
from tests.conftest import TEACHER, sign_in


def test_rules():
    assert game.level_of(0) == (1, 0) and game.level_of(250) == (3, 50)
    assert game.total_xp([True, False, True]) == 22
    assert game.coins_balance(correct_answers=3, finished_sessions=1, hints_bought=2) == 20 + 15 + 10 - 10
    today = date(2026, 11, 18)
    assert game.streak_days({date(2026, 11, 16), date(2026, 11, 17), today}, today) == 3
    assert game.streak_days({date(2026, 11, 16), date(2026, 11, 17)}, today) == 2      # yesterday still counts
    assert game.streak_days({date(2026, 11, 15)}, today) == 0
    assert [game.hearts_left(m) for m in range(5)] == [3, 2, 1, 0, 0]


@pytest.fixture
def player():
    c = TestClient(app)
    r = c.post("/api/auth/guest", json={"name": "  Ada   Lovelace "})
    assert r.status_code == 200 and r.json()["display_name"] == "Ada Lovelace"
    return c


def first_pre(concept="Fractions"):
    return content.find_question(content.get_quiz(concept, "pre")[0]["id"])


def test_quiz_never_reveals_answers(player):
    qs = player.get("/api/game/quiz", params={"variant": "pre"}).json()["questions"]
    assert [q["concept"] for q in qs] == content.topics()
    assert all(set(q) == {"question_id", "concept", "question", "choices"} for q in qs)
    assert player.get("/api/game/quiz", params={"variant": "mid"}).status_code == 400


def test_answering_updates_hud_and_shared_memory(player):
    q = first_pre()
    sess = player.post("/api/game/sessions", json={"kind": "pretest"}).json()["session_id"]
    right = player.post("/api/game/answer", json={"question_id": q["id"], "selected_index": q["answer"], "time_taken_ms": 4000, "session_id": sess}).json()
    assert right["correct"] and right["xp_delta"] == 10 and right["coins_delta"] == 5
    assert right["hud"]["xp"] == 10 and right["hud"]["coins"] == 25 and right["hud"]["streak"] == 1
    wrong_index = (q["answer"] + 1) % 4
    wrong = player.post("/api/game/answer", json={"question_id": q["id"], "selected_index": wrong_index, "session_id": sess}).json()
    assert not wrong["correct"] and wrong["correct_index"] == q["answer"] and wrong["feedback"]
    assert wrong["hud"]["hearts"] == 2
    summary = player.post(f"/api/game/sessions/{sess}/finish").json()
    assert summary["questions"] == 2 and summary["correct"] == 1 and summary["xp_earned"] == 12
    assert summary["hud"]["coins"] == 25 + 10                       # session bonus
    # the Simple dashboard and teacher see the same record
    profile = player.get("/api/profile").json()["profile"]["concept_mastery"]["Fractions"]
    assert profile["consecutive_misses"] == 1 and profile["next_review"]


def test_three_misses_call_the_teacher_and_refill_hearts(player):
    q = first_pre("Geometry")
    wrong = (q["answer"] + 1) % 4
    hearts = [player.post("/api/game/answer", json={"question_id": q["id"], "selected_index": wrong}).json() for _ in range(3)]
    assert [h["hud"]["hearts"] for h in hearts] == [2, 1, 3]
    assert [h["escalated"] for h in hearts] == [False, False, True]
    me = player.get("/api/me").json()["student_id"]
    feed = sign_in(TestClient(app), TEACHER).get("/api/escalations", params={"student_id": me}).json()["escalations"]
    assert len(feed) == 1 and "PixelTutor" in feed[0]["trigger"] and feed[0]["trigger_type"] == "Repeated failure"


def test_hints_cost_coins_but_never_block(player):
    q = first_pre("Algebra")
    first = player.post("/api/game/hint", json={"question_id": q["id"]}).json()
    assert first["clue"] and first["hud"]["coins"] == 15
    again = player.post("/api/game/hint", json={"question_id": q["id"]}).json()
    assert again["hud"]["coins"] == 15                              # same clue again is free
    others = [content.find_question(x["id"]) for t in content.topics() for x in content.get_quiz(t, "post")]
    statuses = [player.post("/api/game/hint", json={"question_id": o["id"]}).status_code for o in others[:4]]
    assert statuses[:3] == [200, 200, 200] and statuses[3] == 402     # 15 coins buy three more
    # a wrong answer still gets its feedback with no coins left
    r = player.post("/api/game/answer", json={"question_id": q["id"], "selected_index": (q["answer"] + 1) % 4}).json()
    assert r["feedback"]


def test_profile_companion_and_leaderboard(player):
    assert player.patch("/api/me", json={"companion_id": "knight"}).json()["companion_id"] == "knight"
    q = first_pre("Probability")
    player.post("/api/game/answer", json={"question_id": q["id"], "selected_index": q["answer"]})
    board = player.get("/api/game/leaderboard").json()["entries"]
    mine = [e for e in board if e["is_me"]]
    assert len(mine) == 1 and mine[0]["name"] == "ADA LOVELACE" and mine[0]["avatar"] == "knight"
    assert all(e["student_id"] is None for e in board if not e["is_me"])     # other students' ids stay private
    assert [e["rank"] for e in board] == list(range(1, len(board) + 1))


def test_progress_views(player):
    q = first_pre("Fractions")
    for i in range(6):
        player.post("/api/game/answer", json={"question_id": q["id"], "selected_index": q["answer"] if i % 2 else (q["answer"] + 1) % 4, "time_taken_ms": 5000})
    curve = player.get("/api/game/curve").json()["points"]
    assert sum(p["attempts"] for p in curve) == 6
    stats = player.get("/api/game/stats").json()
    assert stats["rolling_accuracy"] == 50.0 and stats["rolling_avg_time_ms"] == 5000 and stats["attempts"] == 6


def test_lesson_picks_a_topic(player):
    lesson = player.get("/api/game/lesson").json()
    assert lesson["concept"] in content.topics() and len(lesson["dialog"]) == 5 and lesson["questions"]
    assert lesson["lesson_total"] == 5 and "answer" not in lesson["questions"][0]
    chosen = player.get("/api/game/lesson", params={"concept": "Geometry"}).json()
    assert chosen["concept"] == "Geometry" and chosen["reason"] == "your choice"


def test_game_routes_need_a_session():
    c = TestClient(app)
    for path in ["/api/me", "/api/game/stats", "/api/game/leaderboard", "/api/game/curve"]:
        assert c.get(path).status_code == 401, path
