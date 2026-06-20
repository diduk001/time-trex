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


def list_entries(
    user_id: int,
    *,
    activity_id: int | None = None,
    frm: datetime | None = None,
    to: datetime | None = None,
    running: bool | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> list[TimeEntry]:
    query = db.select(TimeEntry).join(Activity).where(Activity.user_id == user_id)
    if activity_id is not None:
        query = query.where(TimeEntry.activity_id == activity_id)
    if frm is not None:
        query = query.where(TimeEntry.started_at >= frm)
    if to is not None:
        query = query.where(TimeEntry.started_at < to)
    if running is True:
        query = query.where(TimeEntry.ended_at.is_(None))
    elif running is False:
        query = query.where(TimeEntry.ended_at.is_not(None))
    query = query.order_by(TimeEntry.started_at.desc())
    if offset is not None:
        query = query.offset(offset)
    if limit is not None:
        query = query.limit(limit)
    return list(db.session.scalars(query))


def get_entry(user_id: int, entry_id: int) -> TimeEntry:
    return _get_owned_entry(user_id, entry_id)


def update_entry(user_id: int, entry_id: int, data) -> TimeEntry:
    entry = _get_owned_entry(user_id, entry_id)
    fields = data.model_fields_set
    if "activity_id" in fields:
        get_activity(user_id, data.activity_id)  # ownership of the new activity
        entry.activity_id = data.activity_id
    if "started_at" in fields:
        entry.started_at = data.started_at
    if "ended_at" in fields:
        entry.ended_at = data.ended_at
    if "note" in fields:
        entry.note = data.note
    if entry.ended_at is not None and entry.ended_at <= entry.started_at:
        db.session.rollback()
        raise UnprocessableError("ended_at must be after started_at")
    db.session.commit()
    return entry


def delete_entry(user_id: int, entry_id: int) -> None:
    entry = _get_owned_entry(user_id, entry_id)
    db.session.delete(entry)
    db.session.commit()
