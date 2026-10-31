"""Thulla — global stylesheet (glassmorphism dashboard theme).

Usage (already wired in app.py):
    from thulla.ui.styles import CSS
    st.markdown(CSS, unsafe_allow_html=True)

Works with standard Streamlit components only; it just restyles them.
Supports both dark and light Streamlit themes.
"""

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* ───────────── Design tokens ───────────── */
:root {
  --bg-1: #0b1020;
  --bg-2: #141b34;
  --accent-1: #7c5cff;
  --accent-2: #00d4ff;
  --accent-3: #ff5ca8;
  --glass-bg: rgba(255, 255, 255, 0.06);
  --glass-bg-hover: rgba(255, 255, 255, 0.10);
  --glass-border: rgba(255, 255, 255, 0.14);
  --glass-shadow: 0 8px 32px rgba(0, 0, 0, 0.35);
  --text-1: #f4f6ff;
  --text-2: #a9b2d0;
  --radius: 18px;
  --radius-sm: 12px;
  --blur: blur(16px) saturate(160%);
  --grad-main: linear-gradient(135deg, var(--accent-1) 0%, var(--accent-2) 100%);
  --grad-warm: linear-gradient(135deg, var(--accent-3) 0%, var(--accent-1) 100%);
}

@media (prefers-color-scheme: light) {
  :root {
    --bg-1: #eef1ff;
    --bg-2: #e2e8ff;
    --glass-bg: rgba(255, 255, 255, 0.60);
    --glass-bg-hover: rgba(255, 255, 255, 0.85);
    --glass-border: rgba(124, 92, 255, 0.18);
    --glass-shadow: 0 8px 28px rgba(80, 90, 160, 0.18);
    --text-1: #161a33;
    --text-2: #5a6285;
  }
}

/* ───────────── Base / background ───────────── */
html, body, [class*="css"], .stApp {
  font-family: 'Inter', -apple-system, 'Segoe UI', Roboto, sans-serif !important;
  color: var(--text-1);
}

.stApp {
  background:
    radial-gradient(900px 500px at 8% -5%,  rgba(124, 92, 255, 0.35), transparent 60%),
    radial-gradient(800px 500px at 100% 0%, rgba(0, 212, 255, 0.22), transparent 60%),
    radial-gradient(700px 500px at 50% 110%, rgba(255, 92, 168, 0.20), transparent 60%),
    linear-gradient(160deg, var(--bg-1), var(--bg-2));
  background-attachment: fixed;
}

header[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility: hidden; }

.block-container {
  max-width: 1100px;
  padding-top: 2.2rem;
  padding-bottom: 4rem;
}

/* ───────────── Typography ───────────── */
h1, h2, h3, h4 { letter-spacing: -0.02em; font-weight: 700; }

h1 {
  font-weight: 800;
  background: var(--grad-main);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

h2, h3 { color: var(--text-1); }
p, li, label, .stMarkdown { color: var(--text-1); line-height: 1.65; }
small, .stCaption, [data-testid="stCaptionContainer"] { color: var(--text-2) !important; }
hr { border: none; height: 1px; background: linear-gradient(90deg, transparent, var(--glass-border), transparent); }

/* ───────────── Sidebar ───────────── */
[data-testid="stSidebar"] {
  background: var(--glass-bg);
  backdrop-filter: var(--blur);
  -webkit-backdrop-filter: var(--blur);
  border-right: 1px solid var(--glass-border);
}

[data-testid="stSidebar"] .stRadio > label { font-weight: 600; color: var(--text-2); }

[data-testid="stSidebar"] .stRadio [role="radiogroup"] { gap: 6px; }

[data-testid="stSidebar"] .stRadio [role="radiogroup"] > label {
  background: transparent;
  border: 1px solid transparent;
  border-radius: var(--radius-sm);
  padding: 10px 14px;
  transition: all .2s ease;
  cursor: pointer;
}

[data-testid="stSidebar"] .stRadio [role="radiogroup"] > label:hover {
  background: var(--glass-bg-hover);
  border-color: var(--glass-border);
  transform: translateX(3px);
}

[data-testid="stSidebar"] .stRadio [role="radiogroup"] > label:has(input:checked) {
  background: var(--grad-main);
  border-color: transparent;
  box-shadow: 0 6px 18px rgba(124, 92, 255, 0.40);
}

[data-testid="stSidebar"] .stRadio [role="radiogroup"] > label:has(input:checked) p {
  color: #fff !important;
  font-weight: 600;
}

/* hide the radio dot, keep the pill look */
[data-testid="stSidebar"] .stRadio [role="radiogroup"] > label > div:first-child { display: none; }

/* ───────────── Glass cards (reusable classes) ───────────── */
.glass-card {
  background: var(--glass-bg);
  backdrop-filter: var(--blur);
  -webkit-backdrop-filter: var(--blur);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius);
  box-shadow: var(--glass-shadow);
  padding: 1.4rem 1.5rem;
  height: 100%;
  transition: transform .25s ease, background .25s ease, border-color .25s ease;
}

