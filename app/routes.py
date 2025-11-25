# app/routes.py
import json
import os
import time
from collections import defaultdict
from pathlib import Path

from flask import Blueprint, abort, current_app, jsonify, request, send_from_directory

from .leaderboard import add_score, get_top
from .version import __version__

main_bp = Blueprint("main", __name__)

# Simple in-memory rate limiting
rate_limit_store = defaultdict(list)
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX_REQUESTS = 10  # max requests per window


def check_rate_limit(identifier):
    """Simple rate limiter: max 10 requests per 60 seconds per identifier."""
    now = time.time()

    # Clean old entries
    rate_limit_store[identifier] = [timestamp for timestamp in rate_limit_store[identifier] if now - timestamp < RATE_LIMIT_WINDOW]

    # Check if limit exceeded
    if len(rate_limit_store[identifier]) >= RATE_LIMIT_MAX_REQUESTS:
        return False

    # Add current request
    rate_limit_store[identifier].append(now)
    return True


def _distractors_path():
    package_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(package_dir)
    return os.path.join(project_dir, "catalog", "distractors.json")


def _manifest_path():
    package_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(package_dir)
    return os.path.join(project_dir, "catalog", "manifest.json")


def _feedback_path():
    package_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(package_dir)
    return os.path.join(project_dir, "feedback.json")


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

    # Validate name length (max 10 chars as per UI)
    if len(name) > 10:
        return jsonify({"ok": False, "error": "name too long"}), 400

    # Validate score is reasonable (prevent absurd values)
    try:
        score_float = float(score)
        if score_float < 0 or score_float > 100000:
            return jsonify({"ok": False, "error": "invalid score"}), 400
    except (ValueError, TypeError):
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

    import uuid
    from datetime import datetime

    feedback_entry = {"id": str(uuid.uuid4()), "timestamp": datetime.utcnow().isoformat() + "Z", "message": message}

    path = _feedback_path()

    # Read existing feedback or start with empty list
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                feedback_list = json.load(f)
        except json.JSONDecodeError:
            feedback_list = []
    else:
        feedback_list = []

    # Check file size limit (prevent disk fill - max 1000 entries)
    if len(feedback_list) >= 1000:
        return jsonify({"ok": False, "error": "feedback storage full"}), 507

    # Append new feedback
    feedback_list.append(feedback_entry)

    # Write back to file
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(feedback_list, f, indent=2, ensure_ascii=False)
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
        signs_list.append(
            {
                "id": sid,
                "label": s.get("label", sid),
                "video": s.get("video"),
                "pictograms": pics,
            }
        )

    signs_list.sort(key=lambda x: x["label"].lower())
    return jsonify({"signs": signs_list})


# --- React SPA Fallback ---
@main_bp.route("/", defaults={"path": ""})
@main_bp.route("/<path:path>")
def spa_fallback(path):
    if path.startswith(("api/", "media/", "static/")):
        abort(404)

    static_dir = current_app.static_folder
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
