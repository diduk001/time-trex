from sqlalchemy.exc import IntegrityError

from app.errors import ConflictError, NotFoundError
from app.extensions import db
from app.models import Activity, TimeEntry


def list_activities(user_id: int) -> list[Activity]:
    return list(
        db.session.scalars(
            db.select(Activity).filter_by(user_id=user_id).order_by(Activity.created_at)
        )
    )


def get_activity(user_id: int, activity_id: int) -> Activity:
    activity = db.session.scalar(db.select(Activity).filter_by(id=activity_id, user_id=user_id))
    if activity is None:
        raise NotFoundError("Activity not found")
    return activity


def create_activity(user_id: int, name: str, color: str | None) -> Activity:
    activity = Activity(user_id=user_id, name=name, color=color)
    db.session.add(activity)
    try:
        db.session.commit()
    except IntegrityError as exc:
        db.session.rollback()
        raise ConflictError("Activity name already exists") from exc
    return activity


def update_activity(user_id: int, activity_id: int, data) -> Activity:
    activity = get_activity(user_id, activity_id)
    fields = data.model_fields_set
    if "name" in fields:
        activity.name = data.name
    if "color" in fields:
        activity.color = data.color
    try:
        db.session.commit()
    except IntegrityError as exc:
        db.session.rollback()
        raise ConflictError("Activity name already exists") from exc
    return activity


def delete_activity(user_id: int, activity_id: int) -> None:
    activity = get_activity(user_id, activity_id)
    db.session.delete(activity)
    db.session.commit()


def running_activity_ids(user_id: int) -> set[int]:
    rows = db.session.scalars(
        db.select(TimeEntry.activity_id)
        .join(Activity)
        .where(Activity.user_id == user_id, TimeEntry.ended_at.is_(None))
        .distinct()
    )
    return set(rows)
