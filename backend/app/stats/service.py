from datetime import datetime, timedelta

from app.errors import UnprocessableError
from app.extensions import db
from app.models import Activity, TimeEntry
from app.timeutils import isoformat_z, utcnow


def clipped_seconds(
    started_at: datetime,
    ended_at: datetime | None,
    frm: datetime | None,
    to: datetime | None,
    now: datetime,
) -> float:
    """Seconds of [started_at, ended_at or now] that fall within [frm, to]."""
    start = started_at
    end = ended_at or now
    if frm is not None and start < frm:
        start = frm
    if to is not None and end > to:
        end = to
    if end <= start:
        return 0.0
    return (end - start).total_seconds()


def _owned_entries(user_id, frm, to, activity_id):
    query = db.select(TimeEntry, Activity).join(Activity).where(Activity.user_id == user_id)
    if activity_id is not None:
        query = query.where(TimeEntry.activity_id == activity_id)
    if to is not None:
        query = query.where(TimeEntry.started_at < to)
    if frm is not None:
        # keep entries that are still open or end after frm
        query = query.where((TimeEntry.ended_at.is_(None)) | (TimeEntry.ended_at > frm))
    return db.session.execute(query).all()


def summary(user_id, frm, to, activity_id) -> dict:
    now = utcnow()
    rows = _owned_entries(user_id, frm, to, activity_id)
    per_activity: dict[int, dict] = {}
    total = 0.0
    for entry, activity in rows:
        secs = clipped_seconds(entry.started_at, entry.ended_at, frm, to, now)
        if secs <= 0:
            continue
        total += secs
        bucket = per_activity.setdefault(
            activity.id,
            {
                "activity_id": activity.id,
                "name": activity.name,
                "color": activity.color,
                "total_seconds": 0,
                "entry_count": 0,
            },
        )
        bucket["total_seconds"] += int(secs)
        bucket["entry_count"] += 1
    return {
        "from": isoformat_z(frm) if frm else None,
        "to": isoformat_z(to) if to else None,
        "total_seconds": int(total),
        "by_activity": sorted(
            per_activity.values(), key=lambda b: b["total_seconds"], reverse=True
        ),
    }


def _bucket_start(dt: datetime, group_by: str) -> datetime:
    day = dt.replace(hour=0, minute=0, second=0, microsecond=0)
    if group_by == "day":
        return day
    if group_by == "week":
        return day - timedelta(days=day.weekday())
    return day.replace(day=1)  # month


def _next_bucket(start: datetime, group_by: str) -> datetime:
    if group_by == "day":
        return start + timedelta(days=1)
    if group_by == "week":
        return start + timedelta(days=7)
    if start.month == 12:
        return start.replace(year=start.year + 1, month=1)
    return start.replace(month=start.month + 1)


def _period_label(start: datetime, group_by: str) -> str:
    if group_by == "month":
        return start.strftime("%Y-%m")
    return start.strftime("%Y-%m-%d")


def timeline(user_id, frm, to, group_by, activity_id) -> dict:
    if frm is None or to is None:
        raise UnprocessableError("'from' and 'to' are required for timeline")
    if group_by not in {"day", "week", "month"}:
        raise UnprocessableError("group_by must be one of: day, week, month")
    now = utcnow()
    rows = _owned_entries(user_id, frm, to, activity_id)
    buckets = []
    bucket_start = _bucket_start(frm, group_by)
    while bucket_start < to:
        bucket_end = _next_bucket(bucket_start, group_by)
        win_start = max(bucket_start, frm)
        win_end = min(bucket_end, to)
        per_activity: dict[int, dict] = {}
        bucket_total = 0.0
        for entry, activity in rows:
            secs = clipped_seconds(entry.started_at, entry.ended_at, win_start, win_end, now)
            if secs <= 0:
                continue
            bucket_total += secs
            b = per_activity.setdefault(
                activity.id,
                {"activity_id": activity.id, "name": activity.name, "total_seconds": 0},
            )
            b["total_seconds"] += int(secs)
        buckets.append(
            {
                "period": _period_label(bucket_start, group_by),
                "total_seconds": int(bucket_total),
                "by_activity": sorted(
                    per_activity.values(), key=lambda x: x["total_seconds"], reverse=True
                ),
            }
        )
        bucket_start = bucket_end
    return {"group_by": group_by, "buckets": buckets}
