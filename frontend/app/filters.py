def fmt_dt(value: str | None) -> str:
    """'2026-06-20T14:30:00Z' -> '2026-06-20 14:30'."""
    if not value:
        return ""
    return value.replace("T", " ").rstrip("Z")[:16]


def fmt_duration(seconds) -> str:
    if seconds is None:
        return "—"
    seconds = int(seconds)
    hours, minutes = divmod(seconds // 60, 60)
    return f"{hours}h {minutes}m"


def dt_input(value: str | None) -> str:
    """'2026-06-20T14:30:00Z' -> '2026-06-20T14:30' for datetime-local inputs."""
    if not value:
        return ""
    return value.rstrip("Z")[:16]
