from flask import *
from config import get_db

alerts_bp = Blueprint(
    "alerts",
    __name__
)

@alerts_bp.route("/alerts")
def alerts():

    db = get_db()
    cur = db.cursor()

    cur.execute("""
    SELECT *
    FROM alerts
    ORDER BY id DESC
    """)

    data = cur.fetchall()

    return render_template(
        "alerts.html",
        alerts=data
    )
