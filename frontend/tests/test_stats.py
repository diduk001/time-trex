import responses

from app.stats.routes import _norm

BASE = "http://backend.test"


def test_norm():
    assert _norm("2026-06-20", "fb") == "2026-06-20T00:00:00Z"
    assert _norm("2026-06-20T09:00", "fb") == "2026-06-20T09:00:00Z"
    assert _norm("", "fb") == "fb"


def test_stats_require_login(client):
    resp = client.get("/stats")
    assert resp.status_code == 302
    assert resp.headers["Location"] == "/login"


@responses.activate
def test_stats_renders_with_embedded_json(auth_client):
    responses.add(
        responses.GET, f"{BASE}/api/stats/summary",
        json={"from": None, "to": None, "total_seconds": 3600,
              "by_activity": [{"activity_id": 1, "name": "Work", "color": "#3b82f6",
                               "total_seconds": 3600, "entry_count": 1}]},
        status=200,
    )
    responses.add(
        responses.GET, f"{BASE}/api/stats/timeline",
        json={"group_by": "day", "buckets": [
            {"period": "2026-06-20", "total_seconds": 3600, "by_activity": []},
        ]},
        status=200,
    )
    resp = auth_client.get("/stats")
    assert resp.status_code == 200
    assert b"summary-data" in resp.data
    assert b"timeline-data" in resp.data
    assert b"Work" in resp.data
    assert b"2026-06-20" in resp.data


@responses.activate
def test_stats_forwards_params(auth_client):
    responses.add(responses.GET, f"{BASE}/api/stats/summary", json={"by_activity": []}, status=200)
    responses.add(responses.GET, f"{BASE}/api/stats/timeline", json={"buckets": []}, status=200)
    auth_client.get("/stats?from=2026-06-01&to=2026-06-08&group_by=week")
    summary_call = next(c for c in responses.calls if "summary" in c.request.url)
    timeline_call = next(c for c in responses.calls if "timeline" in c.request.url)
    assert "from=2026-06-01T00%3A00%3A00Z" in summary_call.request.url
    assert "group_by=week" in timeline_call.request.url
