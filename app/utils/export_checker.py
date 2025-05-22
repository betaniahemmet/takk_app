from sqlalchemy import func

from app.models import TrackingSession


def get_sessions_ready_for_export():
    now = func.now()

    week_sessions = TrackingSession.query.filter(
        TrackingSession.duration == "week",
        TrackingSession.exported.is_(False),
        TrackingSession.created_at <= func.datetime(now, "-7 days"),
    )

    month_sessions = TrackingSession.query.filter(
        TrackingSession.duration == "month",
        TrackingSession.exported.is_(False),
        TrackingSession.created_at <= func.datetime(now, "-30 days"),
    )

    return week_sessions.union_all(month_sessions).all()
