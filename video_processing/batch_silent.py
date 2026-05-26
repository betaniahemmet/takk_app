import sys
from pathlib import Path

from process_sign import process_sign

BASE_DIR = Path(__file__).resolve().parent.parent
SILENT_ROOT = BASE_DIR / "tysta_tecken"


def main():
    if not SILENT_ROOT.exists():
        print(f"[error] Folder not found: {SILENT_ROOT}")
        sys.exit(1)

    files = sorted(SILENT_ROOT.glob("*_tyst.mp4"))
    if not files:
        print(f"[error] No *_tyst.mp4 files found in {SILENT_ROOT}")
        sys.exit(1)

    print(f"Found {len(files)} silent signs to process.\n")
    errors = []

    for f in files:
        sign_name = f.stem.replace("_tyst", "")
        print(f"--- {sign_name} ---")
        try:
            process_sign(sign_name, regular=None, silent=f)
        except Exception as e:
            print(f"[error] {sign_name}: {e}")
            errors.append(sign_name)

    print(f"\nDone. {len(files) - len(errors)}/{len(files)} succeeded.")
    if errors:
        print("Failed:", ", ".join(errors))
        sys.exit(1)


if __name__ == "__main__":
    main()
