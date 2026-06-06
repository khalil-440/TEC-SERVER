import subprocess
from flask import *
from config import get_db 

app = Flask(__name__)

app.secret_key = "tec_server_secret"

# ======================
# LOGIN
# ======================

@app.route("/", methods=["GET","POST"])
def login():

    if request.method == "POST":

        session["user"] = request.form["username"]

        return redirect("/dashboard")

    return render_template("login.html")


# ======================
# DASHBOARD
# ======================

@app.route("/dashboard")
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


# ======================
# ALERTS
# ======================

@app.route("/alerts")
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
# ======================
# USERS
# ======================

@app.route("/users")
def users():

    users = subprocess.check_output(
        ["bash","scripts/users.sh"]
    ).decode()

    return render_template(
        "users.html",
        users=users
    )


# ======================
# PROCESS
# ======================

@app.route("/processes")
def processes():

    data = subprocess.check_output(
        ["bash","scripts/process.sh"]
    ).decode()

    return render_template(
        "processes.html",
        processes=data
    )

@app.route("/api/chart")
def chart():

    db = get_db()
    cur = db.cursor()

    cur.execute("""
    SELECT timestamp,cpu_usage
    FROM monitoring_logs
    ORDER BY id DESC
    LIMIT 20
    """)

    rows = cur.fetchall()

    rows.reverse()

    return jsonify(rows)
# ======================# REPORT
# ======================

@app.route("/reports")
def reports():

    db = get_db()
    cur = db.cursor()

    cur.execute("""
    SELECT *
    FROM monitoring_logs
    ORDER BY timestamp DESC
    LIMIT 100
    """)

    data = cur.fetchall()

    return render_template(
        "reports.html",
        reports=data
    )

@app.route("/kill-process", methods=["POST"])
def kill_process():

    pid = request.form["pid"]

    try:

        subprocess.run(
            ["kill", "-9", pid],
            check=True
        )

        db = get_db()
        cur = db.cursor()

        cur.execute("""
        INSERT INTO process_logs
        (action,pid,admin)
        VALUES
        (%s,%s,%s)
        """,
        (
            "KILL",
            pid,
            session["user"]
        ))

        db.commit()

    except:
        pass

@app.route("/renice-process", methods=["POST"])
def renice_process():

    pid = request.form["pid"]
    priority = request.form["priority"]

    try:

        if not pid.isdigit():
            return redirect("/processes")

        subprocess.run(
            [
                "renice",
                priority,
                "-p",
                pid
            ],
            check=True
        )

        db = get_db()
        cur = db.cursor()

        cur.execute("""
        INSERT INTO process_logs
        (action,pid,admin)
        VALUES
        (%s,%s,%s)
        """,
        (
            f"RENICE {priority}",
            pid,
            session["user"]
        ))

        db.commit()

    except Exception as e:
        print(e)

    return redirect("/processes")


# ======================
# TEST
# ======================
@app.route("/dbtest")
def dbtest():

    db = get_db()
    cur = db.cursor()

    cur.execute("SELECT 1")

    return "Database Connected"


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
