# tests/test_api.py

import testenv  # noqa: F401


# --- Utilities to point routes to temp files ---
def monkey_manifest(monkeypatch, path):
    from app import routes

    monkeypatch.setattr(routes, "_manifest_path", lambda: str(path))


def monkey_distractors(monkeypatch, path):
    from app import routes

    monkeypatch.setattr(routes, "_distractors_path", lambda: str(path))


def test_api_signs_happy_path(client, write_json, monkeypatch):
    manifest = {
        "version": 2,
        "levels": [{"id": 1, "name": "Nivå 1", "signs": ["hej", "jag_heter"]}],
        "signs": {
            "hej": {
                "label": "Hej",
                "symbol": "/media/signs/hej/hej.jpg",
                "pictograms": ["/media/signs/hej/hej.jpg"],
                "video": "/media/signs/hej/hej_square.mp4",
            },
            "jag_heter": {
                "label": "Jag heter",
                "symbol": "/media/signs/jag_heter/1_jag.jpg",
                "pictograms": [
                    "/media/signs/jag_heter/1_jag.jpg",
                    "/media/signs/jag_heter/2_heta.jpg",
                ],
                "video": "/media/signs/jag_heter/jag_heter_square.mp4",
            },
        },
    }
    mpath = write_json("catalog/manifest.json", manifest)
    monkey_manifest(monkeypatch, mpath)

    r = client.get("/api/signs")
    assert r.status_code == 200
    data = r.get_json()
    assert "signs" in data and isinstance(data["signs"], list)
    # shape
    item = {k: type(v).__name__ for k, v in data["signs"][0].items()}
    assert set(item.keys()) == {"id", "label", "video", "pictograms"}
    # labels present and sorted
    labels = [s["label"] for s in data["signs"]]
    assert labels == sorted(labels, key=str.lower)


def test_api_levels_and_detail(client, write_json, monkeypatch):
    manifest = {
        "version": 2,
        "levels": [
            {"id": 1, "name": "Nivå 1", "signs": ["hej"]},
            {"id": 2, "name": "Nivå 2", "signs": ["tack"]},
        ],
        "signs": {
            "hej": {"label": "Hej", "video": "/v1.mp4", "pictograms": ["/p1.jpg"]},
            "tack": {"label": "Tack", "video": "/v2.mp4", "pictograms": ["/p2.jpg"]},
        },
    }
    mpath = write_json("catalog/manifest.json", manifest)
    monkey_manifest(monkeypatch, mpath)

    # list
    r1 = client.get("/api/levels")
    assert r1.status_code == 200
    L = r1.get_json()["levels"]
    assert len(L) == 2 and L[0]["id"] == 1

    # detail expands signs
    r2 = client.get("/api/levels/1")
    assert r2.status_code == 200
    d = r2.get_json()
    assert d["id"] == 1
    assert d["signs"][0]["id"] == "hej"
    assert d["signs"][0]["video"] == "/v1.mp4"
    assert d["signs"][0]["pictograms"] == ["/p1.jpg"]


def test_api_distractors_fallback_empty(client, monkeypatch, tmp_path):
    # no file present

    monkey_distractors(monkeypatch, tmp_path / "catalog" / "distractors.json")
    r = client.get("/api/distractors")
    assert r.status_code == 200
    data = r.get_json()
    assert data.get("2") == [] and data.get("3") == []


def test_api_distractors_valid(client, write_json, monkeypatch):
    dpath = write_json("catalog/distractors.json", {"2": ["hej"], "3": ["jag heter"]})
    monkey_distractors(monkeypatch, dpath)
    r = client.get("/api/distractors")
    assert r.status_code == 200
    data = r.get_json()
    assert data["2"] == ["hej"]
    assert data["3"] == ["jag heter"]


def test_api_score_post_ok(client, monkeypatch):
    # monkeypatch leaderboard functions
    from app import routes

    def fake_add_score(name, score):
        return ([{"name": name, "score": score}], True)

    monkeypatch.setattr(routes, "add_score", fake_add_score)

    r = client.post("/api/score", json={"name": "HB", "score": 12.34})
    assert r.status_code == 200
    data = r.get_json()
    assert data["ok"] is True
    assert data["madeTop"] is True
    assert data["scores"][0]["name"] == "HB"


def test_api_score_post_bad_request(client):
    r = client.post("/api/score", json={"name": "", "score": None})
    assert r.status_code == 400
