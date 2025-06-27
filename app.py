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

# Upload inputs
logo_file = st.file_uploader("Upload Logo (optional)", type=["png", "jpg", "jpeg"])
background_file = st.file_uploader("Upload Background (Image/GIF/Video)", type=["png", "jpg", "jpeg", "gif", "mp4"])
drumroll_file = st.file_uploader("Upload Drum Roll Sound (optional)", type=["mp3", "wav"])
crash_file = st.file_uploader("Upload Crash Sound (optional)", type=["mp3", "wav"])
applause_file = st.file_uploader("Upload Applause Sound (optional)", type=["mp3", "wav"])

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

winner_log = []
drawn_indices = set()

def logo_position_style():
    return {
        "top": "top: 20px; left: 50%; transform: translateX(-50%);",
        "bottom": "bottom: 20px; left: 50%; transform: translateX(-50%);",
        "left": "top: 50%; left: 20px; transform: translateY(-50%);",
        "right": "top: 50%; right: 20px; transform: translateY(-50%);",
        "center": "top: 50%; left: 50%; transform: translate(-50%, -50%);"
    }[logo_position]

def scroll_draw(df, duration):
    container = st.empty()
    start_time = time.time()
    bg_html = ""

    if background_file:
        bg_bytes = background_file.read()
        bg_base64 = base64.b64encode(bg_bytes).decode()
        mime = background_file.type
        if "image" in mime or "gif" in mime:
            bg_html = f'<img src="data:{mime};base64,{bg_base64}" class="background" style="opacity:{background_opacity}">' 
        elif "video" in mime:
            bg_html = f'<video autoplay loop muted class="background" style="opacity:{background_opacity}"><source src="data:{mime};base64,{bg_base64}"></video>'

    logo_html = ""
    if logo_file:
        logo_b64 = base64.b64encode(logo_file.read()).decode()
        logo_html = f'<img src="data:image/png;base64,{logo_b64}" class="logo-overlay" style="{logo_position_style()} width: {logo_width}px;">'

    if drumroll_file:
        drumroll_b64 = base64.b64encode(drumroll_file.read()).decode()
        st.markdown(f"""
            <audio autoplay loop style='display:none'>
                <source src="data:audio/mp3;base64,{drumroll_b64}" type="audio/mp3">
            </audio>
        """, unsafe_allow_html=True)

    while True:
        elapsed = time.time() - start_time
        if elapsed >= duration:
            break
        sample = df.sample(1).iloc[0]
        scroll_text = f"🔄 {sample['Name']} ({sample['Account Name']})"
        remain = max(0.0, duration - elapsed)
        html = f"""
        <div class='draw-area'>
            {bg_html}
            {logo_html}
            <div class='winner-text' style='font-size:{font_size}px; color:{font_color}'>{scroll_text}</div>
            <div class='timer' style='font-size:{timer_size}px; color:{timer_color}'>⏳ Time Left: {remain:.1f} sec</div>
        </div>
        """
        container.markdown(html, unsafe_allow_html=True)
        time.sleep(0.1)

def display_winner(winner):
    summary = f"🎉 <b>ID:</b> {winner['ID']}<br><b>Name:</b> {winner['Name']}<br><b>Account:</b> {winner['Account Name']}"
    st.markdown(f"<div style='text-align:center; font-size:1.8rem; color:{font_color}'>{summary}</div>", unsafe_allow_html=True)
    st.balloons()

    if crash_file:
        crash_b64 = base64.b64encode(crash_file.read()).decode()
        st.markdown(f"""
            <audio autoplay style='display:none'>
                <source src="data:audio/mp3;base64,{crash_b64}" type="audio/mp3">
            </audio>
        """, unsafe_allow_html=True)

    if applause_file:
        applause_b64 = base64.b64encode(applause_file.read()).decode()
        st.markdown(f"""
            <audio autoplay style='display:none'>
                <source src="data:audio/mp3;base64,{applause_b64}" type="audio/mp3">
            </audio>
        """, unsafe_allow_html=True)

    winner_log.append(summary)

if df is not None:
    if st.button("🎲 Start Draw"):
        with st.spinner("Drawing..."):
            available_df = df.copy()
            for i in range(winner_count):
                st.subheader(f"Winner #{i+1}")
                scroll_draw(df, total_draw_time)
                while True:
                    selected = available_df.sample(1).iloc[0]
                    if not prevent_duplicates or selected.name not in drawn_indices:
                        break
                drawn_indices.add(selected.name)
                display_winner(selected)
                time.sleep(0.5)

    if st.button("🔁 Restart Draw"):
        st.experimental_rerun()

    if winner_log:
        st.markdown("---")
        st.subheader("📜 Winner Log")
        for item in winner_log:
            st.markdown(item, unsafe_allow_html=True)

        export = df.sample(n=winner_count).to_csv(index=False)
        export_b64 = base64.b64encode(export.encode()).decode()
        st.markdown(f'<a href="data:file/csv;base64,{export_b64}" download="winners.csv">📥 Download Winners CSV</a>', unsafe_allow_html=True)
else:
    st.info("📤 Please upload a valid CSV file to begin.")
