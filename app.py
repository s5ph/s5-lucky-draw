# S5.COM Lucky Draw – Complete and Reorganized

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

# --- Helper Functions ---
def save_uploaded_file(upload, name_prefix):
    if upload is None:
        return None
    ext = upload.name.split(".")[-1]
    path = os.path.join(ASSETS_DIR, f"{name_prefix}.{ext}")
    with open(path, "wb") as f:
        f.write(upload.getbuffer())
    return path

# Load or save persistent settings
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        return json.load(open(SETTINGS_FILE))
    return {}

def save_settings(settings):
    json.dump(settings, open(SETTINGS_FILE, "w"))

# --- Sidebar Controls ---
saved = load_settings()

st.sidebar.title("🔧 Settings & Controls")
# Uploads
st.sidebar.markdown("**Uploads**")
logo_upload = st.sidebar.file_uploader("Logo (PNG/JPG)", type=["png", "jpg", "jpeg"])
bg_upload = st.sidebar.file_uploader("Background (Image/GIF/Video)", type=["png","jpg","jpeg","gif","mp4","webm"])
csv_upload = st.sidebar.file_uploader("CSV File (ID, Name, Account)", type=["csv"])
drumroll_upload = st.sidebar.file_uploader("Drumroll Sound", type=["mp3","wav"])
crash_upload = st.sidebar.file_uploader("Crash Sound", type=["mp3","wav"])
applause_upload = st.sidebar.file_uploader("Applause Sound", type=["mp3","wav"])

# Display Options
st.sidebar.markdown("---")
st.sidebar.markdown("**Display Columns**")
show_id = st.sidebar.checkbox("Show ID", value=saved.get("show_id", True))
show_name = st.sidebar.checkbox("Show Name", value=saved.get("show_name", True))
show_account = st.sidebar.checkbox("Show Account", value=saved.get("show_account", True))

# Appearance
st.sidebar.markdown("---")
st.sidebar.markdown("**Appearance**")
font_size = st.sidebar.slider("Font Size (px)", 20, 120, saved.get("font_size", 48))
font_color = st.sidebar.color_picker("Font Color", saved.get("font_color", "#FFFFFF"))
backdrop_color = st.sidebar.color_picker("Backdrop Color", saved.get("backdrop_color", "#000000"))
backdrop_opacity = st.sidebar.slider("Backdrop Opacity", 0.0, 1.0, saved.get("backdrop_opacity", 0.5))
backdrop_padding = st.sidebar.slider("Backdrop Padding (px)", 0, 50, saved.get("backdrop_padding", 10))
winner_offset = st.sidebar.slider("Winner Y Offset (px)", 0, 600, saved.get("winner_offset", 200))

# Draw Settings
draw_time = st.sidebar.slider("Draw Duration (sec)", 5, 60, saved.get("draw_time", 15))
winner_count = st.sidebar.slider("Number of Winners", 1, 10, saved.get("winner_count", 3))

# Audio & Effects
audio_volume = st.sidebar.slider("Audio Volume (%)", 0, 100, saved.get("audio_volume", 70))
mute_audio = st.sidebar.checkbox("Mute Audio", value=saved.get("mute_audio", False))
show_confetti = st.sidebar.checkbox("Show Confetti", value=saved.get("show_confetti", False))

# Control Buttons
start = st.sidebar.button("🎲 Start Draw")
export = st.sidebar.button("📥 Export Winners CSV")
save_btn = st.sidebar.button("💾 Save Settings")

# Save settings
if save_btn:
    save_settings({
        "show_id": show_id,
        "show_name": show_name,
        "show_account": show_account,
        "font_size": font_size,
        "font_color": font_color,
        "backdrop_color": backdrop_color,
        "backdrop_opacity": backdrop_opacity,
        "backdrop_padding": backdrop_padding,
        "winner_offset": winner_offset,
        "draw_time": draw_time,
        "winner_count": winner_count,
        "audio_volume": audio_volume,
        "mute_audio": mute_audio,
        "show_confetti": show_confetti
    })
    st.sidebar.success("Settings saved!")

