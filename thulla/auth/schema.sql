-- SQLite schema (also applied automatically by AuthService)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE COLLATE NOCASE,
    nickname TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    security_question TEXT NOT NULL,
    answer_hash TEXT NOT NULL,
    created_at INTEGER NOT NULL
);
-- Failed attempts for rate limiting: kind = 'login' | 'recovery'
CREATE TABLE IF NOT EXISTS attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL COLLATE NOCASE,
    kind TEXT NOT NULL,
    at INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_attempts ON attempts(username, kind, at);
-- One-time reset sessions (only a hash of the token is stored)
CREATE TABLE IF NOT EXISTS reset_sessions (
    token_hash TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    expires_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS stats (
    user_id INTEGER PRIMARY KEY,
    games_played INTEGER NOT NULL DEFAULT 0,
    wins INTEGER NOT NULL DEFAULT 0,
    thulla_count INTEGER NOT NULL DEFAULT 0
);
