def _activity(client, headers, name="Work"):
    return client.post("/api/activities", headers=headers, json={"name": name}).get_json()["id"]


def test_start_entry(client, auth_headers):
    aid = _activity(client, auth_headers)
    resp = client.post("/api/entries/start", headers=auth_headers, json={"activity_id": aid})
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["activity_id"] == aid
    assert body["ended_at"] is None
    assert body["duration_seconds"] is None


def test_start_when_already_running_conflicts(client, auth_headers):
    aid = _activity(client, auth_headers)
    client.post("/api/entries/start", headers=auth_headers, json={"activity_id": aid})
    resp = client.post("/api/entries/start", headers=auth_headers, json={"activity_id": aid})
    assert resp.status_code == 409


def test_two_activities_can_run_concurrently(client, auth_headers):
    a1 = _activity(client, auth_headers, "Work")
    a2 = _activity(client, auth_headers, "Reading")
    r1 = client.post("/api/entries/start", headers=auth_headers, json={"activity_id": a1})
    r2 = client.post("/api/entries/start", headers=auth_headers, json={"activity_id": a2})
    assert r1.status_code == 201
    assert r2.status_code == 201


def test_stop_entry(client, auth_headers):
    aid = _activity(client, auth_headers)
    eid = client.post(
        "/api/entries/start",
        headers=auth_headers,
        json={"activity_id": aid, "started_at": "2026-06-20T10:00:00Z"},
    ).get_json()["id"]
    resp = client.post(
        f"/api/entries/{eid}/stop", headers=auth_headers, json={"ended_at": "2026-06-20T11:00:00Z"}
    )
    assert resp.status_code == 200
    assert resp.get_json()["duration_seconds"] == 3600


def test_stop_already_stopped_conflicts(client, auth_headers):
    aid = _activity(client, auth_headers)
    start = client.post("/api/entries/start", headers=auth_headers, json={"activity_id": aid})
    eid = start.get_json()["id"]
    client.post(f"/api/entries/{eid}/stop", headers=auth_headers, json={})
    resp = client.post(f"/api/entries/{eid}/stop", headers=auth_headers, json={})
    assert resp.status_code == 409


def test_manual_entry_create(client, auth_headers):
    aid = _activity(client, auth_headers)
    resp = client.post(
        "/api/entries",
        headers=auth_headers,
        json={
            "activity_id": aid,
            "started_at": "2026-06-19T09:00:00Z",
            "ended_at": "2026-06-19T10:30:00Z",
        },
    )
    assert resp.status_code == 201
    assert resp.get_json()["duration_seconds"] == 5400


def test_manual_entry_end_before_start_is_422(client, auth_headers):
    aid = _activity(client, auth_headers)
    resp = client.post(
        "/api/entries",
        headers=auth_headers,
        json={
            "activity_id": aid,
            "started_at": "2026-06-19T10:00:00Z",
            "ended_at": "2026-06-19T09:00:00Z",
        },
    )
    assert resp.status_code == 422


def test_start_on_foreign_activity_is_404(client, auth_headers, make_user):
    aid = _activity(client, auth_headers)
    bob = make_user("bob")
    resp = client.post("/api/entries/start", headers=bob, json={"activity_id": aid})
    assert resp.status_code == 404


def test_entries_require_auth(client):
    assert client.post("/api/entries/start", json={"activity_id": 1}).status_code == 401
