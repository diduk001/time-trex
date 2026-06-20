from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.security import current_client, login_required

bp = Blueprint("activities", __name__)


@bp.get("/activities")
@login_required
def index():
    activities = current_client().list_activities()
    return render_template("activities/index.html", activities=activities)


@bp.post("/activities")
@login_required
def create():
    name = request.form.get("name", "")
    color = request.form.get("color") or None
    current_client().create_activity(name, color)
    flash("Activity created.", "success")
    return redirect(url_for("activities.index"))


@bp.get("/activities/<int:activity_id>/edit")
@login_required
def edit(activity_id):
    activity = current_client().get_activity(activity_id)
    return render_template("activities/edit.html", activity=activity)


@bp.post("/activities/<int:activity_id>/update")
@login_required
def update(activity_id):
    name = request.form.get("name", "")
    color = request.form.get("color") or None
    kwargs: dict = {"name": name}
    if color is not None:
        kwargs["color"] = color
    current_client().update_activity(activity_id, **kwargs)
    flash("Activity updated.", "success")
    return redirect(url_for("activities.index"))


@bp.post("/activities/<int:activity_id>/delete")
@login_required
def delete(activity_id):
    current_client().delete_activity(activity_id)
    flash("Activity deleted.", "success")
    return redirect(url_for("activities.index"))
