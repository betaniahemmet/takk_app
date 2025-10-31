# batch_processor.py
import sys
from pathlib import Path

from video_processor import process_video

# === Global configuration ===
BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_ROOT = BASE_DIR / "raw_clips"
OUTPUT_ROOT = BASE_DIR / "media" / "signs"
LOGO_PATH = BASE_DIR / "media/logotyp.png"
if not LOGO_PATH.exists():
    raise FileNotFoundError(f"Logo not found: {LOGO_PATH}")


def batch_process():
    """
    Recursively processes all videos in INPUT_ROOT and outputs
    cropped + logo versions into a mirrored structure in OUTPUT_ROOT.
    """
    if not INPUT_ROOT.exists():
        print(f"[error] Input folder not found: {INPUT_ROOT}")
        sys.exit(1)

    if OUTPUT_ROOT.exists():
        print(
            f"There is already a folder named '{OUTPUT_ROOT.name}'.\n"
            "Please remove it manually if you want to generate it again.\n"
            "Beware that only the signs currently in 'raw_clips' will be regenerated."
        )
        sys.exit(1)

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=False)
    video_exts = {".mp4", ".mov", ".MOV", ".MP4"}
    count = 0

    for infile in INPUT_ROOT.rglob("*"):
        if infile.suffix in video_exts:

            # Normalize and create a unique folder for each clip
            folder_name = infile.stem.lower().replace(" ", "_")
            out_dir = OUTPUT_ROOT / folder_name
            out_dir.mkdir(parents=True, exist_ok=True)

            outfile = out_dir / f"{folder_name}_square.mp4"

            process_video(
                infile,
                outfile,
                target=1080,
                logo_path=LOGO_PATH,
                logo_rel_width=0.16,
                margin_px=40,
            )
            count += 1

    print(f"\n Finished processing {count} videos.")
    print(f"All outputs are in: {OUTPUT_ROOT.resolve()}")


if __name__ == "__main__":
    batch_process()
