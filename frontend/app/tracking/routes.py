from datetime import UTC, datetime, timedelta

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.security import current_client, login_required

bp = Blueprint("tracking", __name__)


def _to_utc_iso(value):
    if not value:
        return None
    if len(value) == 16:  # 'YYYY-MM-DDTHH:MM'
        return value + ":00Z"
    return value if value.endswith("Z") else value + "Z"


def _today_window():
    start = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    fmt = "%Y-%m-%dT%H:%M:%SZ"
    return start.strftime(fmt), end.strftime(fmt)


@bp.get("/")
@login_required
def index():
    client = current_client()
    activities = client.list_activities()
    frm, to = _today_window()
    entries = client.list_entries(**{"from": frm, "to": to})
    running = client.list_entries(running="true")
    activity_names = {a["id"]: a["name"] for a in activities}
    return render_template(
        "tracking/index.html",
        activities=activities,
        entries=entries,
        running=running,
        activity_names=activity_names,
    )


@bp.post("/entries/start")
@login_required
def start():
    current_client().start_entry(int(request.form["activity_id"]))
    flash("Started.", "success")
    return redirect(url_for("tracking.index"))


@bp.post("/entries/<int:entry_id>/stop")
@login_required
def stop(entry_id):
    current_client().stop_entry(entry_id)
    flash("Stopped.", "success")
    return redirect(url_for("tracking.index"))


@bp.post("/entries")
@login_required
def create():
    current_client().create_entry(
        int(request.form["activity_id"]),
        _to_utc_iso(request.form.get("started_at")),
        _to_utc_iso(request.form.get("ended_at")),
        request.form.get("note") or None,
    )
    flash("Entry added.", "success")
    return redirect(url_for("tracking.index"))


@bp.get("/entries/<int:entry_id>/edit")
@login_required
def edit(entry_id):
    client = current_client()
    entry = client.get_entry(entry_id)
    activities = client.list_activities()
    return render_template("tracking/edit_entry.html", entry=entry, activities=activities)


@bp.post("/entries/<int:entry_id>/update")
@login_required
def update(entry_id):
    fields = {
        "activity_id": int(request.form["activity_id"]),
        "started_at": _to_utc_iso(request.form["started_at"]),
        "note": request.form.get("note") or None,
    }
    ended = _to_utc_iso(request.form.get("ended_at"))
    if ended is not None:
        fields["ended_at"] = ended
    current_client().update_entry(entry_id, **fields)
    flash("Entry updated.", "success")
    return redirect(url_for("tracking.index"))


@bp.post("/entries/<int:entry_id>/delete")
@login_required
def delete(entry_id):
    current_client().delete_entry(entry_id)
    flash("Entry deleted.", "success")
    return redirect(url_for("tracking.index"))
