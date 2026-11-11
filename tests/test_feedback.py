# tests/test_feedback.py
import json

import fakeredis
import pytest

import testenv  # noqa: F401


@pytest.fixture(autouse=True)
def fake_redis(monkeypatch):
    import app.routes as routes

    server = fakeredis.FakeServer()
    fake = fakeredis.FakeRedis(server=server, decode_responses=True)
    monkeypatch.setattr(routes, "_redis_client", fake)
    routes.rate_limit_store.clear()
    return fake


def test_feedback_happy_path(client):
    r = client.post("/api/feedback", json={"message": "Great app!"})
    assert r.status_code == 200
    assert r.get_json() == {"ok": True}


def test_feedback_stored_in_redis(client, fake_redis):
    client.post("/api/feedback", json={"message": "Hello"})
    entries = fake_redis.lrange("takk:feedback", 0, -1)
    assert len(entries) == 1
    entry = json.loads(entries[0])
    assert entry["message"] == "Hello"
    assert "id" in entry
    assert "timestamp" in entry


def test_feedback_missing_message(client):
    r = client.post("/api/feedback", json={})
    assert r.status_code == 400
    assert r.get_json()["ok"] is False


def test_feedback_empty_message(client):
    r = client.post("/api/feedback", json={"message": "   "})
    assert r.status_code == 400


def test_feedback_message_too_long(client):
    r = client.post("/api/feedback", json={"message": "x" * 1001})
    assert r.status_code == 400


def test_feedback_rate_limit(client):
    for _ in range(10):
        client.post("/api/feedback", json={"message": "spam"})
    r = client.post("/api/feedback", json={"message": "spam"})
    assert r.status_code == 429


def test_feedback_keeps_newest_when_full(client, fake_redis):
    import app.routes as routes

    for i in range(routes.MAX_FEEDBACK):
        fake_redis.rpush(routes.FEEDBACK_KEY, json.dumps({"id": str(i), "message": "old", "timestamp": "t"}))

    r = client.post("/api/feedback", json={"message": "newest"})
    assert r.status_code == 200
    assert fake_redis.llen(routes.FEEDBACK_KEY) == routes.MAX_FEEDBACK
    assert json.loads(fake_redis.lindex(routes.FEEDBACK_KEY, 0))["message"] == "newest"


# --- Feedback in the analytics dashboard ---


@pytest.fixture()
def dashboard(monkeypatch, fake_redis):
    import app.analytics as an
    import app.routes as routes

    monkeypatch.setattr(an, "_client", fake_redis)
    monkeypatch.setattr(an, "ANALYTICS_KEY", "testkey")
    monkeypatch.setattr(routes, "ANALYTICS_KEY", "testkey")
    return {"X-Analytics-Key": "testkey"}


def test_dashboard_includes_feedback_newest_first(client, dashboard):
    client.post("/api/feedback", json={"message": "first"})
    client.post("/api/feedback", json={"message": "second"})

    data = client.get("/api/analytics", headers=dashboard).get_json()
    assert data["feedback_total"] == 2
    assert [f["message"] for f in data["feedback"]] == ["second", "first"]
    assert {"id", "timestamp", "message"} <= set(data["feedback"][0])


def test_dashboard_feedback_limited(client, fake_redis, dashboard, monkeypatch):
    import app.routes as routes

    monkeypatch.setattr(routes, "FEEDBACK_SHOWN", 3)
    for i in range(5):
        fake_redis.lpush(routes.FEEDBACK_KEY, json.dumps({"id": str(i), "message": f"m{i}", "timestamp": "t"}))

    data = client.get("/api/analytics", headers=dashboard).get_json()
    assert data["feedback_total"] == 5
    assert [f["message"] for f in data["feedback"]] == ["m4", "m3", "m2"]


def test_dashboard_works_when_feedback_unreadable(client, dashboard, monkeypatch):
    import app.routes as routes

    def broken():
        raise ConnectionError("redis down")

    monkeypatch.setattr(routes, "_get_redis", broken)
    res = client.get("/api/analytics", headers=dashboard)
    assert res.status_code == 200
    assert res.get_json()["feedback"] == []
