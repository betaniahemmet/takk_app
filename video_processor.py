# video_processor.py — minimal, with optional bottom-left pictogram
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
    crop_anchor_y: float = 0.40,  # 0=top, 0.5=center (slight upward bias)
    logo_path: Optional[str | Path] = None,  # bottom-right
    pictogram_path: Optional[str | Path] = None,  # bottom-left (auto if None)
    logo_rel_width: float = 0.16,
    pictogram_rel_width: float = 0.16,
    margin_px: int = 40,
) -> None:
    infile = Path(infile)
    outfile = Path(outfile)
    if not infile.is_file():
        raise FileNotFoundError(f"Input not found: {infile}")

    ffmpeg, _ = _sfrun.get_or_fetch_platform_executables_else_raise()

    args = ["-y", "-i", str(infile)]
    has_logo = False
    has_picto = False

    # Logo (BR)
    if logo_path:
        lp = Path(logo_path)
        if lp.is_file():
            args += ["-loop", "1", "-i", str(lp)]
            has_logo = True
        else:
            print(f"[warn] logo not found, skipping: {lp}")

    # Pictogram (BL): explicit path OR auto-find: {base}_sign.* → {base}.*
    pg = Path(pictogram_path) if pictogram_path else None
    if pg is None:
        base = infile.stem
        for stem in (f"{base}_sign", base):
            for ext in (".png", ".webp", ".jpg", ".jpeg"):
                cand = infile.with_name(stem + ext)
                if cand.is_file():
                    pg = cand
                    break
            if pg:
                break
    if pg and pg.is_file():
        args += ["-loop", "1", "-i", str(pg)]
        has_picto = True
    elif pictogram_path:
        print(f"[warn] pictogram not found, skipping: {pictogram_path}")

    # Base: crop square (+upward bias), scale, fix full→TV range, keep RGBA for overlay
    crop = (
        "crop=min(iw\\,ih):min(iw\\,ih):"
        "(iw-min(iw\\,ih))/2:"
        f"(ih-min(iw\\,ih))*{crop_anchor_y}"
    )
    filters = [
        f"[0:v]{crop},scale={target}:{target}:in_range=pc:out_range=tv,setsar=1,format=yuv420p[v0]"
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

    # Pictogram overlay (bottom-left)
    if has_picto:
        # stream index for pictogram depends on whether logo is present
        pg_idx = 2 if has_logo else 1
        w = max(1, int(round(target * pictogram_rel_width)))
        filters += [
            f"[{pg_idx}:v]format=rgba,scale={w}:-1[pg0]",
            f"[{last}][pg0]overlay=x={margin_px}:y=H-h-{margin_px}[v2]",
        ]
        last = "v2"

    # CFR 30 + finalize pixels
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
    print(" ".join(shlex.quote(c) for c in cmd))
    subprocess.run(cmd, check=True)
