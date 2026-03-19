# tests/test_manifest_integrity.py
"""
Validates catalog/manifest.json against the actual media files on disk.
Catches missing files, broken level references, and structural issues.
"""
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = REPO_ROOT / "catalog" / "manifest.json"
MEDIA_ROOT = REPO_ROOT  # paths in manifest are like /media/signs/... relative to repo root


def load_manifest():
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def resolve(url_path: str) -> Path:
    """Convert a manifest URL path like /media/signs/hej/hej.jpg to an absolute Path."""
    return MEDIA_ROOT / url_path.lstrip("/")


# ---------------------------------------------------------------------------


def test_manifest_file_exists():
    assert MANIFEST_PATH.exists(), "catalog/manifest.json not found"


def test_version_field():
    data = load_manifest()
    assert data.get("version") == 2


def test_signs_have_required_fields():
    data = load_manifest()
    for sign_id, sign in data["signs"].items():
        assert "label" in sign, f"{sign_id}: missing 'label'"
        assert "video" in sign, f"{sign_id}: missing 'video'"
        assert "pictograms" in sign, f"{sign_id}: missing 'pictograms'"
        assert isinstance(sign["pictograms"], list), f"{sign_id}: 'pictograms' must be a list"
        assert len(sign["pictograms"]) > 0, f"{sign_id}: 'pictograms' is empty"
        assert "symbol" in sign, f"{sign_id}: missing 'symbol'"


def test_every_video_exists_on_disk():
    data = load_manifest()
    missing = []
    for sign_id, sign in data["signs"].items():
        path = resolve(sign["video"])
        if not path.exists():
            missing.append(f"{sign_id}: {sign['video']}")
    assert not missing, "Missing video files:\n" + "\n".join(missing)


def test_every_pictogram_exists_on_disk():
    data = load_manifest()
    missing = []
    for sign_id, sign in data["signs"].items():
        for pic in sign["pictograms"]:
            path = resolve(pic)
            if not path.exists():
                missing.append(f"{sign_id}: {pic}")
    assert not missing, "Missing pictogram files:\n" + "\n".join(missing)


def test_every_symbol_exists_on_disk():
    data = load_manifest()
    missing = []
    for sign_id, sign in data["signs"].items():
        path = resolve(sign["symbol"])
        if not path.exists():
            missing.append(f"{sign_id}: {sign['symbol']}")
    assert not missing, "Missing symbol files:\n" + "\n".join(missing)


def test_level_ids_are_unique():
    data = load_manifest()
    ids = [lvl["id"] for lvl in data["levels"]]
    assert len(ids) == len(set(ids)), f"Duplicate level IDs: {ids}"


def test_level_ids_are_contiguous_from_one():
    data = load_manifest()
    ids = sorted(lvl["id"] for lvl in data["levels"])
    expected = list(range(1, len(ids) + 1))
    assert ids == expected, f"Level IDs are not contiguous from 1: {ids}"


def test_levels_reference_known_signs():
    data = load_manifest()
    known = set(data["signs"].keys())
    unknown = []
    for lvl in data["levels"]:
        for sign_id in lvl["signs"]:
            if sign_id not in known:
                unknown.append(f"Level {lvl['id']} ({lvl['name']}): '{sign_id}'")
    assert not unknown, "Levels reference signs not in signs object:\n" + "\n".join(unknown)


def test_levels_have_required_fields():
    data = load_manifest()
    for lvl in data["levels"]:
        assert "id" in lvl, f"Level missing 'id': {lvl}"
        assert "name" in lvl, f"Level {lvl.get('id')}: missing 'name'"
        assert "signs" in lvl, f"Level {lvl.get('id')}: missing 'signs'"
        assert len(lvl["signs"]) > 0, f"Level {lvl['id']} ({lvl['name']}): has no signs"
