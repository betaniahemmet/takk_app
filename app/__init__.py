# app/__init__.py
import os

from flask import Flask
from flask_cors import CORS

from .config import Config  # Config handles all env loading
from .routes import main_bp


def create_app(config_class=Config):
    """
    Flask application factory.
    Environment variables are loaded by config.py before import.
    """
    package_dir = os.path.dirname(os.path.abspath(__file__))
    dist_root = os.path.join(package_dir, "components", "dist")

    app = Flask(__name__, static_folder=dist_root, static_url_path="/")
    app.config.from_object(config_class)
    app.config["DIST_ROOT"] = dist_root

    CORS(app)
    app.register_blueprint(main_bp)

    return app
