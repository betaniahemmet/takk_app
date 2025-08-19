import os

from dotenv import load_dotenv

# Go up one level from /app to project root
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
env = os.getenv("FLASK_ENV", "development")
env_file = os.path.join(BASE_DIR, f".env.{env}")
load_dotenv(env_file)

# Debug print to verify loading
print(f"🌍 Loading .env file: {env_file}")
print(f"➡️  BASE_URL from env: {os.getenv('BASE_URL')}")


class Config:
    BASE_DIR = BASE_DIR
    SECRET_KEY = os.environ["SECRET_KEY"]
    FLASK_ENV = os.environ["FLASK_ENV"]
    SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_URL"]
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = os.environ["DEBUG"].lower() == "true"
    BASE_URL = os.getenv("BASE_URL")  # still crashes if missing in qr_pdf.py
