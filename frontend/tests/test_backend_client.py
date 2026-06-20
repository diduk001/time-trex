import pytest
import responses

from app.backend_client import BackendClient, BackendError

BASE = "http://backend.test"


def _client(token=None):
    return BackendClient(BASE, token=token, timeout=5)


@responses.activate
def test_login_posts_credentials_without_auth_header():
    responses.add(
        responses.POST,
        f"{BASE}/api/auth/login",
        json={"access_token": "abc", "token_type": "bearer"},
        status=200,
    )
    result = _client().login("alice", "pw")
    assert result["access_token"] == "abc"
    assert responses.calls[0].request.headers.get("Authorization") is None


@responses.activate
def test_authorized_call_sends_bearer():
    responses.add(responses.GET, f"{BASE}/api/auth/me", json={"id": 1, "login": "a"}, status=200)
    _client("tok").get_me()
    assert responses.calls[0].request.headers["Authorization"] == "Bearer tok"


@responses.activate
def test_error_response_raises_backend_error():
    responses.add(
        responses.POST,
        f"{BASE}/api/auth/login",
        json={"error": {"code": "auth_error", "message": "Invalid login or password"}},
        status=401,
    )
    with pytest.raises(BackendError) as exc:
        _client().login("x", "y")
    assert exc.value.status == 401
    assert exc.value.code == "auth_error"
    assert "Invalid" in exc.value.message


@responses.activate
def test_delete_returns_none_on_204():
    responses.add(responses.DELETE, f"{BASE}/api/activities/5", status=204)
    assert _client("t").delete_activity(5) is None


@responses.activate
def test_network_failure_raises_503():
    responses.add(responses.GET, f"{BASE}/api/activities", body=responses.ConnectionError())
    with pytest.raises(BackendError) as exc:
        _client("t").list_activities()
    assert exc.value.status == 503
    assert exc.value.code == "backend_unavailable"


@responses.activate
def test_list_entries_forwards_filters_as_query():
    responses.add(responses.GET, f"{BASE}/api/entries", json=[], status=200)
    _client("t").list_entries(activity_id=3, running="true")
    url = responses.calls[0].request.url
    assert "activity_id=3" in url
    assert "running=true" in url


@responses.activate
def test_create_entry_sends_payload():
    responses.add(responses.POST, f"{BASE}/api/entries", json={"id": 1}, status=201)
    _client("t").create_entry(2, "2026-06-20T09:00:00Z", "2026-06-20T10:00:00Z", note="hi")
    import json as _json

    body = _json.loads(responses.calls[0].request.body)
    assert body == {
        "activity_id": 2,
        "started_at": "2026-06-20T09:00:00Z",
        "ended_at": "2026-06-20T10:00:00Z",
        "note": "hi",
    }
