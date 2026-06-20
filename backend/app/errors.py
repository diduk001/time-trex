from collections.abc import Mapping

from flask import jsonify
from pydantic import ValidationError
from werkzeug.exceptions import HTTPException

from app.extensions import jwt


class ApiError(Exception):
    status = 500
    code = "internal_error"

    def __init__(self, message: str, *, details: Mapping[str, object] | None = None):
        super().__init__(message)
        self.message = message
        self.details = details


class NotFoundError(ApiError):
    status = 404
    code = "not_found"


class ConflictError(ApiError):
    status = 409
    code = "conflict"


class UnprocessableError(ApiError):
    status = 422
    code = "validation_error"


class AuthError(ApiError):
    status = 401
    code = "auth_error"


def _envelope(
    code: str, message: str, details: Mapping[str, object] | None = None
) -> dict[str, dict[str, object]]:
    error: dict[str, object] = {"code": code, "message": message}
    if details:
        error["details"] = details
    return {"error": error}


def register_error_handlers(app):
    @app.errorhandler(ApiError)
    def _api(err: ApiError):
        return jsonify(_envelope(err.code, err.message, err.details)), err.status

    @app.errorhandler(ValidationError)
    def _pydantic(err: ValidationError):
        details = {".".join(str(p) for p in e["loc"]): e["msg"] for e in err.errors()}
        return jsonify(_envelope("validation_error", "Validation failed", details)), 422

    @app.errorhandler(HTTPException)
    def _http(err: HTTPException):
        description = err.description or err.name
        return jsonify(_envelope(err.name.lower().replace(" ", "_"), description)), err.code

    @app.errorhandler(Exception)
    def _unhandled(err: Exception):
        return jsonify(_envelope("internal_error", "Internal server error")), 500


def register_jwt_handlers():
    @jwt.unauthorized_loader
    def _missing(reason):
        return jsonify(_envelope("auth_error", reason)), 401

    @jwt.invalid_token_loader
    def _invalid(reason):
        return jsonify(_envelope("auth_error", reason)), 401

    @jwt.expired_token_loader
    def _expired(_header, _payload):
        return jsonify(_envelope("auth_error", "Token has expired")), 401
