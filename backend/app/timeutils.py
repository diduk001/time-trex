from datetime import UTC, datetime


def utcnow() -> datetime:
    """Naive UTC 'now' — SQLite stores naive datetimes."""
    return datetime.now(UTC).replace(tzinfo=None)


def to_naive_utc(dt: datetime) -> datetime:
    if dt.tzinfo is not None:
        dt = dt.astimezone(UTC).replace(tzinfo=None)
    return dt


def parse_iso(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return to_naive_utc(dt)


def isoformat_z(dt: datetime) -> str:
    return dt.replace(microsecond=0).isoformat() + "Z"