.glass-card:hover {
  transform: translateY(-4px);
  background: var(--glass-bg-hover);
  border-color: rgba(124, 92, 255, 0.55);
}

.glass-card .icon {
  width: 46px; height: 46px;
  display: grid; place-items: center;
  font-size: 1.4rem;
  border-radius: 14px;
  background: var(--grad-main);
  box-shadow: 0 8px 20px rgba(124, 92, 255, 0.35);
  margin-bottom: .9rem;
}

.glass-card .icon.warm { background: var(--grad-warm); }
.glass-card h3 { margin: 0 0 .35rem 0; font-size: 1.15rem; }
.glass-card p  { margin: 0; color: var(--text-2); font-size: .95rem; }

.glass-card .badge {
  display: inline-block;
  margin-top: .9rem;
  padding: 3px 12px;
  font-size: .72rem; font-weight: 600; letter-spacing: .04em;
  border-radius: 999px;
  border: 1px solid var(--glass-border);
  color: var(--text-2);
}

/* Hero banner */
.hero {
  position: relative;
  overflow: hidden;
  padding: 2.4rem 2.2rem;
  margin-bottom: 1.6rem;
  border-radius: 24px;
  background:
    linear-gradient(135deg, rgba(124, 92, 255, 0.35), rgba(0, 212, 255, 0.18)),
    var(--glass-bg);
  backdrop-filter: var(--blur);
  -webkit-backdrop-filter: var(--blur);
  border: 1px solid var(--glass-border);
  box-shadow: var(--glass-shadow);
}

.hero::after {
  content: "🃏";
  position: absolute; right: 1.6rem; top: 50%;
  transform: translateY(-50%) rotate(14deg);
  font-size: 7rem; opacity: .16; pointer-events: none;
}

.hero h1 { margin: 0 0 .4rem 0; font-size: 2.6rem; }
.hero p  { margin: 0; max-width: 520px; color: var(--text-2); font-size: 1.05rem; }

/* ───────────── Metrics ───────────── */
[data-testid="stMetric"] {
  background: var(--glass-bg);
  backdrop-filter: var(--blur);
  -webkit-backdrop-filter: var(--blur);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius);
  box-shadow: var(--glass-shadow);
  padding: 1rem 1.2rem;
}

[data-testid="stMetricLabel"] p {
  color: var(--text-2) !important;
  font-size: .8rem; font-weight: 600;
  text-transform: uppercase; letter-spacing: .06em;
}

[data-testid="stMetricValue"] { font-weight: 800; font-size: 1.9rem; }

/* ───────────── Buttons ───────────── */
.stButton > button,
.stDownloadButton > button,
.stFormSubmitButton > button {
  background: var(--grad-main);
  color: #fff;
  border: none;
  border-radius: var(--radius-sm);
  padding: .6rem 1.3rem;
  font-weight: 600;
  letter-spacing: .01em;
  box-shadow: 0 6px 18px rgba(124, 92, 255, 0.35);
  transition: transform .15s ease, box-shadow .15s ease, filter .15s ease;
}

.stButton > button:hover,
.stDownloadButton > button:hover,
.stFormSubmitButton > button:hover {
  transform: translateY(-2px);
  filter: brightness(1.08);
  box-shadow: 0 10px 26px rgba(124, 92, 255, 0.50);
  color: #fff;
}

