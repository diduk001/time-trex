import pytest

from app import create_app


@pytest.fixture
def app():
    return create_app("testing")


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_client(app):
    test_client = app.test_client()
    with test_client.session_transaction() as sess:
        sess["access_token"] = "test-token"
    return test_client
