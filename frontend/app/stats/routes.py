import datetime as dt
from datetime import timedelta

from flask import Blueprint, render_template, request

from app.security import current_client, login_required

bp = Blueprint("stats", __name__)


def _norm(value, fallback):
    if not value:
        return fallback
    if len(value) == 10:  # 'YYYY-MM-DD'
        return value + "T00:00:00Z"
    if len(value) == 16:  # 'YYYY-MM-DDTHH:MM'
        return value + ":00Z"
    return value if value.endswith("Z") else value + "Z"


def _default_range():
    now = dt.datetime.now(dt.UTC).replace(hour=0, minute=0, second=0, microsecond=0)
    end = now + timedelta(days=1)
    start = end - timedelta(days=7)
    fmt = "%Y-%m-%dT%H:%M:%SZ"
    return start.strftime(fmt), end.strftime(fmt)


@bp.get("/stats")
@login_required
def index():
    default_from, default_to = _default_range()
    frm = _norm(request.args.get("from"), default_from)
    to = _norm(request.args.get("to"), default_to)
    group_by = request.args.get("group_by") or "day"
    client = current_client()
    summary = client.stats_summary(**{"from": frm, "to": to})
    timeline = client.stats_timeline(**{"from": frm, "to": to, "group_by": group_by})
    return render_template(
        "stats/index.html",
        summary=summary,
        timeline=timeline,
        from_date=frm[:10],
        to_date=to[:10],
        group_by=group_by,
    )
