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
