from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, PlainSerializer

from app.timeutils import isoformat_z, parse_iso, to_naive_utc


def _coerce_utc(value):
    if isinstance(value, str):
        return parse_iso(value)
    if isinstance(value, datetime):
        return to_naive_utc(value)
    return value


UtcDatetime = Annotated[
    datetime,
    BeforeValidator(_coerce_utc),
    PlainSerializer(isoformat_z, return_type=str),
]


class RegisterIn(BaseModel):
    login: str = Field(min_length=3, max_length=80)
    password: str = Field(min_length=8, max_length=128)


class LoginIn(BaseModel):
    login: str
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    login: str
    created_at: UtcDatetime


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


_HEX_COLOR = r"^#[0-9a-fA-F]{6}$"


class ActivityCreateIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    color: str | None = Field(default=None, pattern=_HEX_COLOR)


class ActivityUpdateIn(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    color: str | None = Field(default=None, pattern=_HEX_COLOR)


class ActivityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    color: str | None
    created_at: UtcDatetime
    running: bool = False


class EntryStartIn(BaseModel):
    activity_id: int
    started_at: UtcDatetime | None = None
    note: str | None = Field(default=None, max_length=500)


class EntryStopIn(BaseModel):
    ended_at: UtcDatetime | None = None


class EntryCreateIn(BaseModel):
    activity_id: int
    started_at: UtcDatetime
    ended_at: UtcDatetime
    note: str | None = Field(default=None, max_length=500)


class EntryUpdateIn(BaseModel):
    activity_id: int | None = None
    started_at: UtcDatetime | None = None
    ended_at: UtcDatetime | None = None
    note: str | None = Field(default=None, max_length=500)


class EntryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    activity_id: int
    started_at: UtcDatetime
    ended_at: UtcDatetime | None
    note: str | None
    created_at: UtcDatetime
    duration_seconds: int | None = None
