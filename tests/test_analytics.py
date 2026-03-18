# tests/test_analytics.py
import fakeredis
import pytest

import testenv  # noqa: F401


@pytest.fixture(autouse=True)
def fake_redis(monkeypatch):
    """Replace the Redis client with a clean in-memory fakeredis for every test."""
    import app.analytics as an

    server = fakeredis.FakeServer()
    fake = fakeredis.FakeRedis(server=server, decode_responses=True)
    monkeypatch.setattr(an, "_client", fake)
    return fake


@pytest.fixture()
def analytics_key(monkeypatch):
    """Set a known ANALYTICS_KEY for route protection tests."""
    import app.analytics as an
    import app.routes as rt

    monkeypatch.setattr(an, "ANALYTICS_KEY", "testkey")
    monkeypatch.setattr(rt, "ANALYTICS_KEY", "testkey")
    return "testkey"


# --- track_event() ---


def test_track_event_valid_returns_true():
    from app.analytics import track_event

    assert track_event("session-1", "page_view", {"page": "home"}) is True


def test_track_event_invalid_type_returns_false():
    from app.analytics import track_event

    assert track_event("session-1", "nonexistent_event", {}) is False


def test_track_event_stores_in_redis(fake_redis):
    import json

    from app.analytics import track_event

    track_event("session-abc", "page_view", {"page": "home"})
    raw = fake_redis.lrange("events:page_view", 0, -1)
    assert len(raw) == 1
    event = json.loads(raw[0])
    assert event["session_id"] == "session-abc"
    assert event["event_type"] == "page_view"
    assert event["data"] == {"page": "home"}
    assert "timestamp" in event


def test_track_event_adds_session(fake_redis):
    from app.analytics import track_event

    track_event("session-1", "page_view", {})
    track_event("session-2", "page_view", {})
    track_event("session-1", "sign_completed", {"sign_id": "hej", "mode": "training"})

    assert fake_redis.scard("analytics:sessions") == 2


def test_track_event_increments_daily_counter(fake_redis):
    from datetime import datetime, timezone
    from unittest.mock import patch

    from app.analytics import track_event

    fixed_date = datetime(2026, 3, 18, 12, 0, 0, tzinfo=timezone.utc)
    with patch("app.analytics.datetime") as mock_dt:
        mock_dt.now.return_value = fixed_date
        track_event("s1", "page_view", {})
        track_event("s1", "page_view", {})

    count = fake_redis.hget("analytics:daily:2026-03-18", "page_view")
    assert int(count) == 2


def test_track_event_sets_ttl(fake_redis):
    from app.analytics import EVENT_TTL, track_event

    track_event("s1", "page_view", {})
    ttl = fake_redis.ttl("events:page_view")
    # TTL should be set and roughly equal to EVENT_TTL (within 5 seconds)
    assert EVENT_TTL - 5 <= ttl <= EVENT_TTL


# --- get_analytics() ---


def test_get_analytics_empty():
    from app.analytics import get_analytics

    result = get_analytics()
    assert result["unique_sessions"] == 0
    assert result["events"]["page_view"] == 0
    assert result["top_signs"] == []
    assert result["top_levels"] == []
    assert result["comp_count"] == 0
    assert result["quiz_count"] == 0
    assert result["recent"] == []


def test_get_analytics_unique_sessions():
    from app.analytics import get_analytics, track_event

    track_event("s1", "page_view", {})
    track_event("s2", "page_view", {})
    track_event("s1", "sign_completed", {"sign_id": "hej", "mode": "training"})

    result = get_analytics()
    assert result["unique_sessions"] == 2


def test_get_analytics_event_counts():
    from app.analytics import get_analytics, track_event

    track_event("s1", "page_view", {"page": "home"})
    track_event("s1", "page_view", {"page": "dictionary"})
    track_event("s1", "sign_completed", {"sign_id": "hej", "mode": "training"})

    result = get_analytics()
    assert result["events"]["page_view"] == 2
    assert result["events"]["sign_completed"] == 1


