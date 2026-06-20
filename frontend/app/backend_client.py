import requests


class BackendError(Exception):
    def __init__(self, status: int, code: str, message: str, details: dict | None = None):
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message
        self.details = details


class BackendClient:
    def __init__(self, base_url: str, token: str | None = None, timeout: float = 10):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout

    def _headers(self) -> dict:
        headers = {"Accept": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _request(self, method: str, path: str, *, json=None, params=None):
        url = f"{self.base_url}{path}"
        try:
            resp = requests.request(
                method,
                url,
                json=json,
                params=params,
                headers=self._headers(),
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise BackendError(503, "backend_unavailable", "Backend is unavailable") from exc
        if resp.status_code >= 400:
            self._raise_from_response(resp)
        if resp.status_code == 204 or not resp.content:
            return None
        return resp.json()

    @staticmethod
    def _raise_from_response(resp):
        try:
            err = resp.json().get("error", {})
            code = err.get("code", "error")
            message = err.get("message", "Request failed")
            details = err.get("details")
        except ValueError:
            code, message, details = "error", "Request failed", None
        raise BackendError(resp.status_code, code, message, details)

    # auth
    def register(self, login, password):
        return self._request(
            "POST", "/api/auth/register", json={"login": login, "password": password}
        )

    def login(self, login, password):
        return self._request("POST", "/api/auth/login", json={"login": login, "password": password})

    def get_me(self):
        return self._request("GET", "/api/auth/me")

    # activities
    def list_activities(self):
        return self._request("GET", "/api/activities")

    def create_activity(self, name, color=None):
        payload = {"name": name}
        if color is not None:
            payload["color"] = color
        return self._request("POST", "/api/activities", json=payload)

    def get_activity(self, activity_id):
        return self._request("GET", f"/api/activities/{activity_id}")

    def update_activity(self, activity_id, **fields):
        return self._request("PATCH", f"/api/activities/{activity_id}", json=fields)

    def delete_activity(self, activity_id):
        return self._request("DELETE", f"/api/activities/{activity_id}")

    # entries
    def start_entry(self, activity_id, started_at=None, note=None):
        payload = {"activity_id": activity_id}
        if started_at is not None:
            payload["started_at"] = started_at
        if note is not None:
            payload["note"] = note
        return self._request("POST", "/api/entries/start", json=payload)

    def stop_entry(self, entry_id, ended_at=None):
        payload = {}
        if ended_at is not None:
            payload["ended_at"] = ended_at
        return self._request("POST", f"/api/entries/{entry_id}/stop", json=payload)

    def create_entry(self, activity_id, started_at, ended_at, note=None):
        payload = {"activity_id": activity_id, "started_at": started_at, "ended_at": ended_at}
        if note is not None:
            payload["note"] = note
        return self._request("POST", "/api/entries", json=payload)

    def list_entries(self, **filters):
        params = {k: v for k, v in filters.items() if v is not None}
        return self._request("GET", "/api/entries", params=params)

    def get_entry(self, entry_id):
        return self._request("GET", f"/api/entries/{entry_id}")

    def update_entry(self, entry_id, **fields):
        return self._request("PATCH", f"/api/entries/{entry_id}", json=fields)

    def delete_entry(self, entry_id):
        return self._request("DELETE", f"/api/entries/{entry_id}")

    # stats
    def stats_summary(self, **params):
        params = {k: v for k, v in params.items() if v is not None}
        return self._request("GET", "/api/stats/summary", params=params)

    def stats_timeline(self, **params):
        params = {k: v for k, v in params.items() if v is not None}
        return self._request("GET", "/api/stats/timeline", params=params)
