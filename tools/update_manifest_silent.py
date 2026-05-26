"""
After running batch_silent.py, run this to add video_silent paths to manifest.json
for every sign that has a *_tyst_square.mp4 file in its folder.

Safe to re-run — overwrites existing video_silent values.
"""

import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MANIFEST = BASE_DIR / "catalog" / "manifest.json"
SIGNS_DIR = BASE_DIR / "media" / "signs"


def main():
    with open(MANIFEST, encoding="utf-8") as f:
        data = json.load(f)

    added = []
    missing = []

    for sign_id, entry in data["signs"].items():
        tyst_file = SIGNS_DIR / sign_id / f"{sign_id}_tyst_square.mp4"
        if tyst_file.exists():
            entry["video_silent"] = f"/media/signs/{sign_id}/{sign_id}_tyst_square.mp4"
            added.append(sign_id)
        else:
            missing.append(sign_id)

    with open(MANIFEST, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Added video_silent to {len(added)} signs:")
    for s in sorted(added):
        print(f"  {s}")

    if missing:
        print(f"\nNo silent version for {len(missing)} signs (will play muted):")
        for s in sorted(missing):
            print(f"  {s}")


if __name__ == "__main__":
    main()
