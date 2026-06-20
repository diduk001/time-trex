from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.timeutils import utcnow


class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)

    activities: Mapped[list["Activity"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    def __init__(self, login: str, password_hash: str, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self.login = login
        self.password_hash = password_hash


class Activity(db.Model):
    __tablename__ = "activities"
    __table_args__ = (UniqueConstraint("user_id", "name", name="uq_activity_user_name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    color: Mapped[str | None] = mapped_column(String(7), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)

    user: Mapped["User"] = relationship(back_populates="activities")
    entries: Mapped[list["TimeEntry"]] = relationship(
        back_populates="activity", cascade="all, delete-orphan"
    )

    def __init__(
        self,
        user_id: int,
        name: str,
        color: str | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(**kwargs)
        self.user_id = user_id
        self.name = name
        self.color = color


class TimeEntry(db.Model):
    __tablename__ = "time_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    activity_id: Mapped[int] = mapped_column(
        ForeignKey("activities.id"), index=True, nullable=False
    )
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)

    activity: Mapped["Activity"] = relationship(back_populates="entries")

    def __init__(
        self,
        activity_id: int,
        started_at: datetime,
        ended_at: datetime | None = None,
        note: str | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(**kwargs)
        self.activity_id = activity_id
        self.started_at = started_at
        self.ended_at = ended_at
        self.note = note
