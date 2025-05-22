from app import create_app, db
from app.config import Config
from app.models import TrackingLog, TrackingSession  # noqa: F401

print("🌍 Loading .env file:", Config.FLASK_ENV)
print("➡️  BASE_URL from env:", Config.BASE_URL)

# Create the Flask app
app = create_app()

# Use the app context to bind SQLAlchemy correctly
with app.app_context():
    db.create_all()
    print("✅ Database created successfully.")
