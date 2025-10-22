# video_processor.py
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional

from static_ffmpeg import run as _sfrun  # pip install static-ffmpeg


def process_video(
    infile: str | Path,
    outfile: str | Path,
    *,
    target: int = 1080,
    logo_path: Optional[str | Path] = None,
    logo_rel_width: float = 0.16,
    margin_px: int = 40,
) -> None:
    """
    Crop a video to a centered square, scale, and optionally add a logo overlay.

    Args:
        infile: Path to the input video (.mp4 or .mov)
        outfile: Path to output video (.mp4)
        target: Output resolution (e.g. 1080 = 1080x1080)
        logo_path: Optional path to logo image for bottom-right overlay
        logo_rel_width: Logo width relative to output width
        margin_px: Margin in pixels from bottom/right edge
    """
    infile = Path(infile)
    outfile = Path(outfile)
    if not infile.is_file():
        raise FileNotFoundError(f"Input not found: {infile}")

    ffmpeg, _ = _sfrun.get_or_fetch_platform_executables_else_raise()

    args = ["-y", "-i", str(infile)]
    has_logo = False

    # Optional logo
    if logo_path:
        lp = Path(logo_path)
        if lp.is_file():
            args += ["-loop", "1", "-i", str(lp)]
            has_logo = True
        else:
            print(f"[warn] logo not found, skipping: {lp}")

    # Center crop to square (keep full height)
    crop = "crop=ih:ih:(iw-ih)/2:0"

    filters = [
        f"[0:v]{crop},scale={target}:{target}:in_range=pc:out_range=tv,"
        "setsar=1,format=yuv420p[v0]"
    ]
    last = "v0"

    # Logo overlay (bottom-right)
    if has_logo:
        w = max(1, int(round(target * logo_rel_width)))
        filters += [
            f"[1:v]format=rgba,scale={w}:-1[lg0]",
            f"[{last}][lg0]overlay=x=W-w-{margin_px}:y=H-h-{margin_px}[v1]",
        ]
        last = "v1"

    filters.append(f"[{last}]fps=30,format=yuv420p[vout]")
    fc = ";".join(filters)

    cmd = [
        ffmpeg,
        *args,
        "-filter_complex",
        fc,
        "-map",
        "[vout]",
        "-map",
        "0:a?",
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
        "-ac",
        "1",
        "-ar",
        "48000",
        "-b:a",
        "96k",
        "-shortest",
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

    print("Processing:", infile.name)
    subprocess.run(cmd, check=True)
