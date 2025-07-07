# S5.COM Lucky Draw – Fully Integrated with Audio, Visuals, and Controls (Enhanced)

import streamlit as st
import pandas as pd
import random
import json
import time
import base64
import os

st.set_page_config("🎰 S5.com Lucky Draw", layout="wide")
ASSETS_DIR = "uploaded_assets"
SETTINGS_FILE = "draw_settings.json"
WINNERS_FILE = "winners.csv"
os.makedirs(ASSETS_DIR, exist_ok=True)

def save_uploaded_file(upload, name):
    ext = upload.name.split(".")[-1]
    path = os.path.join(ASSETS_DIR, f"{name}.{ext}")
    with open(path, "wb") as f:
        f.write(upload.getbuffer())
    return path

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f)

fullscreen_toggle = st.sidebar.checkbox("🖥️ Fullscreen Mode", value=True)

saved = load_settings()

backdrop_color = st.sidebar.color_picker("Backdrop Color", saved.get("backdrop_color", "#000000"))
backdrop_opacity = st.sidebar.slider("Backdrop Opacity", 0.0, 1.0, saved.get("backdrop_opacity", 0.5))
backdrop_padding = st.sidebar.slider("Backdrop Padding (px)", 0, 50, saved.get("backdrop_padding", 10))
winner_pos_top = st.sidebar.slider("Winner Text Top Offset (px)", 0, 600, saved.get("winner_pos_top", 200))

# Upload section in sidebar
st.sidebar.markdown("## 🎨 Upload Files")
logo_upload = st.sidebar.file_uploader("Upload Logo", type=["png", "jpg", "jpeg"])
background_upload = st.sidebar.file_uploader("Upload Background (Image/Video)", type=["png", "jpg", "jpeg", "mp4", "webm", "gif"])
csv_upload = st.sidebar.file_uploader("Upload CSV with Names", type=["csv"])
drumroll_upload = st.sidebar.file_uploader("Upload Drumroll Audio", type=["mp3", "wav"])
crash_upload = st.sidebar.file_uploader("Upload Crash Audio", type=["mp3", "wav"])
applause_upload = st.sidebar.file_uploader("Upload Applause Audio", type=["mp3", "wav"])

fullscreen_style = f"""
<style>
    html, body, [data-testid=\"stApp\"] {{
        height: 100%;
        margin: 0;
        padding: 0;
        {'overflow: hidden;' if fullscreen_toggle else 'overflow: auto;'}
    }}
    .draw-container {{
        position: relative;
        width: 100%;
        height: 100%;
        text-align: center;
    }}
    .background-img, .background-vid {{
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        object-fit: cover;
        z-index: 0;
        opacity: 0.5;
    }}
    .logo-img {{
        position: absolute;
        z-index: 2;
    }}
    .winner-name {{
        position: relative;
        z-index: 4;
        font-weight: bold;
        margin-top: {winner_pos_top}px;
        animation: fadein 1s;
    }}
    .winner-backdrop {{
        position: relative;
        z-index: 3;
        margin: auto;
        width: fit-content;
        padding: {backdrop_padding}px;
        background: rgba({int(backdrop_color[1:3], 16)}, {int(backdrop_color[3:5], 16)}, {int(backdrop_color[5:], 16)}, {backdrop_opacity});
        border-radius: 10px;
        display: inline-block;
    }}
    .timer {{
        position: relative;
        z-index: 3;
        margin-top: 10px;
        font-weight: bold;
    }}
    @keyframes fadein {{
        from {{ opacity: 0; }}
        to {{ opacity: 1; }}
    }}
</style>
"""

st.markdown(fullscreen_style, unsafe_allow_html=True)

# Draw control section in sidebar
with st.sidebar.expander("🎯 Draw Controls", expanded=True):
    start_draw = st.button("🎲 Start Draw")
    export_winners = st.button("📤 Export Winners")

# Display options for result fields
with st.sidebar.expander("📋 Display Columns", expanded=False):
    show_id = st.checkbox("Show ID", value=True)
    show_name = st.checkbox("Show Name", value=True)
    show_account = st.checkbox("Show Account ID", value=True)

# Text and appearance settings in sidebar
with st.sidebar.expander("🔤 Text Appearance", expanded=False):
    font_size = st.slider("Font Size (px)", 20, 120, saved.get("font_size", 48))
    font_color = st.color_picker("Font Color", saved.get("font_color", "#FFFFFF"))

