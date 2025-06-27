# S5.COM Lucky Draw – Rebuilt from Scratch

import streamlit as st
import pandas as pd
import random
import json
import time
import base64
import os

# === Setup ===
st.set_page_config("🎰 S5.com Lucky Draw", layout="wide")
ASSETS_DIR = "uploaded_assets"
SETTINGS_FILE = "draw_settings.json"
os.makedirs(ASSETS_DIR, exist_ok=True)

# === Helpers ===
def save_uploaded_file(upload, name):
    path = os.path.join(ASSETS_DIR, name)
    with open(path, "wb") as f:
        f.write(upload.getbuffer())
    return path

def load_saved_file(name):
    path = os.path.join(ASSETS_DIR, name)
    return open(path, "rb") if os.path.exists(path) else None

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f)

# === Style ===
st.markdown("""
    <style>
        .draw-container { position: relative; height: 600px; overflow: hidden; text-align: center; }
        .background-img, .background-vid { position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; z-index: 0; opacity: 0.5; }
        .logo-img { position: absolute; z-index: 2; }
        .winner-name { position: relative; z-index: 3; font-weight: bold; margin-top: 200px; }
        .timer { position: relative; z-index: 3; margin-top: 10px; }
    </style>
""", unsafe_allow_html=True)

# === Upload Section ===
st.title("🎰 S5.COM Lucky Draw")
logo = st.file_uploader("Logo", type=["png", "jpg"])
bg = st.file_uploader("Background (image/gif/mp4)", type=["png", "jpg", "gif", "mp4"])
csv = st.file_uploader("CSV File", type="csv")

# === Load or Save Files ===
logo_path = save_uploaded_file(logo, "logo") if logo else os.path.join(ASSETS_DIR, "logo")
bg_path = save_uploaded_file(bg, "bg") if bg else os.path.join(ASSETS_DIR, "bg")

# === Settings ===
saved = load_settings()
st.sidebar.header("Settings")
winner_count = st.sidebar.number_input("Number of Winners", 1, 10, saved.get("winner_count", 3))
draw_time = st.sidebar.number_input("Draw Time (sec)", 5.0, 300.0, saved.get("draw_time", 15.0))
font_color = st.sidebar.color_picker("Font Color", saved.get("font_color", "#FFFFFF"))
font_size = st.sidebar.slider("Font Size", 20, 80, saved.get("font_size", 40))
timer_color = st.sidebar.color_picker("Timer Color", saved.get("timer_color", "#FFDD00"))
logo_width = st.sidebar.slider("Logo Width (px)", 100, 400, saved.get("logo_width", 150))

if st.sidebar.button("💾 Save Settings"):
    save_settings({
        "winner_count": winner_count,
        "draw_time": draw_time,
        "font_color": font_color,
        "font_size": font_size,
        "timer_color": timer_color,
        "logo_width": logo_width
    })
    st.sidebar.success("Saved settings!")

# === Control ===
start = st.button("🎲 Start Draw")

# === Run Draw ===
if start and csv:
    df = pd.read_csv(csv)
    if not {"Name", "Account Name"}.issubset(df.columns):
        st.error("CSV must include 'Name' and 'Account Name' columns")
    else:
        placeholder = st.empty()
        names = df["Name"].tolist()
        start_time = time.time()
        elapsed = 0
        with open(bg_path, "rb") as bg_file:
            bg_data = bg_file.read()
        with open(logo_path, "rb") as logo_file:
            logo_data = logo_file.read()

        b_ext = bg_path.split(".")[-1]
        l_ext = logo_path.split(".")[-1]
        b64_bg = base64.b64encode(bg_data).decode()
        b64_logo = base64.b64encode(logo_data).decode()

        bg_html = f'<video class="background-vid" autoplay loop muted><source src="data:video/mp4;base64,{b64_bg}" type="video/mp4"></video>' if b_ext == "mp4" else f'<img src="data:image/{b_ext};base64,{b64_bg}" class="background-img">'
        logo_html = f'<img src="data:image/{l_ext};base64,{b64_logo}" class="logo-img" style="width: {logo_width}px; top: 10px; left: 10px;">'

        while elapsed < draw_time:
            name = random.choice(names)
            time_left = max(0, draw_time - elapsed)

            placeholder.markdown(f"""
                <div class="draw-container">
                    {bg_html}
                    {logo_html}
                    <div class="winner-name" style="color:{font_color}; font-size:{font_size}px">{name}</div>
                    <div class="timer" style="color:{timer_color}; font-size:24px">⏳ {time_left:.1f}s</div>
                </div>
            """, unsafe_allow_html=True)

            time.sleep(0.1)
            elapsed = time.time() - start_time

        winners = df.sample(n=winner_count)
        final_names = "<br>".join([f"🎉 {r['Name']} - {r['Account Name']}" for _, r in winners.iterrows()])
        placeholder.markdown(f"""
            <div class="draw-container">
                {bg_html}
                {logo_html}
                <div class="winner-name" style="color:{font_color}; font-size:{font_size + 10}px">{final_names}</div>
            </div>
        """, unsafe_allow_html=True)
