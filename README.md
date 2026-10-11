<<<<<<< HEAD
# 🃏 Thulla — Streamlit card game with Punjabi comedy reactions

Free & open-source stack: Python, Streamlit, FastAPI, SQLite, Argon2id.

## Status (honest summary)
| Area | State |
|------|-------|
| Rules engine, AI, offline controller | ✅ Implemented + unit/fuzz tested |
| Voice system (events, cooldown, per-player settings) | ✅ Implemented + unit tested |
| Auth, lockouts, security-question recovery, signed tokens | ✅ Implemented + unit tested |
| Online room logic (validation, hidden hands, bot takeover) | ✅ Implemented + unit tested |
| Streamlit pages & FastAPI wrapper | ⚠️ Written, **not yet run/tested** (needs `pip install -r requirements.txt`) |
| Real audio recordings | ❌ None shipped — uses browser speech until you add files |
| Rules vs. reference videos | ⚠️ **Unconfirmed** — see `docs/RULES_CONFIRMATION.md` |
| Android packaging | Not started (phase 2, see below) |

## Quick start
```bash
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                   # then edit THULLA_SECRET
streamlit run app.py                                   # offline mode works right away
```
**Online mode** (second terminal, same `THULLA_SECRET`):
```bash
export THULLA_SECRET=... THULLA_DB=data/thulla.db     # same values as the app
uvicorn thulla.online.server:app --port 8000
```
Then create an account (Account page), sign in, and use the Online page.

## Tests
```bash
python -m unittest discover -s tests -v
```
Manual checks: `docs/MANUAL_TEST_CHECKLIST.md`.

## Layout
```
app.py                    Streamlit entry
thulla/engine/            rules.py (config), cards.py, game.py  (pure, no UI/DB)
thulla/ai.py              bot logic          thulla/offline.py  offline controller
thulla/voice/             lines.py, manager.py (cooldown/settings), player.py (browser playback)
thulla/auth/              service.py, security.py, schema.sql
thulla/online/            rooms.py (logic), server.py (FastAPI), client.py
thulla/ui/                Streamlit pages
assets/audio/             recordings + licence table
docs/                     rules to confirm, manual checklist
tests/                    unittest suites
```

## Design notes
* **Rules** live only in `engine/`; change `RulesConfig` after you confirm them.
* **Hidden cards**: clients only receive `ThullaGame.view_for(seat)`.
* **Voice**: settings live in each browser session and playback runs in each
  player's own browser, so one player's mute/volume never affects another.
  One line per batch of events, global cooldown, no repeats of the last 4 lines.
* **Passwords & recovery answers**: Argon2id hashes (scrypt fallback if argon2 is
  missing). 5 failures / 15 min → 5 min lockout. Generic errors, decoy question
  for unknown users, one-time 10-min reset token stored hashed.
  ⚠️ Security questions are weaker than email/authenticator recovery.
* **Online transport**: REST + 2-second polling (works with Streamlit and free
  hosts). WebSockets would be lower-latency but are harder to host on free tiers.
  Room state is in server memory (lost on restart) — fine for friends' games.

## Known limitations
* Browsers block sound until the first user interaction; press “Test / unlock sound”.
* Punjabi/Urdu TTS voices are rarely installed → falls back to Hindi/English voices.
  For authentic comedy, add your own recordings (`assets/audio/README.md`).
* `THULLA_SECRET` must be identical for app and server; the SQLite file must be
  readable by both (same machine) — otherwise move accounts to a hosted free DB.
* Free hosts (e.g. Streamlit Community Cloud) run only the Streamlit app, not a
  second FastAPI process. Host the server separately (e.g. a free-tier container
  host), verify its current limits, and use HTTPS. **Multiplayer is untested on
  any hosting environment yet.**
* Per-user voice preferences are not saved between sessions.

## Deployment outline
1. Push to GitHub (`.env` and `data/*.db` are git-ignored).
2. Deploy `app.py` to Streamlit Community Cloud; add `THULLA_SECRET` in its Secrets.
3. Deploy the FastAPI server to a free-tier host over HTTPS; set the same secret
   and `THULLA_DB`; set `THULLA_SERVER_URL` in the Streamlit app.
4. Run the manual checklist against the deployed URLs before announcing.

## Optional Android phase (not started)
Easiest path: publish the web app and wrap it as a PWA/Trusted Web Activity
(Bubblewrap). Native packaging of Streamlit is impractical; a Kivy/Flet rewrite of
the UI could reuse `thulla/engine`, `ai`, `offline` and `voice` unchanged.

## Licence
MIT (code). Add audio licences in `assets/audio/README.md`.
=======
# thulla-game
>>>>>>> 7dba50d11b3cd6aa8b9058e379d4ba6a54969041
