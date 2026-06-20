import pytest

from app import create_app
from app.extensions import db as _db


@pytest.fixture
def app():
    application = create_app("testing")
    with application.app_context():
        _db.create_all()
        yield application
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def _register_and_login(client, login, password):
    client.post("/api/auth/register", json={"login": login, "password": password})
    resp = client.post("/api/auth/login", json={"login": login, "password": password})
    token = resp.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers(client):
    return _register_and_login(client, "alice", "password123")


@pytest.fixture
def make_user(client):
    def _make(login="bob", password="password123"):
        return _register_and_login(client, login, password)

    return _make