def test_get_analytics_top_signs():
    from app.analytics import get_analytics, track_event

    track_event("s1", "sign_completed", {"sign_id": "hej", "mode": "training"})
    track_event("s1", "sign_completed", {"sign_id": "hej", "mode": "training"})
    track_event("s1", "sign_completed", {"sign_id": "tack", "mode": "training"})

    result = get_analytics()
    top = result["top_signs"]
    assert top[0][0] == "hej" and top[0][1] == 2
    assert top[1][0] == "tack" and top[1][1] == 1


def test_get_analytics_top_levels():
    from app.analytics import get_analytics, track_event

    track_event("s1", "level_started", {"level": 2})
    track_event("s2", "level_started", {"level": 2})
    track_event("s1", "level_started", {"level": 1})

    result = get_analytics()
    top = result["top_levels"]
    assert top[0][0] == "2"
    assert top[0][1] == 2


def test_get_analytics_comp_stats():
    from app.analytics import get_analytics, track_event

    track_event("s1", "competition_attempt", {"score": 3.5, "total": 10})
    track_event("s2", "competition_attempt", {"score": 4.5, "total": 8})

    result = get_analytics()
    assert result["comp_count"] == 2
    assert result["comp_avg_score"] == 4.0


def test_get_analytics_quiz_count():
    from app.analytics import get_analytics, track_event

    track_event("s1", "quiz_attempt", {"level": 1, "total": 5})
    track_event("s2", "quiz_attempt", {"level": 2, "total": 7})

    result = get_analytics()
    assert result["quiz_count"] == 2


def test_get_analytics_recent_sorted():
    from datetime import datetime, timezone
    from unittest.mock import patch

    from app.analytics import get_analytics, track_event

    t1 = datetime(2026, 3, 18, 10, 0, 0, tzinfo=timezone.utc)
    t2 = datetime(2026, 3, 18, 11, 0, 0, tzinfo=timezone.utc)

    with patch("app.analytics.datetime") as mock_dt:
        mock_dt.now.return_value = t1
        track_event("s1", "page_view", {"page": "home"})
        mock_dt.now.return_value = t2
        track_event("s1", "sign_completed", {"sign_id": "hej", "mode": "training"})

    result = get_analytics()
    recent = result["recent"]
    assert len(recent) == 2
    # Most recent first
    assert recent[0]["timestamp"] > recent[1]["timestamp"]


# --- API routes ---


def test_api_track_valid(client):
    res = client.post(
        "/api/track",
        json={
            "session_id": "abc123",
            "event_type": "page_view",
            "data": {"page": "home"},
        },
    )
    assert res.status_code == 200
    assert res.get_json()["ok"] is True


def test_api_track_missing_fields(client):
    res = client.post("/api/track", json={"session_id": "abc"})
    assert res.status_code == 400


def test_api_track_invalid_event_type(client):
    res = client.post(
        "/api/track",
        json={
            "session_id": "abc",
            "event_type": "made_up_event",
            "data": {},
        },
    )
    assert res.status_code == 400


def test_api_track_session_id_too_long(client):
    res = client.post(
        "/api/track",
        json={
            "session_id": "x" * 65,
            "event_type": "page_view",
            "data": {},
        },
    )
    assert res.status_code == 400


def test_api_analytics_no_key(client, analytics_key):
    res = client.get("/api/analytics")
    assert res.status_code == 401


def test_api_analytics_wrong_key(client, analytics_key):
    res = client.get("/api/analytics?key=wrongkey")
    assert res.status_code == 401


def test_api_analytics_correct_key(client, analytics_key):
    res = client.get(f"/api/analytics?key={analytics_key}")
    assert res.status_code == 200
    data = res.get_json()
    assert "unique_sessions" in data
    assert "events" in data
    assert "daily" in data
    assert "recent" in data


def test_api_analytics_key_via_header(client, analytics_key):
    res = client.get("/api/analytics", headers={"X-Analytics-Key": analytics_key})
    assert res.status_code == 200
