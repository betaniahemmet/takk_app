import io
import uuid

from flask import Blueprint, current_app, jsonify, request, send_file

from app import db
from app.models import TrackingLog, TrackingSession
from app.utils.qr_pdf import generate_qr_pdf  # make sure this exists and works

main_bp = Blueprint("main", __name__)


# ✅ Serve React frontend from dist/index.html for all routes
@main_bp.route("/", defaults={"path": ""})
@main_bp.route("/<path:path>")
def serve_spa(path):
    return current_app.send_static_file("index.html")


@main_bp.route("/admin", methods=["GET", "POST"])
def admin_page():
    if request.method == "POST":
        # Parse form data
        focus = request.form.get("focus")
        min_label = request.form.get("min_label")
        max_label = request.form.get("max_label")
        initials = request.form.get("initials")
        location = request.form.get("location")
        duration = request.form.get("duration")
        admin_email = request.form.get("admin_email")
        tracking_mode = request.form.get(
            "tracking_mode", "scale"
        )  # fallback to 'scale'

        activities = []
        for i in range(1, 8):
            act = request.form.get(f"activity_{i}")
            if act:
                activities.append(act)

        # Create new TrackingSession
        # Prevent duplicates for same initials + location
        existing = TrackingSession.query.filter_by(
            initials=initials, location=location
        ).first()

        if existing:
            return (
                jsonify(
                    {
                        "error": (
                            "En kartläggning för dessa initialer "
                            "och platsen finns redan."
                        )
                    }
                ),
                400,
            )

        tracking_id = str(uuid.uuid4())
        session = TrackingSession(
            tracking_id=tracking_id,
            focus=focus,
            min_label=min_label,
            max_label=max_label,
            initials=initials,
            location=location,
            duration=duration,
            admin_email=admin_email,
            tracking_mode=tracking_mode,
            activity_1=request.form.get("activity_1"),
            activity_2=request.form.get("activity_2"),
            activity_3=request.form.get("activity_3"),
            activity_4=request.form.get("activity_4"),
            activity_5=request.form.get("activity_5"),
            activity_6=request.form.get("activity_6"),
            activity_7=request.form.get("activity_7"),
        )
        db.session.add(session)
        db.session.commit()

        # Generate QR PDF
        pdf_bytes = generate_qr_pdf(tracking_id, initials, location)

        # Return PDF
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"{initials}_{location}_QR.pdf",
        )

    # For GET request
    return current_app.send_static_file("index.html")


@main_bp.route("/log", methods=["GET"])
def log_page_root():
    return current_app.send_static_file("index.html")


@main_bp.route("/log/<path:subpath>", methods=["GET"])
def log_page_sub(subpath):
    return current_app.send_static_file("index.html")


@main_bp.route("/log", methods=["POST"])
def submit_tracking_log():
    data = request.get_json()
    print("📝 Received tracking log:", data)

    session = TrackingSession.query.filter_by(
        tracking_id=data.get("tracking_id")
    ).first()
    if not session:
        return jsonify({"error": "Tracking session not found"}), 404

    log = TrackingLog(
        value=data.get("value"),
        activities=",".join(data.get("activities", [])),
        session_id=session.id,
    )
    db.session.add(log)
    db.session.commit()

    return jsonify({"status": "ok", "log_id": log.id})


@main_bp.route("/get-admin-settings")
def get_admin_settings():
    tracking_id = request.args.get("tracking_id")
    session = TrackingSession.query.filter_by(tracking_id=tracking_id).first()

    if not session:
        return jsonify({"error": "Tracking session not found"}), 404

    activities = [
        session.activity_1,
        session.activity_2,
        session.activity_3,
        session.activity_4,
        session.activity_5,
        session.activity_6,
        session.activity_7,
    ]

    # ✅ Only include non-empty strings
    activities = [a for a in activities if a]

    return jsonify(
        {
            "focus": session.focus,
            "min_label": session.min_label,
            "max_label": session.max_label,
            "activities": activities,
            "tracking_mode": session.tracking_mode,
        }
    )

@main_bp.route("/list-previous-sessions")
def list_previous_sessions():
    initials = request.args.get("initials")
    location = request.args.get("location")

    if not initials or not location:
        return jsonify([])

    sessions = (
        TrackingSession.query
        .filter_by(initials=initials, location=location)
        .order_by(TrackingSession.created_at.desc())
        .limit(10)
        .all()
    )

    result = [
        {
            "tracking_id": s.tracking_id,
            "focus": s.focus,
            "created_at": s.created_at.strftime("%Y-%m-%d"),
        }
        for s in sessions
    ]

    return jsonify(result)


@main_bp.route("/load-previous-session")
def load_previous_session():
    tracking_id = request.args.get("tracking_id")
    if not tracking_id:
        return jsonify({"error": "Missing tracking ID"}), 400

    s = TrackingSession.query.filter_by(tracking_id=tracking_id).first()
    if not s:
        return jsonify(None)

    activities = [
        s.activity_1, s.activity_2, s.activity_3, s.activity_4,
        s.activity_5, s.activity_6, s.activity_7
    ]
    activities = [a for a in activities if a]

    return jsonify({
        "focus": s.focus,
        "min_label": s.min_label,
        "max_label": s.max_label,
        "activities": activities,
        "tracking_mode": s.tracking_mode,
    })


@main_bp.route("/debug-logs")
def debug_logs():
    from app.models import TrackingLog

    logs = TrackingLog.query.all()
    result = {
        "count": len(logs),
        "latest": (
            {
                "id": logs[-1].id,
                "value": logs[-1].value,
                "activities": logs[-1].activities,
                "timestamp": logs[-1].timestamp.isoformat(),
                "session_id": logs[-1].session_id,
            }
            if logs
            else "no logs yet"
        ),
    }
    return jsonify(result)
