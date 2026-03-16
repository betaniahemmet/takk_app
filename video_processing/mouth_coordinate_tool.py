"""
Mouth Coordinate Collection Tool
Collects mouth center coordinates (as % of frame) for blur overlay in Quiz/Competition modes.
Output: catalog/mouth_coordinates.json
Usage: python video_processing/mouth_coordinate_tool.py
"""

import json
import os
import sys

import cv2

SIGNS_DIR = "media/signs"
OUTPUT_FILE = "catalog/mouth_coordinates.json"

coords = {}
click_result = None


def on_click(event, x, y, flags, param):
    global click_result
    if event == cv2.EVENT_LBUTTONDOWN:
        h, w = param
        click_result = {"x": round(x / w * 100, 1), "y": round(y / h * 100, 1)}


def get_middle_frame(video_path):
    cap = cv2.VideoCapture(video_path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.set(cv2.CAP_PROP_POS_FRAMES, total // 2)
    ret, frame = cap.read()
    cap.release()
    return frame if ret else None


def main():
    global click_result

    # Load existing coordinates
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r") as f:
            coords.update(json.load(f))
        print(f"Loaded {len(coords)} existing coordinates from {OUTPUT_FILE}")

    # Find signs missing coordinates
    all_signs = sorted(os.listdir(SIGNS_DIR))
    new_signs = [s for s in all_signs if s not in coords]

    if not new_signs:
        print("All signs already have coordinates. Nothing to do.")
        return

    print(f"\n{len(new_signs)} signs need coordinates (skipping {len(coords)} already done)")
    print("Controls: left-click = set mouth center | s = skip | q = quit\n")

    cv2.namedWindow("Mouth Coordinate Tool")

    for i, sign in enumerate(new_signs):
        video_path = os.path.join(SIGNS_DIR, sign, f"{sign}_square.mp4")
        if not os.path.exists(video_path):
            print(f"  [{i+1}/{len(new_signs)}] {sign}: no video found, skipping")
            continue

        frame = get_middle_frame(video_path)
        if frame is None:
            print(f"  [{i+1}/{len(new_signs)}] {sign}: could not read frame, skipping")
            continue

        h, w = frame.shape[:2]
        click_result = None

        cv2.setMouseCallback("Mouth Coordinate Tool", on_click, (h, w))

        # Draw overlay text on a copy
        display = frame.copy()
        label = f"{sign}  ({i+1}/{len(new_signs)} new signs)"
        cv2.putText(display, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.putText(display, "Click mouth center | s=skip | q=quit", (10, h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 200, 255), 1)

        cv2.imshow("Mouth Coordinate Tool", display)

        while True:
            key = cv2.waitKey(30) & 0xFF

            if click_result is not None:
                coords[sign] = click_result
                print(f"  [{i+1}/{len(new_signs)}] {sign}: x={click_result['x']}%, y={click_result['y']}%")
                # Show crosshair feedback
                fb = frame.copy()
                cx = int(click_result["x"] / 100 * w)
                cy = int(click_result["y"] / 100 * h)
                cv2.drawMarker(fb, (cx, cy), (0, 0, 255), cv2.MARKER_CROSS, 30, 2)
                cv2.putText(fb, f"Saved: ({click_result['x']}%, {click_result['y']}%)", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                cv2.imshow("Mouth Coordinate Tool", fb)
                cv2.waitKey(600)
                click_result = None
                break

            elif key == ord("s"):
                print(f"  [{i+1}/{len(new_signs)}] {sign}: skipped")
                break

            elif key == ord("q"):
                print("\nQuitting — saving progress...")
                _save(coords)
                cv2.destroyAllWindows()
                sys.exit(0)

    cv2.destroyAllWindows()
    _save(coords)
    print(f"\nDone! {len(coords)} total coordinates saved to {OUTPUT_FILE}")


def _save(data):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
    print(f"Saved {len(data)} coordinates to {OUTPUT_FILE}")


if __name__ == "__main__":
    # Run from repo root
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(repo_root)
    main()
