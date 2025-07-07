# Random Winner Picker – Rolodex Fix Integrated

import streamlit as st
import pandas as pd
import random
import json
import time
import base64
import os

# Configuration
st.set_page_config("🎰 S5.COM Lucky Draw", layout="wide")
ASSETS_DIR = "uploaded_assets"
SETTINGS_FILE = "settings.json"
WINNERS_FILE = "winners.csv"

os.makedirs(ASSETS_DIR, exist_ok=True)

# Helpers
def save_file(upload, key):
    if upload is None:
        return None
    ext = upload.name.split('.')[-1]
    path = os.path.join(ASSETS_DIR, f"{key}.{ext}")
    with open(path, 'wb') as f:
        f.write(upload.getbuffer())
    return path

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f)

# Sidebar
saved = load_settings()
st.sidebar.title("🔧 Settings & Controls")

# Uploads
logo_up = st.sidebar.file_uploader("Logo", type=["png","jpg","jpeg"], key="logo_up")
bg_up = st.sidebar.file_uploader("Background", type=["png","jpg","jpeg","gif","mp4"], key="bg_up")
csv_up = st.sidebar.file_uploader("Participants CSV", type=["csv"], key="csv_up")
dr_up = st.sidebar.file_uploader("Drumroll Sound", type=["mp3","wav"], key="dr_up")
cr_up = st.sidebar.file_uploader("Crash Sound", type=["mp3","wav"], key="cr_up")
ap_up = st.sidebar.file_uploader("Applause Sound", type=["mp3","wav"], key="ap_up")

st.sidebar.markdown("---")
# Display Columns
display_cols = st.sidebar.multiselect("Display Columns", ["ID","Name","Account"], default=saved.get('display_cols', ["ID","Name","Account"]), key="display_cols")
show_id = "ID" in display_cols
show_name = "Name" in display_cols
show_account = "Account" in display_cols

st.sidebar.markdown("---")
        # Animation
        if animation == 'Scrolling':
            name = random.choice(names)
            name_html = f"<div class='winner-name'>{name}</div>"
        elif animation == 'Rolodex':
            # Rolodex: single vertical marquee of one random name
            name = random.choice(names)
            marquee_height = font_size + 20  # approximate backdrop padding
            name_html = (
                f"<marquee direction='up' scrollamount='10' height='{marquee_height}px'>"
                f"<span class='winner-name'>{name}</span>"
                f"</marquee>"
            )
        elif animation == 'Letter-by-Letter':
            full = random.choice(names)
            for i in range(1, len(full) + 1):
                scroll_ph.markdown(
                    f"<div class='draw-container'>{left_html}{right_html}" +
                    f"<div class='winner-backdrop'><div class='winner-name'>{full[:i]}</div></div></div>",
                    unsafe_allow_html=True
                )
                time.sleep(0.05)
            continue
        elif animation == 'Fade In':
            name = random.choice(names)
            name_html = f"<div class='winner-name fade'>{name}</div>"
        elif animation == 'Slide In':
            name = random.choice(names)
            name_html = f"<div class='winner-name slide'>{name}</div>"
        else:
            name = random.choice(names)
            name_html = f"<div class='winner-name'>{name}</div>"

        # Render frame
        scroll_ph.markdown(
            f"<div class='draw-container'>{left_html}{right_html}" +
            f"<div class='winner-backdrop'>{name_html}</div></div>",
            unsafe_allow_html=True
        )(f"<div class='draw-container'>{left_html}{right_html}<div class='winner-backdrop'><div class='winner-name'>{full[:i]}</div></div></div>", unsafe_allow_html=True)
                time.sleep(0.05)
            continue
        elif animation == 'Fade In':
            name = random.choice(names)
            name_html = f"<div class='winner-name fade'>{name}</div>"
        elif animation == 'Slide In':
            name = random.choice(names)
            name_html = f"<div class='winner-name slide'>{name}</div>"
        else:
            name = random.choice(names)
            name_html = f"<div class='winner-name'>{name}</div>"

        scroll_ph.markdown(f"<div class='draw-container'>{left_html}{right_html}<div class='winner-backdrop'>{name_html}</div></div>", unsafe_allow_html=True)
        time.sleep(0.1)

    # Stop drumroll
    audio_ph.empty()
    # Crash & Applause
    path = save_file(cr_up, 'crash')
    if path:
        cdata = base64.b64encode(open(path,'rb').read()).decode()
        st.markdown(f"<audio autoplay><source src='data:audio/mp3;base64,{cdata}'></audio>", unsafe_allow_html=True)
    path = save_file(ap_up, 'applause')
    if path:
        adata = base64.b64encode(open(path,'rb').read()).decode()
        st.markdown(f"<audio autoplay><source src='data:audio/mp3;base64,{adata}'></audio>", unsafe_allow_html=True)

    # Final winners
    winners = df.sample(n=winner_count)
    final_html = "<br>".join([
        (str(r[id_col]) + " | " if show_id and id_col else "") +
        (str(r[name_col]) if show_name else "") +
        (" | " + str(r[acc_col]) if show_account and acc_col else "")
        for _, r in winners.iterrows()
    ])
    scroll_ph.markdown(f"<div class='draw-container'><div class='winner-backdrop'><div class='winner-name'>{final_html}</div></div></div>", unsafe_allow_html=True)
    winners.to_csv(WINNERS_FILE, index=False)

# End of Script
