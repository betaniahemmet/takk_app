import json
import os
from datetime import datetime, timedelta, timezone

import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
ANALYTICS_KEY = os.getenv("ANALYTICS_KEY", "")
EVENT_TTL = 90 * 24 * 60 * 60  # 90 days in seconds

VALID_EVENT_TYPES = {
    "page_view",
    "sign_completed",
    "sign_viewed",
    "quiz_attempt",
    "competition_attempt",
    "level_started",
    "level_completed",
}

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = redis.from_url(REDIS_URL, decode_responses=True)
    return _client


def track_event(session_id: str, event_type: str, data: dict) -> bool:
    """Log an event to Redis. Returns True on success."""
    if event_type not in VALID_EVENT_TYPES:
        return False

    r = _get_client()
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")

    event = {
        "session_id": session_id,
        "timestamp": now.isoformat(timespec="seconds"),
        "event_type": event_type,
        "data": data,
    }

    pipe = r.pipeline()

    # Append to per-type list and refresh TTL
    list_key = f"events:{event_type}"
    pipe.rpush(list_key, json.dumps(event))
    pipe.expire(list_key, EVENT_TTL)

    # Track unique sessions
    pipe.sadd("analytics:sessions", session_id)

    # Increment daily counter
    pipe.hincrby(f"analytics:daily:{date_str}", event_type, 1)

    pipe.execute()
    return True


def get_analytics() -> dict:
    """Aggregate and return analytics data."""
    r = _get_client()

    result = {
        "unique_sessions": r.scard("analytics:sessions"),
        "events": {},
        "daily": {},
        "recent": [],
    }

    # Total count per event type
    for event_type in VALID_EVENT_TYPES:
        result["events"][event_type] = r.llen(f"events:{event_type}")

    # Daily stats — last 30 days
    today = datetime.now(timezone.utc).date()
    for i in range(30):
        date = today - timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        day_data = r.hgetall(f"analytics:daily:{date_str}")
        if day_data:
            result["daily"][date_str] = {k: int(v) for k, v in day_data.items()}

    # Recent events — last 10 per type, sorted by timestamp, top 20 total
    recent = []
    for event_type in VALID_EVENT_TYPES:
        for raw in r.lrange(f"events:{event_type}", -10, -1):
            try:
                recent.append(json.loads(raw))
            except json.JSONDecodeError:
                pass

    recent.sort(key=lambda e: e.get("timestamp", ""), reverse=True)
    result["recent"] = recent[:20]

    # Top 10 most practiced signs
    sign_counts = {}
    for raw in r.lrange("events:sign_completed", 0, -1):
        try:
            event = json.loads(raw)
            sign_id = event.get("data", {}).get("sign_id", "unknown")
            sign_counts[sign_id] = sign_counts.get(sign_id, 0) + 1
        except json.JSONDecodeError:
            pass
    result["top_signs"] = sorted(sign_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    # Top 5 most started levels
    level_counts = {}
    for raw in r.lrange("events:level_started", 0, -1):
        try:
            event = json.loads(raw)
            level = str(event.get("data", {}).get("level", "unknown"))
            level_counts[level] = level_counts.get(level, 0) + 1
        except json.JSONDecodeError:
            pass
    result["top_levels"] = sorted(level_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    # Competition stats
    comp_scores = []
    for raw in r.lrange("events:competition_attempt", 0, -1):
        try:
            event = json.loads(raw)
            score = event.get("data", {}).get("score")
            if score is not None:
                comp_scores.append(float(score))
        except (json.JSONDecodeError, ValueError):
            pass
    result["comp_count"] = len(comp_scores)
    result["comp_avg_score"] = round(sum(comp_scores) / len(comp_scores), 2) if comp_scores else 0

    # Quiz count
    result["quiz_count"] = r.llen("events:quiz_attempt")

    return result
