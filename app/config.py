# app/config.py
import os
from pathlib import Path

from dotenv import load_dotenv

# --- Locate project root ---
BASE_DIR = Path(__file__).resolve().parent.parent

# --- Load environment file ONCE (module-level) ---
# Only load if not already loaded (prevents double-loading on reloader)
if not os.environ.get("_TAKK_ENV_LOADED"):
    env = os.getenv("FLASK_ENV", "development")
    env_file = BASE_DIR / f".env.{env}"

    if env_file.exists():
        load_dotenv(env_file)
        print(f"✓ Loaded environment: {env_file.name}")
    else:
        print(f"⚠ No .env file found for '{env}', using defaults")

    # Mark as loaded to prevent duplicate loads
    os.environ["_TAKK_ENV_LOADED"] = "1"


# --- Config class ---
class Config:
    """Central Flask configuration."""

    BASE_DIR = BASE_DIR
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"
    BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")
    SANDBOX_MODE = os.getenv("SANDBOX_MODE", "false").lower() == "true"

    @staticmethod
    def is_sandbox() -> bool:
        """Return True if app runs in sandbox/testing mode."""
        return Config.SANDBOX_MODE or Config.FLASK_ENV == "testing"
