from flask import *
from werkzeug.security import check_password_hash
from config import get_db

auth_bp = Blueprint(
    "auth",
    __name__
)

@auth_bp.route("/", methods=["GET","POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        cur = db.cursor()

        cur.execute(
            """
            SELECT *
            FROM users
            WHERE username=%s
            """,
            (username,)
        )

        user = cur.fetchone()

        if user:

            if check_password_hash(
                user["password_hash"],
                password
            ):

                session["user"] = username
                session["role"] = user["role"]

                return redirect("/dashboard")

        return render_template(
            "login.html",
            error="Login gagal"
        )

    return render_template(
        "login.html"
    )


@auth_bp.route("/logout")
def logout():

    session.clear()

    return redirect("/")
