from flask import *
from config import get_db

reports_bp = Blueprint(
    "reports",
    __name__
)

@reports_bp.route("/reports")
def reports():

    db = get_db()
    cur = db.cursor()

    cur.execute("""
    SELECT *
    FROM monitoring_logs
    ORDER BY timestamp DESC
    """)

    data = cur.fetchall()

    return render_template(
        "reports.html",
        reports=data
    )
