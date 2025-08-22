# app/routes.py
from flask import Blueprint, jsonify, current_app, send_from_directory
import os, json

main_bp = Blueprint("main", __name__)


def _manifest_path():
    package_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(package_dir)
    return os.path.join(project_dir, "catalog", "manifest.json")


def _load_manifest():
    with open(_manifest_path(), encoding="utf-8") as f:
        return json.load(f)


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
        return jsonify({"levels": []})


@main_bp.get("/api/levels/<int:n>")
def api_level_detail(n: int):
    m = _load_manifest()
    level = next((L for L in m.get("levels", []) if L.get("id") == n), None)
    if not level:
        return jsonify({"error": "level not found"}), 404
    signs_meta = m.get("signs", {})
    expanded = [
        {"id": sid, **(signs_meta.get(sid, {"label": sid}))}
        for sid in level.get("signs", [])
    ]
    return jsonify({"id": n, "name": level.get("name"), "signs": expanded})


@main_bp.get("/api/signs")
def api_signs():
    try:
        m = _load_manifest()
        return jsonify(m.get("signs", {}))
    except FileNotFoundError:
        return jsonify({})


# SPA fallback
@main_bp.route("/", defaults={"path": ""})
@main_bp.route("/<path:path>")
def spa(path):
    static_dir = current_app.static_folder  # <- use what create_app() configured
    target = os.path.join(static_dir, path) if path else None
    if path and os.path.isfile(target):
        return send_from_directory(static_dir, path)
    return send_from_directory(static_dir, "index.html")
