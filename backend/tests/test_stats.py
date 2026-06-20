def _activity(client, headers, name="Work"):
    return client.post("/api/activities", headers=headers, json={"name": name}).get_json()["id"]


def _manual(client, headers, aid, start, end):
    return client.post(
        "/api/entries",
        headers=headers,
        json={"activity_id": aid, "started_at": start, "ended_at": end},
    )


def test_summary_totals_per_activity(client, auth_headers):
    work = _activity(client, auth_headers, "Work")
    reading = _activity(client, auth_headers, "Reading")
    _manual(client, auth_headers, work, "2026-06-19T09:00:00Z", "2026-06-19T11:00:00Z")  # 2h
    _manual(client, auth_headers, work, "2026-06-19T13:00:00Z", "2026-06-19T14:00:00Z")  # 1h
    _manual(client, auth_headers, reading, "2026-06-19T20:00:00Z", "2026-06-19T20:30:00Z")  # 30m
    resp = client.get("/api/stats/summary", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["total_seconds"] == 3 * 3600 + 1800
    by_id = {b["activity_id"]: b for b in body["by_activity"]}
    assert by_id[work]["total_seconds"] == 3 * 3600
    assert by_id[work]["entry_count"] == 2
    assert by_id[reading]["total_seconds"] == 1800


def test_summary_clips_to_window(client, auth_headers):
    work = _activity(client, auth_headers, "Work")
    _manual(client, auth_headers, work, "2026-06-19T08:00:00Z", "2026-06-19T12:00:00Z")  # 4h
    resp = client.get(
        "/api/stats/summary?from=2026-06-19T10:00:00Z&to=2026-06-19T11:00:00Z",
        headers=auth_headers,
    )
    assert resp.get_json()["total_seconds"] == 3600  # only the 10-11 hour counts


def test_summary_counts_overlapping_entries_separately(client, auth_headers):
    a1 = _activity(client, auth_headers, "Work")
    a2 = _activity(client, auth_headers, "Reading")
    _manual(client, auth_headers, a1, "2026-06-19T09:00:00Z", "2026-06-19T10:00:00Z")
    _manual(client, auth_headers, a2, "2026-06-19T09:30:00Z", "2026-06-19T10:30:00Z")
    # overlapping 09:30-10:00 is counted toward BOTH activities (not deduped)
    resp = client.get("/api/stats/summary", headers=auth_headers)
    assert resp.get_json()["total_seconds"] == 7200


def test_summary_running_entry_counts_to_now(client, auth_headers):
    work = _activity(client, auth_headers, "Work")
    # start in the past, leave running; clipped to `to` we control
    client.post(
        "/api/entries/start",
        headers=auth_headers,
        json={"activity_id": work, "started_at": "2026-06-19T09:00:00Z"},
    )
    resp = client.get(
        "/api/stats/summary?from=2026-06-19T09:00:00Z&to=2026-06-19T10:00:00Z",
        headers=auth_headers,
    )
    assert resp.get_json()["total_seconds"] == 3600


def test_summary_filter_by_activity(client, auth_headers):
    work = _activity(client, auth_headers, "Work")
    reading = _activity(client, auth_headers, "Reading")
    _manual(client, auth_headers, work, "2026-06-19T09:00:00Z", "2026-06-19T10:00:00Z")
    _manual(client, auth_headers, reading, "2026-06-19T09:00:00Z", "2026-06-19T10:00:00Z")
    resp = client.get(f"/api/stats/summary?activity_id={work}", headers=auth_headers)
    assert resp.get_json()["total_seconds"] == 3600


def test_summary_empty(client, auth_headers):
    resp = client.get("/api/stats/summary", headers=auth_headers)
    assert resp.get_json() == {
        "from": None,
        "to": None,
        "total_seconds": 0,
        "by_activity": [],
    }


def test_summary_requires_auth(client):
    assert client.get("/api/stats/summary").status_code == 401
