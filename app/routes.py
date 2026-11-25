# app/routes.py
import hmac
import json
import os
import time
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import redis as _redis
from flask import Blueprint, abort, current_app, jsonify, request, send_from_directory

from .analytics import ANALYTICS_KEY, VALID_EVENT_TYPES, get_analytics, track_event
from .leaderboard import add_score, get_top
from .version import __version__

main_bp = Blueprint("main", __name__)

_REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
FEEDBACK_KEY = "takk:feedback"
MAX_FEEDBACK = 1000
FEEDBACK_SHOWN = 100  # newest entries returned to the analytics dashboard
_redis_client = None


def _get_redis():
    global _redis_client
    if _redis_client is None:
        _redis_client = _redis.from_url(_REDIS_URL, decode_responses=True)
    return _redis_client


# Simple in-memory rate limiting
rate_limit_store = defaultdict(list)
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX_REQUESTS = 10  # max requests per window
TRACK_RATE_LIMIT_MAX_REQUESTS = 60  # analytics events are more frequent
MAX_TRACK_DATA_BYTES = 512  # serialized size cap for /api/track `data`

# Competition scoring (must match Competition.jsx): each correct answer gives
# at most 1.17 points plus 0.05 per answer already in the streak.
SCORE_MAX_BASE = 1.17
SCORE_STREAK_BONUS = 0.05


def check_rate_limit(identifier, max_requests=RATE_LIMIT_MAX_REQUESTS):
    """Simple rate limiter: max N requests per 60 seconds per identifier."""
    now = time.time()
    recent = [t for t in rate_limit_store.get(identifier, []) if now - t < RATE_LIMIT_WINDOW]
    if len(recent) >= max_requests:
        rate_limit_store[identifier] = recent
        return False
    recent.append(now)
    rate_limit_store[identifier] = recent
    # Drop idle identifiers now and then so the store doesn't grow forever
    if len(rate_limit_store) > 10000:
        for key in [k for k, ts in rate_limit_store.items() if not ts or now - ts[-1] >= RATE_LIMIT_WINDOW]:
            del rate_limit_store[key]
    return True


def max_competition_score() -> float:
    """Highest score possible: every sign in the manifest answered correctly."""
    n = len(_load_manifest().get("signs", {}))
    return SCORE_MAX_BASE * n + SCORE_STREAK_BONUS * n * (n - 1) / 2


def _distractors_path():
    package_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(package_dir)
    return os.path.join(project_dir, "catalog", "distractors.json")


def _manifest_path():
    package_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(package_dir)
    return os.path.join(project_dir, "catalog", "manifest.json")


def _load_manifest():
    with open(_manifest_path(), encoding="utf-8") as f:
        return json.load(f)


@main_bp.get("/api/version")
def api_version():
    return jsonify({"version": __version__})


@main_bp.get("/api/scores")
def api_scores():
    top10 = get_top(limit=10)
    return jsonify({"scores": top10})


@main_bp.post("/api/score")
def api_add_score():
    # Rate limiting by IP
    ip = request.remote_addr
    if not check_rate_limit(f"score_{ip}"):
        return jsonify({"ok": False, "error": "Too many requests. Try again later."}), 429

    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    score = data.get("score")

    if not name or score is None:
        return jsonify({"ok": False, "error": "name and score required"}), 400

    # Validate name length (max 12 chars as per UI)
    if len(name) > 12:
        return jsonify({"ok": False, "error": "name too long"}), 400

    # Validate score is reasonable (prevent absurd values)
    try:
        score_float = float(score)
    except (ValueError, TypeError):
        return jsonify({"ok": False, "error": "invalid score"}), 400
    # Reject anything above what a perfect run could score (small float margin)
    if not 0 <= score_float <= max_competition_score() + 0.01:
        return jsonify({"ok": False, "error": "invalid score"}), 400

    try:
        top10, made_top = add_score(name, score_float)
        return jsonify({"ok": True, "madeTop": made_top, "scores": top10})
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@main_bp.post("/api/feedback")
def api_feedback():
    # Rate limiting by IP
    ip = request.remote_addr
    if not check_rate_limit(f"feedback_{ip}"):
        return jsonify({"ok": False, "error": "Too many requests. Try again later."}), 429

    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()

    if not message:
        return jsonify({"ok": False, "error": "message required"}), 400

    # Limit message length to 1000 characters
    if len(message) > 1000:
        return jsonify({"ok": False, "error": "message too long (max 1000 characters)"}), 400

    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    feedback_entry = {"id": str(uuid.uuid4()), "timestamp": timestamp, "message": message}

    try:
        r = _get_redis()
        # Newest first; keep only the latest MAX_FEEDBACK entries
        pipe = r.pipeline()
        pipe.lpush(FEEDBACK_KEY, json.dumps(feedback_entry, ensure_ascii=False))
        pipe.ltrim(FEEDBACK_KEY, 0, MAX_FEEDBACK - 1)
        pipe.execute()
        return jsonify({"ok": True})
    except Exception as e:
        current_app.logger.error(f"Failed to save feedback: {e}")
        return jsonify({"ok": False, "error": "server error"}), 500


