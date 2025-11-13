# app/routes.py
import json
import os
import uuid
from datetime import datetime

from flask import Blueprint, abort, current_app, jsonify, request, send_from_directory

from .leaderboard import add_score, get_top

main_bp = Blueprint("main", __name__)


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


def _feedback_path():
    package_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(package_dir)
    return os.path.join(project_dir, "feedback.json")


@main_bp.get("/api/scores")
def api_scores():
    top10 = get_top(limit=10)
    return jsonify({"scores": top10})


@main_bp.post("/api/score")
def api_add_score():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    score = data.get("score")
    if not name or score is None:
        return jsonify({"ok": False, "error": "name and score required"}), 400

    try:
        top10, made_top = add_score(name, float(score))
        return jsonify({"ok": True, "madeTop": made_top, "scores": top10})
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400


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
    package_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(package_dir)
    media_dir = os.path.join(project_dir, "media")
    return send_from_directory(media_dir, filename)


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


@main_bp.post("/api/feedback")
def api_feedback():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()

    if not message:
        return jsonify({"ok": False, "error": "message required"}), 400

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

    # Append new feedback
    feedback_list.append(feedback_entry)

    # Write back to file
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(feedback_list, f, indent=2, ensure_ascii=False)
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


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
