"""FastAPI backend.  Run:  uvicorn thulla.online.server:app --port 8000

Transport is HTTPS-friendly REST + short polling (Streamlit-compatible). Moves
are validated server-side in RoomManager/ThullaGame. Set THULLA_SECRET (same
value as the Streamlit app) so tokens verify across processes.
"""
from __future__ import annotations
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel

from ..auth.security import verify_token
from ..auth.service import AuthService
from .rooms import RoomError, RoomManager

app = FastAPI(title="Thulla server")
manager = RoomManager()
auth = AuthService()


class PlayBody(BaseModel):
    card: str


def current_user(authorization: str = Header(default="")) -> dict:
    token = authorization.removeprefix("Bearer ").strip()
    uid = verify_token(token) if token else None
    user = auth.get_user(uid) if uid else None
    if not user:
        raise HTTPException(401, "Please sign in again.")
    return user


def _run(fn, *a):
    try:
        return fn(*a)
    except RoomError as e:
        raise HTTPException(400, str(e))


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/rooms")
def create_room(u: dict = Depends(current_user)):
    return {"code": manager.create(u["id"], u["nickname"])}


@app.post("/rooms/{code}/join")
def join_room(code: str, u: dict = Depends(current_user)):
    return {"code": _run(manager.join, code, u["id"], u["nickname"])}


@app.post("/rooms/{code}/bot")
def add_bot(code: str, u: dict = Depends(current_user)):
    _run(manager.add_bot, code, u["id"]); return {"ok": True}


@app.post("/rooms/{code}/start")
def start(code: str, u: dict = Depends(current_user)):
    _run(manager.start, code, u["id"]); return {"ok": True}


@app.post("/rooms/{code}/play")
def play(code: str, body: PlayBody, u: dict = Depends(current_user)):
    _run(manager.play, code, u["id"], body.card); return {"ok": True}


@app.post("/rooms/{code}/leave")
def leave(code: str, u: dict = Depends(current_user)):
    _run(manager.leave, code, u["id"]); return {"ok": True}


@app.get("/rooms/{code}/state")
def state(code: str, since: int = 0, u: dict = Depends(current_user)):
    return _run(manager.state, code, u["id"], since)
