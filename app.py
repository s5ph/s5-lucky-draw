# Random Winner Picker – Completely Refactored Final Version

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
def encode_file(upload):
    if not upload:
        return None, None
    data = upload.read()
    ext = upload.name.split('.')[-1].lower()
    return base64.b64encode(data).decode(), ext


def load_settings():
    if os.path.exists(SETTINGS_FILE):
        return json.load(open(SETTINGS_FILE))
    return {}


def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f)

# --- Sidebar Controls ---
saved = load_settings()
st.sidebar.title("🔧 Settings & Controls")
# Uploads
logo_up = st.sidebar.file_uploader("Logo (png/jpg)", type=["png","jpg","jpeg"])
bg_up = st.sidebar.file_uploader("Background (img/gif/mp4)", type=["png","jpg","jpeg","gif","mp4"])
csv_up = st.sidebar.file_uploader("Participants CSV (ID,Name,Account)", type=["csv"])
dr_up = st.sidebar.file_uploader("Drumroll Sound", type=["mp3","wav"])
cr_up = st.sidebar.file_uploader("Crash Sound", type=["mp3","wav"])
ap_up = st.sidebar.file_uploader("Applause Sound", type=["mp3","wav"])

st.sidebar.markdown("---")
# Columns
display_cols = st.sidebar.multiselect(
    "Display Columns", ["ID","Name","Account"],
    default=saved.get('display_cols', ["ID","Name","Account"]) )
show_id = "ID" in display_cols
show_name = "Name" in display_cols
show_account = "Account" in display_cols

st.sidebar.markdown("---")
# Animation
animation = st.sidebar.selectbox(
    "Animation Style", ["Scrolling","Rolodex","Letter-by-Letter"],
    index=["Scrolling","Rolodex","Letter-by-Letter"].index(saved.get('animation','Scrolling')) )

# Rolodex controls
rolodex_speed = st.sidebar.slider("Rolodex Scroll Speed (scrollamount)", 1, 50, saved.get('rolodex_speed',10))
rolodex_interval = st.sidebar.slider("Rolodex Frame Interval (ms)", 50, 500, saved.get('rolodex_interval',200))

st.sidebar.markdown("---")
# Draw & Appearance
draw_duration = st.sidebar.slider("Draw Duration (sec)", 5, 60, saved.get('draw_duration',15))
winner_count = st.sidebar.slider("Number of Winners", 1, 10, saved.get('winner_count',3))
font_size = st.sidebar.slider("Font Size (px)", 20, 120, saved.get('font_size',48))
font_color = st.sidebar.color_picker("Font Color", saved.get('font_color','#FFFFFF'))
backdrop_color = st.sidebar.color_picker("Backdrop Color", saved.get('backdrop_color','#000000'))
backdrop_opacity = st.sidebar.slider("Backdrop Opacity", 0.0, 1.0, saved.get('backdrop_opacity',0.5))
backdrop_padding = st.sidebar.slider("Backdrop Padding (px)", 0, 50, saved.get('backdrop_padding',10))
logo_width = st.sidebar.slider("Logo Width (px)", 50, 500, saved.get('logo_width',150))
show_left_timer = st.sidebar.checkbox("Show Left Timer", saved.get('show_left_timer',True))
show_right_timer = st.sidebar.checkbox("Show Right Timer", saved.get('show_right_timer',True))

st.sidebar.markdown("---")
# Actions
start_draw = st.sidebar.button("🎲 Start Draw")
export_btn = st.sidebar.button("📥 Export Winners CSV")
save_btn = st.sidebar.button("💾 Save Settings")

if save_btn:
    save_settings({
        'display_cols':display_cols, 'animation':animation,
        'rolodex_speed':rolodex_speed, 'rolodex_interval':rolodex_interval,
        'draw_duration':draw_duration, 'winner_count':winner_count,
        'font_size':font_size,'font_color':font_color,
        'backdrop_color':backdrop_color,'backdrop_opacity':backdrop_opacity,'backdrop_padding':backdrop_padding,
        'logo_width':logo_width,'show_left_timer':show_left_timer,'show_right_timer':show_right_timer
    })
    st.sidebar.success("Settings saved!")

# --- CSS Styling ---
st.markdown(f"""
<style>
html,body,[data-testid='stApp'] {{margin:0;padding:0;height:100%;}}
.draw-container {{display:flex;align-items:center;justify-content:center;position:relative;width:100%;height:100vh;}}
.background-img,.background-vid {{position:absolute;top:0;left:0;width:100%;height:100%;object-fit:cover;opacity:0.5;z-index:0;}}
.logo-img {{position:absolute;top:10px;left:10px;width:{logo_width}px;z-index:2;}}
.winner-backdrop {{padding:{backdrop_padding}px;background:rgba({int(backdrop_color[1:3],16)},{int(backdrop_color[3:5],16)},{int(backdrop_color[5:],16)},{backdrop_opacity});border-radius:10px;z-index:3;}}
.winner-name {{font-size:{font_size}px;color:{font_color};margin:0;z-index:4;font-weight:bold;}}
.timer-left {{position:absolute;left:20px;top:50%;transform:translateY(-50%);font-size:24px;color:{font_color};z-index:3;}}
.timer-right {{position:absolute;right:20px;top:50%;transform:translateY(-50%);font-size:24px;color:{font_color};z-index:3;}}
</style>
""", unsafe_allow_html=True)

