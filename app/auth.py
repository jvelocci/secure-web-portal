from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from app.db import get_db_connection

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # already logged in? send to home
    if "user_id" in session:
        return redirect(url_for("employees.home"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        error = None

        if not username or not password:
            error = "Username and password are required."
        else:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                """
                SELECT id, username, password_hash, role
                FROM app_user
                WHERE username = %s
                """,
                (username,),
            )
            row = cur.fetchone()
            cur.close()
            conn.close()

            if row is None:
                error = "Invalid username or password."
            else:
                user_id, uname, password_hash, role = row
                if not check_password_hash(password_hash, password):
                    error = "Invalid username or password."
                else:
                    session.clear()
                    session["user_id"] = user_id
                    session["username"] = uname
                    session["role"] = role
                    return redirect(url_for("employees.home"))

        flash(error)

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
