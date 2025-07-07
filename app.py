# app.py — Fully Refactored S5.COM Lucky Draw

import streamlit as st
import pandas as pd
import random
import time
import json
import base64
import os

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
    with open(SETTINGS_FILE, "w") as f:
        json.dump(s, f)

def encode_file(upload):
    data = upload.read()
    upload.seek(0)
    return base64.b64encode(data).decode(), upload.name.split(".")[-1].lower()

# ─── Page Setup ───────────────────────────────────────────────────────────────

st.set_page_config("🎰 S5.COM Lucky Draw", layout="wide")
st.title("🎰 S5.COM Lucky Draw")
settings = load_settings()

# ─── Sidebar ─────────────────────────────────────────────────────────────────

st.sidebar.header("🎨 Upload Assets")
logo_up = st.sidebar.file_uploader("Logo", type=["png","jpg","jpeg"], key="logo_up")
bg_up   = st.sidebar.file_uploader("Background (img/gif/mp4)", type=["png","jpg","jpeg","gif","mp4","webm"], key="bg_up")
csv_up  = st.sidebar.file_uploader("Names CSV", type=["csv"], key="csv_up")
drum_up = st.sidebar.file_uploader("Drumroll", type=["mp3","wav"], key="drum_up")
crash_up= st.sidebar.file_uploader("Crash FX", type=["mp3","wav"], key="crash_up")
ap_up   = st.sidebar.file_uploader("Applause", type=["mp3","wav"], key="applause_up")

st.sidebar.markdown("---")
st.sidebar.header("🎯 Draw Controls")
winner_count    = st.sidebar.number_input(
    "Number of Winners", 1, 10,
    value=settings.get("winner_count", 3),
    key="winner_count"
)
draw_duration   = st.sidebar.number_input(
    "Duration (sec)", 1.0, 60.0,
    value=float(settings.get("draw_duration", 10.0)),
    step=0.1,
    format="%.1f",
    key="draw_duration"
)
animation       = st.sidebar.selectbox(
    "Animation Style",
    ["Scrolling","Rolodex","Letter-by-Letter","Fade In","Slide In"],
    index=["Scrolling","Rolodex","Letter-by-Letter","Fade In","Slide In"].index(settings.get("animation","Scrolling")),
    key="animation"
)
rolodex_speed   = st.sidebar.slider(
    "Rolodex Speed (px/frame)", 1, 50,
    value=settings.get("rolodex_speed", 20),
    key="rolodex_speed"
)
rolodex_interval= st.sidebar.slider(
    "Rolodex Interval (s)", 0.05, 0.5,
    value=settings.get("rolodex_interval", 0.1),
    key="rolodex_interval"
)

st.sidebar.markdown("---")
st.sidebar.header("🔤 Appearance")
font_size       = st.sidebar.slider(
    "Font Size (px)", 20, 100,
    value=settings.get("font_size", 48),
    key="font_size"
)
font_color      = st.sidebar.color_picker(
    "Font Color", settings.get("font_color", "#FFFFFF"),
    key="font_color"
)
backdrop_color  = st.sidebar.color_picker(
    "Backdrop Color", settings.get("backdrop_color", "#000000"),
    key="backdrop_color"
)
backdrop_op     = st.sidebar.slider(
    "Backdrop Opacity", 0.0, 1.0,
    value=settings.get("backdrop_opacity", 0.5),
    key="backdrop_opacity"
)
backdrop_pad    = st.sidebar.slider(
    "Backdrop Padding", 0, 50,
    value=settings.get("backdrop_padding", 10),
    key="backdrop_padding"
)

st.sidebar.markdown("---")
st.sidebar.header("⏱️ Timers")
show_left       = st.sidebar.checkbox(
    "Show Left Timer", value=settings.get("show_left", True),
    key="show_left"
)
show_right      = st.sidebar.checkbox(
    "Show Right Timer", value=settings.get("show_right", True),
    key="show_right"
)

st.sidebar.markdown("---")
st.sidebar.header("🔊 Audio & Effects")
volume          = st.sidebar.slider(
    "Volume (%)", 0, 100,
    value=settings.get("volume", 80),
    key="volume"
)
mute            = st.sidebar.checkbox(
    "Mute All Audio", value=settings.get("mute", False),
    key="mute"
)
confetti        = st.sidebar.checkbox(
    "Show Confetti", value=settings.get("confetti", True),
    key="confetti"
)

st.sidebar.markdown("---")
start_btn       = st.sidebar.button("🎲 Start Draw", key="start")
restart_btn     = st.sidebar.button("🔄 Restart", key="restart")
export_btn      = st.sidebar.button("📥 Export Winners", key="export")

# Save sidebar settings
save_settings({
    "winner_count": winner_count,
    "draw_duration": draw_duration,
    "animation": animation,
    "rolodex_speed": rolodex_speed,
    "rolodex_interval": rolodex_interval,
    "font_size": font_size,
    "font_color": font_color,
    "backdrop_color": backdrop_color,
    "backdrop_opacity": backdrop_op,
    "backdrop_padding": backdrop_pad,
    "show_left": show_left,
    "show_right": show_right,
    "volume": volume,
    "mute": mute,
    "confetti": confetti
})

