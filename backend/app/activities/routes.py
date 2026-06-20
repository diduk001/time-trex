from flask import Blueprint
from flask_jwt_extended import jwt_required

from app import schemas
from app.activities import service
from app.utils import current_user_id, json_response, parse_body

bp = Blueprint("activities", __name__, url_prefix="/api/activities")


@bp.get("")
@jwt_required()
def list_activities():
    uid = current_user_id()
    running = service.running_activity_ids(uid)
    items = []
    for activity in service.list_activities(uid):
        out = schemas.ActivityOut.model_validate(activity)
        out.running = activity.id in running
        items.append(out)
    return json_response(items)


@bp.post("")
@jwt_required()
def create_activity():
    data = parse_body(schemas.ActivityCreateIn)
    activity = service.create_activity(current_user_id(), data.name, data.color)
    return json_response(schemas.ActivityOut.model_validate(activity), 201)


@bp.get("/<int:activity_id>")
@jwt_required()
def get_activity(activity_id: int):
    activity = service.get_activity(current_user_id(), activity_id)
    return json_response(schemas.ActivityOut.model_validate(activity))


@bp.patch("/<int:activity_id>")
@jwt_required()
def update_activity(activity_id: int):
    data = parse_body(schemas.ActivityUpdateIn)
    activity = service.update_activity(current_user_id(), activity_id, data)
    return json_response(schemas.ActivityOut.model_validate(activity))


@bp.delete("/<int:activity_id>")
@jwt_required()
def delete_activity(activity_id: int):
    service.delete_activity(current_user_id(), activity_id)
    return "", 204
