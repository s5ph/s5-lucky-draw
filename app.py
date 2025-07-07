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
# Animation Style
animation = st.sidebar.selectbox("Animation Style", ["Scrolling","Rolodex","Letter-by-Letter","Fade In","Slide In"], index=["Scrolling","Rolodex","Letter-by-Letter","Fade In","Slide In"].index(saved.get('animation','Scrolling')), key="animation")

# Appearance
font_size = st.sidebar.slider("Font Size (px)", 20, 120, saved.get('font_size',48), key="font_size")
font_color = st.sidebar.color_picker("Font Color", saved.get('font_color','#FFFFFF'), key="font_color")
winner_count = st.sidebar.slider("Number of Winners",1,10,saved.get('winner_count',3), key="winner_count")
draw_duration = st.sidebar.slider("Draw Duration (sec)",5,60,saved.get('draw_duration',15), key="draw_duration")
show_left_timer = st.sidebar.checkbox("Left Timer", saved.get('show_left_timer',True), key="show_left_timer")
show_right_timer = st.sidebar.checkbox("Right Timer", saved.get('show_right_timer',True), key="show_right_timer")

st.sidebar.markdown("---")
start_btn = st.sidebar.button("🎲 Start Draw")
export_btn = st.sidebar.button("📥 Export Winners", key="export_btn")

# Save Settings
def _save():
    save_settings({
        'display_cols': display_cols,'animation': animation,
        'font_size': font_size,'winner_count': winner_count,'draw_duration': draw_duration,
        'show_left_timer': show_left_timer,'show_right_timer': show_right_timer
    })
if st.sidebar.button("💾 Save Settings"):
    _save()
    st.sidebar.success("Settings saved!")

# CSS
st.markdown(f"""
<style>
html, body, [data-testid='stApp'] {{ margin:0; padding:0; height:100%; }}
.draw-container {{ display:flex; align-items:center; justify-content:center; position:relative; width:100%; height:100vh; }}
.background-img, .background-vid {{ position:absolute; top:0; left:0; width:100%; height:100%; object-fit:cover; opacity:0.5; z-index:0; }}
.logo-img {{ position:absolute; top:10px; left:10px; width:{font_size*2}px; z-index:2; }}
.winner-backdrop {{ display:inline-block; padding:10px; background:rgba(0,0,0,0.5); border-radius:10px; z-index:3; }}
.winner-name {{ font-size:{font_size}px; color:{font_color}; margin:0; z-index:4; font-weight:bold; }}
.timer-left {{ position:absolute; left:20px; top:50%; transform:translateY(-50%); font-size:24px; color:{font_color}; z-index:3; }}
.timer-right {{ position:absolute; right:20px; top:50%; transform:translateY(-50%); font-size:24px; color:{font_color}; z-index:3; }}
</style>
""", unsafe_allow_html=True)

# Placeholders
bg_ph = st.empty()
logo_ph = st.empty()
scroll_ph = st.empty()
left_ph = st.empty()
right_ph = st.empty()
audio_ph = st.empty()

# Draw Logic
if start_btn and csv_up:
    df = pd.read_csv(csv_up)
    # Detect columns
    id_col = next((c for c in df.columns if c.lower()=='id'), None)
    name_col = next((c for c in df.columns if c.lower()=='name'), None)
    acc_col = next((c for c in df.columns if 'account' in c.lower()), None)
    if not name_col:
        st.error("CSV must contain a 'Name' column.")
        st.stop()
    # Load assets
    # Background
    path = save_file(bg_up, 'background')
    if path:
        ext = path.split('.')[-1]
        data = base64.b64encode(open(path,'rb').read()).decode()
        tag = f"video autoplay loop muted class='background-vid'" if ext in ['mp4','webm'] else f"img src='data:image/{ext};base64,{data}' class='background-img'"
        bg_ph.markdown(f"<{tag}></{tag.split()[0]}>", unsafe_allow_html=True)
    # Logo
    path = save_file(logo_up, 'logo')
    if path:
        ext = path.split('.')[-1]
        data = base64.b64encode(open(path,'rb').read()).decode()
        logo_ph.markdown(f"<img src='data:image/{ext};base64,{data}' class='logo-img'>", unsafe_allow_html=True)
    # Drumroll
    path = save_file(dr_up, 'drumroll')
    if path:
        ddata = base64.b64encode(open(path,'rb').read()).decode()
        audio_ph.markdown(f"<audio autoplay loop><source src='data:audio/mp3;base64,{ddata}'></audio>", unsafe_allow_html=True)

    names = df[name_col].dropna().tolist()
    start = time.time()
    while time.time() - start < draw_duration:
        rem = draw_duration - (time.time() - start)
        left_html = f"<div class='timer-left'>⏳ {rem:.1f}s</div>" if show_left_timer else ''
        right_html = f"<div class='timer-right'>⏳ {rem:.1f}s</div>" if show_right_timer else ''
        # Animation
        if animation == 'Scrolling':
            name = random.choice(names)
            name_html = f"<div class='winner-name'>{name}</div>"
        elif animation == 'Rolodex':
            # single vertical marquee of one random name
            name = random.choice(names)
            name_html = f"<marquee direction='up' scrollamount='10'><div class='winner-name'>{name}</div></marquee>"
        elif animation == 'Letter-by-Letter':
            full = random.choice(names)
            for i in range(1, len(full)+1):
                scroll_ph.markdown(f"<div class='draw-container'>{left_html}{right_html}<div class='winner-backdrop'><div class='winner-name'>{full[:i]}</div></div></div>", unsafe_allow_html=True)
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
