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

# Sidebar controls
fullscreen_toggle = st.sidebar.checkbox("🖥️ Fullscreen Mode", value=True)
saved = load_settings()

backdrop_color = st.sidebar.color_picker("Backdrop Color", saved.get("backdrop_color", "#000000"))
backdrop_opacity = st.sidebar.slider("Backdrop Opacity", 0.0, 1.0, saved.get("backdrop_opacity", 0.5))
backdrop_padding = st.sidebar.slider("Backdrop Padding (px)", 0, 50, saved.get("backdrop_padding", 10))
winner_pos_top = st.sidebar.slider("Winner Text Top Offset (px)", 0, 600, saved.get("winner_pos_top", 200))
font_color = st.sidebar.color_picker("Font Color", saved.get("font_color", "#FFFFFF"))
font_size = st.sidebar.slider("Font Size", 20, 80, saved.get("font_size", 40))
timer_color = st.sidebar.color_picker("Timer Color", saved.get("timer_color", "#FFDD00"))
logo_width = st.sidebar.slider("Logo Width (px)", 100, 400, saved.get("logo_width", 150))
volume = st.sidebar.slider("Sound Volume (%)", 0, 100, saved.get("volume", 70))
winner_count = st.sidebar.number_input("Number of Winners", 1, 10, saved.get("winner_count", 3))
draw_time = st.sidebar.number_input("Draw Time (sec)", 5.0, 300.0, saved.get("draw_time", 15.0))
mute_audio = st.sidebar.checkbox("🔇 Mute Audio")
show_confetti = st.sidebar.checkbox("🎉 Show Confetti Effect")

start = st.sidebar.button("🎲 Start Draw")
export = st.sidebar.button("📥 Export Winners")
if st.sidebar.button("💾 Save Settings"):
    save_settings({
        "winner_count": winner_count,
        "draw_time": draw_time,
        "font_color": font_color,
        "font_size": font_size,
        "timer_color": timer_color,
        "logo_width": logo_width,
        "volume": volume,
        "backdrop_color": backdrop_color,
        "backdrop_opacity": backdrop_opacity,
        "backdrop_padding": backdrop_padding,
        "winner_pos_top": winner_pos_top,
    })
    st.sidebar.success("Settings saved!")

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
            background: rgba({int(backdrop_color[1:3], 16)}, {int(backdrop_color[3:5], 16)}, {int(backdrop_color[5:], 16)},_