@main_bp.get("/api/distractors")
def api_distractors():
    path = _distractors_path()
    if not os.path.exists(path):
        return jsonify({"2": [], "3": [], "meta": {"status": "empty"}})
    with open(path, encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = {"2": [], "3": []}
    # Normalize keys to strings "2","3"
    data = {str(k): v for k, v in (data or {}).items()}
    return jsonify(data)


@main_bp.get("/health")
def health():
    return jsonify({"ok": True})


@main_bp.route("/media/<path:filename>")
def media(filename):
    """Serve media files with path traversal protection."""
    package_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(package_dir)
    media_dir = os.path.join(project_dir, "media")

    # Sanitize filename to prevent path traversal
    # Resolve to absolute path and check it's within media_dir
    try:
        safe_path = Path(media_dir).resolve() / filename
        safe_path = safe_path.resolve()

        # Ensure the resolved path is within media_dir
        if not str(safe_path).startswith(str(Path(media_dir).resolve())):
            current_app.logger.warning(f"Path traversal attempt: {filename}")
            abort(403)

        # Check file exists
        if not safe_path.is_file():
            abort(404)

        return send_from_directory(media_dir, filename)
    except (ValueError, OSError):
        abort(404)


@main_bp.get("/api/levels")
def api_levels():
    try:
        m = _load_manifest()
        return jsonify({"levels": m.get("levels", [])})
    except FileNotFoundError:
        return jsonify({"levels": []}), 404
    except json.JSONDecodeError:
        return jsonify({"message": "Data corrupted"}), 500


@main_bp.get("/api/levels/<int:n>")
def api_level_detail(n: int):
    try:
        m = _load_manifest()
    except FileNotFoundError:
        return jsonify({"levels": []}), 404
    except json.JSONDecodeError:
        return jsonify({"message": "Data corrupted"}), 500

    level = next((L for L in m.get("levels", []) if L.get("id") == n), None)
    if not level:
        return jsonify({"error": "level not found"}), 404
    signs_meta = m.get("signs", {})
    expanded = [{"id": sid, **(signs_meta.get(sid, {"label": sid}))} for sid in level.get("signs", [])]
    return jsonify({"id": n, "name": level.get("name"), "signs": expanded})


@main_bp.get("/api/levels/<int:n>/cumulative")
def api_level_cumulative(n: int):
    """Return current level signs + cumulative signs for distractors."""
    try:
        m = _load_manifest()
    except FileNotFoundError:
        return jsonify({"levels": []}), 404
    except json.JSONDecodeError:
        return jsonify({"message": "Data corrupted"}), 500

    # Get the current level info
    current_level = next((L for L in m.get("levels", []) if L.get("id") == n), None)
    if not current_level:
        return jsonify({"error": "level not found"}), 404

    signs_meta = m.get("signs", {})

    # Current level signs only (for questions)
    current_signs = [{"id": sid, **(signs_meta.get(sid, {"label": sid}))} for sid in current_level.get("signs", [])]

    # Collect all sign IDs from levels 1 through n (for distractors)
    all_sign_ids = []
    for level in m.get("levels", []):
        if level.get("id", 0) <= n:
            all_sign_ids.extend(level.get("signs", []))

    # Remove duplicates
    seen = set()
    unique_sign_ids = []
    for sid in all_sign_ids:
        if sid not in seen:
            seen.add(sid)
            unique_sign_ids.append(sid)

    # Expand all cumulative signs
    cumulative_signs = [{"id": sid, **(signs_meta.get(sid, {"label": sid}))} for sid in unique_sign_ids]

    return jsonify(
        {"id": n, "name": current_level.get("name"), "signs": current_signs, "cumulativeSigns": cumulative_signs}  # Only current level  # All levels 1→n
    )


@main_bp.get("/api/signs")
def api_signs():
    """Return all signs as a sorted array (label, video, pictograms)."""
    try:
        m = _load_manifest()
    except FileNotFoundError:
        return jsonify({"message": "Data not found", "signs": []}), 404
    except json.JSONDecodeError:
        return jsonify({"message": "Data corrupted"}), 500

    signs_obj = m.get("signs", {})
    signs_list = []
    for sid, s in signs_obj.items():
        pics = s.get("pictograms") or ([s["symbol"]] if s.get("symbol") else [])
        entry = {
            "id": sid,
            "label": s.get("label", sid),
            "video": s.get("video"),
            "pictograms": pics,
        }
        if s.get("video_silent"):
            entry["video_silent"] = s["video_silent"]
        signs_list.append(entry)

    signs_list.sort(key=lambda x: x["label"].lower())
    return jsonify({"signs": signs_list})


# --- Analytics ---


@main_bp.post("/api/track")
def api_track():
    ip = request.remote_addr
    if not check_rate_limit(f"track_{ip}", max_requests=TRACK_RATE_LIMIT_MAX_REQUESTS):
        return jsonify({"ok": False, "error": "Too many requests"}), 429

    data = request.get_json(silent=True) or {}
    session_id = (data.get("session_id") or "").strip()
    event_type = (data.get("event_type") or "").strip()
    event_data = data.get("data") or {}

    if not session_id or not event_type:
        return jsonify({"ok": False, "error": "session_id and event_type required"}), 400

    if len(session_id) > 64:
        return jsonify({"ok": False, "error": "session_id too long"}), 400

    if event_type not in VALID_EVENT_TYPES:
        return jsonify({"ok": False, "error": "invalid event_type"}), 400

    if not isinstance(event_data, dict):
        return jsonify({"ok": False, "error": "data must be an object"}), 400

    if len(json.dumps(event_data)) > MAX_TRACK_DATA_BYTES:
        return jsonify({"ok": False, "error": "data too large"}), 400

    try:
        track_event(session_id, event_type, event_data)
        return jsonify({"ok": True})
    except Exception as e:
        current_app.logger.warning(f"Analytics unavailable (Redis down?): {e}")
        return jsonify({"ok": True})


@main_bp.get("/api/analytics")
def api_analytics():
    ip = request.remote_addr or "unknown"
    if not check_rate_limit(f"analytics_{ip}", max_requests=5):
        return jsonify({"error": "rate limit exceeded"}), 429

    if ANALYTICS_KEY:
        # Header only: query strings end up in nginx/gunicorn access logs
        provided = request.headers.get("X-Analytics-Key", "")
        if not hmac.compare_digest(provided.encode(), ANALYTICS_KEY.encode()):
            return jsonify({"error": "unauthorized"}), 401

    try:
        result = get_analytics()
    except Exception as e:
        current_app.logger.error(f"Analytics query error: {e}")
        return jsonify({"error": "server error"}), 500

    result["feedback"], result["feedback_total"] = _recent_feedback()
    return jsonify(result)


def _recent_feedback():
    """Newest FEEDBACK_SHOWN entries first. Never fails the dashboard: returns ([], 0) on error."""
    try:
        r = _get_redis()
        entries = []
        for raw in r.lrange(FEEDBACK_KEY, 0, FEEDBACK_SHOWN - 1):
            try:
                entries.append(json.loads(raw))
            except json.JSONDecodeError:
                pass
        return entries, r.llen(FEEDBACK_KEY)
    except Exception as e:
        current_app.logger.warning(f"Could not read feedback: {e}")
        return [], 0


# --- React SPA Fallback ---
@main_bp.route("/", defaults={"path": ""})
@main_bp.route("/<path:path>")
def spa_fallback(path):
    if path.startswith(("api/", "media/", "static/")):
        abort(404)

    static_dir = current_app.config["DIST_ROOT"]
    full_path = os.path.join(static_dir, path)

    # serve a real file if it exists
    if path and os.path.isfile(full_path):
        return send_from_directory(static_dir, path)

    # otherwise, fall back to index.html
    index_path = os.path.join(static_dir, "index.html")
    if not os.path.exists(index_path):
        current_app.logger.error(f"React index.html not found in {static_dir}")
        abort(500, description=f"index.html not found in {static_dir}")

    return send_from_directory(static_dir, "index.html")
