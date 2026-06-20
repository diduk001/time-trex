import json as _json

import responses

from app.tracking.routes import _to_utc_iso

BASE = "http://backend.test"


def test_to_utc_iso():
    assert _to_utc_iso("2026-06-20T14:30") == "2026-06-20T14:30:00Z"
    assert _to_utc_iso("") is None
    assert _to_utc_iso("2026-06-20T14:30:00Z") == "2026-06-20T14:30:00Z"


def test_index_requires_login(client):
    resp = client.get("/")
    assert resp.status_code == 302
    assert resp.headers["Location"] == "/login"


@responses.activate
def test_index_renders_entries(auth_client):
    responses.add(
        responses.GET, f"{BASE}/api/activities",
        json=[{"id": 1, "name": "Work", "color": None, "running": False}], status=200,
    )
    responses.add(
        responses.GET, f"{BASE}/api/entries",
        json=[{"id": 9, "activity_id": 1, "started_at": "2026-06-20T09:00:00Z",
               "ended_at": "2026-06-20T10:00:00Z", "note": "stuff", "duration_seconds": 3600}],
        status=200,
    )
    resp = auth_client.get("/")
    assert resp.status_code == 200
    assert b"Work" in resp.data
    assert b"1h 0m" in resp.data


@responses.activate
def test_start_posts_to_backend(auth_client):
    responses.add(responses.POST, f"{BASE}/api/entries/start", json={"id": 1}, status=201)
    resp = auth_client.post("/entries/start", data={"activity_id": "3"})
    assert resp.status_code == 302
    assert resp.headers["Location"] == "/"
    assert _json.loads(responses.calls[0].request.body) == {"activity_id": 3}


@responses.activate
def test_stop_posts_to_backend(auth_client):
    responses.add(responses.POST, f"{BASE}/api/entries/7/stop", json={"id": 7}, status=200)
    resp = auth_client.post("/entries/7/stop")
    assert resp.status_code == 302
    assert resp.headers["Location"] == "/"


@responses.activate
def test_manual_create_converts_times(auth_client):
    responses.add(responses.POST, f"{BASE}/api/entries", json={"id": 1}, status=201)
    resp = auth_client.post(
        "/entries",
        data={
            "activity_id": "2",
            "started_at": "2026-06-19T09:00",
            "ended_at": "2026-06-19T10:30",
            "note": "x",
        },
    )
    assert resp.status_code == 302
    body = _json.loads(responses.calls[0].request.body)
    assert body == {
        "activity_id": 2,
        "started_at": "2026-06-19T09:00:00Z",
        "ended_at": "2026-06-19T10:30:00Z",
        "note": "x",
    }


@responses.activate
def test_edit_renders_form(auth_client):
    responses.add(
        responses.GET, f"{BASE}/api/entries/9",
        json={"id": 9, "activity_id": 1, "started_at": "2026-06-20T09:00:00Z",
              "ended_at": "2026-06-20T10:00:00Z", "note": "n", "duration_seconds": 3600},
        status=200,
    )
    responses.add(
        responses.GET, f"{BASE}/api/activities",
        json=[{"id": 1, "name": "Work"}], status=200,
    )
    resp = auth_client.get("/entries/9/edit")
    assert resp.status_code == 200
    assert b'value="2026-06-20T09:00"' in resp.data


@responses.activate
def test_update_posts_to_backend(auth_client):
    responses.add(responses.PATCH, f"{BASE}/api/entries/9", json={"id": 9}, status=200)
    resp = auth_client.post(
        "/entries/9/update",
        data={
            "activity_id": "1",
            "started_at": "2026-06-20T09:00",
            "ended_at": "2026-06-20T11:00",
            "note": "",
        },
    )
    assert resp.status_code == 302
    body = _json.loads(responses.calls[0].request.body)
    assert body["started_at"] == "2026-06-20T09:00:00Z"
    assert body["ended_at"] == "2026-06-20T11:00:00Z"


@responses.activate
def test_delete_posts_to_backend(auth_client):
    responses.add(responses.DELETE, f"{BASE}/api/entries/9", status=204)
    resp = auth_client.post("/entries/9/delete")
    assert resp.status_code == 302
    assert resp.headers["Location"] == "/"