# ─── Reset State ───────────────────────────────────────────────────────────────

if restart_btn:
    for key in ["start", "drum_b64", "crash_b64", "appl_b64", "names", "name_col"]:
        st.session_state.pop(key, None)
    st.experimental_rerun()

# ─── Pre-encode Media ──────────────────────────────────────────────────────────

def load_media(session_key, uploader):
    if uploader and session_key not in st.session_state:
        b64, ext = encode_file(uploader)
        st.session_state[session_key] = (b64, ext)
    return st.session_state.get(session_key, (None, None))

drum_b64, drum_ext   = load_media("drum_b64", drum_up)
crash_b64, crash_ext = load_media("crash_b64", crash_up)
appl_b64, appl_ext   = load_media("appl_b64", ap_up)
logo_b64, logo_ext   = load_media("logo_b64", logo_up)
bg_b64, bg_ext       = load_media("bg_b64", bg_up)

# ─── Run Draw ─────────────────────────────────────────────────────────────────

if start_btn:
    # Load and validate CSV
    if not csv_up:
        st.error("Please upload a Names CSV.")
        st.stop()
    df = pd.read_csv(csv_up)
    name_col = next((c for c in df.columns if c.lower() == "name"), None)
    id_col   = next((c for c in df.columns if c.lower() in ("id","uid")), None)
    acc_col  = next((c for c in df.columns if "account" in c.lower()), None)
    if name_col is None:
        st.error("CSV must contain a 'name' column.")
        st.stop()
    names = df[name_col].dropna().tolist()

    # Prepare HTML snippets
    if bg_b64:
        if bg_ext in ("mp4","webm"):
            bg_html = f"""<video autoplay loop muted style="position:absolute;top:0;left:0;width:100%;height:100%;object-fit:cover;opacity:{backdrop_op};"><source src="data:video/{bg_ext};base64,{bg_b64}"></video>"""
        else:
            bg_html = f"""<div style="position:absolute;top:0;left:0;width:100%;height:100%;background:url('data:image/{bg_ext};base64,{bg_b64}') center/cover;opacity:{backdrop_op};"></div>"""
    else:
        bg_html = ""
    logo_html = f"""<img src="data:image/{logo_ext};base64,{logo_b64}" style="position:absolute;top:10px;left:10px;width:{settings.get('logo_width',150)}px;z-index:2;">""" if logo_b64 else ""

    draw_ph  = st.empty()
    audio_ph = st.empty()

    # Play drumroll
    if not mute and drum_b64:
        audio_ph.markdown(f"""<audio autoplay loop><source src="data:audio/{drum_ext};base64,{drum_b64}"></audio>""", unsafe_allow_html=True)

    # Draw loop
    start_t = time.time()
    while (elapsed := time.time() - start_t) < draw_duration:
        rem = draw_duration - elapsed
        # Animation styles
        if animation == "Scrolling":
            disp = random.choice(names)
        elif animation == "Rolodex":
            idx = int(elapsed / rolodex_interval) % len(names)
            disp = names[idx]
        elif animation == "Letter-by-Letter":
            full = random.choice(names)
            pos = int((elapsed / draw_duration) * len(full))
            disp = full[: pos + 1]
        elif animation == "Fade In":
            disp = random.choice(names)
        else:  # Slide In
            disp = random.choice(names)

        # Timers
        left_t = f"<div style='position:absolute;left:10px;top:50%;transform:translateY(-50%);font-size:24px;color:{font_color};'>{int(rem)}</div>" if show_left else ""
        right_t= f"<div style='position:absolute;right:10px;top:50%;transform:translateY(-50%);font-size:24px;color:{font_color};'>{int(rem)}</div>" if show_right else ""

        # Render frame
        draw_ph.markdown(f"""
        <div style="position:relative;width:100%;height:100vh;display:flex;align-items:center;justify-content:center;">
            {bg_html}
            {logo_html}
            {left_t}{right_t}
            <div style="position:relative;z-index:3;padding:{backdrop_pad}px;background:{backdrop_color};color:{font_color};font-size:{font_size}px;border-radius:10px;">
                {disp}
            </div>
        </div>
        """, unsafe_allow_html=True)

        time.sleep(0.1)

    # End sounds
    audio_ph.empty()
    if not mute and crash_b64:
        audio_ph.markdown(f"""<audio autoplay><source src="data:audio/{crash_ext};base64,{crash_b64}"></audio>""", unsafe_allow_html=True)
    if not mute and appl_b64:
        audio_ph.markdown(f"""<audio autoplay><source src="data:audio/{appl_ext};base64,{appl_b64}"></audio>""", unsafe_allow_html=True)

    # Final winners
    winners = df.sample(n=winner_count)
    if confetti:
        st.balloons()

    final_html = "<br>".join(
        " | ".join(str(row[col]) for col in (id_col, name_col, acc_col) if col)
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

    # Save winners
    pd.DataFrame(winners).to_csv(WINNERS_FILE, index=False)

# ─── Export ───────────────────────────────────────────────────────────────────

if export_btn and os.path.exists(WINNERS_FILE):
    st.sidebar.download_button("Download Winners CSV", open(WINNERS_FILE, "rb"), file_name="winners.csv")
