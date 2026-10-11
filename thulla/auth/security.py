"""Password hashing and signed session tokens.

Uses Argon2id (argon2-cffi) when installed (it is in requirements.txt). If it is
missing, falls back to stdlib scrypt so the app/tests still run. Hash strings
are self-describing, so both formats verify.
"""
from __future__ import annotations
import base64
import hashlib
import hmac
import os
import secrets
import time

try:
    from argon2 import PasswordHasher
    from argon2.exceptions import VerifyMismatchError, InvalidHashError
    _ph = PasswordHasher()
except Exception:  # pragma: no cover
    _ph = None

_SCRYPT_N, _SCRYPT_R, _SCRYPT_P = 2 ** 14, 8, 1


def hash_secret(secret: str) -> str:
    if _ph is not None:
        return _ph.hash(secret)
    salt = os.urandom(16)
    dk = hashlib.scrypt(secret.encode(), salt=salt, n=_SCRYPT_N, r=_SCRYPT_R, p=_SCRYPT_P)
    return "scrypt$" + base64.b64encode(salt).decode() + "$" + base64.b64encode(dk).decode()


def verify_secret(secret: str, stored: str) -> bool:
    try:
        if stored.startswith("scrypt$"):
            _, s, d = stored.split("$")
            dk = hashlib.scrypt(secret.encode(), salt=base64.b64decode(s),
                                n=_SCRYPT_N, r=_SCRYPT_R, p=_SCRYPT_P)
            return hmac.compare_digest(dk, base64.b64decode(d))
        if _ph is not None:
            return _ph.verify(stored, secret)
    except Exception:
        return False
    return False


def normalize_answer(answer: str) -> str:
    return " ".join(answer.strip().lower().split())


def get_secret_key() -> bytes:
    """Signing key from THULLA_SECRET (required in production)."""
    key = os.environ.get("THULLA_SECRET")
    if not key:
        # Dev fallback: random per process. Tokens won't verify across processes,
        # so set THULLA_SECRET when running the online server separately.
        global _DEV_KEY
        try:
            return _DEV_KEY
        except NameError:
            _DEV_KEY = secrets.token_bytes(32)
            return _DEV_KEY
    return key.encode()


def make_token(user_id: int, ttl: int = 8 * 3600, key: bytes | None = None) -> str:
    key = key or get_secret_key()
    payload = f"{user_id}|{int(time.time()) + ttl}"
    sig = hmac.new(key, payload.encode(), hashlib.sha256).hexdigest()
    return base64.urlsafe_b64encode(f"{payload}|{sig}".encode()).decode()


def verify_token(token: str, key: bytes | None = None):
    """Return user_id or None."""
    key = key or get_secret_key()
    try:
        raw = base64.urlsafe_b64decode(token.encode())
        if base64.urlsafe_b64encode(raw).decode() != token:   # reject non-canonical encodings
            return None
        uid, exp, sig = raw.decode().split("|")
        good = hmac.new(key, f"{uid}|{exp}".encode(), hashlib.sha256).hexdigest()
        if hmac.compare_digest(sig, good) and int(exp) > time.time():
            return int(uid)
    except Exception:
        pass
    return None
