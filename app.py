# app.py — Fully Refactored S5.COM Lucky Draw

import streamlit as st
import pandas as pd
import random, time, json, base64, os

# ─── Helpers ─────────────────────────────────────────────────────────────────

ASSETS_DIR = "uploaded_assets"
SETTINGS_FILE = "draw_settings.json"
WINNERS_FILE = "winners.csv"
os.makedirs(ASSETS_DIR, exist_ok=True)

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        return json.load(open(SETTINGS_FILE))
    return {}

def save_settings(s):
    json.dump(s, open(SETTINGS_FILE, "w"))

def encode_file(upload):
    """Read and return base64 + extension, without draining buffer."""
    data = upload.read()
    upload.seek(0)
    return base64.b64encode(data).decode(), upload.name.split(".")[-1].lower()

# ─── Streamlit Page Setup ────────────────────────────────────────────────────

st.set_page_config("🎰 S5.COM Lucky Draw", layout="wide")
st.title("🎰 S5.COM Lucky Draw")
settings = load_settings()

# ─── Sidebar ─────────────────────────────────────────────────────────────────

st.sidebar.header("🎨 Upload Assets")
logo_up = st.sidebar.file_uploader("Logo", type=["png","jpg","jpeg"], key="logo_up")
bg_up   = st.sidebar.file_uploader("Background\n(img/gif/mp4)", type=["png","jpg","jpeg","gif","mp4"], key="bg_up")
csv_up  = st.sidebar.file_uploader("Names CSV", type=["csv"], key="csv_up")
dr_up   = st.sidebar.file_uploader("Drumroll", type=["mp3","wav"], key="drum_up")
cr_up   = st.sidebar.file_uploader("Crash FX", type=["mp3","wav"], key="crash_up")
ap_up   = st.sidebar.file_uploader("Applause", type=["mp3","wav"], key="applause_up")

st.sidebar.markdown("---")
st.sidebar.header("🎯 Draw Controls")
winner_count    = st.sidebar.number_input("Number of Winners", 1, 10, settings.get("winner_count", 3), key="wc")
draw_duration   = st.sidebar.number_input("Duration (sec)", 1.0, 60.0, settings.get("draw_duration", 10.0), key="dd")
animation       = st.sidebar.selectbox("Animation Style", ["Scrolling","Rolodex","Letter-by-Letter","Fade In","Slide In"], key="anim")
rolodex_speed   = st.sidebar.slider("Rolodex Speed (px/frame)", 1, 50, settings.get("rolodex_speed", 20), key="rs")
rolodex_interval= st.sidebar.slider("Rolodex Interval (s)", 0.05, 0.5, settings.get("rolodex_int", 0.1), key="ri")

st.sidebar.markdown("---")
st.sidebar.header("🔤 Appearance")
font_size       = st.sidebar.slider("Font Size (px)", 20, 100, settings.get("font_size", 48), key="fs")
font_color      = st.sidebar.color_picker("Font Color", settings.get("font_color","#FFFFFF"), key="fc")
backdrop_color  = st.sidebar.color_picker("Backdrop Color", settings.get("backdrop_color","#000000"), key="bc")
backdrop_op     = st.sidebar.slider("Backdrop Opacity", 0.0, 1.0, settings.get("backdrop_op",0.5), key="bo")
backdrop_pad    = st.sidebar.slider("Backdrop Padding", 0, 50, settings.get("backdrop_pad",10), key="bp")

st.sidebar.markdown("---")
st.sidebar.header("⏱️ Timers")
show_left       = st.sidebar.checkbox("Left Timer", value=settings.get("show_left",True), key="sl")
show_right      = st.sidebar.checkbox("Right Timer",value=settings.get("show_right",True), key="sr")

st.sidebar.markdown("---")
st.sidebar.header("🔊 Audio & Effects")
volume          = st.sidebar.slider("Volume", 0, 100, settings.get("vol",80), key="vol")
mute            = st.sidebar.checkbox("Mute", value=settings.get("mute",False), key="mute")
confetti        = st.sidebar.checkbox("Confetti", value=settings.get("confetti",True), key="confetti")

st.sidebar.markdown("---")
start_btn       = st.sidebar.button("🎲 Start Draw", key="start")
restart_btn     = st.sidebar.button("🔄 Restart", key="restart")
export_btn      = st.sidebar.button("📥 Export Winners", key="export")

# Save sidebar settings
save_settings({
    "winner_count": winner_count, "draw_duration": draw_duration,
    "rolodex_speed": rolodex_speed, "rolodex_int": rolodex_interval,
    "font_size": font_size, "font_color": font_color,
    "backdrop_color": backdrop_color, "backdrop_op": backdrop_op,
    "backdrop_pad": backdrop_pad, "show_left": show_left,
    "show_right": show_right, "vol": volume, "mute": mute,
    "confetti": confetti
})

# ─── State Reset ───────────────────────────────────────────────────────────────

if restart_btn:
    for k in ["start","drum_b64","crash_b64","applause_b64","name_col","names","winners"]:
        st.session_state.pop(k, None)
    st.experimental_rerun()

# ─── Pre-encode Media (persist in session_state) ──────────────────────────────

