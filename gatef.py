"""
AI Smart Gate — Streamlit Edition
Run:  streamlit run gatef.py
Install: pip install streamlit opencv-python easyocr pillow numpy certifi
"""

import ssl, certifi
ssl._create_default_https_context = lambda: ssl.create_default_context(cafile=certifi.where())

import cv2, numpy as np, re, csv, io, platform, time
from datetime import datetime
import streamlit as st
from PIL import Image

# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE CONFIG
# ═══════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="AI Smart Gate", page_icon="🚗", layout="wide",
                   initial_sidebar_state="collapsed")

# ═══════════════════════════════════════════════════════════════════════════════
#  AUTH
# ═══════════════════════════════════════════════════════════════════════════════
USERS = {"sathvik": "124"}   # id → password

# ═══════════════════════════════════════════════════════════════════════════════
#  SHARED CSS
# ═══════════════════════════════════════════════════════════════════════════════
BASE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;800&family=Syne:wght@400;700;800&display=swap');

*, *::before, *::after { box-sizing: border-box; }
.stApp { background: #080c10 !important; color: #d4e4f4; font-family: 'Syne', sans-serif; }
section[data-testid="stSidebar"] { display: none !important; }
.block-container { padding: 1.2rem 1.6rem !important; max-width: 100% !important; }
h1,h2,h3,h4 { font-family: 'Syne', sans-serif !important; }

/* ── scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #0d1520; }
::-webkit-scrollbar-thumb { background: #1e3a5f; border-radius: 3px; }

/* ── topbar ── */
.topbar {
  display: flex; align-items: center; gap: 14px; flex-wrap: wrap;
  background: linear-gradient(135deg, #0d1a26 0%, #0a1520 100%);
  border: 1px solid #1a2d42; border-radius: 12px;
  padding: 12px 20px; margin-bottom: 18px;
  box-shadow: 0 4px 24px rgba(0,0,0,.5);
}
.topbar-logo { font-family:'JetBrains Mono',monospace; font-weight:800; font-size:18px; color:#e2f0ff; letter-spacing:1px; }
.topbar-logo span { color:#3b9eff; }
.chip {
  display:inline-block; border-radius:5px; padding:2px 9px;
  font-family:'JetBrains Mono',monospace; font-size:10px; font-weight:600;
  letter-spacing:.5px; margin-right:4px;
}
.topbar-right { margin-left:auto; display:flex; align-items:center; gap:12px; }
.topbar-time { font-family:'JetBrains Mono',monospace; font-size:11px; color:#4a6680; }
.topbar-user { font-family:'JetBrains Mono',monospace; font-size:11px;
  color:#3b9eff; background:#0d1f30; border:1px solid #1a3a55;
  border-radius:6px; padding:3px 10px; }

/* ── nav tabs ── */
.nav-bar {
  display:flex; gap:4px; background:#0d1520;
  border:1px solid #1a2d42; border-radius:10px;
  padding:5px; margin-bottom:18px;
}
.nav-btn {
  flex:1; text-align:center; padding:9px 0;
  border-radius:7px; cursor:pointer;
  font-family:'Syne',sans-serif; font-size:13px; font-weight:700;
  border:1px solid transparent; transition:all .15s;
  color:#4a6680;
}
.nav-btn.active { background:#0e2240; border-color:#1a4a80; color:#3b9eff; }
.nav-btn:hover:not(.active) { background:#111e2e; color:#8ab8e0; }

/* ── cards ── */
.card {
  background:#0d1a26; border:1px solid #1a2d42;
  border-radius:12px; padding:16px 18px; margin-bottom:12px;
}
.card-sm { background:#0a1520; border:1px solid #152030; border-radius:8px; padding:10px 14px; margin-bottom:8px; }

/* ── stat tiles ── */
.stat-row { display:flex; gap:10px; margin-bottom:14px; flex-wrap:wrap; }
.stat-tile {
  flex:1; min-width:100px; background:#0d1a26; border:1px solid #1a2d42;
  border-radius:10px; padding:12px 14px; text-align:center;
}
.stat-num { font-family:'JetBrains Mono',monospace; font-size:28px; font-weight:800; }
.stat-lbl { font-size:11px; color:#4a6680; margin-top:2px; font-family:'JetBrains Mono',monospace; }

/* ── log table ── */
.log-wrap { overflow-x:auto; }
.log-tbl { width:100%; border-collapse:collapse; font-family:'JetBrains Mono',monospace; font-size:12px; }
.log-tbl th { background:#0a1520; color:#3b7ab0; padding:7px 10px; text-align:left;
  border-bottom:1px solid #1a2d42; white-space:nowrap; }
.log-tbl td { padding:7px 10px; border-bottom:1px solid #0f1e2e; vertical-align:middle; }
.log-tbl tr:hover td { background:#0d1f30; }
.badge {
  display:inline-block; border-radius:4px; padding:2px 8px;
  font-size:10px; font-weight:700; font-family:'JetBrains Mono',monospace; letter-spacing:.5px;
}
.b-grant { background:#0a2e14; border:1px solid #22c55e; color:#22c55e; }
.b-deny  { background:#2e0a0a; border:1px solid #ef4444; color:#ef4444; }
.b-over  { background:#1a1a00; border:1px solid #f59e0b; color:#f59e0b; }
.b-auto  { background:#0a1a2e; border:1px solid #3b82f6; color:#3b82f6; }
.b-manual{ background:#1a0a2e; border:1px solid #8b5cf6; color:#8b5cf6; }

/* ── user row ── */
.user-row {
  display:flex; align-items:center; gap:10px; flex-wrap:wrap;
  background:#0d1a26; border:1px solid #1a2d42;
  border-radius:8px; padding:10px 14px; margin-bottom:7px;
}
.user-plate { font-family:'JetBrains Mono',monospace; font-weight:800; font-size:15px;
  color:#e2f0ff; background:#0a1520; border:1px solid #1a3a55;
  border-radius:5px; padding:3px 10px; }
.user-name  { font-weight:700; font-size:14px; color:#c8dff0; flex:1; min-width:120px; }
.user-meta  { font-family:'JetBrains Mono',monospace; font-size:11px; color:#4a6680; }
.user-actions { display:flex; gap:6px; margin-left:auto; }
.act-btn {
  font-family:'JetBrains Mono',monospace; font-size:11px; font-weight:700;
  border-radius:5px; padding:4px 10px; cursor:pointer; border:1px solid;
  background:transparent; transition:all .12s;
}
.act-edit { color:#3b9eff; border-color:#1a4a80; }
.act-edit:hover { background:#0e2240; }
.act-del  { color:#ef4444; border-color:#4a1010; }
.act-del:hover  { background:#2e0a0a; }

/* ── override card ── */
.ov-card {
  background:#0d1a26; border:1px solid #2a1a00;
  border-radius:10px; padding:12px 16px; margin-bottom:8px;
  display:flex; align-items:center; gap:12px; flex-wrap:wrap;
}
.ov-plate { font-family:'JetBrains Mono',monospace; font-size:18px; font-weight:800;
  color:#f59e0b; background:#1a1200; border:1px solid #3a2a00;
  border-radius:5px; padding:4px 12px; }
.ov-info  { flex:1; }
.ov-name  { font-size:13px; color:#c8dff0; font-weight:700; }
.ov-time  { font-family:'JetBrains Mono',monospace; font-size:11px; color:#4a6680; }

/* ── result card ── */
.res-card { border-radius:12px; padding:20px; margin-bottom:12px; border:3px solid; }
.res-grant { background:#0a220e; border-color:#22c55e; }
.res-deny  { background:#220a0a; border-color:#ef4444; }
.res-idle  { background:#0d1a26; border-color:#1a2d42; }
.verdict-txt { font-family:'JetBrains Mono',monospace; font-size:22px; font-weight:800;
  letter-spacing:2px; text-align:center; margin-bottom:6px; }
.plate-xl { font-family:'JetBrains Mono',monospace; font-size:44px; font-weight:800;
  text-align:center; letter-spacing:4px; margin:6px 0 12px; }
.det-row { font-family:'JetBrains Mono',monospace; font-size:12px; margin:3px 0; }
.det-lbl { color:#4a6680; }
.det-val { color:#d4e4f4; }
.gate-badge {
  border-radius:8px; border:2px solid; padding:8px; font-family:'JetBrains Mono',monospace;
  font-weight:800; font-size:20px; text-align:center; letter-spacing:2px; margin-top:12px; }

/* ── pipe strip ── */
.pipe-strip { display:flex; gap:5px; margin:8px 0 14px; flex-wrap:wrap; }
.pipe-step {
  flex:1; min-width:90px; border-radius:6px; padding:6px 8px;
  font-family:'JetBrains Mono',monospace; font-size:10px; border:1px solid; text-align:left; }

/* ── login page ── */
.login-wrap {
  min-height:100vh; display:flex; align-items:center; justify-content:center;
  background:radial-gradient(ellipse at 30% 40%, #0a1e35 0%, #080c10 60%);
}
.login-box {
  width:380px; background:#0d1a26; border:1px solid #1a3a55;
  border-radius:16px; padding:40px 36px;
  box-shadow:0 24px 80px rgba(0,0,0,.7);
}
.login-icon { text-align:center; font-size:48px; margin-bottom:10px; }
.login-title { text-align:center; font-family:'JetBrains Mono',monospace;
  font-size:22px; font-weight:800; color:#e2f0ff; letter-spacing:2px; margin-bottom:4px; }
.login-sub { text-align:center; font-size:12px; color:#3b6080; margin-bottom:28px;
  font-family:'JetBrains Mono',monospace; }

/* ── toast ── */
.toast-ok  { position:fixed; bottom:24px; right:24px; z-index:9999;
  background:#0a2e14; border:1px solid #22c55e; color:#22c55e;
  border-radius:10px; padding:12px 20px; font-family:'JetBrains Mono',monospace;
  font-size:13px; box-shadow:0 8px 32px rgba(0,0,0,.5); }
.toast-err { position:fixed; bottom:24px; right:24px; z-index:9999;
  background:#2e0a0a; border:1px solid #ef4444; color:#ef4444;
  border-radius:10px; padding:12px 20px; font-family:'JetBrains Mono',monospace;
  font-size:13px; box-shadow:0 8px 32px rgba(0,0,0,.5); }
.toast-info{ position:fixed; bottom:24px; right:24px; z-index:9999;
  background:#0d1f30; border:1px solid #3b82f6; color:#3b82f6;
  border-radius:10px; padding:12px 20px; font-family:'JetBrains Mono',monospace;
  font-size:13px; box-shadow:0 8px 32px rgba(0,0,0,.5); }
.toast-warn{ position:fixed; bottom:24px; right:24px; z-index:9999;
  background:#1a1200; border:1px solid #f59e0b; color:#f59e0b;
  border-radius:10px; padding:12px 20px; font-family:'JetBrains Mono',monospace;
  font-size:13px; box-shadow:0 8px 32px rgba(0,0,0,.5); }

/* ── streamlit overrides ── */
div[data-testid="stButton"] > button {
  background:#0e2240 !important; color:#3b9eff !important;
  border:1px solid #1a4a80 !important; border-radius:7px !important;
  font-family:'JetBrains Mono',monospace !important; font-size:13px !important;
  font-weight:700 !important; padding:8px 0 !important;
}
div[data-testid="stButton"] > button:hover { background:#142e50 !important; }
div[data-testid="stTextInput"] input,
div[data-testid="stSelectbox"] > div,
div[data-testid="stTextArea"] textarea {
  background:#0a1520 !important; border:1px solid #1a2d42 !important;
  color:#d4e4f4 !important; border-radius:6px !important;
  font-family:'JetBrains Mono',monospace !important; font-size:13px !important;
}
div[data-testid="stForm"] { background:transparent !important; border:none !important; }
.stAlert { border-radius:8px !important; }
div[data-testid="stExpander"] { background:#0d1a26 !important; border:1px solid #1a2d42 !important; border-radius:8px !important; }
</style>
"""
st.markdown(BASE_CSS, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  SESSION STATE INIT
# ═══════════════════════════════════════════════════════════════════════════════
_defaults = dict(
    logged_in=False, current_user="",
    admin_tab="history",
    # gate
    last_result=None, last_plate="", all_reads=[], log=[],
    phase="idle", pipe_step=0, scan_image=None,
    ocr_ms=None, preprocess_ms=None, lookup_ms=None,
    # admin
    plate_db={
        "MH12AB1234": {"name":"Rajesh Kumar",  "role":"Resident","flat":"A-204","car":"Honda City Silver",  "active":True},
        "DL05CD7788": {"name":"Priya Sharma",  "role":"Visitor", "flat":"Guest","car":"Maruti Swift White", "active":True},
        "KA03EF5566": {"name":"Amit Patel",    "role":"Resident","flat":"C-101","car":"Toyota Innova Grey", "active":True},
        "MH14GH9900": {"name":"Suresh Nair",   "role":"Staff",   "flat":"Gate", "car":"Tata Safari Black",  "active":True},
        "KL07MN2211": {"name":"Dr. Meena Iyer","role":"Resident","flat":"B-302","car":"Hyundai Creta White","active":True},
        "TN09ZZ8877": {"name":"Kiran Raj",     "role":"Resident","flat":"D-501","car":"Maruti Baleno Red",  "active":True},
        "GJ01QQ1122": {"name":"Delivery Pass", "role":"Visitor", "flat":"Guest","car":"Registered Visitor", "active":True},
    },
    blacklist={"RJ14XX4455","BR05MM2233","UP32XY0001"},
    toast=None, toast_type="ok", toast_time=0,
    edit_plate=None,
    history=[],   # full history with method field
)
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ═══════════════════════════════════════════════════════════════════════════════
#  TOAST HELPERS
# ═══════════════════════════════════════════════════════════════════════════════
def show_toast(msg: str, kind: str = "ok"):
    st.session_state.toast      = msg
    st.session_state.toast_type = kind
    st.session_state.toast_time = time.time()

def render_toast():
    if not st.session_state.toast:
        return
    if time.time() - st.session_state.toast_time > 4:
        st.session_state.toast = None
        return
    cls = {"ok":"toast-ok","err":"toast-err","info":"toast-info","warn":"toast-warn"}.get(
        st.session_state.toast_type, "toast-info")
    icon = {"ok":"✓","err":"✕","info":"ℹ","warn":"⚠"}.get(st.session_state.toast_type, "•")
    st.markdown(f'<div class="{cls}">{icon} &nbsp;{st.session_state.toast}</div>',
                unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  OCR + PIPELINE
# ═══════════════════════════════════════════════════════════════════════════════
@st.cache_resource(show_spinner="Loading EasyOCR model (~100 MB first run)…")
def load_ocr():
    import easyocr
    return easyocr.Reader(["en"], gpu=False, verbose=False)

def preprocess(frame: np.ndarray) -> np.ndarray:
    h, w = frame.shape[:2]
    if w < 800:
        s = 800/w
        frame = cv2.resize(frame, (int(w*s), int(h*s)), interpolation=cv2.INTER_CUBIC)
    smooth   = cv2.bilateralFilter(frame, 9, 75, 75)
    lab      = cv2.cvtColor(smooth, cv2.COLOR_BGR2LAB)
    l, a, b  = cv2.split(lab)
    lab      = cv2.merge([cv2.createCLAHE(3.0,(8,8)).apply(l), a, b])
    enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    return cv2.filter2D(enhanced, -1, np.array([[0,-1,0],[-1,5,-1],[0,-1,0]]))

def clean_plate(raw: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", raw.upper())[:12]

def decide(plate: str, method: str = "auto") -> dict:
    now = datetime.now()
    db  = st.session_state.plate_db
    bl  = plate in st.session_state.blacklist
    rec = db.get(plate)
    if bl:
        ok,name,role,flat,car,reason = False,"BLACKLISTED","Blacklisted","—","—","On security blacklist"
    elif rec and rec.get("active", True):
        ok,name,role,flat,car = True,rec["name"],rec["role"],rec["flat"],rec["car"]
        reason = f"{rec['role']} — Flat {rec['flat']}"
    elif rec and not rec.get("active", True):
        ok,name,role,flat,car,reason = False,rec["name"],rec["role"],rec["flat"],rec["car"],"Vehicle inactive"
    else:
        ok,name,role,flat,car,reason = False,"Unknown","Unknown","—","—","Plate not in database"
    entry = dict(plate=plate, ok=ok, name=name, role=role, flat=flat, car=car,
                 reason=reason, method=method,
                 time=now.strftime("%H:%M:%S"), date=now.strftime("%Y-%m-%d"))
    st.session_state.log.insert(0, entry)
    st.session_state.history.insert(0, entry)
    if len(st.session_state.log) > 500:
        st.session_state.log = st.session_state.log[:500]
    if len(st.session_state.history) > 1000:
        st.session_state.history = st.session_state.history[:1000]
    return entry

def run_ocr(frame_bgr: np.ndarray):
    st.session_state.pipe_step = 1
    t0 = time.perf_counter()
    processed = preprocess(frame_bgr)
    st.session_state.preprocess_ms = round((time.perf_counter()-t0)*1000)
    st.session_state.pipe_step = 2
    reader = load_ocr()
    t0 = time.perf_counter()
    results = reader.readtext(processed,
                              allowlist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ",
                              detail=1, paragraph=False)
    st.session_state.ocr_ms = round((time.perf_counter()-t0)*1000)
    st.session_state.pipe_step = 3
    t0 = time.perf_counter()
    db = st.session_state.plate_db
    candidates = [(clean_plate(t), c) for _,t,c in results if len(clean_plate(t)) >= 4]
    plate = ""
    if candidates:
        for p,_ in candidates:
            if p in db or p in st.session_state.blacklist:
                plate = p; break
        else:
            plate = sorted(candidates, key=lambda x:-x[1])[0][0]
    plate = plate or "UNREADABLE"
    st.session_state.lookup_ms = round((time.perf_counter()-t0)*1000)
    st.session_state.pipe_step = 4
    now    = datetime.now()
    result = decide(plate, method="auto")
    st.session_state.all_reads.append(dict(
        plate=plate, time=now.strftime("%H:%M:%S"),
        date=now.strftime("%Y-%m-%d"), ok=result["ok"], name=result["name"]))
    st.session_state.last_plate  = plate
    st.session_state.last_result = result
    st.session_state.phase       = "done"
    st.session_state.pipe_step   = 5

PIPE_STEPS = [
    ("CAPTURE",    "cv2.VideoCapture",         "#3b82f6"),
    ("PREPROCESS", "OpenCV bilateral+CLAHE",    "#8b5cf6"),
    ("OCR",        "EasyOCR (CPU)",             "#f59e0b"),
    ("LOOKUP",     "Python dict.get()",         "#06b6d4"),
    ("VERDICT",    "if/else → GRANTED/DENIED",  "#22c55e"),
]

def pipeline_html(step: int) -> str:
    timings = [None,
               f"{st.session_state.preprocess_ms}ms" if st.session_state.preprocess_ms else None,
               f"{st.session_state.ocr_ms}ms"        if st.session_state.ocr_ms        else None,
               f"{st.session_state.lookup_ms}ms"     if st.session_state.lookup_ms     else None,
               None]
    parts = []
    for i,(label,sub,col) in enumerate(PIPE_STEPS):
        done = i < step
        r,g,b = int(col[1:3],16),int(col[3:5],16),int(col[5:7],16)
        bg = f"rgba({r},{g},{b},.12)" if done else "#0a1520"
        bc = col if done else "#1a2d42"
        tc = col if done else "#2a4060"
        tick = "✓" if done else str(i+1)
        tm = f' <span style="color:#4a6680">({timings[i]})</span>' if (done and timings[i]) else ""
        parts.append(
            f'<div class="pipe-step" style="background:{bg};border-color:{bc};color:{tc}">'
            f'<b>{tick} {label}</b>{tm}<br>'
            f'<span style="color:#2a4060;font-size:9px">{sub}</span></div>')
    return '<div class="pipe-strip">'+"".join(parts)+"</div>"

def grab_frame():
    for idx in range(4):
        cap = cv2.VideoCapture(idx)
        if cap.isOpened():
            for _ in range(3): cap.read()
            ret, frame = cap.read()
            cap.release()
            if ret and frame is not None and frame.size > 0:
                return frame
    return None

def make_csv() -> bytes:
    buf = io.StringIO()
    fields = ["date","time","plate","name","role","flat","car","ok","method","reason"]
    w = csv.DictWriter(buf, fieldnames=fields)
    w.writeheader()
    for e in st.session_state.history:
        w.writerow({k: e.get(k,"") for k in fields})
    return buf.getvalue().encode()

# ═══════════════════════════════════════════════════════════════════════════════
#  TOPBAR (shared across pages)
# ═══════════════════════════════════════════════════════════════════════════════
def render_topbar():
    py_ver  = platform.python_version()
    cv2_ver = cv2.__version__
    chips = (
        f'<span class="chip" style="background:rgba(59,130,246,.12);border:1px solid #1a3a80;color:#3b82f6">Python {py_ver}</span>'
        f'<span class="chip" style="background:rgba(139,92,246,.12);border:1px solid #3a1a80;color:#8b5cf6">OpenCV {cv2_ver}</span>'
        f'<span class="chip" style="background:rgba(245,158,11,.12);border:1px solid #6a3a00;color:#f59e0b">EasyOCR CPU</span>'
    )
    user_html = (
        f'<span class="topbar-user">◉ {st.session_state.current_user.upper()}</span>'
        if st.session_state.logged_in else ""
    )
    st.markdown(
        f'<div class="topbar">'
        f'<span class="topbar-logo">🚗 AI <span>SMART</span> GATE</span>'
        f'{chips}'
        f'<div class="topbar-right">'
        f'<span class="topbar-time">{datetime.now().strftime("%H:%M · %d %b %Y")}</span>'
        f'{user_html}'
        f'</div></div>',
        unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  ██████  LOGIN PAGE
# ═══════════════════════════════════════════════════════════════════════════════
def page_login():
    render_topbar()
    # Center the login box using columns
    _, mid, _ = st.columns([1, 1.2, 1])
    with mid:
        st.markdown("""
        <div style="background:#0d1a26;border:1px solid #1a3a55;border-radius:16px;
                    padding:40px 36px;box-shadow:0 24px 80px rgba(0,0,0,.7);margin-top:30px;">
          <div style="text-align:center;font-size:52px;margin-bottom:8px;">🔒</div>
          <div style="text-align:center;font-family:'JetBrains Mono',monospace;font-size:20px;
                      font-weight:800;color:#e2f0ff;letter-spacing:2px;margin-bottom:4px;">
            OFFICER LOGIN</div>
          <div style="text-align:center;font-size:12px;color:#3b6080;margin-bottom:28px;
                      font-family:'JetBrains Mono',monospace;">
            Gate Management System · Restricted Access</div>
        </div>""", unsafe_allow_html=True)

        # Overlay form on top using Streamlit widgets
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        with st.form("login_form"):
            uid = st.text_input("Officer ID", placeholder="Enter your ID",
                                autocomplete="username")
            pw  = st.text_input("Password",   placeholder="••••••••",
                                type="password", autocomplete="current-password")
            submitted = st.form_submit_button("SIGN IN  →", use_container_width=True)
            if submitted:
                if uid in USERS and USERS[uid] == pw:
                    st.session_state.logged_in   = True
                    st.session_state.current_user = uid
                    show_toast(f"Welcome, {uid.upper()}!", "ok")
                    st.rerun()
                else:
                    st.error("Invalid ID or password.")

        st.markdown(
            '<div style="text-align:center;font-family:JetBrains Mono,monospace;'
            'font-size:11px;color:#1a3a55;margin-top:12px;">Demo: sathvik / 124</div>',
            unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  ██████  GATE PAGE  (the live scan screen)
# ═══════════════════════════════════════════════════════════════════════════════
def page_gate():
    left, right = st.columns([3, 2], gap="medium")

    with left:
        phase    = st.session_state.phase
        scan_img = st.session_state.scan_image
        if scan_img is not None and phase in ("scanning","done"):
            display = scan_img
        else:
            lf = grab_frame()
            display = Image.fromarray(cv2.cvtColor(lf, cv2.COLOR_BGR2RGB)) if lf is not None else None

        if display is not None:
            res = st.session_state.last_result
            if phase == "done" and res:
                tint = Image.new("RGBA", display.size, (0,40,10,60) if res["ok"] else (40,0,0,60))
                display = Image.alpha_composite(display.convert("RGBA"), tint).convert("RGB")
            st.image(display, use_container_width=True)
        else:
            st.markdown('<div class="card" style="text-align:center;padding:40px;color:#2a4060;">'
                        '📷 No camera — upload an image or use Manual Entry</div>',
                        unsafe_allow_html=True)

        st.markdown(pipeline_html(st.session_state.pipe_step), unsafe_allow_html=True)

        # Mini log
        st.markdown('<div style="font-family:JetBrains Mono,monospace;font-size:11px;'
                    'color:#3b9eff;margin-bottom:6px;">RECENT ACCESS LOG</div>',
                    unsafe_allow_html=True)
        if st.session_state.log:
            rows = ""
            for e in st.session_state.log[:15]:
                bc = "b-grant" if e["ok"] else "b-deny"
                bt = "AUTH" if e["ok"] else "DENY"
                rows += (f'<tr><td>{e.get("time","")}</td>'
                         f'<td><b>{e.get("plate","")}</b></td>'
                         f'<td>{e.get("name","")[:18]}</td>'
                         f'<td>{e.get("role","")}</td>'
                         f'<td><span class="badge {bc}">{bt}</span></td></tr>')
            st.markdown(f'<div class="log-wrap"><table class="log-tbl">'
                        f'<tr><th>TIME</th><th>PLATE</th><th>NAME</th><th>ROLE</th><th>STATUS</th></tr>'
                        f'{rows}</table></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="font-family:JetBrains Mono,monospace;font-size:12px;'
                        'color:#1a2d42;padding:8px;">No entries yet.</div>', unsafe_allow_html=True)

    with right:
        # Session counter
        st.markdown(f'<div class="card-sm" style="text-align:center;">'
                    f'<span style="font-family:JetBrains Mono,monospace;font-size:28px;'
                    f'font-weight:800;color:#3b9eff;">{len(st.session_state.all_reads)}</span>'
                    f'<div style="font-size:11px;color:#4a6680;font-family:JetBrains Mono,monospace;">'
                    f'plates scanned this session</div></div>', unsafe_allow_html=True)

        st.markdown("#### 📷 Webcam Scan")
        if st.button("▶  CAPTURE & READ PLATE", use_container_width=True):
            frame = grab_frame()
            if frame is None:
                st.error("No camera. Upload an image or use Manual Entry.")
            else:
                st.session_state.scan_image    = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                st.session_state.phase         = "scanning"
                st.session_state.pipe_step     = 0
                st.session_state.ocr_ms        = None
                st.session_state.preprocess_ms = None
                st.session_state.lookup_ms     = None
                with st.spinner("Running OpenCV + EasyOCR…"):
                    run_ocr(frame)
                st.rerun()

        st.markdown("#### 🖼 Upload Image")
        uploaded = st.file_uploader("Upload plate photo",
                                    type=["jpg","jpeg","png","bmp","webp"],
                                    label_visibility="collapsed")
        if uploaded:
            img_pil   = Image.open(uploaded).convert("RGB")
            frame_bgr = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
            st.image(img_pil, use_container_width=True)
            if st.button("🔍 Run OCR on this image", use_container_width=True):
                st.session_state.scan_image    = img_pil
                st.session_state.phase         = "scanning"
                st.session_state.pipe_step     = 0
                st.session_state.ocr_ms        = None
                st.session_state.preprocess_ms = None
                st.session_state.lookup_ms     = None
                with st.spinner("Running OCR…"):
                    run_ocr(frame_bgr)
                st.rerun()

        st.markdown("#### ✏️ Manual Entry")
        with st.form("manual_form", clear_on_submit=True):
            mp = st.text_input("Plate number", placeholder="e.g. MH12AB1234",
                               max_chars=12, label_visibility="collapsed")
            if st.form_submit_button("✅ Lookup", use_container_width=True) and mp.strip():
                plate  = re.sub(r"[^A-Z0-9]","",mp.strip().upper())[:12]
                result = decide(plate, method="manual")
                now    = datetime.now()
                st.session_state.all_reads.append(dict(
                    plate=plate, time=now.strftime("%H:%M:%S"),
                    date=now.strftime("%Y-%m-%d"), ok=result["ok"], name=result["name"]))
                st.session_state.last_plate  = plate
                st.session_state.last_result = result
                st.session_state.phase       = "done"
                st.session_state.pipe_step   = 5
                st.session_state.scan_image  = None
                st.rerun()

        # Result card
        res = st.session_state.last_result
        if res:
            ok  = res["ok"]
            cls = "res-grant" if ok else "res-deny"
            vt  = "✅ ACCESS GRANTED" if ok else "❌ ACCESS DENIED"
            vc  = "#22c55e" if ok else "#ef4444"
            tp  = []
            if st.session_state.preprocess_ms: tp.append(f"pre {st.session_state.preprocess_ms}ms")
            if st.session_state.ocr_ms:        tp.append(f"ocr {st.session_state.ocr_ms}ms")
            eng = " · ".join(tp) if tp else "manual lookup"
            dets = "".join(
                f'<div class="det-row"><span class="det-lbl">{l}:&nbsp;</span>'
                f'<span class="det-val">{v}</span></div>'
                for l,v in [("NAME",res["name"]),("ROLE",res["role"]),
                             ("FLAT",res["flat"]),("CAR",res["car"]),
                             ("REASON",res["reason"]),("TIME",res["time"]),("TIMING",eng)])
            st.markdown(
                f'<div class="res-card {cls}">'
                f'<div class="verdict-txt" style="color:{vc}">{vt}</div>'
                f'<div class="plate-xl" style="color:{vc}">{res["plate"]}</div>'
                f'<hr style="border-color:{vc};opacity:.25;margin:8px 0">'
                f'{dets}'
                f'<div class="gate-badge" style="color:{vc};border-color:{vc}">'
                f'GATE: {"OPEN" if ok else "STOP"}</div></div>',
                unsafe_allow_html=True)
            if st.button("🔄 Reset", use_container_width=True):
                for k in ("last_result","scan_image"):
                    st.session_state[k] = None
                for k in ("last_plate","phase"):
                    st.session_state[k] = "" if k=="last_plate" else "idle"
                st.session_state.pipe_step = 0
                st.session_state.ocr_ms = st.session_state.preprocess_ms = st.session_state.lookup_ms = None
                st.rerun()
        else:
            st.markdown('<div class="res-card res-idle" style="text-align:center;padding:36px 16px;">'
                        '<div style="font-size:36px;margin-bottom:8px;">🚗</div>'
                        '<div style="font-family:JetBrains Mono,monospace;color:#1a3a55;font-size:16px;">'
                        'AWAITING SCAN</div>'
                        '<div style="font-family:JetBrains Mono,monospace;color:#1a2d42;font-size:11px;margin-top:6px;">'
                        'Scan, upload, or enter a plate</div></div>',
                        unsafe_allow_html=True)

        if st.session_state.history:
            st.download_button("⬇️ Export Full Log (CSV)", data=make_csv(),
                               file_name=f"gate_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                               mime="text/csv", use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  ██████  ADMIN — ACCESS HISTORY TAB
# ═══════════════════════════════════════════════════════════════════════════════
def tab_history():
    h = st.session_state.history

    # Stats row
    total   = len(h)
    granted = sum(1 for e in h if e["ok"])
    denied  = total - granted
    overrides = sum(1 for e in h if e.get("method") == "override")
    st.markdown(
        f'<div class="stat-row">'
        f'<div class="stat-tile"><div class="stat-num" style="color:#3b9eff">{total}</div>'
        f'<div class="stat-lbl">TOTAL</div></div>'
        f'<div class="stat-tile"><div class="stat-num" style="color:#22c55e">{granted}</div>'
        f'<div class="stat-lbl">GRANTED</div></div>'
        f'<div class="stat-tile"><div class="stat-num" style="color:#ef4444">{denied}</div>'
        f'<div class="stat-lbl">DENIED</div></div>'
        f'<div class="stat-tile"><div class="stat-num" style="color:#f59e0b">{overrides}</div>'
        f'<div class="stat-lbl">OVERRIDES</div></div>'
        f'</div>', unsafe_allow_html=True)

    # Filters
    fc1, fc2, fc3 = st.columns([2, 2, 3])
    with fc1:
        status_filter = st.selectbox("Status", ["All","Granted","Denied","Override"],
                                     label_visibility="collapsed", key="hist_status")
    with fc2:
        method_filter = st.selectbox("Method", ["All","Auto","Manual","Override"],
                                     label_visibility="collapsed", key="hist_method")
    with fc3:
        search = st.text_input("Search plate or name…", label_visibility="collapsed",
                               placeholder="Search plate or name…", key="hist_search")

    # Apply filters
    filtered = h
    if status_filter == "Granted":  filtered = [e for e in filtered if e["ok"]]
    elif status_filter == "Denied": filtered = [e for e in filtered if not e["ok"]]
    elif status_filter == "Override": filtered = [e for e in filtered if e.get("method")=="override"]
    if method_filter != "All":
        filtered = [e for e in filtered if e.get("method","").lower() == method_filter.lower()]
    if search.strip():
        q = search.strip().upper()
        filtered = [e for e in filtered if q in e.get("plate","").upper() or q in e.get("name","").upper()]

    if not filtered:
        st.markdown('<div class="card" style="text-align:center;padding:32px;color:#2a4060;">'
                    'No entries match the filter.</div>', unsafe_allow_html=True)
        return

    rows = ""
    for e in filtered[:100]:
        sc  = "b-grant" if e["ok"] else ("b-over" if e.get("method")=="override" else "b-deny")
        st_lbl = "GRANTED" if e["ok"] else ("OVERRIDE" if e.get("method")=="override" else "DENIED")
        mc  = "b-auto" if e.get("method","auto")=="auto" else ("b-over" if e.get("method")=="override" else "b-manual")
        rows += (
            f'<tr>'
            f'<td>{e.get("date","")} {e.get("time","")}</td>'
            f'<td><b>{e.get("plate","")}</b></td>'
            f'<td>{e.get("name","")[:20]}</td>'
            f'<td>{e.get("role","")}</td>'
            f'<td>{e.get("flat","")}</td>'
            f'<td><span class="badge {mc}">{e.get("method","auto").upper()}</span></td>'
            f'<td><span class="badge {sc}">{st_lbl}</span></td>'
            f'<td style="color:#4a6680;font-size:11px">{e.get("reason","")[:30]}</td>'
            f'</tr>'
        )
    st.markdown(
        f'<div class="log-wrap"><table class="log-tbl">'
        f'<tr><th>DATE · TIME</th><th>PLATE</th><th>NAME</th><th>ROLE</th>'
        f'<th>FLAT</th><th>METHOD</th><th>STATUS</th><th>REASON</th></tr>'
        f'{rows}</table></div>',
        unsafe_allow_html=True)

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    if st.session_state.history:
        st.download_button("⬇️ Export CSV", data=make_csv(),
                           file_name=f"gate_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                           mime="text/csv")

# ═══════════════════════════════════════════════════════════════════════════════
#  ██████  ADMIN — AUTHORISED USERS TAB
# ═══════════════════════════════════════════════════════════════════════════════
def tab_users():
    db = st.session_state.plate_db

    # ── Add user form ──────────────────────────────────────────────────────────
    with st.expander("➕  ADD NEW VEHICLE / USER", expanded=False):
        with st.form("add_user_form", clear_on_submit=True):
            r1c1, r1c2 = st.columns(2)
            with r1c1: new_plate = st.text_input("Plate Number *", max_chars=12)
            with r1c2: new_name  = st.text_input("Full Name *")
            r2c1, r2c2, r2c3 = st.columns(3)
            with r2c1: new_role = st.selectbox("Role", ["Resident","Visitor","Staff","Delivery"])
            with r2c2: new_flat = st.text_input("Flat / Unit", placeholder="A-204")
            with r2c3: new_car  = st.text_input("Vehicle Description", placeholder="Honda City Silver")
            if st.form_submit_button("✅ Register Vehicle", use_container_width=True):
                p = re.sub(r"[^A-Z0-9]","",new_plate.strip().upper())[:12]
                n = new_name.strip()
                if not p or not n:
                    st.error("Plate and Name are required.")
                elif p in db:
                    st.error(f"{p} is already registered.")
                else:
                    db[p] = {"name":n,"role":new_role,"flat":new_flat.strip() or "—",
                             "car":new_car.strip() or "—","active":True}
                    show_toast(f"✓ {p} — {n} registered", "ok")
                    st.rerun()

    # ── Edit form (shown when edit_plate is set) ───────────────────────────────
    if st.session_state.edit_plate and st.session_state.edit_plate in db:
        ep  = st.session_state.edit_plate
        rec = db[ep]
        st.markdown(f'<div class="card" style="border-color:#1a4a80;">'
                    f'<b style="font-family:JetBrains Mono,monospace;color:#3b9eff;">EDITING: {ep}</b></div>',
                    unsafe_allow_html=True)
        with st.form("edit_form"):
            ec1, ec2 = st.columns(2)
            with ec1: e_name = st.text_input("Name",  value=rec["name"])
            with ec2: e_role = st.selectbox("Role",   ["Resident","Visitor","Staff","Delivery"],
                                             index=["Resident","Visitor","Staff","Delivery"].index(
                                                 rec.get("role","Resident")))
            ec3, ec4 = st.columns(2)
            with ec3: e_flat = st.text_input("Flat",  value=rec["flat"])
            with ec4: e_car  = st.text_input("Vehicle", value=rec["car"])
            sb1, sb2 = st.columns(2)
            with sb1:
                if st.form_submit_button("💾 Save Changes", use_container_width=True):
                    db[ep].update({"name":e_name.strip(),"role":e_role,
                                   "flat":e_flat.strip(),"car":e_car.strip()})
                    st.session_state.edit_plate = None
                    show_toast(f"✓ {ep} updated", "ok")
                    st.rerun()
            with sb2:
                if st.form_submit_button("✕ Cancel", use_container_width=True):
                    st.session_state.edit_plate = None
                    st.rerun()

    # ── Filter ─────────────────────────────────────────────────────────────────
    uf1, uf2 = st.columns([3, 2])
    with uf1:
        user_search = st.text_input("Search users…", label_visibility="collapsed",
                                    placeholder="Search plate or name…", key="user_search")
    with uf2:
        role_filter = st.selectbox("Role filter", ["All","Resident","Visitor","Staff","Delivery"],
                                   label_visibility="collapsed", key="role_filter")

    filtered_db = {p: info for p, info in db.items()
                   if (not user_search or user_search.upper() in p or
                       user_search.lower() in info["name"].lower())
                   and (role_filter == "All" or info["role"] == role_filter)}

    st.markdown(f'<div style="font-family:JetBrains Mono,monospace;font-size:11px;'
                f'color:#4a6680;margin-bottom:8px;">{len(filtered_db)} user(s)</div>',
                unsafe_allow_html=True)

    for plate, info in filtered_db.items():
        active = info.get("active", True)
        act_color = "#22c55e" if active else "#4a6680"
        act_lbl   = "ACTIVE" if active else "INACTIVE"

        c_main, c_toggle, c_edit, c_del = st.columns([6, 1.5, 1, 1])
        with c_main:
            st.markdown(
                f'<div class="user-row">'
                f'<span class="user-plate">{plate}</span>'
                f'<div><div class="user-name">{info["name"]}</div>'
                f'<div class="user-meta">{info["role"]} · {info["flat"]} · {info["car"]}</div></div>'
                f'<span class="badge" style="color:{act_color};background:transparent;'
                f'border-color:{act_color};">{act_lbl}</span>'
                f'</div>', unsafe_allow_html=True)
        with c_toggle:
            tog_lbl = "Deactivate" if active else "Activate"
            if st.button(tog_lbl, key=f"tog_{plate}", use_container_width=True):
                db[plate]["active"] = not active
                show_toast(f"{'Deactivated' if active else 'Activated'}: {plate}", "warn" if active else "ok")
                st.rerun()
        with c_edit:
            if st.button("Edit", key=f"edit_{plate}", use_container_width=True):
                st.session_state.edit_plate = plate
                st.rerun()
        with c_del:
            if st.button("Del", key=f"del_{plate}", use_container_width=True):
                del st.session_state.plate_db[plate]
                show_toast(f"Deleted: {plate}", "err")
                if st.session_state.edit_plate == plate:
                    st.session_state.edit_plate = None
                st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
#  ██████  ADMIN — MANUAL OVERRIDE TAB
# ═══════════════════════════════════════════════════════════════════════════════
def tab_override():
    officer = st.session_state.current_user.upper()

    st.markdown(f'<div class="card-sm" style="margin-bottom:14px;">'
                f'<span style="font-family:JetBrains Mono,monospace;font-size:12px;color:#f59e0b;">⚠</span>'
                f'&nbsp;<span style="font-size:13px;color:#a0b4c8;">All overrides are logged with officer ID '
                f'<b style="color:#f59e0b">{officer}</b> and timestamped into Access History.</span>'
                f'</div>', unsafe_allow_html=True)

    # ── Custom plate override ──────────────────────────────────────────────────
    st.markdown("#### 🔑 Grant Access to Any Plate")
    with st.form("custom_override", clear_on_submit=True):
        oc1, oc2 = st.columns([3, 1])
        with oc1:
            custom_p = st.text_input("Plate number", placeholder="Enter any plate number",
                                     max_chars=12, label_visibility="collapsed")
        with oc2:
            if st.form_submit_button("GRANT ACCESS", use_container_width=True) and custom_p.strip():
                p  = re.sub(r"[^A-Z0-9]","",custom_p.strip().upper())[:12]
                now = datetime.now()
                entry = dict(
                    plate=p, ok=True, name=f"Override by {officer}",
                    role="Override", flat="—", car="—",
                    reason=f"Manual override by officer {officer}",
                    method="override",
                    time=now.strftime("%H:%M:%S"), date=now.strftime("%Y-%m-%d"),
                )
                st.session_state.log.insert(0, entry)
                st.session_state.history.insert(0, entry)
                show_toast(f"✓ Override granted: {p}", "warn")
                st.rerun()

    # ── Recent denied entries as quick-override cards ──────────────────────────
    st.markdown("#### ⚡ Recent Denied — Quick Override")
    denied_recent = [e for e in st.session_state.history if not e["ok"]
                     and e.get("method") != "override"][:10]

    if not denied_recent:
        st.markdown('<div class="card" style="text-align:center;padding:28px;color:#2a4060;">'
                    'No recent denied entries.</div>', unsafe_allow_html=True)
        return

    for e in denied_recent:
        c_info, c_btn = st.columns([5, 1.5])
        with c_info:
            st.markdown(
                f'<div class="ov-card">'
                f'<span class="ov-plate">{e["plate"]}</span>'
                f'<div class="ov-info">'
                f'<div class="ov-name">{e["name"]} &nbsp;·&nbsp; '
                f'<span style="color:#4a6680">{e["role"]}</span></div>'
                f'<div class="ov-time">{e["date"]} · {e["time"]} &nbsp;|&nbsp; '
                f'{e.get("reason","")[:40]}</div>'
                f'</div></div>',
                unsafe_allow_html=True)
        with c_btn:
            if st.button(f"OVERRIDE", key=f"ov_{e['plate']}_{e['time']}",
                         use_container_width=True):
                now = datetime.now()
                ov_entry = dict(
                    plate=e["plate"], ok=True,
                    name=f"Override by {officer} (was: {e['name']})",
                    role="Override", flat=e.get("flat","—"), car=e.get("car","—"),
                    reason=f"Manual override by officer {officer}",
                    method="override",
                    time=now.strftime("%H:%M:%S"), date=now.strftime("%Y-%m-%d"),
                )
                st.session_state.log.insert(0, ov_entry)
                st.session_state.history.insert(0, ov_entry)
                show_toast(f"✓ Override logged: {e['plate']}", "warn")
                st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
#  ██████  ADMIN SHELL  (nav + tabs)
# ═══════════════════════════════════════════════════════════════════════════════
def page_admin():
    tab = st.session_state.admin_tab

    # Nav bar (rendered as clickable columns)
    n1, n2, n3, n4, _, logout_col = st.columns([2,2,2,2,3,1.5])
    tabs_cfg = [
        (n1, "gate",    "🚗 Gate"),
        (n2, "history", "🕐 History"),
        (n3, "users",   "👥 Users"),
        (n4, "override","🔓 Override"),
    ]
    for col, key, label in tabs_cfg:
        with col:
            active_style = "background:#0e2240;border-color:#1a4a80;color:#3b9eff;" if tab==key \
                           else "background:transparent;border-color:#1a2d42;color:#4a6680;"
            if st.button(label, key=f"nav_{key}", use_container_width=True):
                st.session_state.admin_tab = key
                st.rerun()
    with logout_col:
        if st.button("Sign Out", use_container_width=True):
            st.session_state.logged_in    = False
            st.session_state.current_user = ""
            show_toast("Signed out", "info")
            st.rerun()

    # Tab content
    if tab == "gate":
        page_gate()
    elif tab == "history":
        tab_history()
    elif tab == "users":
        tab_users()
    elif tab == "override":
        tab_override()

# ═══════════════════════════════════════════════════════════════════════════════
#  ██████  ROUTER
# ═══════════════════════════════════════════════════════════════════════════════
render_topbar()
render_toast()

if not st.session_state.logged_in:
    page_login()
else:
    page_admin()