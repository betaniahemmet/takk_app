# video_processor.py — minimal & boring, with safe label names (no "logo")
from __future__ import annotations
from pathlib import Path
import subprocess, shlex
from typing import Optional
from static_ffmpeg import run as _sfrun  # pip install static-ffmpeg

def process_video(
    infile: str | Path,
    outfile: str | Path,
    *,
    target: int = 1080,
    crop_anchor_y: float = 0.40,   # 0=top, 0.5=center (slight upward bias)
    logo_path: Optional[str | Path] = None,
    logo_rel_width: float = 0.16,  # a bit larger so it's obvious
    margin_px: int = 40,
) -> None:
    infile = Path(infile)
    outfile = Path(outfile)
    if not infile.is_file():
        raise FileNotFoundError(f"Input not found: {infile}")

    ffmpeg, _ = _sfrun.get_or_fetch_platform_executables_else_raise()

    # inputs
    args = ["-y", "-i", str(infile)]
    has_logo = False
    if logo_path:
        lp = Path(logo_path)
        if lp.is_file():
            args += ["-loop", "1", "-i", str(lp)]  # loop still image for full duration
            has_logo = True
        else:
            print(f"[warn] logo not found, skipping: {lp}")

    # crop to square with upward bias, scale, set range to TV (kills yuvj420p warnings)
    crop = (
        "crop=min(iw\\,ih):min(iw\\,ih):"
        "(iw-min(iw\\,ih))/2:"
        f"(ih-min(iw\\,ih))*{crop_anchor_y}"
    )
    filters = [f"[0:v]{crop},scale={target}:{target}:in_range=pc:out_range=tv,setsar=1,format=rgba[v0]"]
    last = "v0"

    if has_logo:
        w = max(1, int(round(target * logo_rel_width)))
        # NOTE: labels are lg0 / v1 to avoid any 'logo' naming oddities
        filters += [
            f"[1:v]format=rgba,scale={w}:-1[lg0]",
            f"[{last}][lg0]overlay=x=W-w-{margin_px}:y=H-h-{margin_px}[v1]",
        ]
        last = "v1"

    # CFR 30 + finalize pixels
    filters.append(f"[{last}]fps=30,format=yuv420p[vout]")
    filter_complex = ";".join(filters)

    cmd = [
        ffmpeg,
        *args,
        "-filter_complex", filter_complex,
        "-map", "[vout]", "-map", "0:a?",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
        "-g", "60",
        "-pix_fmt", "yuv420p",
        "-metadata:s:v:0", "rotate=0",
        "-movflags", "+faststart",
        "-c:a", "aac", "-ac", "1", "-ar", "48000", "-b:a", "96k",
        "-shortest",
        # tag output as Rec.709 TV range (some players care)
        "-colorspace", "bt709", "-color_primaries", "bt709",
        "-color_trc", "bt709", "-color_range", "tv",
        str(outfile),
    ]
    print(" ".join(shlex.quote(c) for c in cmd))
    subprocess.run(cmd, check=True)
