from flask import *
import subprocess

users_bp = Blueprint(
    "users",
    __name__
)

@users_bp.route("/users")
def users():

    output = subprocess.check_output(
        [
            "cut",
            "-d:",
            "-f1",
            "/etc/passwd"
        ]
    ).decode()

    users = output.splitlines()

    return render_template(
        "users.html",
        users=users
    )
