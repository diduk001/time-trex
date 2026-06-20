def _create(client, headers, name="Work", color="#3b82f6"):
    return client.post("/api/activities", headers=headers, json={"name": name, "color": color})


def test_create_activity(client, auth_headers):
    resp = _create(client, auth_headers)
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["name"] == "Work"
    assert body["color"] == "#3b82f6"
    assert body["running"] is False


def test_create_duplicate_name_conflicts(client, auth_headers):
    _create(client, auth_headers)
    resp = _create(client, auth_headers)
    assert resp.status_code == 409


def test_create_invalid_color_is_422(client, auth_headers):
    resp = _create(client, auth_headers, color="blue")
    assert resp.status_code == 422


def test_list_activities(client, auth_headers):
    _create(client, auth_headers, name="Work")
    _create(client, auth_headers, name="Reading")
    resp = client.get("/api/activities", headers=auth_headers)
    assert resp.status_code == 200
    assert {a["name"] for a in resp.get_json()} == {"Work", "Reading"}


def test_get_activity(client, auth_headers):
    aid = _create(client, auth_headers).get_json()["id"]
    resp = client.get(f"/api/activities/{aid}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["id"] == aid


def test_update_activity(client, auth_headers):
    aid = _create(client, auth_headers).get_json()["id"]
    resp = client.patch(f"/api/activities/{aid}", headers=auth_headers, json={"name": "Deep Work"})
    assert resp.status_code == 200
    assert resp.get_json()["name"] == "Deep Work"
    assert resp.get_json()["color"] == "#3b82f6"  # unchanged


def test_delete_activity(client, auth_headers):
    aid = _create(client, auth_headers).get_json()["id"]
    assert client.delete(f"/api/activities/{aid}", headers=auth_headers).status_code == 204
    assert client.get(f"/api/activities/{aid}", headers=auth_headers).status_code == 404


def test_activities_are_isolated_per_user(client, auth_headers, make_user):
    aid = _create(client, auth_headers).get_json()["id"]
    bob = make_user("bob")
    assert client.get(f"/api/activities/{aid}", headers=bob).status_code == 404
    assert client.get("/api/activities", headers=bob).get_json() == []


def test_activities_require_auth(client):
    assert client.get("/api/activities").status_code == 401
