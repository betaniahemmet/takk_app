"""
Guided script for adding new signs to the TAKK app.
Run from the project root: python tools/add_signs.py

Expects signs staged in incoming/:
  incoming/
    glad/
      glad.mov          (vanlig video — valfri)
      glad_tyst.mov     (tyst video — valfri, minst en av dem krävs)
      glad.jpg          (ett piktogram)
      -- ELLER för sammansatta tecken --
      1_glad.jpg
      2_ord.jpg
"""

import json
import shutil
import sys
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent
INCOMING_DIR = BASE_DIR / "incoming"
SIGNS_DIR = BASE_DIR / "media" / "signs"
MANIFEST_PATH = BASE_DIR / "catalog" / "manifest.json"
LOGO_PATH = BASE_DIR / "media" / "logotyp.png"

VIDEO_EXTS = {".mov", ".mp4", ".MOV", ".MP4"}
PIC_EXTS = {".jpg", ".jpeg", ".png", ".webp"}

SEP = "─" * 50


# ── Helpers ────────────────────────────────────────────────────────────────────


def die(msg: str):
    print(f"\n✗ FEL: {msg}")
    sys.exit(1)


def load_manifest() -> dict:
    with open(MANIFEST_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_manifest(data: dict):
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def prompt(question: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    try:
        answer = input(f"  {question}{suffix}: ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\n\nAvbruten.")
        sys.exit(0)
    return answer or default


def confirm(question: str) -> bool:
    answer = prompt(f"{question} (j/n)", "j").lower()
    return answer in ("j", "ja", "y", "yes")


# ── File detection ──────────────────────────────────────────────────────────────


def detect_files(folder: Path) -> dict:
    """Return detected videos and pictograms in a sign folder."""
    files = list(folder.iterdir())
    videos_regular = [f for f in files if f.suffix.lower() in VIDEO_EXTS and "_tyst" not in f.stem]
    videos_silent = [f for f in files if f.suffix.lower() in VIDEO_EXTS and "_tyst" in f.stem]
    pictograms = sorted(f for f in files if f.suffix.lower() in PIC_EXTS)
    unknown = [f for f in files if f.suffix.lower() not in VIDEO_EXTS | PIC_EXTS and not f.name.startswith(".")]
    return {
        "regular": videos_regular,
        "silent": videos_silent,
        "pictograms": pictograms,
        "unknown": unknown,
    }


# ── Validation ──────────────────────────────────────────────────────────────────


def validate_folder(folder: Path) -> list[str]:
    """Return list of error strings. Empty = valid."""
    errors = []
    sid = folder.name
    detected = detect_files(folder)

    if not detected["regular"] and not detected["silent"]:
        errors.append("Ingen videofil hittades. Lägg till en .mov- eller .mp4-fil.")

    if len(detected["regular"]) > 1:
        names = ", ".join(f.name for f in detected["regular"])
        errors.append(f"Flera vanliga videofiler hittades ({names}). Behåll bara en.")

    if len(detected["silent"]) > 1:
        names = ", ".join(f.name for f in detected["silent"])
        errors.append(f"Flera tysta videofiler hittades ({names}). Behåll bara en.")

    if not detected["pictograms"]:
        errors.append("Inget piktogram hittades. Lägg till en .jpg-fil.")

    if len(detected["pictograms"]) > 1:
        unnumbered = [p for p in detected["pictograms"] if not p.stem[0].isdigit()]
        if unnumbered:
            names = ", ".join(p.name for p in unnumbered)
            errors.append(f"Flera piktogram hittades men inte alla är numrerade ({names}). " f"Döp om dem till t.ex. 1_{sid}.jpg, 2_ord.jpg")

    if detected["unknown"]:
        names = ", ".join(f.name for f in detected["unknown"])
        errors.append(f"Okända filer hittades och ignorerades: {names}")

    return errors


# ── Manifest helpers ────────────────────────────────────────────────────────────


def pick_level(manifest: dict) -> int | None:
    """Show level list and prompt user to pick one. Returns level id or None."""
    levels = manifest.get("levels", [])
    print()
    print("  Tillgängliga nivåer:")
    for lvl in levels:
        print(f"    {lvl['id']}. {lvl['name']}")
    print("    0. Lägg inte till på någon nivå just nu")
    while True:
        raw = prompt("Välj nivånummer").strip()
        if raw == "0" or raw == "":
            return None
        if raw.isdigit():
            num = int(raw)
            if any(lvl["id"] == num for lvl in levels):
                return num
        print("  Ogiltigt val, försök igen.")


def build_manifest_entry(sign_id: str, label: str, out_dir: Path, processed: dict) -> dict:
    """Build a manifest signs{} entry from processed output."""
    pics = sorted(out_dir.glob("*.jpg")) + sorted(out_dir.glob("*.png")) + sorted(out_dir.glob("*.webp"))
    # Exclude video thumbnails — only real pictogram files
    pics = [p for p in pics if "_square" not in p.stem and "_tyst" not in p.stem]
    pics = sorted(pics, key=lambda p: p.name)

    if not pics:
        raise ValueError(f"Inga piktogram hittades i {out_dir}")

    symbol = f"/media/signs/{sign_id}/{pics[0].name}"
    pictogram_paths = [f"/media/signs/{sign_id}/{p.name}" for p in pics]

    entry = {
        "label": label,
        "symbol": symbol,
        "pictograms": pictogram_paths,
    }
    if processed.get("regular"):
        entry["video"] = f"/media/signs/{sign_id}/{sign_id}_square.mp4"
    if processed.get("silent"):
        entry["video_silent"] = f"/media/signs/{sign_id}/{sign_id}_tyst_square.mp4"

    return entry


# ── Processing ──────────────────────────────────────────────────────────────────


def process_sign_folder(sign_id: str, folder: Path, detected: dict) -> dict:
    """Run ffmpeg via process_sign.py logic. Returns what was processed."""
    sys.path.insert(0, str(BASE_DIR / "video_processing"))
    from process_sign import process_sign  # noqa

    out_dir = SIGNS_DIR / sign_id
    out_dir.mkdir(parents=True, exist_ok=True)

    regular = detected["regular"][0] if detected["regular"] else None
    silent = detected["silent"][0] if detected["silent"] else None

    process_sign(sign_id, regular=regular, silent=silent)

    # Copy pictograms
    for pic in detected["pictograms"]:
        dest = out_dir / pic.name
        if not dest.exists() or dest.stat().st_mtime < pic.stat().st_mtime:
            shutil.copy2(pic, dest)
            print(f"  Kopierade piktogram: {pic.name}")

    return {"regular": regular is not None, "silent": silent is not None}


# ── Main ────────────────────────────────────────────────────────────────────────


def print_instructions():
    print()
    print("=" * 54)
    print("     Lägg till nya tecken i TAKK-appen")
    print("=" * 54)
    print(
        """
Det här skriptet hjälper dig att lägga till nya tecken.

FÖRBEREDELSE — gör följande innan du fortsätter:

  1. Skapa en mapp i 'incoming/' för varje tecken.
     Mappen ska heta tecknet med understreck istället för mellanslag,
     och bara små bokstäver.
     Exempel:  incoming/glad/
               incoming/vill_du_ha/

  2. Lägg videofiler i mappen:
       Vanlig video:  glad.mov  (eller .mp4)
       Tyst video:    glad_tyst.mov  (eller .mp4)
     Minst en av dem krävs.

  3. Lägg piktogram i mappen:
       Ett piktogram:       glad.jpg
       Flera piktogram:     1_glad.jpg och 2_ord.jpg  (numrerade)

  Exempel på en färdig mapp:
    incoming/glad/
      glad.mov
      glad_tyst.mov
      glad.jpg
"""
    )
    prompt("Tryck Enter för att fortsätta")


def main():
    print_instructions()

    # Ensure incoming/ exists
    if not INCOMING_DIR.exists():
        INCOMING_DIR.mkdir()
        die(f"Mappen 'incoming/' saknades och har nu skapats.\n" f"  Lägg till dina teckenmappar i:  {INCOMING_DIR}\n" f"  Kör sedan skriptet igen.")

    folders = sorted(f for f in INCOMING_DIR.iterdir() if f.is_dir() and not f.name.startswith("."))
    if not folders:
        die("Inga mappar hittades i 'incoming/'.\n" f"  Lägg till dina teckenmappar i:  {INCOMING_DIR}\n" "  Kör sedan skriptet igen.")

    print(f"\n{SEP}")
    print(f"Hittade {len(folders)} mapp(ar): {', '.join(f.name for f in folders)}")
    print(SEP)

    # ── Validate all folders first ───────────────────────────────────────────
    print("\nKontrollerar mappar...")
    all_valid = True
    folder_data = {}

    for folder in folders:
        detected = detect_files(folder)
        errors = validate_folder(folder)
        folder_data[folder.name] = {"folder": folder, "detected": detected, "errors": errors}

        if errors:
            all_valid = False
            print(f"\n  ✗ {folder.name}/")
            for err in errors:
                print(f"      → {err}")
        else:
            vids = []
            if detected["regular"]:
                vids.append("vanlig video")
            if detected["silent"]:
                vids.append("tyst video")
            pics = f"{len(detected['pictograms'])} piktogram"
            print(f"  ✓ {folder.name}/  ({', '.join(vids)}, {pics})")

    if not all_valid:
        print(f"\n{'─'*50}")
        print("Åtgärda felen ovan och kör skriptet igen.")
        sys.exit(1)

    print("\nAlla mappar är godkända.\n")

    # ── Load manifest ────────────────────────────────────────────────────────
    manifest = load_manifest()
    existing_sign_ids = set(manifest["signs"].keys())

    # ── Collect metadata for each sign ──────────────────────────────────────
    sign_metadata = {}

    for sign_id, data in folder_data.items():
        print(SEP)
        is_existing = sign_id in existing_sign_ids
        if is_existing:
            existing_label = manifest["signs"][sign_id].get("label", sign_id)
            print(f'Tecken: {sign_id}  (finns redan i appen som "{existing_label}")')
            print("  Videofiler kommer att ersättas. Label och nivå ändras inte.")
            sign_metadata[sign_id] = {"label": existing_label, "level": None, "is_existing": True}
        else:
            print(f"Nytt tecken: {sign_id}")
            label = ""
            while not label:
                label = prompt('Vad ska tecknet heta i appen? (t.ex. "Glad")')
                if not label:
                    print("  Namnet får inte vara tomt.")

            print(f'\n  På vilken nivå ska "{label}" läggas?')
            level = pick_level(manifest)
            sign_metadata[sign_id] = {"label": label, "level": level, "is_existing": False}

    # ── Confirmation ─────────────────────────────────────────────────────────
    print(f"\n{SEP}")
    print("SAMMANFATTNING — följande kommer att göras:")
    print()
    for sign_id, meta in sign_metadata.items():
        data = folder_data[sign_id]
        detected = data["detected"]
        action = "Uppdatera" if meta["is_existing"] else "Lägga till"
        vids = []
        if detected["regular"]:
            vids.append("vanlig video")
        if detected["silent"]:
            vids.append("tyst video")
        pics = f"{len(detected['pictograms'])} piktogram"
        level_str = ""
        if not meta["is_existing"] and meta["level"]:
            lvl = next(lv for lv in manifest["levels"] if lv["id"] == meta["level"])
            level_str = f"  →  {lvl['name']}"
        print(f"  {action}: {sign_id} (\"{meta['label']}\")  [{', '.join(vids)}, {pics}]{level_str}")

    print()
    if not confirm("Vill du fortsätta?"):
        print("Avbruten. Inga ändringar gjorda.")
        sys.exit(0)

    # ── Process ───────────────────────────────────────────────────────────────
    print()
    errors_during = []

    for sign_id, meta in sign_metadata.items():
        print(f"\n{SEP}")
        print(f"Bearbetar: {sign_id}")
        data = folder_data[sign_id]
        try:
            processed = process_sign_folder(sign_id, data["folder"], data["detected"])
        except Exception as e:
            errors_during.append((sign_id, str(e)))
            print(f"  ✗ Fel vid bearbetning: {e}")
            continue

        # Update manifest
        out_dir = SIGNS_DIR / sign_id
        if meta["is_existing"]:
            entry = manifest["signs"][sign_id]
            if processed["regular"]:
                entry["video"] = f"/media/signs/{sign_id}/{sign_id}_square.mp4"
            if processed["silent"]:
                entry["video_silent"] = f"/media/signs/{sign_id}/{sign_id}_tyst_square.mp4"
        else:
            try:
                entry = build_manifest_entry(sign_id, meta["label"], out_dir, processed)
            except ValueError as e:
                errors_during.append((sign_id, str(e)))
                print(f"  ✗ {e}")
                continue
            manifest["signs"][sign_id] = entry
            if meta["level"] is not None:
                for lvl in manifest["levels"]:
                    if lvl["id"] == meta["level"]:
                        if sign_id not in lvl["signs"]:
                            lvl["signs"].append(sign_id)
                        break

        save_manifest(manifest)
        print("  ✓ Manifest uppdaterat")

        # Move processed folder to incoming/done/
        done_dir = INCOMING_DIR / "done"
        done_dir.mkdir(exist_ok=True)
        dest = done_dir / sign_id
        if dest.exists():
            shutil.rmtree(dest)
        shutil.move(str(data["folder"]), dest)
        print(f"  ✓ Källmappen flyttad till incoming/done/{sign_id}/")

    # ── Validate ──────────────────────────────────────────────────────────────
    print(f"\n{SEP}")
    print("Kör validering...")
    import subprocess

    result = subprocess.run([sys.executable, str(BASE_DIR / "tools" / "validate_catalog.py")], capture_output=True, text=True)
    if result.returncode == 0:
        print("  ✓ Validering godkänd")
    else:
        print("  ✗ Valideringsfel:")
        for line in result.stdout.splitlines():
            print(f"    {line}")

    # ── Done ──────────────────────────────────────────────────────────────────
    print(f"\n{SEP}")
    succeeded = len(sign_metadata) - len(errors_during)
    print(f"Klart! {succeeded}/{len(sign_metadata)} tecken tillagda.")
    if errors_during:
        print("Misslyckades:")
        for sign_id, err in errors_during:
            print(f"  ✗ {sign_id}: {err}")
    print()
    print("Glöm inte att bygga om appen:")
    print("  cd app/components && npm run build")
    print()


if __name__ == "__main__":
    main()
