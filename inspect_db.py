from app import create_app
from app.models import TrackingSession

app = create_app()

with app.app_context():
    sessions = TrackingSession.query.all()

    print("=== All Tracking Sessions ===")
    for session in sessions:
        print(f"ID: {session.id}")
        print(f"Tracking ID: {session.tracking_id}")
        print(f"Focus: {session.focus}")
        print(f"Min Label: {session.min_label}")
        print(f"Max Label: {session.max_label}")

        activities = [
            session.activity_1,
            session.activity_2,
            session.activity_3,
            session.activity_4,
            session.activity_5,
            session.activity_6,
            session.activity_7,
        ]
        activities = [a for a in activities if a]
        print(f"Activities: {', '.join(activities)}")
        print("-" * 40)
