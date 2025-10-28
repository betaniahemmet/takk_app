import os, json, threading, tempfile
from datetime import datetime, timezone

# Paths
PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(PACKAGE_DIR)
CATALOG_DIR = os.path.join(PROJECT_DIR, "catalog")
LEADERBOARD_PATH = os.path.join(CATALOG_DIR, "leaderboard.json")

_LOCK = threading.Lock()

def _ensure_files():
    os.makedirs(CATALOG_DIR, exist_ok=True)
    if not os.path.exists(LEADERBOARD_PATH):
        with open(LEADERBOARD_PATH, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False)

def _read_all():
    _ensure_files()
    with open(LEADERBOARD_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def _atomic_write(data):
    os.makedirs(CATALOG_DIR, exist_ok=True)
    tmp_fd, tmp_path = tempfile.mkstemp(dir=CATALOG_DIR, prefix="lb_", suffix=".json")
    try:
        with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        os.replace(tmp_path, LEADERBOARD_PATH)  # atomic on POSIX/NT
    finally:
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass

def add_score(name: str, score: float, max_keep: int = 1000):
    if not isinstance(name, str) or not name.strip():
        raise ValueError("name required")
    try:
        score = float(score)
    except Exception:
        raise ValueError("score must be a number")

    entry = {
        "name": name.strip()[:32],
        "score": round(score, 2),
        "date": datetime.now(timezone.utc).isoformat(timespec="seconds")
    }

    with _LOCK:
        data = _read_all()
        data.append(entry)
        # sort descending by score, then by date (latest first)
        data.sort(key=lambda e: (e.get("score", 0.0), e.get("date", "")), reverse=True)
        if max_keep:
            data = data[:max_keep]
        _atomic_write(data)

    # after write, compute whether this entry made top 10
    top10 = data[:10]
    made_top = any(
        e["name"] == entry["name"] and e["score"] == entry["score"]
        for e in top10
    )
    return top10, made_top

def get_top(limit: int = 10):
    data = _read_all()
    return data[:max(0, int(limit))]
