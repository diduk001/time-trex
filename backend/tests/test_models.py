import pytest
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Activity, TimeEntry, User
from app.timeutils import utcnow


def _user(login="alice"):
    user = User(login=login, password_hash="hash")
    db.session.add(user)
    db.session.commit()
    return user


def test_create_user_activity_entry(app):
    user = _user()
    activity = Activity(user_id=user.id, name="Work", color="#3b82f6")
    db.session.add(activity)
    db.session.commit()
    entry = TimeEntry(activity_id=activity.id, started_at=utcnow())
    db.session.add(entry)
    db.session.commit()
    assert entry.id is not None
    assert entry.ended_at is None  # running


def test_login_is_unique(app):
    _user("bob")
    db.session.add(User(login="bob", password_hash="other"))
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


def test_activity_name_unique_per_user(app):
    user = _user("carol")
    db.session.add(Activity(user_id=user.id, name="Reading"))
    db.session.commit()
    db.session.add(Activity(user_id=user.id, name="Reading"))
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


def test_deleting_activity_cascades_to_entries(app):
    user = _user("dave")
    activity = Activity(user_id=user.id, name="Work")
    db.session.add(activity)
    db.session.commit()
    db.session.add(TimeEntry(activity_id=activity.id, started_at=utcnow()))
    db.session.commit()
    db.session.delete(activity)
    db.session.commit()
    assert db.session.query(TimeEntry).count() == 0
