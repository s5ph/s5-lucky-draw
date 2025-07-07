# Random Winner Picker – Stable Final Version

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

# Helper: encode upload to base64
def encode_file(upload):
    if not upload:
        return None, None
    data = upload.read()
    upload.seek(0)
    ext = upload.name.split('.')[-1].lower()
    return base64.b64encode(data).decode(), ext

# Settings load/save
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE,'r') as f:
            return json.load(f)
    return {}

def save_settings(s):
    with open(SETTINGS_FILE,'w') as f:
        json.dump(s,f)

# --- Sidebar ---
saved = load_settings()
st.sidebar.title("🔧 Settings & Controls")
# Uploads\logo_up = st.sidebar.file_uploader("Logo (png/jpg)", type=["png","jpg","jpeg"])
bg_up = st.sidebar.file_uploader("Background (img/gif/mp4)", type=["png","jpg","jpeg","gif","mp4"])
csv_up = st.sidebar.file_uploader("Participants CSV", type=["csv"])
dr_up = st.sidebar.file_uploader("Drumroll Sound", type=["mp3","wav"])
cr_up = st.sidebar.file_uploader("Crash Sound", type=["mp3","wav"])
ap_up = st.sidebar.file_uploader("Applause Sound", type=["mp3","wav"])

# Columns
display_cols = st.sidebar.multiselect(
    "Display Columns", ["ID","Name","Account"],
    default=saved.get('display_cols',["ID","Name","Account"]) )
show_id = "ID" in display_cols
show_name = "Name" in display_cols
show_account = "Account" in display_cols

# Animation & controls
animation = st.sidebar.selectbox(
    "Animation Style", ["Scrolling","Rolodex","Letter-by-Letter"]
)
rolodex_speed = st.sidebar.slider("Rolodex Scroll Speed",1,50,saved.get('rolodex_speed',10))
rolodex_interval = st.sidebar.slider("Rolodex Interval (ms)",50,500,saved.get('rolodex_interval',200))

draw_duration = st.sidebar.slider("Draw Duration (sec)",5,60,saved.get('draw_duration',15))
winner_count = st.sidebar.slider("Number of Winners",1,10,saved.get('winner_count',3))
font_size = st.sidebar.slider("Font Size (px)",20,120,saved.get('font_size',48))
font_color = st.sidebar.color_picker("Font Color",saved.get('font_color','#FFF'))
logo_width = st.sidebar.slider("Logo Width (px)",50,500,saved.get('logo_width',150))
show_left_timer = st.sidebar.checkbox("Show Left Timer",saved.get('show_left_timer',True))
show_right_timer = st.sidebar.checkbox("Show Right Timer",saved.get('show_right_timer',True))

# Actions
start_draw = st.sidebar.button("🎲 Start Draw")
export_btn = st.sidebar.button("📥 Export Winners CSV")
save_btn = st.sidebar.button("💾 Save Settings")
if save_btn:
    save_settings({
        'display_cols':display_cols, 'animation':animation,
        'rolodex_speed':rolodex_speed,'rolodex_interval':rolodex_interval,
        'draw_duration':draw_duration,'winner_count':winner_count,
        'font_size':font_size,'font_color':font_color,'logo_width':logo_width,
        'show_left_timer':show_left_timer,'show_right_timer':show_right_timer
    })
    st.sidebar.success("Settings saved!")

# CSS
st.markdown(f"""
<style>
.draw-container {{position:relative; width:100%; height:100vh; display:flex; align-items:center; justify-content:center;}}
.background-img, .background-vid {{position:absolute; top:0; left:0; width:100%; height:100%; object-fit:cover; opacity:0.5; z-index:0;}}
.logo-img {{position:absolute; top:10px; left:10px; width:{logo_width}px; z-index:2;}}
.winner-name {{font-size:{font_size}px; color:{font_color}; margin:0; z-index:3;}}
.timer-left {{position:absolute; left:20px; top:50%; transform:translateY(-50%); z-index:3;}}
.timer-right {{position:absolute; right:20px; top:50%; transform:translateY(-50%); z-index:3;}}
</style>
""",unsafe_allow_html=True)

