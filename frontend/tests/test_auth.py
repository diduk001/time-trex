import responses

BASE = "http://backend.test"


def test_login_get_renders_form(client):
    resp = client.get("/login")
    assert resp.status_code == 200
    assert b"Log in" in resp.data


@responses.activate
def test_login_success_stores_token_and_redirects(client):
    responses.add(
        responses.POST, f"{BASE}/api/auth/login",
        json={"access_token": "tok123", "token_type": "bearer"}, status=200,
    )
    resp = client.post("/login", data={"login": "alice", "password": "password123"})
    assert resp.status_code == 302
    assert resp.headers["Location"] == "/"
    with client.session_transaction() as sess:
        assert sess["access_token"] == "tok123"


@responses.activate
def test_login_bad_credentials_flashes_and_no_token(client):
    responses.add(
        responses.POST, f"{BASE}/api/auth/login",
        json={"error": {"code": "auth_error", "message": "Invalid login or password"}}, status=401,
    )
    resp = client.post("/login", data={"login": "alice", "password": "wrong"})
    assert resp.status_code == 400
    assert b"Invalid login or password" in resp.data
    with client.session_transaction() as sess:
        assert "access_token" not in sess


@responses.activate
def test_register_auto_logs_in(client):
    responses.add(
        responses.POST, f"{BASE}/api/auth/register", json={"id": 1, "login": "bob"}, status=201
    )
    responses.add(
        responses.POST, f"{BASE}/api/auth/login",
        json={"access_token": "tok456", "token_type": "bearer"}, status=200,
    )
    resp = client.post("/register", data={"login": "bob", "password": "password123"})
    assert resp.status_code == 302
    assert resp.headers["Location"] == "/"
    with client.session_transaction() as sess:
        assert sess["access_token"] == "tok456"


@responses.activate
def test_register_duplicate_login_flashes(client):
    responses.add(
        responses.POST, f"{BASE}/api/auth/register",
        json={"error": {"code": "conflict", "message": "Login already taken"}}, status=409,
    )
    resp = client.post("/register", data={"login": "bob", "password": "password123"})
    assert resp.status_code == 400
    assert b"Login already taken" in resp.data


def test_logout_clears_session(auth_client):
    resp = auth_client.post("/logout")
    assert resp.status_code == 302
    assert resp.headers["Location"] == "/login"
    with auth_client.session_transaction() as sess:
        assert "access_token" not in sess
