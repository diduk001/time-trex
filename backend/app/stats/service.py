from datetime import datetime

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
    query = (
        db.select(TimeEntry, Activity)
        .join(Activity)
        .where(Activity.user_id == user_id)
    )
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
