# S5.COM Lucky Draw – Fully Fixed & Organized

import streamlit as st
import pandas as pd
import random
import json
import time
import base64
import os

# --- Configuration ---
st.set_page_config("🎰 S5.COM Lucky Draw", layout="wide")
ASSETS_DIR = "uploaded_assets"
SETTINGS_FILE = "draw_settings.json"
WINNERS_FILE = "winners.csv"
os.makedirs(ASSETS_DIR, exist_ok=True)

# --- Helpers ---
def save_file(upload, name):
    if not upload:
        return None
    ext = upload.name.split('.')[-1]
    path = os.path.join(ASSETS_DIR, f"{name}.{ext}")
    with open(path, "wb") as f:
        f.write(upload.getbuffer())
    return path

# Load/save persistent settings
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        return json.load(open(SETTINGS_FILE))
    return {}

def save_settings(settings):
    json.dump(settings, open(SETTINGS_FILE, 'w'))

# --- Sidebar Controls ---
saved = load_settings()
st.sidebar.title("🔧 Settings & Controls")

# Uploads
logo_up = st.sidebar.file_uploader("Logo (png/jpg)", type=["png","jpg","jpeg"])
bg_up = st.sidebar.file_uploader("Background (img/gif/mp4)", type=["png","jpg","jpeg","gif","mp4"])
csv_up = st.sidebar.file_uploader("CSV (ID,Name,Account)", type=["csv"])
drum_up = st.sidebar.file_uploader("Drumroll Sound", type=["mp3","wav"])
crash_up = st.sidebar.file_uploader("Crash Sound", type=["mp3","wav"])
applause_up = st.sidebar.file_uploader("Applause Sound", type=["mp3","wav"])

st.sidebar.markdown("---")
# Display columns
show_id = st.sidebar.checkbox("Show ID", value=saved.get("show_id", True))
show_name = st.sidebar.checkbox("Show Name", value=saved.get("show_name", True))
show_account = st.sidebar.checkbox("Show Account", value=saved.get("show_account", True))

st.sidebar.markdown("---")
# Appearance
display_font_size = st.sidebar.slider("Font Size (px)", 20, 120, saved.get("font_size", 48))
display_font_color = st.sidebar.color_picker("Font Color", value=saved.get("font_color", "#FFFFFF"))
backdrop_color = st.sidebar.color_picker("Backdrop Color", value=saved.get("backdrop_color", "#000000"))
backdrop_opacity = st.sidebar.slider("Backdrop Opacity", 0.0, 1.0, saved.get("backdrop_opacity", 0.5))
backdrop_padding = st.sidebar.slider("Backdrop Padding (px)", 0, 50, saved.get("backdrop_padding", 10))
winner_offset = st.sidebar.slider("Winner Y Offset (px)", 0, 600, saved.get("winner_offset", 200))

st.sidebar.markdown("---")
# Draw settings
draw_duration = st.sidebar.slider("Draw Duration (sec)", 5, 60, saved.get("draw_time", 15))
winner_count = st.sidebar.slider("Number of Winners", 1, 10, saved.get("winner_count", 3))

st.sidebar.markdown("---")
# Audio & Effects
audio_volume = st.sidebar.slider("Audio Volume (%)", 0, 100, saved.get("audio_volume", 70))
mute_audio = st.sidebar.checkbox("Mute Audio", value=saved.get("mute_audio", False))
show_confetti = st.sidebar.checkbox("Show Confetti", value=saved.get("show_confetti", False))

st.sidebar.markdown("---")
# Actions
start_draw = st.sidebar.button("🎲 Start Draw")
export_csv = st.sidebar.button("📥 Export Winners CSV")
save_btn = st.sidebar.button("💾 Save Settings")

# Save sidebar settings\if save_btn:
    save_settings({
        "show_id": show_id,
        "show_name": show_name,
        "show_account": show_account,
        "font_size": display_font_size,
        "font_color": display_font_color,
        "backdrop_color": backdrop_color,
        "backdrop_opacity": backdrop_opacity,
        "backdrop_padding": backdrop_padding,
        "winner_offset": winner_offset,
        "draw_time": draw_duration,
        "winner_count": winner_count,
        "audio_volume": audio_volume,
        "mute_audio": mute_audio,
        "show_confetti": show_confetti
    })
    st.sidebar.success("Settings saved!")

