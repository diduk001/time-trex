from flask import Blueprint
from flask_jwt_extended import jwt_required

from app import schemas
from app.entries import service
from app.utils import current_user_id, json_response, parse_body

bp = Blueprint("entries", __name__, url_prefix="/api/entries")


def serialize_entry(entry) -> schemas.EntryOut:
    out = schemas.EntryOut.model_validate(entry)
    if entry.ended_at is not None:
        out.duration_seconds = int((entry.ended_at - entry.started_at).total_seconds())
    return out


@bp.post("/start")
@jwt_required()
def start_entry():
    data = parse_body(schemas.EntryStartIn)
    entry = service.start_entry(
        current_user_id(), data.activity_id, data.started_at, data.note
    )
    return json_response(serialize_entry(entry), 201)


@bp.post("/<int:entry_id>/stop")
@jwt_required()
def stop_entry(entry_id: int):
    data = parse_body(schemas.EntryStopIn)
    entry = service.stop_entry(current_user_id(), entry_id, data.ended_at)
    return json_response(serialize_entry(entry))


@bp.post("")
@jwt_required()
def create_entry():
    data = parse_body(schemas.EntryCreateIn)
    entry = service.create_manual(
        current_user_id(), data.activity_id, data.started_at, data.ended_at, data.note
    )
    return json_response(serialize_entry(entry), 201)
