# app/__init__.py
import os

from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from .config import Config  # Config handles all env loading
from .routes import main_bp


def create_app(config_class=Config):
    """
    Flask application factory.
    Environment variables are loaded by config.py before import.
    """
    package_dir = os.path.dirname(os.path.abspath(__file__))
    dist_root = os.path.join(package_dir, "components", "dist")

    # static_folder=None disables Flask's built-in static handler (which would
    # intercept /<path> requests and 404 before the SPA catch-all fires).
    # The blueprint's /<path:path> route serves both real dist files and index.html.
    app = Flask(__name__, static_folder=None)
    app.config.from_object(config_class)
    app.config["DIST_ROOT"] = dist_root

    # Behind nginx every request comes from 127.0.0.1. Trust exactly one proxy
    # hop so request.remote_addr is the real client IP (used for rate limiting).
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)
    app.register_blueprint(main_bp)

    return app
