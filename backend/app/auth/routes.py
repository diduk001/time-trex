from flask import Blueprint
from flask_jwt_extended import create_access_token, jwt_required

from app import schemas
from app.auth import service
from app.utils import current_user_id, json_response, parse_body

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@bp.post("/register")
def register():
    data = parse_body(schemas.RegisterIn)
    user = service.register_user(data.login, data.password)
    return json_response(schemas.UserOut.model_validate(user), 201)


@bp.post("/login")
def login():
    data = parse_body(schemas.LoginIn)
    user = service.authenticate(data.login, data.password)
    token = create_access_token(identity=str(user.id))
    return json_response(schemas.TokenOut(access_token=token))


@bp.get("/me")
@jwt_required()
def me():
    user = service.get_user(current_user_id())
    return json_response(schemas.UserOut.model_validate(user))
