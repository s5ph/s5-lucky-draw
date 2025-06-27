# This Streamlit script must be run in a local Python environment where Streamlit is installed and the necessary file and media access is available.
# Install Streamlit using: pip install streamlit
# Then run the script using: streamlit run <this_file.py>

import streamlit as st
import pandas as pd
import base64
import time
import json
import os

st.set_page_config(page_title="🎰 S5.com Lucky Draw", layout="wide")
SETTINGS_FILE = "s5_draw_settings.json"
ASSETS_DIR = "uploaded_assets"
os.makedirs(ASSETS_DIR, exist_ok=True)

def save_file(uploaded_file, name):
    path = os.path.join(ASSETS_DIR, name)
    with open(path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return path

def load_file(name):
    path = os.path.join(ASSETS_DIR, name)
    return open(path, "rb") if os.path.exists(path) else None

# Load saved settings if available
if os.path.exists(SETTINGS_FILE):
    with open(SETTINGS_FILE, "r") as f:
        saved_settings = json.load(f)
else:
    saved_settings = {}

st.markdown("""
    <style>
        .draw-area {
            position: relative;
            width: 100%;
            height: 600px;
            overflow: hidden;
            display: flex;
            justify-content: center;
            align-items: center;
            flex-direction: column;
            text-align: center;
        }
        .background {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;
            z-index: 0;
        }
        .logo-overlay {
            position: absolute;
            z-index: 2;
        }
        .winner-text {
            z-index: 3;
            font-weight: bold;
        }
        .timer {
            z-index: 3;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>🎰 S5.COM Lucky Draw</h1><hr>", unsafe_allow_html=True)

# Upload inputs and persist them
uploaded_files = {
    "logo": st.file_uploader("Upload Logo (optional)", type=["png", "jpg", "jpeg"]),
    "background": st.file_uploader("Upload Background (Image/GIF/Video)", type=["png", "jpg", "jpeg", "gif", "mp4"]),
    "drumroll": st.file_uploader("Upload Drum Roll Sound (optional)", type=["mp3", "wav"]),
    "crash": st.file_uploader("Upload Crash Sound (optional)", type=["mp3", "wav"]),
    "applause": st.file_uploader("Upload Applause Sound (optional)", type=["mp3", "wav"])
}

assets = {}
for key, file in uploaded_files.items():
    if file:
        save_file(file, key)
        assets[key] = open(os.path.join(ASSETS_DIR, key), "rb")
    else:
        assets[key] = load_file(key)

if st.button("🗑️ Clear Uploaded Files"):
    for key in uploaded_files:
        path = os.path.join(ASSETS_DIR, key)
        if os.path.exists(path):
            os.remove(path)
    st.success("Uploaded files cleared. Please refresh.")

csv_file = st.file_uploader("Upload CSV File", type="csv")
if csv_file:
    df = pd.read_csv(csv_file)
    if not {"ID", "Name", "Account Name"}.issubset(df.columns):
        st.error("CSV must contain columns: ID, Name, Account Name")
        df = None
else:
    df = None

# Sidebar controls
st.sidebar.header("Draw Settings")
winner_count = st.sidebar.slider("Number of Winners", 1, 10, saved_settings.get("winner_count", 3))
total_draw_time = st.sidebar.number_input("Draw Time (seconds)", min_value=1.0, max_value=300.0, value=saved_settings.get("total_draw_time", 15.0))
font_size = st.sidebar.slider("Winner Font Size", 10, 80, saved_settings.get("font_size", 32))
timer_size = st.sidebar.slider("Timer Font Size", 10, 50, saved_settings.get("timer_size", 20))
font_color = st.sidebar.color_picker("Font Color", saved_settings.get("font_color", "#FFFFFF"))
timer_color = st.sidebar.color_picker("Timer Color", saved_settings.get("timer_color", "#FFFF00"))
logo_width = st.sidebar.slider("Logo Width (px)", 50, 500, saved_settings.get("logo_width", 150))
logo_position = st.sidebar.selectbox("Logo Position", ["top", "bottom", "left", "right", "center"], index=["top", "bottom", "left", "right", "center"].index(saved_settings.get("logo_position", "top")))
background_opacity = st.sidebar.slider("Background Opacity", 0.0, 1.0, saved_settings.get("background_opacity", 0.4))
prevent_duplicates = st.sidebar.checkbox("Prevent Duplicate Winners", value=saved_settings.get("prevent_duplicates", True))

if st.sidebar.button("💾 Save Settings"):
    new_settings = {
        "winner_count": winner_count,
        "total_draw_time": total_draw_time,
        "font_size": font_size,
        "timer_size": timer_size,
        "font_color": font_color,
        "timer_color": timer_color,
        "logo_width": logo_width,
        "logo_position": logo_position,
        "background_opacity": background_opacity,
        "prevent_duplicates": prevent_duplicates
    }
    with open(SETTINGS_FILE, "w") as f:
        json.dump(new_settings, f)
    st.sidebar.success("Settings saved successfully!")

# Add control buttons to sidebar
if df is not None:
    if st.sidebar.button("🎲 Start Draw"):
        st.session_state["start_draw"] = True

    if st.sidebar.button("🔁 Restart Draw"):
        st.experimental_rerun()
