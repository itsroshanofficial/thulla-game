"""Browser-side playback (free): recorded files if present, else Web Speech API.

Playback happens in each player's own browser, so volume/mute are naturally
per-player. Browser voices for Punjabi/Urdu vary by device; the code falls back
to Hindi/English voices (documented in README).
"""
from __future__ import annotations
import base64
import html
import json
from pathlib import Path

AUDIO_DIR = Path(__file__).resolve().parents[2] / "assets" / "audio"
_LANG_PREFS = {"pa": ["pa-IN", "pa", "hi-IN", "en-IN"],
               "ur": ["ur-PK", "ur", "hi-IN", "en-IN"],
               "en": ["en-IN", "en-GB", "en-US", "en"]}


def _recording_data_uri(line_id: str):
    for ext, mime in (("mp3", "audio/mpeg"), ("ogg", "audio/ogg"), ("wav", "audio/wav")):
        p = AUDIO_DIR / f"{line_id}.{ext}"
        if p.is_file():
            return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()
    return None


def build_playback_html(line: dict, volume: float) -> str:
    """HTML snippet (for st.components.v1.html) that plays one line once."""
    volume = max(0.0, min(1.0, float(volume)))
    uri = _recording_data_uri(line["id"])
    text = json.dumps(line["text"])
    prefs = json.dumps(_LANG_PREFS.get(line["lang"], ["en"]))
    uri_js = json.dumps(uri)
    return f"""
<div style="font:14px sans-serif;opacity:.75">🔊 {html.escape(line['text'])}</div>
<script>
(function() {{
  const vol = {volume}, uri = {uri_js};
  if (uri) {{ const a = new Audio(uri); a.volume = vol; a.play().catch(()=>{{}}); return; }}
  if (!('speechSynthesis' in window)) return;
  const speak = () => {{
    const u = new SpeechSynthesisUtterance({text});
    const voices = speechSynthesis.getVoices();
    for (const p of {prefs}) {{
      const v = voices.find(v => v.lang && v.lang.toLowerCase().startsWith(p.toLowerCase()));
      if (v) {{ u.voice = v; u.lang = v.lang; break; }}
    }}
    u.volume = vol; u.rate = 1.05; u.pitch = 1.1;
    speechSynthesis.cancel();          // never overlap two reactions
    speechSynthesis.speak(u);
  }};
  if (speechSynthesis.getVoices().length) speak();
  else speechSynthesis.onvoiceschanged = speak;
}})();
</script>"""
