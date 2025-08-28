from pathlib import Path
from video_processor import process_video

BASE = Path(__file__).resolve().parent
MEDIA = BASE / "media"
OUT = BASE / "processed_videos"
OUT.mkdir(exist_ok=True)

infile = MEDIA / "signs/dricka/quiz.mp4"
outfile = OUT / f"{infile.stem}_square{infile.suffix}"
logo = MEDIA / "logotyp.png"
pict = MEDIA / "signs/dricka/pict.jpg"

print("Logo path:", logo)
print("Logo exists:", logo.exists())
print("pictogram exists: ", pict.exists())

process_video(
    infile,
    outfile,
    logo_path=logo,  # <- use the exact path you just printed
    pictogram_path=pict,
    target=1080,
    crop_anchor_y=0.40,
)
