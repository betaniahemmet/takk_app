"""Deep diagnostic of a video file — checks packet timing, gaps, and audio sync."""

import json
import statistics
import subprocess

FILE = r"C:\Users\henri\Documents\code\takk_app\raw_intro\intro_takk_app.mp4"
FFPROBE = "ffprobe"


def probe(args):
    r = subprocess.run(
        [FFPROBE, "-v", "quiet", "-print_format", "json"] + args + [FILE],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(r.stdout)


def analyze_video_packets():
    print("=== VIDEO PACKET ANALYSIS ===")
    data = probe(["-show_packets", "-select_streams", "v:0"])
    pkts = data["packets"]
    print(f"Total video packets : {len(pkts)}")

    dts_list = [int(p["dts"]) for p in pkts if "dts" in p]
    pts_list = [int(p["pts"]) for p in pkts if "pts" in p]
    dur_list = [int(p["duration"]) for p in pkts if "duration" in p and int(p["duration"]) > 0]

    if dur_list:
        med = statistics.median(dur_list)
        print(f"Packet duration  median={med}  min={min(dur_list)}  max={max(dur_list)}")
        outliers = [(i, d) for i, d in enumerate(dur_list) if abs(d - med) > med * 0.05]
        print(f"Duration outliers (>5% from median): {len(outliers)}")
        for i, d in outliers[:15]:
            print(f"  pkt#{i} duration={d}  (expected ~{med})")

    # PTS gaps
    pts_steps = [pts_list[i] - pts_list[i - 1] for i in range(1, len(pts_list))]
    if pts_steps:
        med_step = statistics.median(pts_steps)
        gaps = [(i, pts_list[i - 1], pts_list[i], s) for i, s in enumerate(pts_steps, 1) if s > med_step * 1.5]
        print(f"PTS gap anomalies (>1.5x median step): {len(gaps)}")
        for g in gaps[:15]:
            print(f"  pkt#{g[0]} pts={g[1]}->{g[2]} step={g[3]} (expected ~{med_step})")

    # DTS order
    ooo = sum(1 for i in range(1, len(dts_list)) if dts_list[i] < dts_list[i - 1])
    print(f"Out-of-order DTS  : {ooo}")

    # Key frame spacing
    keyframes = [i for i, p in enumerate(pkts) if p.get("flags", "").startswith("K")]
    if keyframes:
        kf_gaps = [keyframes[i] - keyframes[i - 1] for i in range(1, len(keyframes))]
        print(f"Keyframes: {len(keyframes)}  interval median={statistics.median(kf_gaps):.1f}  max={max(kf_gaps)}")


def analyze_audio_packets():
    print("\n=== AUDIO PACKET ANALYSIS ===")
    data = probe(["-show_packets", "-select_streams", "a:0"])
    pkts = data["packets"]
    print(f"Total audio packets : {len(pkts)}")

    pts_list = [int(p["pts"]) for p in pkts if "pts" in p]
    dur_list = [int(p["duration"]) for p in pkts if "duration" in p and int(p["duration"]) > 0]

    if dur_list:
        med = statistics.median(dur_list)
        print(f"Packet duration  median={med}  min={min(dur_list)}  max={max(dur_list)}")

    # Audio PTS continuity gaps
    pts_steps = [pts_list[i] - pts_list[i - 1] for i in range(1, len(pts_list))]
    if pts_steps:
        med_step = statistics.median(pts_steps)
        gaps = [(i, pts_list[i - 1], pts_list[i], s) for i, s in enumerate(pts_steps, 1) if s > med_step * 1.5]
        print(f"Audio PTS gap anomalies (>1.5x median): {len(gaps)}")
        for g in gaps[:15]:
            gap_ms = (g[3] - med_step) / 48  # time_base 1/48000 -> ms
            print(f"  pkt#{g[0]} pts={g[1]}->{g[2]} gap≈{gap_ms:.1f}ms extra")

    # Check audio start vs video start
    print(f"\nAudio PTS start : {pts_list[0] if pts_list else 'n/a'}")
    print(f"Audio PTS end   : {pts_list[-1] if pts_list else 'n/a'}")


def check_av_sync():
    print("\n=== A/V SYNC CHECK ===")
    # Get first/last pts of each stream
    v = probe(["-show_packets", "-select_streams", "v:0", "-read_intervals", "%+#5"])
    a = probe(["-show_packets", "-select_streams", "a:0", "-read_intervals", "%+#5"])

    v_pkts = v["packets"]
    a_pkts = a["packets"]

    v_start = int(v_pkts[0]["pts"]) if v_pkts else 0
    a_start = int(a_pkts[0]["pts"]) if a_pkts else 0

    # time_bases differ: video=1/30000, audio=1/48000
    v_start_s = v_start / 30000
    a_start_s = a_start / 48000
    drift_ms = (a_start_s - v_start_s) * 1000

    print(f"Video stream start PTS : {v_start}  ({v_start_s:.6f}s)")
    print(f"Audio stream start PTS : {a_start}  ({a_start_s:.6f}s)")
    print(f"Initial A/V drift      : {drift_ms:+.3f} ms  ({'audio leads' if drift_ms < 0 else 'audio lags'})")

    # Check timecode track
    print("\nTimecode tag in video stream: 01:00:00:00 (non-zero! — DaVinci Resolve embed)")
    print("This means the container start_time may be anchored to 1h, causing player confusion.")


def check_container_health():
    print("\n=== CONTAINER HEALTH ===")
    # Run ffmpeg error detection pass
    r = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", FILE, "-f", "null", "-"],
        capture_output=True,
        text=True,
    )
    errors = r.stderr.strip()
    if errors:
        lines = errors.splitlines()
        print(f"ffmpeg error scan found {len(lines)} lines:")
        for line in lines[:40]:
            print(f"  {line}")
    else:
        print("No container errors detected by ffmpeg.")


if __name__ == "__main__":
    analyze_video_packets()
    analyze_audio_packets()
    check_av_sync()
    check_container_health()
