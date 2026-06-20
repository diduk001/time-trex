from datetime import datetime

from app.activities.service import get_activity
from app.errors import ConflictError, NotFoundError, UnprocessableError
from app.extensions import db
from app.models import Activity, TimeEntry
from app.timeutils import utcnow


def _get_owned_entry(user_id: int, entry_id: int) -> TimeEntry:
    entry = db.session.scalar(
        db.select(TimeEntry).join(Activity).where(
            TimeEntry.id == entry_id, Activity.user_id == user_id
        )
    )
    if entry is None:
        raise NotFoundError("Time entry not found")
    return entry


def _has_running_entry(activity_id: int) -> bool:
    running = db.session.scalar(
        db.select(TimeEntry.id).filter_by(activity_id=activity_id, ended_at=None)
    )
    return running is not None


def start_entry(
    user_id: int, activity_id: int, started_at: datetime | None, note: str | None
) -> TimeEntry:
    get_activity(user_id, activity_id)  # ownership / existence -> 404
    if _has_running_entry(activity_id):
        raise ConflictError("Activity already has a running entry")
    entry = TimeEntry(
        activity_id=activity_id, started_at=started_at or utcnow(), note=note
    )
    db.session.add(entry)
    db.session.commit()
    return entry


def stop_entry(user_id: int, entry_id: int, ended_at: datetime | None) -> TimeEntry:
    entry = _get_owned_entry(user_id, entry_id)
    if entry.ended_at is not None:
        raise ConflictError("Time entry is already stopped")
    end = ended_at or utcnow()
    if end <= entry.started_at:
        raise UnprocessableError("ended_at must be after started_at")
    entry.ended_at = end
    db.session.commit()
    return entry


def create_manual(
    user_id: int,
    activity_id: int,
    started_at: datetime,
    ended_at: datetime,
    note: str | None,
) -> TimeEntry:
    get_activity(user_id, activity_id)  # ownership / existence -> 404
    if ended_at <= started_at:
        raise UnprocessableError("ended_at must be after started_at")
    entry = TimeEntry(
        activity_id=activity_id, started_at=started_at, ended_at=ended_at, note=note
    )
    db.session.add(entry)
    db.session.commit()
    return entry
