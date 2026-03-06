import os
from datetime import datetime, timezone

import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
LEADERBOARD_KEY = "takk:leaderboard"
MAX_KEEP = 20

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = redis.from_url(REDIS_URL, decode_responses=True)
    return _client


def add_score(name: str, score: float):
    """Add a score entry and return (top10, made_top)."""
    if not isinstance(name, str) or not name.strip():
        raise ValueError("name required")
    try:
        score = float(score)
    except Exception:
        raise ValueError("score must be a number")

    name = name.strip()[:32]
    score = round(score, 2)
    date = datetime.now(timezone.utc).isoformat(timespec="seconds")

    # Member encodes date + name so the same player can appear multiple times
    member = f"{date}|{name}"

    r = _get_client()
    r.zadd(LEADERBOARD_KEY, {member: score})
    # Trim to top MAX_KEEP by removing the lowest-scored entries beyond the limit
    r.zremrangebyrank(LEADERBOARD_KEY, 0, -(MAX_KEEP + 1))

    top10 = get_top(limit=10)
    made_top = any(e["name"] == name and e["score"] == score for e in top10)
    return top10, made_top


def get_top(limit: int = 10):
    """Return the top `limit` scores as a list of {name, score, date} dicts."""
    r = _get_client()
    results = r.zrevrange(LEADERBOARD_KEY, 0, max(0, int(limit)) - 1, withscores=True)
    entries = []
    for member, score in results:
        date, _, name = member.partition("|")
        entries.append({"name": name, "score": round(score, 2), "date": date})
    return entries