.stButton > button:active { transform: translateY(0); }
.stButton > button:focus-visible { outline: 2px solid var(--accent-2); outline-offset: 2px; }
.stButton > button:disabled { opacity: .45; box-shadow: none; }

/* secondary buttons = glass */
.stButton > button[kind="secondary"] {
  background: var(--glass-bg);
  color: var(--text-1);
  border: 1px solid var(--glass-border);
  box-shadow: none;
}
.stButton > button[kind="secondary"]:hover { background: var(--glass-bg-hover); }

/* ───────────── Inputs ───────────── */
.stTextInput input,
.stNumberInput input,
.stTextArea textarea,
.stSelectbox [data-baseweb="select"] > div,
.stMultiSelect [data-baseweb="select"] > div {
  background: var(--glass-bg) !important;
  border: 1px solid var(--glass-border) !important;
  border-radius: var(--radius-sm) !important;
  color: var(--text-1) !important;
  transition: border-color .2s ease, box-shadow .2s ease;
}

.stTextInput input:focus,
.stNumberInput input:focus,
.stTextArea textarea:focus {
  border-color: var(--accent-1) !important;
  box-shadow: 0 0 0 3px rgba(124, 92, 255, 0.28) !important;
}

/* ───────────── Alerts (st.info / success / warning / error) ───────────── */
[data-testid="stAlert"] {
  background: var(--glass-bg);
  backdrop-filter: var(--blur);
  -webkit-backdrop-filter: var(--blur);
  border: 1px solid var(--glass-border);
  border-left-width: 4px;
  border-radius: var(--radius-sm);
  box-shadow: var(--glass-shadow);
}

/* ───────────── Tabs, expanders, forms, containers ───────────── */
.stTabs [data-baseweb="tab-list"] {
  gap: 6px;
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-sm);
  padding: 5px;
}

.stTabs [data-baseweb="tab"] {
  border-radius: 9px;
  padding: 8px 16px;
  color: var(--text-2);
  font-weight: 600;
}

.stTabs [aria-selected="true"] { background: var(--grad-main); color: #fff; }
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none; }

[data-testid="stExpander"],
[data-testid="stForm"],
[data-testid="stVerticalBlockBorderWrapper"]:has(> div > [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"] .glass-card) {
  background: var(--glass-bg);
  backdrop-filter: var(--blur);
  -webkit-backdrop-filter: var(--blur);
  border: 1px solid var(--glass-border) !important;
  border-radius: var(--radius);
  box-shadow: var(--glass-shadow);
}

[data-testid="stExpander"] summary { font-weight: 600; }

/* ───────────── Tables / dataframes ───────────── */
[data-testid="stDataFrame"], [data-testid="stTable"] {
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-sm);
  overflow: hidden;
}

/* ───────────── Progress, spinner, slider ───────────── */
.stProgress > div > div > div > div { background: var(--grad-main); border-radius: 999px; }
.stSlider [role="slider"] { background: var(--accent-1); box-shadow: 0 0 0 4px rgba(124, 92, 255, 0.25); }

/* ───────────── Scrollbar ───────────── */
::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-thumb { background: rgba(124, 92, 255, 0.45); border-radius: 999px; }
::-webkit-scrollbar-thumb:hover { background: rgba(124, 92, 255, 0.70); }
::-webkit-scrollbar-track { background: transparent; }

/* ───────────── Entrance animation ───────────── */
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(14px); }
  to   { opacity: 1; transform: translateY(0); }
}
.block-container > div { animation: fadeUp .5s ease both; }

/* ───────────── Responsive ───────────── */
@media (max-width: 768px) {
  .block-container { padding: 1.2rem 1rem 3rem; }
  .hero { padding: 1.6rem 1.3rem; }
  .hero h1 { font-size: 2rem; }
  .hero::after { font-size: 4.5rem; }
}

@media (prefers-reduced-motion: reduce) {
  * { animation: none !important; transition: none !important; }
}
/* Streamlit Header Toolbar Hide karne ke liye */
header[data-testid="stHeader"] {
    display: none !important;
}

/* Agar upar thodi extra space bache toh usay bhi kam karne ke liye */
.block-container {
    padding-top: 1rem !important;
}
</style>
"""
