# testenv.py
# testenv.py
"""
Ensures pytest runs in isolation and uses a clean environment.
Import this at the top of your tests if you need shared settings.
"""

import os
import sys
from pathlib import Path

# --- Project root ---
BASE_DIR = Path(__file__).resolve().parent

# --- Ensure imports for app/ and video_processing/ ---
sys.path.insert(0, str(BASE_DIR))

# --- Base testing environment variables ---
os.environ["FLASK_SKIP_DOTENV"] = "1"
os.environ.setdefault("FLASK_ENV", "testing")
os.environ.setdefault("PYTHONPATH", str(BASE_DIR))
os.environ.setdefault("DO_NOT_TOUCH_REAL_DATA", "1")

# --- Explicit test mode ---
os.environ["SANDBOX_MODE"] = "true"

# --- Temporary isolated dirs for media/catalog ---
TMP_DIR = BASE_DIR / "tests" / "_tmp"
TMP_DIR.mkdir(parents=True, exist_ok=True)

os.environ.setdefault("CATALOG_DIR", str(TMP_DIR / "catalog"))
os.environ.setdefault("MEDIA_DIR", str(TMP_DIR / "media"))

print("[testenv] Environment initialized for pytest")
print(f"[testenv] Using isolated dirs under: {TMP_DIR}")
