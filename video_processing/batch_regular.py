import sys
from pathlib import Path

from process_sign import process_sign

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_ROOT = BASE_DIR / "raw_clips"

VIDEO_EXTS = {".mp4", ".mov", ".MP4", ".MOV"}


def main():
    if not INPUT_ROOT.exists():
        print(f"[error] Folder not found: {INPUT_ROOT}")
        sys.exit(1)

    files = sorted(f for f in INPUT_ROOT.iterdir() if f.suffix in VIDEO_EXTS)
    if not files:
        print(f"[error] No video files found in {INPUT_ROOT}")
        sys.exit(1)

    print(f"Found {len(files)} regular signs to process.\n")
    errors = []

    for f in files:
        sign_name = f.stem.lower().replace(" ", "_")
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
