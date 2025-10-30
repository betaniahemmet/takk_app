import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CATALOG = os.path.join(ROOT, "catalog", "manifest.json")
MEDIA = os.path.join(ROOT, "media")


def main():
    with open(CATALOG, encoding="utf-8") as f:
        m = json.load(f)

    ok, errs = True, []

    # Levels refer only to known signs
    signs = m.get("signs", {})
    for lvl in m.get("levels", []):
        for sid in lvl.get("signs", []):
            if sid not in signs:
                ok = False
                errs.append(f"Level {lvl.get('id')} references unknown sign '{sid}'")

    # Files exist
    for sid, s in signs.items():
        for key in ("symbol", "training_video", "quiz_video"):
            url = s.get(key, "")
            if not url.startswith("/media/"):
                ok = False
                errs.append(f"{sid}.{key} should start with /media/")
                continue
            path = os.path.join(ROOT, url.lstrip("/"))
            if not os.path.exists(path):
                ok = False
                errs.append(f"Missing file: {url}")

    print("OK" if ok else "ERRORS:")
    for e in errs:
        print(" -", e)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
