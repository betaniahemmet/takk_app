# tests/test_hardening.py
"""Rate limiting behind a proxy, and competition score bounds."""
import fakeredis
import pytest

import testenv  # noqa: F401


@pytest.fixture()
def real_app(monkeypatch):
    """The production app factory (with ProxyFix), on fake Redis."""
    import app.routes as routes
    from app import create_app

    monkeypatch.setattr(routes, "_redis_client", fakeredis.FakeRedis(decode_responses=True))
    routes.rate_limit_store.clear()
    application = create_app()
    application.config["TESTING"] = True
    return application.test_client()


def _post_feedback(client, ip):
    # nginx connects from 127.0.0.1 and appends the real client to X-Forwarded-For
    return client.post(
        "/api/feedback",
        json={"message": "hej"},
        headers={"X-Forwarded-For": ip},
        environ_base={"REMOTE_ADDR": "127.0.0.1"},
    )


def test_rate_limit_is_per_client_behind_proxy(real_app):
    from app.routes import FEEDBACK_RATE_LIMIT_MAX_REQUESTS

    for _ in range(FEEDBACK_RATE_LIMIT_MAX_REQUESTS):
        assert _post_feedback(real_app, "203.0.113.1").status_code == 200
    assert _post_feedback(real_app, "203.0.113.1").status_code == 429
    # A different visitor is not affected by the first one's limit
    assert _post_feedback(real_app, "203.0.113.2").status_code == 200


def test_group_on_one_ip_fits_in_the_limits(real_app, monkeypatch):
    """30 people on one workplace wifi: all finish a competition and browse at once."""
    import app.analytics as an
    import app.leaderboard as lb

    fake = fakeredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr(an, "_client", fake)
    monkeypatch.setattr(lb, "_client", fake)
    env = {"REMOTE_ADDR": "127.0.0.1"}
    headers = {"X-Forwarded-For": "203.0.113.5"}
    for i in range(30):
        r = real_app.post("/api/score", json={"name": f"P{i}", "score": 0.5}, headers=headers, environ_base=env)
        assert r.status_code == 200
    for _ in range(30 * 10):
        r = real_app.post(
            "/api/track",
            json={"session_id": "s", "event_type": "sign_viewed", "data": {"sign_id": "hej"}},
            headers=headers,
            environ_base=env,
        )
        assert r.status_code == 200


def test_cors_headers_not_sent(real_app):
    r = real_app.get("/api/version", headers={"Origin": "https://evil.example"})
    assert "Access-Control-Allow-Origin" not in r.headers


def test_max_competition_score_matches_formula(monkeypatch):
    from app import routes

    monkeypatch.setattr(routes, "_load_manifest", lambda: {"signs": {f"s{i}": {} for i in range(3)}})
    # 3 correct answers: (1.17 + 0) + (1.17 + 0.05) + (1.17 + 0.10)
    assert routes.max_competition_score() == pytest.approx(3.66)


@pytest.mark.parametrize("score,status", [(3.66, 200), (3.665, 200), (3.7, 400), (-1, 400)])
def test_score_capped_at_perfect_run(client, monkeypatch, score, status):
    from app import routes

    routes.rate_limit_store.clear()
    monkeypatch.setattr(routes, "_load_manifest", lambda: {"signs": {f"s{i}": {} for i in range(3)}})
    monkeypatch.setattr(routes, "add_score", lambda name, s: ([{"name": name, "score": s}], True))
    r = client.post("/api/score", json={"name": "HB", "score": score})
    assert r.status_code == status
