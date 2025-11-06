# tests/conftest.py
import json

import pytest
from flask import Flask

import testenv  # noqa: F401
from app.routes import main_bp


@pytest.fixture()
def app():
    app = Flask(__name__, static_folder="static")
    app.register_blueprint(main_bp)
    app.config["TESTING"] = True
    return app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def write_json(tmp_path):
    def _write(rel, data):
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return p

    return _write
