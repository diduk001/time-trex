from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity
from pydantic import BaseModel

from app.errors import UnprocessableError
from app.timeutils import parse_iso


def parse_body(model_cls):
    return model_cls.model_validate(request.get_json(silent=True) or {})


def json_response(payload, status: int = 200):
    if isinstance(payload, BaseModel):
        payload = payload.model_dump(mode="json")
    elif isinstance(payload, list):
        payload = [p.model_dump(mode="json") if isinstance(p, BaseModel) else p for p in payload]
    return jsonify(payload), status


def current_user_id() -> int:
    return int(get_jwt_identity())


def query_dt(name: str):
    raw = request.args.get(name)
    if raw is None:
        return None
    try:
        return parse_iso(raw)
    except ValueError as exc:
        raise UnprocessableError(f"Invalid datetime for '{name}'") from exc


def query_int(name: str, default=None):
    raw = request.args.get(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise UnprocessableError(f"Invalid integer for '{name}'") from exc
