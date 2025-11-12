# manifest_builder.py
import json
import sys
from pathlib import Path

# === Configuration ===
BASE_DIR = Path(__file__).resolve().parent.parent
PUBLIC_BASE = "/media/signs"


def MEDIA_SIGNS_ROOT() -> Path:
    return BASE_DIR / "media" / "signs"


def CATALOG_DIR() -> Path:
    return BASE_DIR / "catalog"


def OUTPUT_FILE() -> Path:
    return CATALOG_DIR() / "manifest.json"


# === Helpers ===
def title_from_name(name: str) -> str:
    """Turn 'jag_heter' into 'Jag heter'."""
    return name.replace("_", " ").capitalize()


def prompt_level(sign_name: str) -> int:
    """Ask the user which level a sign belongs to."""
    while True:
        val = input(f"Assign level (1-9, or 0/Enter to skip) for '{sign_name}': ").strip()
        if val == "" or val == "0":
            return 0
        if val.isdigit() and 1 <= int(val) <= 9:
            return int(val)
        print("Please enter a number between 1-9, or press Enter to skip.")


# === Main logic ===
def build_manifest():
    media_root = MEDIA_SIGNS_ROOT()
    out_file = OUTPUT_FILE()

    media_root.mkdir(parents=True, exist_ok=True)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    if not media_root.exists():
        print(f"[error] Media folder not found: {media_root}")
        sys.exit(1)

    signs = {}
    levels = {}

    # Walk through media/signs and collect sign data
    for folder in sorted(media_root.iterdir()):
        if not folder.is_dir():
            continue

        sign_key = folder.name.lower().replace(" ", "_")
        label = title_from_name(sign_key)
        video = None
        pictos = []

        for f in sorted(folder.iterdir()):
            if f.suffix.lower() == ".mp4":
                video = f"{PUBLIC_BASE}/{sign_key}/{f.name}"
            elif f.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
                pictos.append(f"{PUBLIC_BASE}/{sign_key}/{f.name}")

        if not video:
            print(f"[warn] No video found in {folder.name}, skipping.")
            continue

        print(f"\nFound sign: {sign_key}")
        print(f"  Label: {label}")
        print(f"  Pictograms: {len(pictos)} found")
        print(f"  Video: {video}")

        level_id = prompt_level(sign_key)

        signs[sign_key] = {
            "label": label,
            "symbol": pictos[0] if pictos else None,
            "pictograms": pictos,
            "video": video,
        }

        if level_id:
            levels.setdefault(level_id, []).append(sign_key)

    # Construct manifest
    manifest = {
        "version": 2,
        "levels": [{"id": lvl, "name": f"Nivå {lvl}", "signs": sorted(signs_in_lvl)} for lvl, signs_in_lvl in sorted(levels.items())],
        "signs": signs,
    }

    # Write JSON
    with out_file.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f"\n Manifest written to: {out_file}")
    print(f"   {len(signs)} signs processed, {len(levels)} levels assigned.")


if __name__ == "__main__":
    build_manifest()
