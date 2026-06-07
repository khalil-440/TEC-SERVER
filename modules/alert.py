from flask import *
from config import get_db

alerts_bp = Blueprint(
    "alert",
    __name__
)

@alert_bp.route("/alert")
def alert():

    db = get_db()
    cur = db.cursor()

    cur.execute("""
    SELECT *
    FROM alert
    ORDER BY id DESC
    """)

    data = cur.fetchall()

    return render_template(
        "alert.html",
        alert=data
    )
