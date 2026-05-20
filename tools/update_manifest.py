"""
One-time manifest update:
  - Rename sign keys: sen->sedan, toa->toalett
  - Remove deleted signs: jag_heter, nu_ska_du_åka_hem, nu_ska_du_åka_till_jobbet
  - Fix level references to match
  - Bump version to 3

Run once, then delete or keep for the record.
"""

import json
from pathlib import Path

MANIFEST = Path(__file__).resolve().parent.parent / "catalog" / "manifest.json"

RENAMES = {
    "sen": "sedan",
    "toa": "toalett",
}
REMOVALS = {
    "jag_heter",
    "nu_ska_du_åka_hem",
    "nu_ska_du_åka_till_jobbet",
}


def rename_sign(data: dict, old: str, new: str) -> None:
    signs = data["signs"]
    entry = signs.pop(old)
    entry["label"] = new.replace("_", " ").capitalize()
    for key in ("symbol", "video"):
        if key in entry:
            entry[key] = entry[key].replace(f"/{old}/", f"/{new}/").replace(f"{old}.", f"{new}.").replace(f"{old}_square", f"{new}_square")
    if "pictograms" in entry:
        entry["pictograms"] = [p.replace(f"/{old}/", f"/{new}/").replace(f"{old}.", f"{new}.") for p in entry["pictograms"]]
    signs[new] = entry

    for level in data["levels"]:
        level["signs"] = [new if s == old else s for s in level["signs"]]


def remove_sign(data: dict, key: str) -> None:
    data["signs"].pop(key, None)
    for level in data["levels"]:
        level["signs"] = [s for s in level["signs"] if s != key]


def main():
    with open(MANIFEST, encoding="utf-8") as f:
        data = json.load(f)

    for old, new in RENAMES.items():
        if old in data["signs"]:
            rename_sign(data, old, new)
            print(f"Renamed: {old} -> {new}")
        else:
            print(f"Skip rename (not found): {old}")

    for key in REMOVALS:
        if key in data["signs"]:
            remove_sign(data, key)
            print(f"Removed: {key}")
        else:
            print(f"Skip removal (not found): {key}")

    data["version"] = 3

    with open(MANIFEST, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\nManifest updated -> version {data['version']}")


if __name__ == "__main__":
    main()
