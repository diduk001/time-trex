from flask import flash, redirect, render_template, request, session, url_for

from app.backend_client import BackendError


def register_error_handlers(app):
    @app.errorhandler(BackendError)
    def handle_backend_error(err: BackendError):
        if err.status == 401:
            session.clear()
            flash("Your session has expired, please log in again.", "warning")
            return redirect(url_for("auth.login"))
        if err.status >= 500:
            return render_template("errors/backend_unavailable.html", message=err.message), 503
        flash(err.message, "danger")
        return redirect(request.referrer or "/")
