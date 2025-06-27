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

st.markdown("""
    <style>
        .draw-container { position: relative; height: 600px; overflow: hidden; text-align: center; }
        .background-img, .background-vid { position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; z-index: 0; opacity: 0.5; }
        .logo-img { position: absolute; z-index: 2; }
        .winner-name { position: relative; z-index: 3; font-weight: bold; margin-top: 200px; animation: fadein 1s; }
        .timer { position: relative; z-index: 3; margin-top: 10px; font-weight: bold; }
        @keyframes fadein { from { opacity: 0; } to { opacity: 1; } }
    </style>
""", unsafe_allow_html=True)

st.title("🎰 S5.COM Lucky Draw")
logo = st.file_uploader("Logo", type=["png", "jpg"])
bg = st.file_uploader("Background (image/gif/mp4)", type=["png", "jpg", "gif", "mp4"])
csv = st.file_uploader("CSV File", type="csv")
drumroll = st.file_uploader("Drumroll Sound", type=["mp3", "wav"])
crash = st.file_uploader("Crash Effect Sound", type=["mp3", "wav"])
applause = st.file_uploader("Applause Sound", type=["mp3", "wav"])

mute_audio = st.sidebar.checkbox("🔇 Mute Audio")
show_confetti = st.sidebar.checkbox("🎉 Show Confetti Effect")

logo_path = save_uploaded_file(logo, "logo") if logo else os.path.join(ASSETS_DIR, "logo.png")
bg_path = save_uploaded_file(bg, "bg") if bg else os.path.join(ASSETS_DIR, "bg.png")
drumroll_path = save_uploaded_file(drumroll, "drumroll") if drumroll else os.path.join(ASSETS_DIR, "drumroll.mp3")
crash_path = save_uploaded_file(crash, "crash") if crash else os.path.join(ASSETS_DIR, "crash.mp3")
applause_path = save_uploaded_file(applause, "applause") if applause else os.path.join(ASSETS_DIR, "applause.mp3")

saved = load_settings()
st.sidebar.header("Settings")
winner_count = st.sidebar.number_input("Number of Winners", 1, 10, saved.get("winner_count", 3))
draw_time = st.sidebar.number_input("Draw Time (sec)", 5.0, 300.0, saved.get("draw_time", 15.0))
font_color = st.sidebar.color_picker("Font Color", saved.get("font_color", "#FFFFFF"))
font_size = st.sidebar.slider("Font Size", 20, 80, saved.get("font_size", 40))
timer_color = st.sidebar.color_picker("Timer Color", saved.get("timer_color", "#FFDD00"))
logo_width = st.sidebar.slider("Logo Width (px)", 100, 400, saved.get("logo_width", 150))
volume = st.sidebar.slider("Sound Volume (%)", 0, 100, saved.get("volume", 70))

if st.sidebar.button("💾 Save Settings"):
    save_settings({
        "winner_count": winner_count,
        "draw_time": draw_time,
        "font_color": font_color,
        "font_size": font_size,
        "timer_color": timer_color,
        "logo_width": logo_width,
        "volume": volume
    })
    st.sidebar.success("Saved settings!")

start = st.sidebar.button("🎲 Start Draw")
export = st.sidebar.button("📥 Export Winners")

if export and os.path.exists(WINNERS_FILE):
    with open(WINNERS_FILE, "rb") as f:
        st.download_button("Download Winners CSV", f, file_name="winners.csv")

if start and csv:
    df = pd.read_csv(csv)
    if not {"Name", "Account Name"}.issubset(df.columns):
        st.error("CSV must include 'Name' and 'Account Name' columns")
    else:
        scroll_placeholder = st.empty()
        final_placeholder = st.empty()
        audio_placeholder = st.empty()
        names = df["Name"].tolist()

        with open(bg_path, "rb") as bg_file:
            b_ext = bg_path.split(".")[-1].lower()
            b64_bg = base64.b64encode(bg_file.read()).decode()
        with open(logo_path, "rb") as logo_file:
            l_ext = logo_path.split(".")[-1].lower()
            b64_logo = base64.b64encode(logo_file.read()).decode()

        bg_html = f'<video class="background-vid" autoplay loop muted><source src="data:video/{b_ext};base64,{b64_bg}" type="video/{b_ext}"></video>' if b_ext == "mp4" else f'<img src="data:image/{b_ext};base64,{b64_bg}" class="background-img">'
        logo_html = f'<img src="data:image/{l_ext};base64,{b64_logo}" class="logo-img" style="width: {logo_width}px; top: 10px; left: 10px;">'

        if not mute_audio and os.path.exists(drumroll_path):
            with open(drumroll_path, "rb") as f:
                b64_drum = base64.b64encode(f.read()).decode()
                audio_placeholder.markdown(f'<audio autoplay loop id="drumroll" style="display:none;"><source src="data:audio/mp3;base64,{b64_drum}" type="audio/mp3"></audio>', unsafe_allow_html=True)

        start_time = time.time()
        while (elapsed := time.time() - start_time) < draw_time:
            scroll_name = random.choice(names)
            scroll_placeholder.markdown(f"""
                <div class="draw-container">
                    {bg_html}
                    {logo_html}
                    <div class="winner-name" style="color:{font_color}; font-size:{font_size}px">{scroll_name}</div>
                    <div class="timer" style="color:{timer_color}; font-size:24px">⏳ {draw_time - elapsed:.1f}s</div>
                </div>
            """, unsafe_allow_html=True)
            time.sleep(0.1)

        winners = df.sample(n=winner_count)
        winners.to_csv(WINNERS_FILE, index=False)
        final_names = "<br>".join([f"🎉 {r['Name']} - {r['Account Name']}" for _, r in winners.iterrows()])

        winner_audio = ""
        if not mute_audio and os.path.exists(crash_path):
            with open(crash_path, "rb") as f:
                winner_audio += f'<audio autoplay id="crash"><source src="data:audio/mp3;base64,{base64.b64encode(f.read()).decode()}" type="audio/mp3"></audio>'
        if not mute_audio and os.path.exists(applause_path):
            with open(applause_path, "rb") as f:
                winner_audio += f'<audio autoplay id="applause"><source src="data:audio/mp3;base64,{base64.b64encode(f.read()).decode()}" type="audio/mp3"></audio>'

        confetti_script = """
        <script>
        const duration = 5000;
        const end = Date.now() + duration;
        (function frame() {
            confetti({particleCount: 3, angle: 60, spread: 55, origin: {x: 0}});
            confetti({particleCount: 3, angle: 120, spread: 55, origin: {x: 1}});
            if (Date.now() < end) requestAnimationFrame(frame);
        })();
        </script>
        <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.5.1/dist/confetti.browser.min.js"></script>
        """ if show_confetti else ""

        scroll_placeholder.empty()
        audio_placeholder.empty()
        final_placeholder.markdown(f"""
            <div class="draw-container">
                {bg_html}
                {logo_html}
                <div class="winner-name" style="color:{font_color}; font-size:{font_size + 10}px">{final_names}</div>
            </div>
            {winner_audio}
            {confetti_script}
        """, unsafe_allow_html=True)
