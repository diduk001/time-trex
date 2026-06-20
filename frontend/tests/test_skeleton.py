from app.backend_client import BackendError
from app.filters import dt_input, fmt_dt, fmt_duration


def test_ping(client):
    resp = client.get("/ping")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}


def test_fmt_dt():
    assert fmt_dt("2026-06-20T14:30:00Z") == "2026-06-20 14:30"
    assert fmt_dt(None) == ""


def test_fmt_duration():
    assert fmt_duration(3660) == "1h 1m"
    assert fmt_duration(None) == "—"


def test_dt_input():
    assert dt_input("2026-06-20T14:30:00Z") == "2026-06-20T14:30"


def test_current_client_uses_session_token(app):
    from flask import session

    from app.security import current_client

    with app.test_request_context():
        session["access_token"] = "tok"
        c = current_client()
        assert c.token == "tok"
        assert c.base_url == "http://backend.test"


def test_backend_error_500_renders_unavailable_page(app, client):
    """Test that BackendError with status 500 renders backend_unavailable page."""

    @app.route("/test_500")
    def test_500_route():
        raise BackendError(500, "internal_error", "Internal server error")

    resp = client.get("/test_500")
    assert resp.status_code == 503


def test_backend_error_503_renders_unavailable_page(app, client):
    """Test that BackendError with status 503 renders backend_unavailable page."""

    @app.route("/test_503")
    def test_503_route():
        raise BackendError(503, "backend_unavailable", "Backend is unavailable")

    resp = client.get("/test_503")
    assert resp.status_code == 503
