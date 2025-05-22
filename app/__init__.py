import os

from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from app.config import Config

db = SQLAlchemy()


def create_app(config_class=Config):
    app = Flask(
        __name__,
        instance_path=os.path.abspath("."),
        static_folder="../dist",  # ✅ Vite's output folder
        static_url_path="/",  # ✅ So /admin and /log hit index.html
    )

    app.config.from_object(config_class)
    db.init_app(app)
    CORS(app)

    from app.routes import main_bp

    app.register_blueprint(main_bp)

    return app
