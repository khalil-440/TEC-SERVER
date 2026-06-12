import psutil
import subprocess
import os
import signal
from flask import *
from config import get_db
import pwd 
from flask import redirect
from datetime import datetime
from werkzeug.security import check_password_hash
from flask import Response
import csv
from reportlab.pdfgen import canvas
from flask import send_file
import io


app = Flask(__name__)

app.secret_key = "tec_server_secret"

# ======================
# LOGIN
# ======================
@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        try:

            db = get_db()
            cur = db.cursor()

            cur.execute("""
                SELECT *
                FROM users
                WHERE TRIM(username) = TRIM(%s)
            """, (username,))

            user = cur.fetchone()

            print("USERNAME INPUT =", username)
            print("PASSWORD INPUT =", password)
            print("USER DB =", user)

            if user and str(user["password_hash"]).strip() == password:

                session["user"] = user["username"]
                session["role"] = user["role"]
                session["user_id"] = user["id"]

                cur.execute("""
                    UPDATE users
                    SET last_login = NOW(),
                    last_seen = NOW()
                    WHERE id = %s
                """, (user["id"],))

                db.commit()

                print("LOGIN UPDATED:", user["username"])

                return redirect("/dashboard")

            return render_template(
                "login.html",
                error="Username atau password salah"
            )

        except Exception as e:

            print("LOGIN ERROR =", e)

            return render_template(
                "login.html",
                error="Terjadi kesalahan sistem"
            )

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
    SELECT
        id,
        type,
        value,
        status,
	created_at
	DATE_ADD(created_at, INTERVAL 7 HOUR) AS created_at
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
@app.route("/clear_alerts", methods=["POST"])
def clear_alerts():

    try:
        db = get_db()
        cur = db.cursor()

        cur.execute("DELETE FROM alerts")

        db.commit()

        cur.close()
        db.close()

        return jsonify({
            "success": True
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/api/alerts')
def api_alerts():
    conn = get_db()
    cur = conn.cursor(pymysql.cursors.DictCursor)

    cur.execute("""
        SELECT *
        FROM alerts
        ORDER BY created_at DESC
    """)

    data = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify(data)

# ======================
# USERS
# ======================

from datetime import datetime, timedelta

@app.route("/users")
def users():

    print("USERS ROUTE V3")

    db = get_db()
    cur = db.cursor()

    cur.execute("""
        SELECT
            username,
            role,
            last_login,
            last_seen
        FROM users
        ORDER BY username
    """)

    rows = cur.fetchall()

    users = []

    for row in rows:

        status = "Offline"

        if row["last_seen"]:

            selisih = datetime.now() - row["last_seen"]

            if selisih < timedelta(minutes=2):
                status = "Online"

        last_login = row["last_login"]

        if last_login:
            last_login = last_login + timedelta(hours=7)

        users.append({
            "username": row["username"],
            "role": row["role"],
            "last_login": last_login,
            "status": status
        })

    return render_template(
        "users.html",
        users=users
    )

from datetime import datetime, timedelta

@app.get("/api/users")
def get_users():

    db = get_db()
    cur = db.cursor()

    cur.execute("""
        SELECT
            id,
            username,
            role,
            last_login,
            last_seen
        FROM users
        ORDER BY username
    """)

    rows = cur.fetchall()

    users = []

    for row in rows:

        online = False

        if row["last_seen"]:

            if (
                datetime.now() - row["last_seen"]
            ) < timedelta(minutes=2):
                online = True

        users.append({
            "id": row["id"],
            "username": row["username"],
            "role": row["role"],
            "last_login": (
                row["last_login"].strftime("%Y-%m-%d %H:%M:%S")
                if row["last_login"]
                else "-"
            ),
            "status": "Online" if online else "Offline"
        })

    return jsonify(users)


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

@app.route("/kick_user/<username>")
def kick_user(username):

    try:

        subprocess.run(
            ["pkill", "-KILL", "-u", username],
            check=False
        )

    except Exception as e:
        print("KICK USER ERROR:", e)

    return redirect("/users")

# ======================
# PROCESS
# ======================

#@app.route("/processes")
#def processes():

#   data = subprocess.check_output(
#        ["bash","scripts/process.sh"]
#    ).decode()
#
#    9273hjasasadhreturn render_template(
#        "processes.html",
#        processes=data
#    )

@app.get("/api/processes")
def get_processes():

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            pid,
            user,
            cpu,
            mem,
            nice,
            command
        FROM processes
        ORDER BY cpu DESC
    """)

    data = cur.fetchall()

    return jsonify(data)

@app.post("/api/processes/kill/<int:pid>")
def kill_process(pid):

    try:

        conn = get_db()
        cur = conn.cursor()

        # simpan request kill
        cur.execute("""
        INSERT INTO kill_requests(pid)
        VALUES(%s)
        """, (pid,))

        # simpan log
        cur.execute("""
        INSERT INTO process_logs
        (action, pid, admin)
        VALUES (%s, %s, %s)
        """, (
            "kill",
            pid,
            "admin"
        ))

        conn.commit()

        cur.close()
        conn.close()

        return {
            "success": True
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }

@app.route("/processes")
def show_processes():
    return render_template("processes.html")

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

    db = get_db()
    cur = db.cursor()

    cur.execute("""
        SELECT *
        FROM monitoring_logs
        ORDER BY timestamp DESC
        LIMIT 100
    """)

    reports = cur.fetchall()

    cur.execute("""
        SELECT
            MIN(timestamp) AS start_date,
            MAX(timestamp) AS end_date
        FROM monitoring_logs
    """)

    date_range = cur.fetchone()

    if reports:

        avg_cpu = round(
            sum(r["cpu_usage"] for r in reports)
            / len(reports), 1
        )

        max_ram = max(
            r["ram_usage"] for r in reports
        )

        disk_growth = (
            reports[0]["disk_usage"]
            - reports[-1]["disk_usage"]
        )

    else:

        avg_cpu = 0
        max_ram = 0
        disk_growth = 0

    if reports:
        start_date = reports[-1]["timestamp"].strftime("%d %b %Y")
        end_date = reports[0]["timestamp"].strftime("%d %b %Y")
    else:
        start_date = "-"
        end_date = "-"

    return render_template(
    "reports.html",
    reports=reports,
    avg_cpu=avg_cpu,
    max_ram=max_ram,
    disk_growth=disk_growth,
    start_date=date_range["start_date"],
    end_date=date_range["end_date"]
)

@app.route("/kill-process", methods=["POST"])
def kill_process_reports():

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
A        VALUES
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

@app.route("/export-csv")
def export_csv():

    db = get_db()
    cur = db.cursor()

    cur.execute("""
        SELECT timestamp,
               cpu_usage,
               ram_usage,
               disk_usage,
               swap_usage
        FROM monitoring_logs
        ORDER BY timestamp DESC
    """)

    rows = cur.fetchall()

    def generate():
        yield "timestamp,cpu_usage,ram_usage,disk_usage,swap_usage\n"

        for row in rows:
            yield f"{row['timestamp']},{row['cpu_usage']},{row['ram_usage']},{row['disk_usage']},{row['swap_usage']}\n"

    return Response(
        generate(),
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=monitoring_report.csv"
        }
    )

from reportlab.pdfgen import canvas

@app.route('/export/pdf')
def export_pdf():

    pdf_file = "report.pdf"
    c = canvas.Canvas(pdf_file)

    c.drawString(100, 800, "TEC SERVER REPORT")
    c.drawString(100, 780, "CPU AVG : 0.4%")
    c.drawString(100, 760, "RAM MAX : 8.25%")
    c.drawString(100, 740, "DISK GROWTH : 0.0%")

    c.save()

    return send_file(pdf_file, as_attachment=True)


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

@app.route("/api/reports/filter")
def filter_reports():

    hours = request.args.get("hours", 24)

    db = get_db()
    cur = db.cursor()

    cur.execute("""
        SELECT *
        FROM monitoring_logs
        WHERE timestamp >= NOW() - INTERVAL %s HOUR
        ORDER BY timestamp DESC
    """, (hours,))

    reports = cur.fetchall()

    return jsonify(reports)

# ======================
# TEST
# ======================
@app.route("/dbtest")
def dbtest():

    db = get_db()
    cur = db.cursor()

    cur.execute("SELECT 1")

    return "Database Connected"


@app.route("/api/heartbeat", methods=["POST"])
def heartbeat():

    if "user_id" not in session:
        return jsonify({"success": False}), 401

    db = get_db()
    cur = db.cursor()

    cur.execute("""
        UPDATE users
        SET last_seen = NOW()
        WHERE id = %s
    """, (session["user_id"],))

    db.commit()

    return jsonify({"success": True})

@app.route("/settings")
def settings():
    return render_template("settings.html")


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
