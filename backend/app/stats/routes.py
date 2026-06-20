from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.stats import service
from app.utils import current_user_id, json_response, query_dt, query_int

bp = Blueprint("stats", __name__, url_prefix="/api/stats")


@bp.get("/summary")
@jwt_required()
def summary():
    result = service.summary(
        current_user_id(), query_dt("from"), query_dt("to"), query_int("activity_id")
    )
    return json_response(result)


@bp.get("/timeline")
@jwt_required()
def timeline():
    result = service.timeline(
        current_user_id(),
        query_dt("from"),
        query_dt("to"),
        request.args.get("group_by", "day"),
        query_int("activity_id"),
    )
    return json_response(result)
