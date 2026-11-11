"""Batch-process regular (non-silent) sign recordings into media/signs/.

Usage:
    python batch_regular.py

Reads every video directly in raw_clips/ (subfolders such as
raw_clips/tysta_tecken/ and raw_clips/intro/ are ignored).
File names are normalised to sign ids: "Byta blöja.mp4" -> "byta_blöja".
NAME_MAP handles recordings whose file name differs from the sign id.
"""

import sys
from pathlib import Path

from process_sign import process_sign

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_ROOT = BASE_DIR / "raw_clips"

VIDEO_EXTS = {".mp4", ".mov"}

# Raw file name (normalised) -> sign id used in media/signs and the manifest
NAME_MAP = {
    "hjälp": "hjälpa",
    "toa": "toalett",
}


def sign_id_from_file(f: Path) -> str:
    name = "_".join(f.stem.strip().lower().split())
    return NAME_MAP.get(name, name)


def main():
    if not INPUT_ROOT.exists():
        print(f"[error] Folder not found: {INPUT_ROOT}")
        sys.exit(1)

    files = sorted(f for f in INPUT_ROOT.iterdir() if f.is_file() and f.suffix.lower() in VIDEO_EXTS)
    if not files:
        print(f"[error] No video files found in {INPUT_ROOT}")
        sys.exit(1)

    ids = [sign_id_from_file(f) for f in files]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        print(f"[error] Several files map to the same sign: {', '.join(sorted(dupes))}")
        sys.exit(1)

    print(f"Found {len(files)} regular signs to process.\n")
    errors = []

    for f, sign_name in zip(files, ids):
        print(f"--- {sign_name} ---")
        try:
            process_sign(sign_name, regular=f, silent=None)
        except Exception as e:
            print(f"[error] {sign_name}: {e}")
            errors.append(sign_name)

    print(f"\nDone. {len(files) - len(errors)}/{len(files)} succeeded.")
    if errors:
        print("Failed:", ", ".join(errors))
        sys.exit(1)


if __name__ == "__main__":
    main()
