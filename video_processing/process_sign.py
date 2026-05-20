import argparse
import sys
from pathlib import Path

from video_processor import process_video

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_ROOT = BASE_DIR / "media" / "signs"
LOGO_PATH = BASE_DIR / "media" / "logotyp.png"


def process_sign(sign_name: str, regular: Path | None, silent: Path | None) -> None:
    sign_dir = OUTPUT_ROOT / sign_name
    sign_dir.mkdir(parents=True, exist_ok=True)

    logo = LOGO_PATH if LOGO_PATH.exists() else None
    if not logo:
        print("[warn] Logo not found, processing without overlay.")

    if regular:
        outfile = sign_dir / f"{sign_name}_square.mp4"
        process_video(regular, outfile, logo_path=logo)
        print(f"[done] Regular: {outfile}")

    if silent:
        outfile = sign_dir / f"{sign_name}_tyst_square.mp4"
        process_video(silent, outfile, logo_path=logo)
        print(f"[done] Silent:  {outfile}")


def main():
    parser = argparse.ArgumentParser(description="Process one sign into media/signs/.")
    parser.add_argument("sign_name", help="Sign folder name, e.g. 'hej'")
    parser.add_argument("--regular", type=Path, help="Path to regular video (.mov/.mp4)")
    parser.add_argument("--silent", type=Path, help="Path to silent video (.mov/.mp4)")
    args = parser.parse_args()

    if not args.regular and not args.silent:
        print("[error] Provide at least --regular or --silent.")
        sys.exit(1)

    for flag, path in [("--regular", args.regular), ("--silent", args.silent)]:
        if path and not path.is_file():
            print(f"[error] {flag} file not found: {path}")
            sys.exit(1)

    process_sign(args.sign_name, args.regular, args.silent)


if __name__ == "__main__":
    main()