def load_media(key, uploader):
    if uploader and key not in st.session_state:
        b64, ext = encode_file(uploader)
        st.session_state[key] = (b64, ext)
    return st.session_state.get(key, (None,None))

drum_b64, drum_ext   = load_media("drum_b64", drum_up)
crash_b64, crash_ext = load_media("crash_b64", cr_up)
appl_b64, appl_ext   = load_media("appl_b64", ap_up)
logo_b64, logo_ext   = load_media("logo_b64", logo_up)
bg_b64, bg_ext       = load_media("bg_b64", bg_up)

# ─── Start Draw ────────────────────────────────────────────────────────────────

if start_btn:
    # 1) Load CSV & detect columns
    df = pd.read_csv(csv_up) if csv_up else pd.DataFrame()
    name_col = next((c for c in df.columns if c.lower()=="name"), None)
    id_col   = next((c for c in df.columns if c.lower() in ("id","uid")), None)
    acc_col  = next((c for c in df.columns if "account" in c.lower()), None)
    if name_col is None or df.empty:
        st.error("CSV needs a 'name' column")
        st.stop()
    names = df[name_col].dropna().tolist()

    # 2) Prepare HTML snippets
    bg_html = ""
    if bg_b64:
        if bg_ext in ("mp4","webm"):
            bg_html = f"""<video class="background" autoplay loop muted style="position:absolute;top:0;left:0;width:100%;height:100%;object-fit:cover;opacity: {backdrop_op};"><source src="data:video/{bg_ext};base64,{bg_b64}"></video>"""
        else:
            bg_html = f"""<div style="position:absolute;top:0;left:0;width:100%;height:100%;background:url('data:image/{bg_ext};base64,{bg_b64}') center/cover;opacity:{backdrop_op};"></div>"""
    logo_html = f"""<img src="data:image/{logo_ext};base64,{logo_b64}" style="position:absolute;top:10px;left:10px;width: {settings.get('logo_width',150)}px;z-index:2;">""" if logo_b64 else ""

    # 3) Placeholders
    draw_ph   = st.empty()
    audio_ph  = st.empty()

    # 4) Play drumroll
    if not mute and drum_b64:
        audio_ph.markdown(f"""<audio autoplay loop><source src="data:audio/{drum_ext};base64,{drum_b64}"></audio>""", unsafe_allow_html=True)

    # 5) Draw loop
    start_t = time.time()
    while (elapsed:=time.time()-start_t) < draw_duration:
        rem = draw_duration - elapsed
        # Select name per style
        if animation=="Scrolling":
            disp_name = random.choice(names)
        elif animation=="Rolodex":
            disp_name = names[int(elapsed/rolodex_interval)%len(names)]
        elif animation=="Letter-by-Letter":
            full = random.choice(names)
            pos = int((elapsed/draw_duration)*len(full))
            disp_name = full[:pos+1]
        elif animation=="Fade In":
            disp_name = random.choice(names)
        else:  # Slide In
            disp_name = random.choice(names)

        # 6) Build timers
        left_timer = f"<div style='position:absolute;left:10px;top:50%;transform:translateY(-50%);font-size:24px;color:{font_color};'>{int(rem)}</div>" if show_left else ""
        right_timer= f"<div style='position:absolute;right:10px;top:50%;transform:translateY(-50%);font-size:24px;color:{font_color};'>{int(rem)}</div>" if show_right else ""

        # 7) Render frame
        draw_ph.markdown(f"""
        <div style="position:relative;width:100%;height:100vh;display:flex;align-items:center;justify-content:center;">
            {bg_html}
            {logo_html}
            {left_timer}{right_timer}
            <div style="position:relative;z-index:3;padding:{backdrop_pad}px;background:{backdrop_color};color:{font_color};font-size:{font_size}px;border-radius:10px;">
                {disp_name}
            </div>
        </div>
        """, unsafe_allow_html=True)

        time.sleep(0.1)

    # 8) End sounds
    audio_ph.empty()
    if not mute and crash_b64:
        audio_ph.markdown(f"""<audio autoplay><source src="data:audio/{crash_ext};base64,{crash_b64}"></audio>""", unsafe_allow_html=True)
    if not mute and appl_b64:
        audio_ph.markdown(f"""<audio autoplay><source src="data:audio/{appl_ext};base64,{appl_b64}"></audio>""", unsafe_allow_html=True)

    # 9) Final winners
    winners = df.sample(n=winner_count)
    st.balloons() if confetti else None

    final_html = "<br>".join(
        " | ".join(
            str(row[col]) for col in (id_col,name_col,acc_col) if col
        )
        for _, row in winners.iterrows()
    )
    draw_ph.markdown(f"""
    <div style="position:relative;width:100%;height:100vh;display:flex;align-items:center;justify-content:center;">
        {bg_html}
        {logo_html}
        <div style="position:relative;z-index:3;padding:{backdrop_pad}px;background:{backdrop_color};color:{font_color};font-size:{font_size+10}px;border-radius:10px;">
            {final_html}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 10) Save winners
    pd.DataFrame(winners).to_csv(WINNERS_FILE, index=False)

# ─── Export ───────────────────────────────────────────────────────────────────

if export_btn and os.path.exists(WINNERS_FILE):
    st.sidebar.download_button("Download Winners CSV", open(WINNERS_FILE,"rb"), file_name="winners.csv")
