import os
import json
import httpx
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.environ["ERPNEXT_URL"].rstrip("/")
AUTH_HEADER = f"token {os.environ['ERPNEXT_API_KEY']}:{os.environ['ERPNEXT_API_SECRET']}"


class ERPNextError(Exception):
    pass


class ERPNextClient:
    def __init__(self):
        self.client = httpx.Client(
            base_url=BASE_URL,
            headers={"Authorization": AUTH_HEADER},
            timeout=30.0,
        )

    def _check(self, r: httpx.Response):
        if r.status_code >= 400:
            try:
                body = r.json()
                msg = body.get("exception") or body.get("message") or r.text
            except Exception:
                msg = r.text
            raise ERPNextError(f"ERPNext API error ({r.status_code}): {msg}")
        return r

    def get_list(self, doctype: str, filters=None, fields=None, limit: int = 20):
        params = {"limit_page_length": limit}
        if filters:
            params["filters"] = json.dumps(filters)
        if fields:
            params["fields"] = json.dumps(fields)
        r = self._check(self.client.get(f"/api/resource/{doctype}", params=params))
        return r.json().get("data", [])

    def get_doc(self, doctype: str, name: str):
        r = self._check(self.client.get(f"/api/resource/{doctype}/{name}"))
        return r.json().get("data", {})

    def create_doc(self, doctype: str, payload: dict):
        r = self._check(self.client.post(f"/api/resource/{doctype}", json=payload))
        return r.json().get("data", {})