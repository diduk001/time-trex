from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app.backend_client import BackendError
from app.security import current_client

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("auth/login.html")
    login_value = request.form.get("login", "")
    password = request.form.get("password", "")
    try:
        result = current_client().login(login_value, password)
    except BackendError as exc:
        message = "Invalid login or password." if exc.status == 401 else exc.message
        flash(message, "danger")
        return render_template("auth/login.html", login=login_value), 400
    session["access_token"] = result["access_token"]
    return redirect("/")  # tracking home


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("auth/register.html")
    login_value = request.form.get("login", "")
    password = request.form.get("password", "")
    try:
        client = current_client()
        client.register(login_value, password)
        result = client.login(login_value, password)
    except BackendError as exc:
        flash(exc.message, "danger")
        return render_template("auth/register.html", login=login_value), 400
    session["access_token"] = result["access_token"]
    return redirect("/")  # tracking home


@bp.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
