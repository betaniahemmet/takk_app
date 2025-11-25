# app/version.py
"""Version management for TAKK app."""
from pathlib import Path


def get_version():
    """Read version from VERSION file."""
    version_file = Path(__file__).parent.parent / "VERSION"
    try:
        with open(version_file, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "unknown"


__version__ = get_version()
