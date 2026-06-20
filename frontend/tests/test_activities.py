import responses

BASE = "http://backend.test"


def test_activities_require_login(client):
    resp = client.get("/activities")
    assert resp.status_code == 302
    assert resp.headers["Location"] == "/login"


@responses.activate
def test_index_lists_activities(auth_client):
    responses.add(
        responses.GET, f"{BASE}/api/activities",
        json=[{"id": 1, "name": "Work", "color": "#3b82f6", "running": True}], status=200,
    )
    resp = auth_client.get("/activities")
    assert resp.status_code == 200
    assert b"Work" in resp.data
    assert b"running" in resp.data


@responses.activate
def test_create_posts_to_backend(auth_client):
    responses.add(
        responses.POST, f"{BASE}/api/activities",
        json={"id": 2, "name": "Reading"}, status=201,
    )
    resp = auth_client.post("/activities", data={"name": "Reading", "color": "#abcdef"})
    assert resp.status_code == 302
    assert resp.headers["Location"] == "/activities"
    import json as _json
    assert _json.loads(responses.calls[0].request.body) == {"name": "Reading", "color": "#abcdef"}


@responses.activate
def test_create_duplicate_flashes(auth_client):
    responses.add(
        responses.POST, f"{BASE}/api/activities",
        json={"error": {"code": "conflict", "message": "Activity name already exists"}}, status=409,
    )
    resp = auth_client.post(
        "/activities", data={"name": "Work"}, headers={"Referer": "/activities"}
    )
    assert resp.status_code == 302
    assert resp.headers["Location"] == "/activities"
    responses.add(responses.GET, f"{BASE}/api/activities", json=[], status=200)
    auth_client.get("/activities")


@responses.activate
def test_edit_renders_form(auth_client):
    responses.add(
        responses.GET, f"{BASE}/api/activities/5",
        json={"id": 5, "name": "Work", "color": "#3b82f6"}, status=200,
    )
    resp = auth_client.get("/activities/5/edit")
    assert resp.status_code == 200
    assert b'value="Work"' in resp.data


@responses.activate
def test_update_posts_to_backend(auth_client):
    responses.add(
        responses.PATCH, f"{BASE}/api/activities/5",
        json={"id": 5, "name": "Deep Work"}, status=200,
    )
    resp = auth_client.post(
        "/activities/5/update", data={"name": "Deep Work", "color": "#3b82f6"}
    )
    assert resp.status_code == 302
    assert resp.headers["Location"] == "/activities"


@responses.activate
def test_delete_posts_to_backend(auth_client):
    responses.add(responses.DELETE, f"{BASE}/api/activities/5", status=204)
    resp = auth_client.post("/activities/5/delete")
    assert resp.status_code == 302
    assert resp.headers["Location"] == "/activities"
