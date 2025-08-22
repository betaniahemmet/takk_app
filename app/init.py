# app/__init__.py
import os
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from .config import Config
from .routes import main_bp

db = SQLAlchemy()


def create_app(config_class=Config):
    package_dir = os.path.dirname(os.path.abspath(__file__))  # .../app
    dist_root = os.path.join(package_dir, "components", "dist")  # Vite build root
    assets_dir = os.path.join(dist_root, "assets")  # Vite assets

    app = Flask(
        __name__,
        static_folder=assets_dir,  # serve ONLY /assets/* from here
        static_url_path="/assets",
    )
    app.config.from_object(config_class)
    app.config["DIST_ROOT"] = dist_root

    db.init_app(app)
    CORS(app)

    app.register_blueprint(main_bp)
    return app