# Add countdown settings and logic
with st.sidebar.expander("⏳ Countdown Settings", expanded=True):
    draw_duration = st.slider("Countdown Duration (seconds)", 5, 60, saved.get("draw_duration", 10))

# Store all settings back to disk
save_settings({
    "backdrop_color": backdrop_color,
    "backdrop_opacity": backdrop_opacity,
    "backdrop_padding": backdrop_padding,
    "winner_pos_top": winner_pos_top,
    "font_size": font_size,
    "font_color": font_color,
    "draw_duration": draw_duration
})

# Run draw when button is clicked
if start_draw and csv_upload is not None:
    df = pd.read_csv(csv_upload)
    if df.empty or "name" not in df.columns:
        st.error("CSV must contain a 'name' column.")
    else:
        names = df['name'].dropna().tolist()
        placeholder = st.empty()
        timer_placeholder = st.empty()
        audio_placeholder = st.empty()
        bg_placeholder = st.empty()

        # Show background
        if background_upload is not None:
            bg_ext = background_upload.name.split(".")[-1].lower()
            bg_bytes = background_upload.read()
            encoded = base64.b64encode(bg_bytes).decode()
            if bg_ext in ["mp4", "webm"]:
                bg_html = f"""
                <video autoplay loop muted class='background-vid'>
                    <source src="data:video/{bg_ext};base64,{encoded}" type="video/{bg_ext}">
                </video>
                """
            else:
                bg_html = f"<img src='data:image/{bg_ext};base64,{encoded}' class='background-img'>"
            bg_placeholder.markdown(bg_html, unsafe_allow_html=True)

        # Play drumroll
        if drumroll_upload:
            audio_bytes = drumroll_upload.read()
            drumroll_b64 = base64.b64encode(audio_bytes).decode()
            audio_placeholder.markdown(f"""
            <audio autoplay loop>
                <source src="data:audio/mp3;base64,{drumroll_b64}" type="audio/mp3">
            </audio>
            """, unsafe_allow_html=True)

        for i in range(draw_duration, 0, -1):
            timer_placeholder.markdown(f"<div class='timer'>Drawing in: {i} seconds...</div>", unsafe_allow_html=True)
            placeholder.markdown(f"<div class='winner-backdrop'><div class='winner-name' style='color:{font_color}; font-size:{font_size}px;'>{random.choice(names)}</div></div>", unsafe_allow_html=True)
            time.sleep(1)

        winner_row = df.sample(1).iloc[0]
        winner_display = []
        if show_id and 'id' in winner_row:
            winner_display.append(str(winner_row['id']))
        if show_name and 'name' in winner_row:
            winner_display.append(str(winner_row['name']))
        if show_account and 'account' in winner_row:
            winner_display.append(str(winner_row['account']))
        winner = " | ".join(winner_display)
        st.balloons()

        # Stop drumroll, play crash and applause
        audio_placeholder.empty()
        if crash_upload:
            crash_bytes = crash_upload.read()
            crash_b64 = base64.b64encode(crash_bytes).decode()
            st.markdown(f"""
            <audio autoplay>
                <source src="data:audio/mp3;base64,{crash_b64}" type="audio/mp3">
            </audio>
            """, unsafe_allow_html=True)
        if applause_upload:
            applause_bytes = applause_upload.read()
            applause_b64 = base64.b64encode(applause_bytes).decode()
            st.markdown(f"""
            <audio autoplay>
                <source src="data:audio/mp3;base64,{applause_b64}" type="audio/mp3">
            </audio>
            """, unsafe_allow_html=True)

        placeholder.markdown(f"<div class='winner-backdrop'><div class='winner-name' style='color:{font_color}; font-size:{font_size}px;'>🎉 {winner} 🎉</div></div>", unsafe_allow_html=True)
        timer_placeholder.empty()

        pd.DataFrame([[winner]], columns=["Winner"]).to_csv(WINNERS_FILE, mode='a', header=not os.path.exists(WINNERS_FILE), index=False)

if export_winners and os.path.exists(WINNERS_FILE):
    with open(WINNERS_FILE, "rb") as f:
        st.sidebar.download_button("Download Winners CSV", f, file_name="winners.csv")
