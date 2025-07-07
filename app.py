# Random Winner Picker – Final Corrected Version

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
        return json.load(open(SETTINGS_FILE))
    return {}

def save_settings(settings):
    json.dump(settings, open(SETTINGS_FILE, 'w'))

# Sidebar Controls
saved = load_settings()
st.sidebar.title("🔧 Settings & Controls")

# Uploads
logo_up = st.sidebar.file_uploader("Logo (png/jpg)", type=["png","jpg","jpeg"], key="logo_up")
bg_up = st.sidebar.file_uploader("Background (img/gif/mp4)", type=["png","jpg","jpeg","gif","mp4"], key="bg_up")
csv_up = st.sidebar.file_uploader("Participants CSV (ID,Name,Account)", type=["csv"], key="csv_up")
dr_up = st.sidebar.file_uploader("Drumroll Sound", type=["mp3","wav"], key="dr_up")
cr_up = st.sidebar.file_uploader("Crash Sound", type=["mp3","wav"], key="cr_up")
ap_up = st.sidebar.file_uploader("Applause Sound", type=["mp3","wav"], key="ap_up")

st.sidebar.markdown("---")
# Display Columns
display_cols = st.sidebar.multiselect("Display Columns", ["ID","Name","Account"], default=saved.get('display_cols',["ID","Name","Account"]), key="display_cols")
show_id = "ID" in display_cols
show_name = "Name" in display_cols
show_account = "Account" in display_cols

st.sidebar.markdown("---")
# Animation Style
animation = st.sidebar.selectbox("Animation Style", ["Scrolling","Rolodex","Letter-by-Letter"], index=["Scrolling","Rolodex","Letter-by-Letter"].index(saved.get('animation','Scrolling')), key="animation")

st.sidebar.markdown("---")
# Appearance & Timers
draw_duration = st.sidebar.slider("Draw Duration (sec)", 5, 60, saved.get('draw_duration',15), key="draw_duration")
winner_count = st.sidebar.slider("Number of Winners", 1, 10, saved.get('winner_count',3), key="winner_count")
font_size = st.sidebar.slider("Font Size (px)", 20, 120, saved.get('font_size',48), key="font_size")
font_color = st.sidebar.color_picker("Font Color", saved.get('font_color','#FFFFFF'), key="font_color")
backdrop_color = st.sidebar.color_picker("Backdrop Color", saved.get('backdrop_color','#000000'), key="backdrop_color")
backdrop_opacity = st.sidebar.slider("Backdrop Opacity", 0.0, 1.0, saved.get('backdrop_opacity',0.5), key="backdrop_opacity")
backdrop_padding = st.sidebar.slider("Backdrop Padding (px)", 0, 50, saved.get('backdrop_padding',10), key="backdrop_padding")
logo_width = st.sidebar.slider("Logo Width (px)", 50, 500, saved.get('logo_width',150), key="logo_width")
show_left_timer = st.sidebar.checkbox("Show Left Timer", saved.get('show_left_timer',True), key="show_left_timer")
show_right_timer = st.sidebar.checkbox("Show Right Timer", saved.get('show_right_timer',True), key="show_right_timer")

st.sidebar.markdown("---")
# Actions
start_draw = st.sidebar.button("🎲 Start Draw", key="start_draw")
export_csv = st.sidebar.button("📥 Export Winners", key="export_csv")
save_btn = st.sidebar.button("💾 Save Settings", key="save_settings")

if save_btn:
    save_settings({
        'display_cols':display_cols, 'animation':animation, 'draw_duration':draw_duration,
        'winner_count':winner_count, 'font_size':font_size, 'font_color':font_color,
        'backdrop_color':backdrop_color, 'backdrop_opacity':backdrop_opacity, 'backdrop_padding':backdrop_padding,
        'logo_width':logo_width, 'show_left_timer':show_left_timer, 'show_right_timer':show_right_timer
    })
    st.sidebar.success("Settings saved!")

