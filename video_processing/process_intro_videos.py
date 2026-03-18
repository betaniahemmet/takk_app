# process_intro_videos.py
# Converts raw intro videos to web-ready mp4 — same pipeline as sign videos
# but WITHOUT square crop (native aspect ratio is preserved).
#
# Input:  raw_intro/*.mov or *.mp4
# Output: media/intro/{name}.mp4
# Usage:  python video_processing/process_intro_videos.py

import json
import subprocess
import sys
from pathlib import Path

from static_ffmpeg import run as _sfrun

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = BASE_DIR / "raw_intro"
OUTPUT_DIR = BASE_DIR / "media" / "intro"
LOGO_PATH = BASE_DIR / "media" / "logotyp.png"
VIDEO_EXTS = {".mp4", ".mov", ".MP4", ".MOV"}

LOGO_REL_WIDTH = 0.16  # same as sign videos
MARGIN_PX = 40  # same as sign videos


def get_video_duration(infile: Path, ffprobe: str) -> float:
    result = subprocess.run(
        [ffprobe, "-v", "quiet", "-print_format", "json", "-show_streams", "-select_streams", "v:0", str(infile)],
        capture_output=True,
        text=True,
        check=True,
    )
    return float(json.loads(result.stdout)["streams"][0]["duration"])


def process(infile: Path, outfile: Path, ffmpeg: str, duration: float) -> None:
    # Scale to 1080px height, keep native aspect ratio
    # Logo overlay is commented out — input video already has logo embedded
    target_h = 1080
    # logo_w = max(1, int(round(target_h * LOGO_REL_WIDTH)))
    filters = [
        f"[0:v]scale=-2:{target_h}:in_range=pc:out_range=tv,setsar=1,format=yuv420p[vout]",
        # f"[1:v]format=rgba,scale={logo_w}:-1[lg]",
        # f"[v0][lg]overlay=x=W-w-{MARGIN_PX}:y=H-h-{MARGIN_PX}[v1]",
        # "[v1]format=yuv420p[vout]",
        "[0:a]pan=mono|c0=0.5*c0+0.5*c1[aout]",
    ]
    filter_chain = ";".join(filters)
    cmd = [
        ffmpeg,
        "-y",
        "-i",
        str(infile),
        # Logo input removed — re-enable these two lines to add logo overlay:
        # "-loop", "1",
        # "-i", str(LOGO_PATH),
        "-filter_complex",
        filter_chain,
        "-map",
        "[vout]",
        "-map",
        "[aout]",
        "-t",
        str(duration),
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "22",
        "-g",
        "60",
        "-pix_fmt",
        "yuv420p",
        "-metadata:s:v:0",
        "rotate=0",
        "-movflags",
        "+faststart",
        "-c:a",
        "aac",
        "-ar",
        "48000",
        "-b:a",
        "96k",
        "-colorspace",
        "bt709",
        "-color_primaries",
        "bt709",
        "-color_trc",
        "bt709",
        "-color_range",
        "tv",
        str(outfile),
    ]
    subprocess.run(cmd, check=True)


def main():
    # Logo check disabled — logo overlay is currently commented out
    # if not LOGO_PATH.exists():
    #     print(f"[error] Logo not found: {LOGO_PATH}")
    #     sys.exit(1)

    if not INPUT_DIR.exists():
        print(f"[error] Input folder not found: {INPUT_DIR}")
        print("        Create raw_intro/ and place .mov/.mp4 files in it.")
        sys.exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    candidates = [f for f in INPUT_DIR.iterdir() if f.suffix in VIDEO_EXTS]
    if not candidates:
        print(f"No video files found in {INPUT_DIR}")
        sys.exit(0)

    ffmpeg, ffprobe = _sfrun.get_or_fetch_platform_executables_else_raise()

    skipped = 0
    processed = 0

    for infile in sorted(candidates):
        name = infile.stem.lower().replace(" ", "_")
        outfile = OUTPUT_DIR / f"{name}.mp4"

        if outfile.exists():
            print(f"[skip]    {infile.name}  ->  {outfile.name}  (already exists)")
            skipped += 1
            continue

        print(f"[process] {infile.name}  ->  {outfile.name}")
        try:
            duration = get_video_duration(infile, ffprobe)
            process(infile, outfile, ffmpeg, duration)
            print(f"[done]    {outfile.name}")
            processed += 1
        except subprocess.CalledProcessError as e:
            print(f"[error]   {infile.name}: ffmpeg exited with code {e.returncode}")

    print(f"\nFinished: {processed} processed, {skipped} skipped.")
    print(f"Output:   {OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    main()
