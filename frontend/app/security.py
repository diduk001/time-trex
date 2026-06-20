from functools import wraps

from flask import current_app, redirect, session, url_for

from app.backend_client import BackendClient


def current_client() -> BackendClient:
    return BackendClient(
        current_app.config["BACKEND_URL"],
        token=session.get("access_token"),
        timeout=current_app.config["REQUEST_TIMEOUT"],
    )


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "access_token" not in session:
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped
