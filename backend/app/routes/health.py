from flask import Blueprint

bp = Blueprint("health", __name__)


@bp.get("/api/health")
def health():
    return {"status": "ok"}
