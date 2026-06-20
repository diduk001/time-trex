from werkzeug.security import check_password_hash, generate_password_hash

from app.errors import AuthError, ConflictError, NotFoundError
from app.extensions import db
from app.models import User


def register_user(login: str, password: str) -> User:
    exists = db.session.scalar(db.select(User).filter_by(login=login))
    if exists is not None:
        raise ConflictError("Login already taken")
    user = User(login=login, password_hash=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()
    return user


def authenticate(login: str, password: str) -> User:
    user = db.session.scalar(db.select(User).filter_by(login=login))
    if user is None or not check_password_hash(user.password_hash, password):
        raise AuthError("Invalid login or password")
    return user


def get_user(user_id: int) -> User:
    user = db.session.get(User, user_id)
    if user is None:
        raise NotFoundError("User not found")
    return user