# Placeholders
scroll_ph = st.empty()
audio_ph = st.empty()

# --- Draw Logic ---
if start_draw and csv_up:
    df = pd.read_csv(csv_up)
    id_col = next((c for c in df.columns if c.lower()=='id'), None)
    name_col = next((c for c in df.columns if c.lower()=='name'), None)
    acc_col = next((c for c in df.columns if 'account' in c.lower()), None)
    if not name_col:
        st.error("CSV must contain a 'Name' column.")
        st.stop()

    # Encode media once
drum_b64, drum_ext = encode_file(dr_up)
crash_b64, crash_ext = encode_file(cr_up)
applause_b64, applause_ext = encode_file(ap_up)
bg_b64, bg_ext = encode_file(bg_up)
logo_b64, logo_ext = encode_file(logo_up)

    # Play drumroll
if drum_b64:
    audio_ph.markdown(f"<audio autoplay loop><source src='data:audio/{drum_ext};base64,{drum_b64}'></audio>", unsafe_allow_html=True)

    names = df[name_col].dropna().tolist()
    start_time = time.time()
    while time.time() - start_time < draw_duration:
        rem = draw_duration - (time.time() - start_time)
        left_html = f"<div class='timer-left'>⏳ {rem:.1f}s</div>" if show_left_timer else ''
        right_html = f"<div class='timer-right'>⏳ {rem:.1f}s</div>" if show_right_timer else ''

        # Background and logo HTML
        bg_html = ''
        if bg_b64:
            if bg_ext in ['mp4','webm']:
                bg_html = f"<video autoplay loop muted class='background-vid'><source src='data:video/{bg_ext};base64,{bg_b64}' type='video/{bg_ext}'></video>"
            else:
                bg_html = f"<img src='data:image/{bg_ext};base64,{bg_b64}' class='background-img'>"
        logo_html = ''
        if logo_b64:
            logo_html = f"<img src='data:image/{logo_ext};base64,{logo_b64}' class='logo-img'>"

        # Animation
        sleep_time = 0.1
        if animation == 'Scrolling':
            name = random.choice(names)
            name_html = f"<div class='winner-name'>{name}</div>"
        elif animation == 'Rolodex':
            name = random.choice(names)
            m_h = font_size + backdrop_padding*2
            name_html = f"<marquee direction='up' scrollamount='{rolodex_speed}' height='{m_h}px'><div class='winner-name'>{name}</div></marquee>"
            sleep_time = rolodex_interval / 1000.0
        else:  # Letter-by-Letter
            full = random.choice(names)
            for i in range(1, len(full)+1):
                scroll_ph.markdown(
                    f"<div class='draw-container'>{bg_html}{logo_html}{left_html}{right_html}<div class='winner-backdrop'><div class='winner-name'>{full[:i]}</div></div></div>", unsafe_allow_html=True
                )
                time.sleep(0.05)
            continue

        scroll_ph.markdown(
            f"<div class='draw-container'>{bg_html}{logo_html}{left_html}{right_html}<div class='winner-backdrop'>{name_html}</div></div>", unsafe_allow_html=True
        )
        time.sleep(sleep_time)

    # End of draw: stop drumroll, play crash & applause
    audio_ph.empty()
    if crash_b64:
        st.markdown(f"<audio autoplay><source src='data:audio/{crash_ext};base64,{crash_b64}'></audio>", unsafe_allow_html=True)
    if applause_b64:
        st.markdown(f"<audio autoplay><source src='data:audio/{applause_ext};base64,{applause_b64}'></audio>", unsafe_allow_html=True)

    # Final winners display
    winners = df.sample(n=winner_count)
    lines = []
    for _, r in winners.iterrows():
        parts = []
        if show_id and id_col: parts.append(str(r[id_col]))
        if show_name: parts.append(str(r[name_col]))
        if show_account and acc_col: parts.append(str(r[acc_col]))
        lines.append(" | ".join(parts))
    final_html = "<br>".join(lines)

    scroll_ph.markdown(
        f"<div class='draw-container'>{bg_html}{logo_html}<div class='winner-backdrop'><div class='winner-name'>{final_html}</div></div></div>", unsafe_allow_html=True
    )
    winners.to_csv(WINNERS_FILE, index=False)
