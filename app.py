import psutil
import subprocess
from flask import *
from config import get_db
import pwd 
from flask import redirect
from datetime import datetime
import pytz

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

    try:

        db = get_db()
        cur = db.cursor()

        cur.execute("""
            SELECT *
            FROM monitoring_logs
            ORDER BY id DESC
            LIMIT 1
        """)

        monitoring = cur.fetchone()

    except Exception as e:

        print(e)

        monitoring = {
            "cpu_usage": 0,
            "ram_usage": 0,
            "disk_usage": 0,
            "swap_usage": 0,
            "active_users": 0
        }

    return render_template(
        "dashboard.html",
        monitoring=monitoring
    )

from flask import jsonify

@app.route("/api/monitoring")
def api_monitoring():

    try:

        db = get_db()
        cur = db.cursor()

        cur.execute("""
            SELECT cpu_usage,
                   ram_usage,
                   disk_usage,
                   swap_usage,
                   active_users
            FROM monitoring_logs
            ORDER BY id DESC
            LIMIT 1
        """)

        monitoring = cur.fetchone()

        if monitoring is None:
            return jsonify({
                "cpu_usage": 0,
                "ram_usage": 0,
                "disk_usage": 0,
                "swap_usage": 0,
                "active_users": 0
            })

        return jsonify(monitoring)

    except Exception as e:

        print("API MONITORING ERROR:", e)

        return jsonify({
            "cpu_usage": 0,
            "ram_usage": 0,
            "disk_usage": 0,
            "swap_usage": 0,
            "active_users": 0
        })

@app.route("/api/monitoring/history")
def monitoring_history():

    db = get_db()
    cur = db.cursor()

    cur.execute("""
        SELECT cpu_usage, ram_usage, timestamp
        FROM monitoring_logs
        ORDER BY id DESC
        LIMIT 20
    """)

    rows = cur.fetchall()

    rows.reverse()

    return jsonify(rows)

@app.route("/test-login")
def test_login():

    session["user"] = "tecadmin"

    return redirect("/dashboard")

# ======================
# ALERTS
# ======================
@app.route("/alert")
def alert():

    db = get_db()
    cur = db.cursor()

    # Alert history
    cur.execute("""
        SELECT *
        FROM alerts
        ORDER BY id DESC
    """)
    alerts = cur.fetchall()

    # Dispatch log (simulasi email)
    cur.execute("""
        SELECT *
        FROM activity_logs
        ORDER BY id DESC
        LIMIT 10
    """)
    logs = cur.fetchall()

    return render_template(
        "alert.html",
        alert=alerts,
        logs=logs
    )
# ======================
# USERS
# ======================

@app.route("/users")
def users():

    users = []

    for u in pwd.getpwall():
        users.append({
            "username": u.pw_name,
            "uid": u.pw_uid,
            "gid": u.pw_gid,
            "home": u.pw_dir,
            "shell": u.pw_shell
        })

    return render_template(
        "users.html",
        users=users
    )

@app.get("/api/users")
def get_users():
    users = []

    for user in pwd.getpwall():
        users.append({
            "username": user.pw_name,
            "uid": user.pw_uid,
            "gid": user.pw_gid,
            "home": user.pw_dir,
            "shell": user.pw_shell
        })

    return users

from werkzeug.security import generate_password_hash

@app.route("/add_user", methods=["POST"])
def add_user():

    username = request.form["username"]
    password = request.form["password"]
    role = request.form["role"]

    password_hash = generate_password_hash(password)

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO users
        (username, password_hash, role, last_login)
        VALUES (%s, %s, %s, NULL)
    """, (
        username,
        password_hash,
        role
    ))

    conn.commit()
    cur.close()
    conn.close()

    return redirect("/users")

@app.route("/lock_user/<username>")
def lock_user(username):

    subprocess.run(
        ["usermod", "-L", username],
        check=True
    )

    return redirect("/users")

@app.route("/unlock_user/<username>")
def unlock_user(username):

    subprocess.run(
        ["usermod", "-U", username],
        check=True
    )

    return redirect("/users")

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

@app.get("/api/processes")
def get_processes():
    processes = []

    for p in psutil.process_iter([
        'pid',
        'username',
        'nice',
        'memory_percent',
        'cpu_percent',
        'name'
    ]):
        try:
            processes.append({
                "pid": p.info["pid"],
                "user": p.info["username"],
                "cpu": p.info["cpu_percent"],
                "mem": round(p.info["memory_percent"], 2),
                "nice": p.info["nice"],
                "command": p.info["name"]
            })
        except:
            pass

    return processes

@app.route("/processes")
def show_processes():
    conn = get_db()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT * FROM processes")
    processes = cur.fetchall()

    return render_template(
        "processes.html",
        processes=processes
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
# ======================
# REPORT
# ======================

@app.route("/reports")
def reports():

    try:

        db = get_db()
        cur = db.cursor()

        cur.execute("""
        SELECT *
        FROM monitoring_logs
        ORDER BY timestamp DESC
        LIMIT 100
        """)

        data = cur.fetchall()

    except Exception as e:

        print("DB ERROR:", e)

        data = []

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
