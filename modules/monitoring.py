from flask import *
from config import get_db

monitor_bp = Blueprint(
    "monitor",
    __name__
)

@monitor_bp.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/")

    db = get_db()
    cur = db.cursor()

    cur.execute("""
    SELECT *
    FROM monitoring_logs
    ORDER BY id DESC
    LIMIT 1
    """)

    monitoring = cur.fetchone()

    return render_template(
        "dashboard.html",
        monitoring=monitoring
    )


@monitor_bp.route("/api/monitoring")
def api_monitoring():

    db = get_db()
    cur = db.cursor()

    cur.execute("""
    SELECT *
    FROM monitoring_logs
    ORDER BY id DESC
    LIMIT 1
    """)

    data = cur.fetchone()

    return jsonify(data)
