# tests/test_manifest_builder.py
import json

import testenv  # noqa: F401


def test_manifest_builder_reads_media_signs(tmp_path, monkeypatch):
    # simulate media/signs/<sign>/{mp4, pictos}
    media_signs = tmp_path / "media" / "signs"
    (media_signs / "jag_heter").mkdir(parents=True, exist_ok=True)
    (media_signs / "hej").mkdir(parents=True, exist_ok=True)

    # videos
    (media_signs / "jag_heter" / "jag_heter_square.mp4").write_bytes(b"\x00")
    (media_signs / "hej" / "hej_square.mp4").write_bytes(b"\x00")
    # pictograms (ordered by filename)
    (media_signs / "jag_heter" / "1_jag.jpg").write_bytes(b"\x00")
    (media_signs / "jag_heter" / "2_heta.jpg").write_bytes(b"\x00")
    (media_signs / "hej" / "hej.jpg").write_bytes(b"\x00")

    # patch builder paths
    from video_processing import manifest_builder as mb

    monkeypatch.setattr(mb, "BASE_DIR", tmp_path)
    monkeypatch.setattr(mb, "prompt_level", lambda name: 0)

    out_file = tmp_path / "catalog" / "manifest.json"

    # run
    mb.build_manifest()

    # assert
    data = json.loads(out_file.read_text(encoding="utf-8"))
    assert data["version"] == 2
    assert set(data["signs"].keys()) == {"jag_heter", "hej"}
    jh = data["signs"]["jag_heter"]
    assert jh["video"].endswith("/media/signs/jag_heter/jag_heter_square.mp4")
    assert jh["pictograms"] == [
        "/media/signs/jag_heter/1_jag.jpg",
        "/media/signs/jag_heter/2_heta.jpg",
    ]