# --- CSS customizations ---
css = f"""
<style>
.draw-container {{ position: relative; width:100%; height:600px; text-align:center; }}
.background-img, .background-vid {{ position:absolute; top:0; left:0; width:100%; height:100%; object-fit:cover; opacity:0.5; z-index:0; }}
.logo-img {{ position:absolute; top:10px; left:10px; width:{display_font_size*1.5}px; z-index:2; }}
.winner-backdrop {{ display:inline-block; padding:{backdrop_padding}px; background:rgba({int(backdrop_color[1:3],16)},{int(backdrop_color[3:5],16)},{int(backdrop_color[5:],16)},{backdrop_opacity}); border-radius:10px; z-index:3; }}
.winner-name {{ font-size:{display_font_size}px; color:{display_font_color}; margin-top:{winner_offset}px; z-index:4; font-weight:bold; }}
.timer {{ font-size:24px; color:{display_font_color}; margin-top:20px; z-index:3; }}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# --- Save uploaded assets ---
logo_path = save_file(logo_up, "logo")
bg_path = save_file(bg_up, "background")
dr_path = save_file(drum_up, "drumroll")
cr_path = save_file(crash_up, "crash")
ap_path = save_file(applause_up, "applause")

# Export winners file\if export_csv and os.path.exists(WINNERS_FILE):
    with open(WINNERS_FILE, 'rb') as f:
        st.sidebar.download_button("Download Winners", f, file_name="winners.csv")

# --- Main placeholders ---
bg_placeholder = st.empty()
logo_placeholder = st.empty()
scroll_placeholder = st.empty()
timer_placeholder = st.empty()
audio_placeholder = st.empty()

# --- Draw Logic ---
if start_draw and csv_up:
    df = pd.read_csv(csv_up)
    # Detect columns\ n    id_col   = next((c for c in df.columns if c.lower()=="id"), None)
    name_col = next((c for c in df.columns if c.lower()=="name"), None)
    acc_col  = next((c for c in df.columns if "account" in c.lower()), None)
    if not name_col:
        st.error("CSV must contain a 'Name' column.")
        st.stop()

    # Display background
    if bg_path:
        ext = bg_path.split('.')[-1].lower()
        data = base64.b64encode(open(bg_path,'rb').read()).decode()
        if ext in ['mp4','webm']:
            bg_placeholder.markdown(f"<video autoplay loop muted class='background-vid'><source src='data:video/{ext};base64,{data}' type='video/{ext}'></video>", unsafe_allow_html=True)
        else:
            bg_placeholder.markdown(f"<img src='data:image/{ext};base64,{data}' class='background-img'>", unsafe_allow_html=True)

    # Display logo
    if logo_path:
        ext = logo_path.split('.')[-1].lower()
        data = base64.b64encode(open(logo_path,'rb').read()).decode()
        logo_placeholder.markdown(f"<img src='data:image/{ext};base64,{data}' class='logo-img'>", unsafe_allow_html=True)

    # Play drumroll\ n    if not mute_audio and dr_path:
        b = base64.b64encode(open(dr_path,'rb').read()).decode()
        audio_placeholder.markdown(f"<audio autoplay loop><source src='data:audio/mp3;base64,{b}'></audio>", unsafe_allow_html=True)

    # Scrolling
    names = df[name_col].dropna().tolist()
    seq = names*2
    delay = draw_duration / len(seq)
    for n in seq:
        scroll_placeholder.markdown(f"<div class='draw-container'><div class='winner-backdrop'><div class='winner-name'>{n}</div></div></div>", unsafe_allow_html=True)
        timer_placeholder.markdown(f"<div class='timer'>Drawing...</div>", unsafe_allow_html=True)
        time.sleep(delay)

    # Final winners
    winners = df.sample(n=winner_count)
    audio_placeholder.empty()
    if not mute_audio and cr_path:
        b = base64.b64encode(open(cr_path,'rb').read()).decode()
        st.markdown(f"<audio autoplay><source src='data:audio/mp3;base64,{b}'></audio>", unsafe_allow_html=True)
    if not mute_audio and ap_path:
        b = base64.b64encode(open(ap_path,'rb').read()).decode()
        st.markdown(f"<audio autoplay><source src='data:audio/mp3;base64,{b}'></audio>", unsafe_allow_html=True)

    # Display winners
    for _,r in winners.iterrows():
        parts = []
        if show_id and id_col: parts.append(str(r[id_col]))
        if show_name: parts.append(str(r[name_col]))
        if show_account and acc_col: parts.append(str(r[acc_col]))
        text = " | ".join(parts)
        scroll_placeholder.markdown(f"<div class='draw-container'><div class='winner-backdrop'><div class='winner-name'>{text}</div></div></div>", unsafe_allow_html=True)

    timer_placeholder.empty()
    winners.to_csv(WINNERS_FILE, index=False)
