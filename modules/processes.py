from flask import *
from config import get_db
import subprocess
import os

process_bp = Blueprint(
    "process",
    __name__
)

@process_bp.route("/processes")
def processes():

    output = subprocess.check_output(
        ["ps","aux"]
    ).decode()

    return render_template(
        "processes.html",
        output=output
    )


@process_bp.route("/kill/<int:pid>")
def kill_process(pid):

    try:

        os.system(
            f"kill {pid}"
        )

        db = get_db()
        cur = db.cursor()

        cur.execute("""
        INSERT INTO process_logs
        (
        action,
        pid,
        admin
        )
        VALUES
        (
        'Kill Process',
        %s,
        %s
        )
        """,
        (
        pid,
        session["user"]
        ))

        db.commit()

    except:
        pass

    return redirect("/processes")
