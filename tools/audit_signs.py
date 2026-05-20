"""
Audits media/signs/ against catalog/manifest.json and reports what needs attention.

Checks each folder in media/signs/ for:
  - Missing pictogram (no .jpg/.png/.webp)
  - Missing regular video (*_square.mp4)
  - Missing silent video (*_tyst_square.mp4)
  - Not in manifest

Also checks manifest for entries whose folder doesn't exist.
"""

import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SIGNS_DIR = BASE_DIR / "media" / "signs"
MANIFEST = BASE_DIR / "catalog" / "manifest.json"
PIC_EXTS = {".jpg", ".jpeg", ".png", ".webp"}


def main():
    with open(MANIFEST, encoding="utf-8") as f:
        manifest = json.load(f)
    manifest_ids = set(manifest["signs"].keys())

    folders = sorted(p for p in SIGNS_DIR.iterdir() if p.is_dir())
    folder_ids = {p.name for p in folders}

    missing_pictogram = []
    missing_regular = []
    missing_silent = []
    not_in_manifest = []

    for folder in folders:
        sid = folder.name
        files = list(folder.iterdir())
        names = {f.name for f in files}

        has_pic = any(f.suffix.lower() in PIC_EXTS for f in files)
        has_regular = f"{sid}_square.mp4" in names
        has_silent = f"{sid}_tyst_square.mp4" in names

        if not has_pic:
            missing_pictogram.append(sid)
        if not has_regular:
            missing_regular.append(sid)
        if not has_silent:
            missing_silent.append(sid)
        if sid not in manifest_ids:
            not_in_manifest.append(sid)

    ghost_entries = sorted(manifest_ids - folder_ids)

    def section(title, items):
        print(f"\n=== {title} ({len(items)}) ===")
        for s in items:
            print(f"  {s}")
        if not items:
            print("  (none)")

    section("Missing pictogram — needs .jpg added", missing_pictogram)
    section("Missing regular video — waiting for recording", missing_regular)
    section("Missing silent video — no _tyst_square.mp4", missing_silent)
    section("Not in manifest — needs manifest entry", not_in_manifest)
    section("In manifest but folder missing — stale entry", ghost_entries)


if __name__ == "__main__":
    main()
