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
