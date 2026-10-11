"""Registration, login, and security-question password recovery (SQLite / Turso)."""
from __future__ import annotations
import hashlib
import os
import re
import secrets
import sqlite3
import time
from pathlib import Path

from .security import hash_secret, normalize_answer, verify_secret

SCHEMA = (Path(__file__).parent / "schema.sql").read_text()
USERNAME_RE = re.compile(r"^[A-Za-z0-9_]{3,20}$")
MAX_FAILS, WINDOW, LOCKOUT = 5, 15 * 60, 5 * 60   # 5 fails / 15 min -> locked for 5 min
RESET_TTL = 10 * 60
GENERIC_FAIL = "Invalid username or password."
GENERIC_RECOVERY_FAIL = "Recovery failed. Check your details and try again."
SECURITY_QUESTIONS = [
    "What was the name of your first school?",
    "What is your favourite childhood game?",
    "What is the name of the street you grew up on?",
    "What was the name of your first pet?",
    "What is your favourite dish at a family gathering?",
]


class AuthError(Exception):
    """Safe-to-display error message."""


def _th(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


class AuthService:
    def __init__(self, db_path: str | None = None, clock=time.time):
        self.turso_url = os.environ.get("TURSO_DATABASE_URL")
        self.turso_token = os.environ.get("TURSO_AUTH_TOKEN")
        
        if not self.turso_url:
            self.db_path = db_path or os.environ.get("THULLA_DB", "data/thulla.db")
            if self.db_path != ":memory:":
                Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.clock = clock
        self._mem = sqlite3.connect(":memory:") if (db_path == ":memory:") else None
        
        with self._db() as c:
            c.executescript(SCHEMA)

    def _db(self):
        if self._mem:
            conn = self._mem
            conn.row_factory = sqlite3.Row
            return _Ctx(conn, keep=True)
            
        if self.turso_url:
            import libsql_client
            # Turso remote connection wrapper for sqlite3-like behavior
            url = self.turso_url.replace("libsql://", "https://")
            client = libsql_client.create_client_sync(url=url, auth_token=self.turso_token)
            return _TursoCtx(client)
        else:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return _Ctx(conn, keep=False)

    # ------------------------------------------------------------ rate limit
    def _locked(self, c, username: str, kind: str) -> bool:
        now = int(self.clock())
        rows = c.execute("SELECT at FROM attempts WHERE username=? AND kind=? AND at>? ORDER BY at",
                         (username, kind, now - WINDOW)).fetchall()
        return len(rows) >= MAX_FAILS and now - rows[-1]["at"] < LOCKOUT

    def _fail(self, c, username, kind):
        c.execute("INSERT INTO attempts(username,kind,at) VALUES(?,?,?)",
                  (username, kind, int(self.clock())))

    def _clear(self, c, username, kind=None):
        if kind:
            c.execute("DELETE FROM attempts WHERE username=? AND kind=?", (username, kind))
        else:
            c.execute("DELETE FROM attempts WHERE username=?", (username,))

    # ------------------------------------------------------------ register
    @staticmethod
    def check_password_strength(pw: str) -> None:
        if len(pw) < 8:
            raise AuthError("Password must be at least 8 characters.")
        if pw.lower() in {"password", "12345678", "qwerty123", "password1"}:
            raise AuthError("That password is too common.")

    def register(self, username, nickname, password, confirm, question, answer, answer_confirm) -> int:
        username, nickname = username.strip(), nickname.strip()
        if not USERNAME_RE.match(username):
            raise AuthError("Username must be 3-20 letters, numbers or underscores.")
        if not (1 <= len(nickname) <= 20):
            raise AuthError("Nickname must be 1-20 characters.")
        if password != confirm:
            raise AuthError("Passwords do not match.")
        self.check_password_strength(password)
        if question not in SECURITY_QUESTIONS:
            raise AuthError("Please choose a security question from the list.")
        a = normalize_answer(answer)
        if len(a) < 3:
            raise AuthError("Recovery answer is too short.")
        if a != normalize_answer(answer_confirm):
            raise AuthError("Recovery answers do not match.")
        with self._db() as c:
            try:
                cur = c.execute(
                    "INSERT INTO users(username,nickname,password_hash,security_question,answer_hash,created_at)"
                    " VALUES(?,?,?,?,?,?)",
                    (username, nickname, hash_secret(password), question, hash_secret(a), int(self.clock())))
            except Exception:
                raise AuthError("That username is already taken.")
            c.execute("INSERT INTO stats(user_id) VALUES(?)", (cur.lastrowid,))
            return cur.lastrowid

    # ------------------------------------------------------------ login
    def login(self, username: str, password: str) -> dict:
        username = username.strip()
        with self._db() as c:
            if self._locked(c, username, "login"):
                raise AuthError("Too many attempts. Please wait a few minutes and try again.")
            row = c.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
            ok = verify_secret(password, row["password_hash"]) if row else \
                verify_secret(password, hash_secret("dummy-timing-equaliser"))
            if not row or not ok:
                self._fail(c, username, "login")
                raise AuthError(GENERIC_FAIL)
            self._clear(c, username, "login")
            return {"id": row["id"], "username": row["username"], "nickname": row["nickname"]}

    # ------------------------------------------------------------ recovery
    def start_recovery(self, username: str) -> str:
        username = username.strip()
        with self._db() as c:
            row = c.execute("SELECT security_question FROM users WHERE username=?", (username,)).fetchone()
        if row:
            return row["security_question"]
        idx = int(hashlib.sha256(username.lower().encode()).hexdigest(), 16) % len(SECURITY_QUESTIONS)
        return SECURITY_QUESTIONS[idx]

    def verify_recovery(self, username: str, answer: str) -> str:
        username = username.strip()
        with self._db() as c:
            if self._locked(c, username, "recovery"):
                raise AuthError("Too many attempts. Please wait a few minutes and try again.")
            row = c.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
            ok = verify_secret(normalize_answer(answer), row["answer_hash"]) if row else \
                verify_secret("x", hash_secret("dummy-timing-equaliser"))
            if not row or not ok:
                self._fail(c, username, "recovery")
                raise AuthError(GENERIC_RECOVERY_FAIL)
            self._clear(c, username, "recovery")
            c.execute("DELETE FROM reset_sessions WHERE user_id=?", (row["id"],))
            token = secrets.token_urlsafe(32)
            c.execute("INSERT INTO reset_sessions VALUES(?,?,?)",
                      (_th(token), row["id"], int(self.clock()) + RESET_TTL))
            return token

    def reset_password(self, token: str, new_password: str, confirm: str) -> None:
        if new_password != confirm:
            raise AuthError("Passwords do not match.")
        self.check_password_strength(new_password)
        with self._db() as c:
            r = c.execute("SELECT * FROM reset_sessions WHERE token_hash=?", (_th(token),)).fetchone()
            if not r or r["expires_at"] < self.clock():
                raise AuthError("Reset session expired. Please start again.")
            c.execute("UPDATE users SET password_hash=? WHERE id=?", (hash_secret(new_password), r["user_id"]))
            c.execute("DELETE FROM reset_sessions WHERE user_id=?", (r["user_id"],))
            name = c.execute("SELECT username FROM users WHERE id=?", (r["user_id"],)).fetchone()["username"]
            self._clear(c, name)

    def get_user(self, user_id: int):
        with self._db() as c:
            r = c.execute("SELECT id,username,nickname FROM users WHERE id=?", (user_id,)).fetchone()
            return dict(r) if r else None

    def record_result(self, user_id: int, won: bool, was_thulla: bool) -> None:
        with self._db() as c:
            c.execute("UPDATE stats SET games_played=games_played+1, wins=wins+?, thulla_count=thulla_count+?"
                      " WHERE user_id=?", (int(won), int(was_thulla), user_id))

    def get_stats(self, user_id: int) -> dict:
        with self._db() as c:
            r = c.execute("SELECT games_played,wins,thulla_count FROM stats WHERE user_id=?", (user_id,)).fetchone()
            return dict(r) if r else {"games_played": 0, "wins": 0, "thulla_count": 0}


class _Ctx:
    def __init__(self, conn, keep):
        self.conn, self.keep = conn, keep

    def __enter__(self):
        return self.conn

    def __exit__(self, et, ev, tb):
        ok = et is None or issubclass(et, AuthError)
        (self.conn.commit if ok else self.conn.rollback)()
        if not self.keep:
            self.conn.close()


class _TursoCursor:
    def __init__(self, client):
        self.client = client
        self.lastrowid = None

    def execute(self, sql, params=()):
        # Convert sqlite ? placeholders if needed, standard libsql supports them
        res = self.client.execute(sql, params)
        self.lastrowid = res.last_insert_rowid
        self._res = res
        return self

    def fetchone(self):
        rows = self._res.rows
        if not rows:
            return None
        cols = self._res.columns
        return dict(zip(cols, rows[0]))

    def fetchall(self):
        rows = self._res.rows
        if not rows:
            return []
        cols = self._res.columns
        return [dict(zip(cols, r)) for r in rows]

    def executescript(self, script):
        for stmt in script.split(";"):
            if stmt.strip():
                self.client.execute(stmt)
        return self


class _TursoCtx:
    def __init__(self, client):
        self.client = client

    def __enter__(self):
        return self

    def execute(self, sql, params=()):
        return _TursoCursor(self.client).execute(sql, params)

    def __exit__(self, et, ev, tb):
        # libsql-client handles auto-commits per statement or transaction context
        pass
