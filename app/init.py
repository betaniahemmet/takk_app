# app/__init__.py
import os

from flask import Flask
from flask_cors import CORS

from .config import Config
from .routes import main_bp


def create_app(config_class=Config):
    package_dir = os.path.dirname(os.path.abspath(__file__))
    dist_root = os.path.join(package_dir, "components", "dist")

    app = Flask(
        __name__,
        static_folder=dist_root,  # 👈 full dist, not /assets
        static_url_path="/",  # serve from root
    )
    app.config.from_object(config_class)
    app.config["DIST_ROOT"] = dist_root

    CORS(app)

    app.register_blueprint(main_bp)
    print("🧭 Flask static_folder =", app.static_folder)

    return app
