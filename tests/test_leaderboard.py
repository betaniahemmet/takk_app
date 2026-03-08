# tests/test_leaderboard.py
import fakeredis
import pytest

import testenv  # noqa: F401


@pytest.fixture(autouse=True)
def fake_redis(monkeypatch):
    """Replace the Redis client with an in-memory fakeredis instance.

    This prevents any test in this file from touching a real Redis server.
    The fixture is autouse so every test gets a clean, empty leaderboard.
    """
    import app.leaderboard as lb

    server = fakeredis.FakeServer()
    fake = fakeredis.FakeRedis(server=server, decode_responses=True)
    # Reset the module-level singleton so _get_client() returns our fake
    monkeypatch.setattr(lb, "_client", fake)
    return fake


def test_get_top_empty():
    from app.leaderboard import get_top

    assert get_top() == []


def test_add_score_returns_entry():
    from app.leaderboard import add_score

    top, made_top = add_score("Alice", 5.5)
    assert made_top is True
    assert top[0]["name"] == "Alice"
    assert top[0]["score"] == 5.5


def test_scores_sorted_descending():
    from app.leaderboard import add_score, get_top

    add_score("Low", 1.0)
    add_score("High", 9.9)
    add_score("Mid", 5.0)

    top = get_top(limit=10)
    scores = [e["score"] for e in top]
    assert scores == sorted(scores, reverse=True)


def test_made_top_false_when_below_cutoff():
    from app.leaderboard import MAX_KEEP, add_score

    # Fill the board with MAX_KEEP high scores
    for i in range(MAX_KEEP):
        add_score(f"Player{i}", float(100 - i))

    # A very low score should not make the top list
    _, made_top = add_score("Loser", 0.01)
    assert made_top is False


def test_trimmed_to_max_keep():
    from app.leaderboard import MAX_KEEP, add_score, get_top

    for i in range(MAX_KEEP + 5):
        add_score(f"Player{i}", float(i))

    # Even asking for more than MAX_KEEP, we never return more than MAX_KEEP
    top = get_top(limit=MAX_KEEP + 10)
    assert len(top) <= MAX_KEEP


def test_same_player_can_appear_multiple_times():
    """Member key encodes timestamp + name, so one player can appear multiple times
    as long as the submissions happen in different seconds.

    leaderboard.py uses timespec="seconds", so two calls within the same second
    produce the same Redis member key and ZADD just updates the score (only the
    higher score survives). We mock datetime to force distinct timestamps.
    """
    from datetime import datetime, timezone
    from unittest.mock import patch

    from app.leaderboard import add_score, get_top

    t1 = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    t2 = datetime(2026, 1, 1, 12, 0, 1, tzinfo=timezone.utc)

    with patch("app.leaderboard.datetime") as mock_dt:
        mock_dt.now.return_value = t1
        add_score("Alice", 3.0)
        mock_dt.now.return_value = t2
        add_score("Alice", 7.0)

    top = get_top(limit=10)
    alice_entries = [e for e in top if e["name"] == "Alice"]
    assert len(alice_entries) == 2


def test_score_rounded_to_two_decimals():
    from app.leaderboard import add_score

    top, _ = add_score("Bob", 3.14159)
    assert top[0]["score"] == 3.14


def test_entry_has_required_fields():
    from app.leaderboard import add_score

    top, _ = add_score("Alice", 5.0)
    entry = top[0]
    assert set(entry.keys()) == {"name", "score", "date"}
    assert isinstance(entry["name"], str)
    assert isinstance(entry["score"], float)
    assert isinstance(entry["date"], str)


def test_name_stripped_and_truncated():
    from app.leaderboard import add_score

    # name > 32 chars should be silently truncated (leaderboard.py:29 slices at 32)
    long_name = "A" * 50
    top, _ = add_score(long_name, 1.0)
    assert len(top[0]["name"]) <= 32


def test_empty_name_raises():
    from app.leaderboard import add_score

    with pytest.raises(ValueError, match="name required"):
        add_score("", 5.0)


def test_invalid_score_raises():
    from app.leaderboard import add_score

    with pytest.raises(ValueError, match="score must be a number"):
        add_score("Alice", "not-a-number")