# --- Main Display CSS ---
css = f"""
<style>
.draw-container {{ position: relative; width:100%; height:600px; text-align:center; }}
.background-img, .background-vid {{ position:absolute; top:0; left:0; width:100%; height:100%; object-fit:cover; opacity:0.5; z-index:0; }}
.logo-img {{ position:absolute; z-index:2; top:10px; left:10px; width:{font_size*1.5}px; }}
.winner-backdrop {{ display:inline-block; padding:{backdrop_padding}px; background:rgba({int(backdrop_color[1:3],16)},{int(backdrop_color[3:5],16)},{int(backdrop_color[5:],16)},{backdrop_opacity}); border-radius:10px; z-index:3; }}
.winner-name {{ font-size:{font_size}px; color:{font_color}; margin-top:{winner_offset}px; z-index:4; font-weight:bold; }}
.timer {{ font-size:24px; font-weight:bold; color:{font_color}; margin-top:20px; z-index:3; }}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# --- Upload Assets ---
logo_path = save_uploaded_file(logo_upload, "logo")
bg_path = save_uploaded_file(bg_upload, "background")
# sounds not saved to disk; we'll embed directly

# --- Export Winners ---
if export and os.path.exists(WINNERS_FILE):
    with open(WINNERS_FILE, "rb") as f:
        st.sidebar.download_button("Download Winners CSV", f, file_name="winners.csv")

# --- Run Draw Logic ---
if start and csv_upload is not None:
    df = pd.read_csv(csv_upload)
    id_col = next((c for c in df.columns if c.lower() == 'id'), None)
    name_col = next((c for c in df.columns if c.lower() == 'name'), None)
    acc_col = next((c for c in df.columns if 'account' in c.lower()), None)
    if df.empty or name_col is None:
        st.error("CSV must contain a 'Name' column.")
    else:
        # Prepare placeholders
        disp = st.empty()
        timer = st.empty()
        audio_ph = st.empty()
        # Load background bytes
        if bg_upload:
            bg_bytes = bg_upload.read()
            b_ext = bg_upload.name.split('.')[-1].lower()
        elif bg_path and os.path.exists(bg_path):
            bg_bytes = open(bg_path,'rb').read()
            b_ext = bg_path.split('.')[-1].lower()
        else:
            bg_bytes = None
            b_ext = None
        # Load logo bytes
        if logo_upload:
            logo_bytes = logo_upload.read()
            l_ext = logo_upload.name.split('.')[-1].lower()
        elif logo_path and os.path.exists(logo_path):
            logo_bytes = open(logo_path,'rb').read()
            l_ext = logo_path.split('.')[-1].lower()
        else:
            logo_bytes = None
            l_ext = None
        # Display background and logo
        if bg_bytes:
            encoded_bg = base64.b64encode(bg_bytes).decode()
            if b_ext in ['mp4','webm']:
                disp.markdown(f"<video autoplay loop muted class='background-vid'><source src='data:video/{b_ext};base64,{encoded_bg}' type='video/{b_ext}'></video>", unsafe_allow_html=True)
            else:
                disp.markdown(f"<img src='data:image/{b_ext};base64,{encoded_bg}' class='background-img'>", unsafe_allow_html=True)
        if logo_bytes:
            encoded_logo = base64.b64encode(logo_bytes).decode()
            disp.markdown(f"<img src='data:image/{l_ext};base64,{encoded_logo}' class='logo-img'>", unsafe_allow_html=True)
        # Play drumroll
        if not mute_audio and drumroll_upload:
            drum_bytes = drumroll_upload.read()
            drum_b64 = base64.b64encode(drum_bytes).decode()
            audio_ph.markdown(f"<audio autoplay loop><source src='data:audio/mp3;base64,{drum_b64}'></audio>", unsafe_allow_html=True)
        # Scrolling effect
        names = df[name_col].dropna().tolist()
        scroll_list = names * 2
        delay = draw_time / len(scroll_list)
        for n in scroll_list:
            disp.markdown(f"<div class='draw-container'><div class='winner-backdrop'><div class='winner-name'>{n}</div></div></div>", unsafe_allow_html=True)
            timer.markdown(f"<div class='timer'>Drawing...</div>", unsafe_allow_html=True)
            time.sleep(delay)
        # Select winners
        winners = df.sample(n=winner_count)
        audio_ph.empty()
        # Crash & applause
        if not mute_audio and crash_upload:
            crash_b64 = base64.b64encode(crash_upload.read()).decode()
            st.markdown(f"<audio autoplay><source src='data:audio/mp3;base64,{crash_b64}'></audio>", unsafe_allow_html=True)
        if not mute_audio and applause_upload:
            applause_b64 = base64.b64encode(applause_upload.read()).decode()
            st.markdown(f"<audio autoplay><source src='data:audio/mp3;base64,{applause_b64}'></audio>", unsafe_allow_html=True)
        # Display winners
        for idx, row in winners.iterrows():
            parts = []
            if show_id and id_col:
                parts.append(str(row[id_col]))
            if show_name:
                parts.append(str(row[name_col]))
            if show_account and acc_col:
                parts.append(str(row[acc_col]))
            text = " | ".join(parts)
            disp.markdown(f"<div class='draw-container'><div class='winner-backdrop'><div class='winner-name'>{text}</div></div></div>", unsafe_allow_html=True)
        timer.empty()
        # Save winners
        winners.to_csv(WINNERS_FILE, index=False)
