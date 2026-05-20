"""
Guided script for removing signs from the TAKK app.
Run from the project root: python tools/remove_sign.py
"""

import json
import shutil
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SIGNS_DIR = BASE_DIR / "media" / "signs"
MANIFEST_PATH = BASE_DIR / "catalog" / "manifest.json"

SEP = "─" * 54

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# ── Helpers ────────────────────────────────────────────────────────────────────


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


def confirm(question: str, default: str = "n") -> bool:
    answer = prompt(question, default).lower()
    return answer in ("j", "ja", "y", "yes")


# ── Selectable list ─────────────────────────────────────────────────────────────


def pick_signs(signs: dict) -> list[str]:
    """Show a numbered list of all signs and let the user pick one or several."""
    entries = sorted(signs.items(), key=lambda x: x[1].get("label", x[0]).lower())

    print()
    print("  Alla tecken i appen:")
    print()
    col_width = max(len(label) for _, s in entries for label in [s.get("label", "")])
    for i, (sid, s) in enumerate(entries, 1):
        label = s.get("label", sid)
        print(f"  {i:>3}.  {label:<{col_width}}   ({sid})")

    print()
    print("  Ange numren på tecknen du vill ta bort.")
    print("  Flera tecken: separera med kommatecken, t.ex.  3, 7, 12")
    print()

    while True:
        raw = prompt("Ditt val (eller 'avbryt')").lower()
        if raw in ("avbryt", "a", "q", ""):
            print("\nAvbruten. Inga ändringar gjorda.")
            sys.exit(0)

        parts = [p.strip() for p in raw.replace(",", " ").split()]
        if not all(p.isdigit() for p in parts):
            print("  Ogiltigt val — ange bara siffror separerade med kommatecken.")
            continue

        indices = [int(p) for p in parts]
        invalid = [i for i in indices if i < 1 or i > len(entries)]
        if invalid:
            print(f"  Ogiltiga nummer: {', '.join(str(i) for i in invalid)}. Välj mellan 1 och {len(entries)}.")
            continue

        selected = [entries[i - 1][0] for i in indices]
        return selected


# ── Main ────────────────────────────────────────────────────────────────────────


def main():
    print()
    print("=" * 54)
    print("     Ta bort tecken från TAKK-appen")
    print("=" * 54)
    print()
    print("  Det här skriptet tar bort tecken från appen.")
    print("  Du får välja vilka och bekräfta innan något raderas.")
    print()

    manifest = load_manifest()
    signs = manifest.get("signs", {})

    if not signs:
        print("  Inga tecken hittades i manifestet.")
        sys.exit(0)

    selected_ids = pick_signs(signs)

    # ── Confirmation ─────────────────────────────────────────────────────────
    print()
    print(SEP)
    print(f"  Du har valt att ta bort {len(selected_ids)} tecken:")
    print()
    for sid in selected_ids:
        label = signs[sid].get("label", sid)
        folder_exists = (SIGNS_DIR / sid).exists()
        folder_note = "  (mapp finns på disk)" if folder_exists else "  (ingen mapp på disk)"
        print(f"    - {label}  ({sid}){folder_note}")

    print()
    also_delete_files = confirm("Vill du också radera videofilerna och bilderna från disk? (j/n)", "n")
    print()
    print("  Följande kommer att göras:")
    print("    • Ta bort från manifest.json")
    print("    • Ta bort från alla nivåer")
    if also_delete_files:
        print("    • Radera mapp(arna) i media/signs/  (kan inte ångras!)")
    print()

    if not confirm("Är du säker? Detta kan inte ångras", "n"):
        print("\nAvbruten. Inga ändringar gjorda.")
        sys.exit(0)

    # ── Remove ────────────────────────────────────────────────────────────────
    print()
    for sid in selected_ids:
        label = signs[sid].get("label", sid)

        # Remove from signs{}
        del manifest["signs"][sid]

        # Remove from all levels
        for lvl in manifest["levels"]:
            lvl["signs"] = [s for s in lvl["signs"] if s != sid]

        # Optionally delete files
        if also_delete_files:
            folder = SIGNS_DIR / sid
            if folder.exists():
                shutil.rmtree(folder)
                print(f"  ✓ {label}: borttaget från manifest och disk")
            else:
                print(f"  ✓ {label}: borttaget från manifest (ingen mapp att radera)")
        else:
            print(f"  ✓ {label}: borttaget från manifest")

    save_manifest(manifest)

    # ── Validate ──────────────────────────────────────────────────────────────
    print()
    print(SEP)
    print("  Kör validering...")
    import subprocess

    result = subprocess.run(
        [sys.executable, str(BASE_DIR / "tools" / "validate_catalog.py")],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        print("  ✓ Validering godkänd")
    else:
        print("  ✗ Valideringsfel:")
        for line in result.stdout.splitlines():
            print(f"      {line}")

    print()
    print(SEP)
    print(f"  Klart! {len(selected_ids)} tecken borttagna.")
    print()
    print("  Glöm inte att bygga om appen:")
    print("    cd app/components && npm run build")
    print()


if __name__ == "__main__":
    main()
