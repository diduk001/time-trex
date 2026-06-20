def test_register_returns_user(client):
    resp = client.post("/api/auth/register", json={"login": "alice", "password": "password123"})
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["login"] == "alice"
    assert "id" in body and body["created_at"].endswith("Z")
    assert "password" not in body and "password_hash" not in body


def test_register_duplicate_login_conflicts(client):
    client.post("/api/auth/register", json={"login": "alice", "password": "password123"})
    resp = client.post("/api/auth/register", json={"login": "alice", "password": "password123"})
    assert resp.status_code == 409
    assert resp.get_json()["error"]["code"] == "conflict"


def test_register_short_password_is_422(client):
    resp = client.post("/api/auth/register", json={"login": "alice", "password": "short"})
    assert resp.status_code == 422
    assert resp.get_json()["error"]["code"] == "validation_error"


def test_login_returns_token(client):
    client.post("/api/auth/register", json={"login": "alice", "password": "password123"})
    resp = client.post("/api/auth/login", json={"login": "alice", "password": "password123"})
    assert resp.status_code == 200
    assert resp.get_json()["token_type"] == "bearer"
    assert resp.get_json()["access_token"]


def test_login_wrong_password_is_401(client):
    client.post("/api/auth/register", json={"login": "alice", "password": "password123"})
    resp = client.post("/api/auth/login", json={"login": "alice", "password": "WRONG_pass"})
    assert resp.status_code == 401


def test_login_unknown_user_is_401(client):
    resp = client.post("/api/auth/login", json={"login": "ghost", "password": "password123"})
    assert resp.status_code == 401


def test_me_with_token(client, auth_headers):
    resp = client.get("/api/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["login"] == "alice"


def test_me_without_token_is_401(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401
    assert resp.get_json()["error"]["code"] == "auth_error"


def test_me_with_garbage_token_is_401(client):
    resp = client.get("/api/auth/me", headers={"Authorization": "Bearer not.a.jwt"})
    assert resp.status_code == 401
