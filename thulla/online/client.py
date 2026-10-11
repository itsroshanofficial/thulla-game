"""Tiny HTTP client used by the Streamlit app."""
from __future__ import annotations
import requests


class OnlineError(Exception):
    pass


class OnlineClient:
    def __init__(self, base_url: str, token: str, timeout: float = 8.0):
        self.base, self.timeout = base_url.rstrip("/"), timeout
        self.h = {"Authorization": f"Bearer {token}"}

    def _call(self, method, path, **kw):
        try:
            r = requests.request(method, self.base + path, headers=self.h, timeout=self.timeout, **kw)
        except requests.RequestException:
            raise OnlineError("Cannot reach the game server.")
        if r.status_code != 200:
            try:
                msg = r.json().get("detail", "Request failed.")
            except Exception:
                msg = "Request failed."
            raise OnlineError(msg)
        return r.json()

    def create_room(self): return self._call("POST", "/rooms")["code"]
    def join(self, code): return self._call("POST", f"/rooms/{code}/join")["code"]
    def add_bot(self, code): self._call("POST", f"/rooms/{code}/bot")
    def start(self, code): self._call("POST", f"/rooms/{code}/start")
    def play(self, code, card): self._call("POST", f"/rooms/{code}/play", json={"card": card})
    def leave(self, code): self._call("POST", f"/rooms/{code}/leave")
    def state(self, code, since=0): return self._call("GET", f"/rooms/{code}/state", params={"since": since})
