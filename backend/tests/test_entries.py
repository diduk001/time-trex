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


def test_list_entries_newest_first(client, auth_headers):
    aid = _activity(client, auth_headers)
    client.post(
        "/api/entries",
        headers=auth_headers,
        json={
            "activity_id": aid,
            "started_at": "2026-06-18T09:00:00Z",
            "ended_at": "2026-06-18T10:00:00Z",
        },
    )
    client.post(
        "/api/entries",
        headers=auth_headers,
        json={
            "activity_id": aid,
            "started_at": "2026-06-19T09:00:00Z",
            "ended_at": "2026-06-19T10:00:00Z",
        },
    )
    resp = client.get("/api/entries", headers=auth_headers)
    assert resp.status_code == 200
    starts = [e["started_at"] for e in resp.get_json()]
    assert starts == ["2026-06-19T09:00:00Z", "2026-06-18T09:00:00Z"]


def test_list_entries_filter_by_activity(client, auth_headers):
    a1 = _activity(client, auth_headers, "Work")
    a2 = _activity(client, auth_headers, "Reading")
    client.post("/api/entries/start", headers=auth_headers, json={"activity_id": a1})
    client.post("/api/entries/start", headers=auth_headers, json={"activity_id": a2})
    resp = client.get(f"/api/entries?activity_id={a1}", headers=auth_headers)
    assert [e["activity_id"] for e in resp.get_json()] == [a1]


def test_list_entries_filter_running(client, auth_headers):
    aid = _activity(client, auth_headers)
    client.post(
        "/api/entries",
        headers=auth_headers,
        json={
            "activity_id": aid,
            "started_at": "2026-06-18T09:00:00Z",
            "ended_at": "2026-06-18T10:00:00Z",
        },
    )
    client.post("/api/entries/start", headers=auth_headers, json={"activity_id": aid})
    resp = client.get("/api/entries?running=true", headers=auth_headers)
    assert all(e["ended_at"] is None for e in resp.get_json())
    assert len(resp.get_json()) == 1


def test_patch_entry_edits_times(client, auth_headers):
    aid = _activity(client, auth_headers)
    eid = client.post(
        "/api/entries",
        headers=auth_headers,
        json={
            "activity_id": aid,
            "started_at": "2026-06-19T09:00:00Z",
            "ended_at": "2026-06-19T10:00:00Z",
        },
    ).get_json()["id"]
    resp = client.patch(
        f"/api/entries/{eid}", headers=auth_headers, json={"ended_at": "2026-06-19T11:00:00Z"}
    )
    assert resp.status_code == 200
    assert resp.get_json()["duration_seconds"] == 7200


def test_patch_entry_invalid_range_is_422(client, auth_headers):
    aid = _activity(client, auth_headers)
    eid = client.post(
        "/api/entries",
        headers=auth_headers,
        json={
            "activity_id": aid,
            "started_at": "2026-06-19T09:00:00Z",
            "ended_at": "2026-06-19T10:00:00Z",
        },
    ).get_json()["id"]
    resp = client.patch(
        f"/api/entries/{eid}", headers=auth_headers, json={"started_at": "2026-06-19T12:00:00Z"}
    )
    assert resp.status_code == 422


def test_patch_entry_reassign_activity(client, auth_headers):
    a1 = _activity(client, auth_headers, "Work")
    a2 = _activity(client, auth_headers, "Reading")
    eid = client.post(
        "/api/entries/start", headers=auth_headers, json={"activity_id": a1}
    ).get_json()["id"]
    resp = client.patch(f"/api/entries/{eid}", headers=auth_headers, json={"activity_id": a2})
    assert resp.status_code == 200
    assert resp.get_json()["activity_id"] == a2


def test_delete_entry(client, auth_headers):
    aid = _activity(client, auth_headers)
    eid = client.post(
        "/api/entries/start", headers=auth_headers, json={"activity_id": aid}
    ).get_json()["id"]
    assert client.delete(f"/api/entries/{eid}", headers=auth_headers).status_code == 204
    assert client.get(f"/api/entries/{eid}", headers=auth_headers).status_code == 404


def test_entry_isolation_between_users(client, auth_headers, make_user):
    aid = _activity(client, auth_headers)
    eid = client.post(
        "/api/entries/start", headers=auth_headers, json={"activity_id": aid}
    ).get_json()["id"]
    bob = make_user("bob")
    assert client.get(f"/api/entries/{eid}", headers=bob).status_code == 404
    assert client.get("/api/entries", headers=bob).get_json() == []


def test_list_entries_with_offset_zero(client, auth_headers):
    aid = _activity(client, auth_headers)
    # Create 3 entries
    for i in range(3):
        client.post(
            "/api/entries",
            headers=auth_headers,
            json={
                "activity_id": aid,
                "started_at": f"2026-06-{20 - i}T09:00:00Z",
                "ended_at": f"2026-06-{20 - i}T10:00:00Z",
            },
        )
    # With offset=0, should return all 3
    resp = client.get("/api/entries?offset=0", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.get_json()) == 3


def test_list_entries_with_limit_zero(client, auth_headers):
    aid = _activity(client, auth_headers)
    # Create 2 entries
    for i in range(2):
        client.post(
            "/api/entries",
            headers=auth_headers,
            json={
                "activity_id": aid,
                "started_at": f"2026-06-{20 - i}T09:00:00Z",
                "ended_at": f"2026-06-{20 - i}T10:00:00Z",
            },
        )
    # With limit=0, should return empty list
    resp = client.get("/api/entries?limit=0", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.get_json()) == 0


def test_list_entries_with_offset_and_limit(client, auth_headers):
    aid = _activity(client, auth_headers)
    # Create 5 entries
    for i in range(5):
        client.post(
            "/api/entries",
            headers=auth_headers,
            json={
                "activity_id": aid,
                "started_at": f"2026-06-{25 - i}T09:00:00Z",
                "ended_at": f"2026-06-{25 - i}T10:00:00Z",
            },
        )
    # With offset=2 and limit=2, should return entries 2 and 3 (0-indexed)
    resp = client.get("/api/entries?offset=2&limit=2", headers=auth_headers)
    assert resp.status_code == 200
    entries = resp.get_json()
    assert len(entries) == 2