# Placeholders
scroll_ph = st.empty()
audio_ph = st.empty()

# --- Draw Logic ---
if start_draw and csv_up:
    # Load data
    df = pd.read_csv(csv_up)
    id_col = next((c for c in df.columns if c.lower()=='id'),None)
    name_col = next((c for c in df.columns if c.lower()=='name'),None)
    acc_col = next((c for c in df.columns if 'account' in c.lower()),None)
    if not name_col:
        st.error("CSV needs a 'Name' column.")
        st.stop()

    # Encode media
    drum_b64, drum_ext = encode_file(dr_up)
    crash_b64, crash_ext = encode_file(cr_up)
    applause_b64, applause_ext = encode_file(ap_up)
    bg_b64, bg_ext = encode_file(bg_up)
    logo_b64, logo_ext = encode_file(logo_up)

    # Play drumroll
    if drum_b64:
        audio_ph.markdown(f"<audio autoplay loop><source src='data:audio/{drum_ext};base64,{drum_b64}'></audio>",unsafe_allow_html=True)

    names = df[name_col].dropna().tolist()
    start=time.time()
    while time.time()-start < draw_duration:
        rem = draw_duration - (time.time()-start)
        left_html = f"<div class='timer-left'>⏳ {rem:.1f}s</div>" if show_left_timer else ''
        right_html = f"<div class='timer-right'>⏳ {rem:.1f}s</div>" if show_right_timer else ''

        # Render background/logo
        bg_html = ''
        if bg_b64:
            if bg_ext in ['mp4','webm']:
                bg_html = f"<video autoplay loop muted class='background-vid'><source src='data:video/{bg_ext};base64,{bg_b64}'></video>"
            else:
                bg_html = f"<img src='data:image/{bg_ext};base64,{bg_b64}' class='background-img'>"
        logo_html = f"<img src='data:image/{logo_ext};base64,{logo_b64}' class='logo-img'>" if logo_b64 else ''

        # Animation
        sleep_t=0.1
        if animation=='Scrolling':
            name=random.choice(names)
            name_html=f"<div class='winner-name'>{name}</div>"
        elif animation=='Rolodex':
            name=random.choice(names)
            mh=font_size
            name_html=f"<marquee direction='up' scrollamount='{rolodex_speed}' height='{mh}px'><div class='winner-name'>{name}</div></marquee>"
            sleep_t=rolodex_interval/1000
        else:
            full=random.choice(names)
            for i in range(1,len(full)+1):
                scroll_ph.markdown(f"<div class='draw-container'>{bg_html}{logo_html}{left_html}{right_html}<div class='winner-name'>{full[:i]}</div></div>",unsafe_allow_html=True)
                time.sleep(0.05)
            continue

        scroll_ph.markdown(f"<div class='draw-container'>{bg_html}{logo_html}{left_html}{right_html}{name_html}</div>",unsafe_allow_html=True)
        time.sleep(sleep_t)

    # End sounds
    audio_ph.empty()
    if crash_b64:
        st.markdown(f"<audio autoplay><source src='data:audio/{crash_ext};base64,{crash_b64}'></audio>",unsafe_allow_html=True)
    if applause_b64:
        st.markdown(f"<audio autoplay><source src='data:audio/{applause_ext};base64,{applause_b64}'></audio>",unsafe_allow_html=True)

    # Final winners
    winners=df.sample(winner_count)
    lines=[" | ".join([str(r[col]) for col,flag in [(id_col,show_id),(name_col,show_name),(acc_col,show_account)] if flag and col]) for _,r in winners.iterrows()]
    scroll_ph.markdown(f"<div class='draw-container'>{bg_html}{logo_html}<div class='winner-backdrop'><div class='winner-name'>{'<br>'.join(lines)}</div></div></div>",unsafe_allow_html=True)
    winners.to_csv(WINNERS_FILE,index=False)
