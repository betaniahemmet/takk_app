import os

from flask import Flask
from flask_cors import CORS

from .config import Config


def create_app(config_class=Config):
    package_dir = os.path.dirname(os.path.abspath(__file__))  # .../app
    frontend_dist = os.path.join(package_dir, "components", "dist")

    app = Flask(
        __name__,
        static_folder=frontend_dist,
        static_url_path="",  # serve at /
    )
    app.config.from_object(config_class)
    CORS(app)

    from .routes import main_bp

    app.register_blueprint(main_bp)

    return app