# CSS
css = f"""
<style>
html, body, [data-testid='stApp'] {{ margin:0; padding:0; height:100%; }}
.draw-container {{ display:flex; align-items:center; justify-content:center; position:relative; width:100%; height:100vh; }}
.background-img, .background-vid {{ position:absolute; top:0; left:0; width:100%; height:100%; object-fit:cover; opacity:0.5; z-index:0; }}
.logo-img {{ position:absolute; top:10px; left:10px; width:{logo_width}px; z-index:2; }}
.winner-backdrop {{ padding:{backdrop_padding}px; background:rgba({int(backdrop_color[1:3],16)},{int(backdrop_color[3:5],16)},{int(backdrop_color[5:],16)},{backdrop_opacity}); border-radius:10px; z-index:3; }}
.winner-name {{ font-size:{font_size}px; color:{font_color}; margin:0; z-index:4; font-weight:bold; }}
.timer-left {{ position:absolute; left:20px; top:50%; transform:translateY(-50%); font-size:24px; color:{font_color}; z-index:3; }}
.timer-right {{ position:absolute; right:20px; top:50%; transform:translateY(-50%); font-size:24px; color:{font_color}; z-index:3; }}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# Placeholders
bg_ph = st.empty()
logo_ph = st.empty()
scroll_ph = st.empty()
left_ph = st.empty()
right_ph = st.empty()
audio_ph = st.empty()

# Draw Logic
if start_draw and csv_up:
    df = pd.read_csv(csv_up)
    id_col = next((c for c in df.columns if c.lower()=='id'), None)
    name_col = next((c for c in df.columns if c.lower()=='name'), None)
    acc_col = next((c for c in df.columns if 'account' in c.lower()), None)
    if not name_col:
        st.error("CSV must contain a 'Name' column.")
        st.stop()

    # Prepare background data
    bg_data = None
    bg_ext = None
    if bg_up is not None:
        bg_bytes = bg_up.read()
        bg_ext = bg_up.name.split('.')[-1].lower()
        bg_data = base64.b64encode(bg_bytes).decode()

    # Prepare logo data
    logo_data = None
    logo_ext = None
    if logo_up is not None:
        logo_bytes = logo_up.read()
        logo_ext = logo_up.name.split('.')[-1].lower()
        logo_data = base64.b64encode(logo_bytes).decode()

    # Play drumroll
    if dr_up is not None:
        drum_bytes = dr_up.read()
        drum_b64 = base64.b64encode(drum_bytes).decode()
        audio_ph.markdown(f"<audio autoplay loop><source src='data:audio/mp3;base64,{drum_b64}' type='audio/mp3'></audio>", unsafe_allow_html=True)

    names = df[name_col].dropna().tolist()
    start_time = time.time()
    while time.time() - start_time < draw_duration:
        rem = draw_duration - (time.time() - start_time)
        left_html = f"<div class='timer-left'>⏳ {rem:.1f}s</div>" if show_left_timer else ''
        right_html = f"<div class='timer-right'>⏳ {rem:.1f}s</div>" if show_right_timer else ''

        # Choose animation style
        if animation == 'Scrolling':
            name = random.choice(names)
            name_html = f"<div class='winner-name'>{name}</div>"
        elif animation == 'Rolodex':
            name = random.choice(names)
            marquee_h = font_size + backdrop_padding*2
            name_html = (
                f"<marquee direction='up' scrollamount='5' height='{marquee_h}px'>"
                f"<div class='winner-name'>{name}</div>"
                f"</marquee>"
            )
        else:  # Letter-by-Letter
            full = random.choice(names)
            for i in range(1, len(full)+1):
                scroll_ph.markdown(
                    f"<div class='draw-container' style='background-image:url(data:image/{bg_ext};base64,{bg_data}); background-size:cover;'>" +
                    (f"<img src='data:image/{logo_ext};base64,{logo_data}' class='logo-img'>" if logo_data else "") +
                    f"{left_html}{right_html}<div class='winner-backdrop'><div class='winner-name'>{full[:i]}</div></div></div>",
                    unsafe_allow_html=True
                )
                time.sleep(0.05)
            continue

        # Render frame with background and logo
        scroll_ph.markdown(
            f"<div class='draw-container' style='background-image:url(data:image/{bg_ext};base64,{bg_data}); background-size:cover;'>" +
            (f"<img src='data:image/{logo_ext};base64,{logo_data}' class='logo-img'>" if logo_data else "") +
            f"{left_html}{right_html}<div class='winner-backdrop'>{name_html}</div></div>",
            unsafe_allow_html=True
        )
        time.sleep(0.1)

    # Stop drumroll
    audio_ph.empty()
    if cr_up is not None:
        crash_b64 = base64.b64encode(cr_up.read()).decode()
        st.markdown(f"<audio autoplay><source src='data:audio/mp3;base64,{crash_b64}' type='audio/mp3'></audio>", unsafe_allow_html=True)
    if ap_up is not None:
        applause_b64 = base64.b64encode(ap_up.read()).decode()
        st.markdown(f"<audio autoplay><source src='data:audio/mp3;base64,{applause_b64}' type='audio/mp3'></audio>", unsafe_allow_html=True)

    # Display final winners
    winners = df.sample(n=winner_count)
    final_html = '<br>'.join([
        (str(r[id_col]) + ' | ' if show_id and id_col else '') +
        (str(r[name_col]) if show_name else '') +
        (' | ' + str(r[acc_col]) if show_account and acc_col else '')
        for _, r in winners.iterrows()
    ])
    scroll_ph.markdown(
        f"<div class='draw-container' style='background-image:url(data:image/{bg_ext};base64,{bg_data}); background-size:cover;'>" +
        (f"<img src='data:image/{logo_ext};base64,{logo_data}' class='logo-img'>" if logo_data else "") +
        f"<div class='winner-backdrop'><div class='winner-name'>{final_html}</div></div></div>",
        unsafe_allow_html=True
    )
    winners.to_csv(WINNERS_FILE, index=False)

# End of Script
