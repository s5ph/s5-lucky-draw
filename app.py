# Random Winner Picker – Complete with Left/Right Timers and Toggles

import streamlit as st
import pandas as pd
import random
import json
import time
import base64
import os

# --- Configuration ---
st.set_page_config("🎰 S5.COM Lucky Draw", layout="wide")
ASSETS_DIR = "uploaded_assets"
SETTINGS_FILE = "settings.json"
WINNERS_FILE = "winners.csv"

os.makedirs(ASSETS_DIR, exist_ok=True)

# --- Helper Functions ---
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

# --- Sidebar Controls ---
saved = load_settings()
st.sidebar.title("🔧 Settings & Controls")

# File uploads (unique keys)
logo_up = st.sidebar.file_uploader("Logo", type=["png","jpg","jpeg"], key="logo_up")
bg_up = st.sidebar.file_uploader("Background (Image/GIF/Video)", type=["png","jpg","jpeg","gif","mp4"], key="bg_up")
csv_up = st.sidebar.file_uploader("Participants CSV (ID,Name,Account)", type=["csv"], key="csv_up")
drum_up = st.sidebar.file_uploader("Drumroll Sound", type=["mp3","wav"], key="drum_up")
crash_up = st.sidebar.file_uploader("Crash Sound", type=["mp3","wav"], key="crash_up")
applause_up = st.sidebar.file_uploader("Applause Sound", type=["mp3","wav"], key="applause_up")

st.sidebar.markdown("---")
# Display columns (unique)
display_cols = st.sidebar.multiselect(
    "Display Columns", ["ID", "Name", "Account"],
    default=[c for c in ["ID","Name","Account"] if saved.get(f'show_{c.lower()}', True)],
    key="display_cols"
)
show_id = "ID" in display_cols
show_name = "Name" in display_cols
show_account = "Account" in display_cols

st.sidebar.markdown("---")
# Animation style selection
animation = st.sidebar.selectbox(
    "Animation Style",
    ["Scrolling", "Rolodex", "Letter-by-Letter", "Fade In", "Slide In"],
    index=["Scrolling", "Rolodex", "Letter-by-Letter", "Fade In", "Slide In"].index(saved.get('animation', 'Scrolling'))
)

st.sidebar.markdown("---")
# Display columns
display_cols = st.sidebar.multiselect(
    "Display Columns", ["ID", "Name", "Account"],
    default=[c for c in ["ID","Name","Account"] if saved.get(f'show_{c.lower()}', True)]
)
show_id = "ID" in display_cols
show_name = "Name" in display_cols
show_account = "Account" in display_cols

st.sidebar.markdown("---")
# Appearance
font_size = st.sidebar.slider("Font Size (px)", 20, 120, saved.get('font_size', 48), key="font_size")
font_color = st.sidebar.color_picker("Font Color", value=saved.get('font_color', '#FFFFFF'), key="font_color")
logo_width = st.sidebar.slider("Logo Width (px)", 50, 500, saved.get('logo_width', 150), key="logo_width")
backdrop_color = st.sidebar.color_picker("Backdrop Color", value=saved.get('backdrop_color', '#000000'), key="backdrop_color")
backdrop_opacity = st.sidebar.slider("Backdrop Opacity", 0.0, 1.0, saved.get('backdrop_opacity', 0.5), key="backdrop_opacity")
backdrop_padding = st.sidebar.slider("Backdrop Padding (px)", 0, 50, saved.get('backdrop_padding', 10), key="backdrop_padding")
winner_offset = st.sidebar.slider("Winner Y Offset (px)", 0, 600, saved.get('winner_offset', 200), key="winner_offset")

st.sidebar.markdown("---")
# Draw Settings
draw_duration = st.sidebar.slider("Draw Duration (sec)", 5, 60, saved.get('draw_duration', 15), key="draw_duration")
winner_count = st.sidebar.slider("Number of Winners", 1, 10, saved.get('winner_count', 3), key="winner_count")

st.sidebar.markdown("---")
# Audio & Effects
audio_volume = st.sidebar.slider("Audio Volume (%)", 0, 100, saved.get('audio_volume', 70), key="audio_volume")
mute_audio = st.sidebar.checkbox("Mute Audio", value=saved.get('mute_audio', False), key="mute_audio")
show_confetti = st.sidebar.checkbox("Show Confetti", value=saved.get('show_confetti', False), key="show_confetti")

st.sidebar.markdown("---")
# Timer toggles
show_left_timer = st.sidebar.checkbox("Show Left Timer", value=saved.get('show_left_timer', True), key="show_left_timer")
show_right_timer = st.sidebar.checkbox("Show Right Timer", value=saved.get('show_right_timer', True), key="show_right_timer")

st.sidebar.markdown("---")
# Actions
start_draw = st.sidebar.button("🎲 Start Draw", key="start_draw")
export_csv = st.sidebar.button("📥 Export Winners CSV", key="export_csv")
save_btn = st.sidebar.button("💾 Save Settings", key="save_settings")

# Save settings
if save_btn:
    settings = {
        'font_size': font_size, 'font_color': font_color, 'logo_width': logo_width,
        'backdrop_color': backdrop_color, 'backdrop_opacity': backdrop_opacity,
        'backdrop_padding': backdrop_padding, 'winner_offset': winner_offset,
        'draw_duration': draw_duration, 'winner_count': winner_count,
        'audio_volume': audio_volume, 'mute_audio': mute_audio,
        'show_confetti': show_confetti,
        'show_left_timer': show_left_timer, 'show_right_timer': show_right_timer,
        'show_id': show_id, 'show_name': show_name, 'show_account': show_account
    }
    save_settings(settings)
    st.sidebar.success("Settings saved!")

# --- Styles ---
# CSS animations
css = f"""
<style>
html, body, [data-testid='stApp'] {{ margin:0; padding:0; height:100%; }}
.draw-container {{ display:flex; align-items:center; justify-content:center; position:relative; width:100%; height:100vh; margin:0; padding:0; }}
.background-img, .background-vid {{ position:absolute; top:0; left:0; width:100%; height:100%; object-fit:cover; opacity:0.5; z-index:0; }}
.logo-img {{ position:absolute; top:10px; left:10px; width:{logo_width}px; z-index:2; }}
.winner-backdrop {{ display:inline-block; padding:{backdrop_padding}px; background:rgba({int(backdrop_color[1:3],16)},{int(backdrop_color[3:5],16)},{int(backdrop_color[5:],16)},{backdrop_opacity}); border-radius:10px; z-index:3; }}
.winner-name {{ font-size:{font_size}px; color:{font_color}; margin:0; transform:none; z-index:4; font-weight:bold; }}
.timer-left {{ position:absolute; left:20px; top:50%; transform:translateY(-50%); font-size:24px; color:{font_color}; margin:0; z-index:3; }}
.timer-right {{ position:absolute; right:20px; top:50%; transform:translateY(-50%); font-size:24px; color:{font_color}; margin:0; z-index:3; }}
@keyframes fadein {{ from {{ opacity:0; }} to {{ opacity:1; }} }}
@keyframes slidein {{ from {{ transform:translateX(-100%); }} to {{ transform:translateX(0); }} }}
.fade {{ animation: fadein 1s infinite; }}
.slide {{ animation: slidein 0.5s ease-in-out; }}
</style>
"""
st.markdown(css, unsafe_allow_html=True)
css = f"""
<style>
html, body, [data-testid='stApp'] {{ margin:0; padding:0; height:100%; }}
.draw-container {{ display:flex; align-items:center; justify-content:center; position:relative; width:100%; height:100vh; margin:0; padding:0; }}
.background-img, .background-vid {{ position:absolute; top:0; left:0; width:100%; height:100%; object-fit:cover; opacity:0.5; z-index:0; }}
.logo-img {{ position:absolute; top:10px; left:10px; width:{logo_width}px; z-index:2; }}
.winner-backdrop {{ display:inline-block; padding:{backdrop_padding}px; background:rgba({int(backdrop_color[1:3],16)},{int(backdrop_color[3:5],16)},{int(backdrop_color[5:],16)},{backdrop_opacity}); border-radius:10px; z-index:3; }}
.winner-name {{ font-size:{font_size}px; color:{font_color}; margin:0; transform: none; z-index:4; font-weight:bold; }}
.timer-left {{ position:absolute; left:20px; top:50%; transform:translateY(-50%); font-size:24px; color:{font_color}; margin:0; z-index:3; }}
.timer-right {{ position:absolute; right:20px; top:50%; transform:translateY(-50%); font-size:24px; color:{font_color}; margin:0; z-index:3; }}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# --- Asset Persistence ---
logo_path = save_file(logo_up, 'logo')
bg_path = save_file(bg_up, 'background')
dr_path = save_file(drum_up, 'drumroll')
cr_path = save_file(crash_up, 'crash')
ap_path = save_file(applause_up, 'applause')

# Export winners CSV
if export_csv and os.path.exists(WINNERS_FILE):
    with open(WINNERS_FILE, 'rb') as f:
        st.sidebar.download_button("Download Winners CSV", f, file_name="winners.csv")

# --- Placeholders ---
bg_ph = st.empty()
logo_ph = st.empty()
scroll_ph = st.empty()
left_timer_ph = st.empty()
right_timer_ph = st.empty()
audio_ph = st.empty()

# --- Draw Logic ---
if start_draw and csv_up:
    df = pd.read_csv(csv_up)
    # Column detection
    id_col = next((c for c in df.columns if c.lower()=='id'), None)
    name_col = next((c for c in df.columns if c.lower()=='name'), None)
    acc_col = next((c for c in df.columns if 'account' in c.lower()), None)
    if name_col is None:
        st.error("CSV must contain a 'Name' column.")
        st.stop()

    # Build HTML
    bg_html = ''
    if bg_path and os.path.exists(bg_path):
        ext = bg_path.rsplit('.',1)[-1].lower()
        data = base64.b64encode(open(bg_path,'rb').read()).decode()
        if ext in ['mp4','webm']:
            bg_html = f"<video autoplay loop muted class='background-vid'><source src='data:video/{ext};base64,{data}' type='video/{ext}'></video>"
        else:
            bg_html = f"<img src='data:image/{ext};base64,{data}' class='background-img'>"
    logo_html = ''
    if logo_path and os.path.exists(logo_path):
        ext = logo_path.rsplit('.',1)[-1].lower()
        data = base64.b64encode(open(logo_path,'rb').read()).decode()
        logo_html = f"<img src='data:image/{ext};base64,{data}' class='logo-img'>"

    # Drumroll
    if not mute_audio and dr_path and os.path.exists(dr_path):
        ddata = base64.b64encode(open(dr_path,'rb').read()).decode()
        audio_ph.markdown(f"<audio autoplay loop><source src='data:audio/mp3;base64,{ddata}' type='audio/mp3'></audio>", unsafe_allow_html=True)

    # Scroll effect with dual timers and animation styles
names = df[name_col].dropna().tolist()
start_time = time.time()
while (elapsed := time.time() - start_time) < draw_duration:
    remaining = draw_duration - elapsed
    # Animation handling
    if animation == 'Scrolling':
        name = random.choice(names)
    elif animation == 'Rolodex':
        # sequential roll
        idx = int(elapsed / (draw_duration/len(names))) % len(names)
        name = names[idx]
    elif animation == 'Letter-by-Letter':
        full_name = random.choice(names)
        for i in range(1, len(full_name)+1):
            scroll_ph.markdown(f"<div class='draw-container'>{bg_html}{logo_html}<div class='winner-backdrop'><div class='winner-name'>{full_name[:i]}</div></div></div>", unsafe_allow_html=True)
            time.sleep(0.05)
        continue
    elif animation == 'Fade In':
        name = random.choice(names)
        style = 'fade'
    elif animation == 'Slide In':
        name = random.choice(names)
        style = 'slide'
    else:
        name = random.choice(names)
        style = ''
    # Timer HTML
    timer_left_html = f"<div class='timer-left'>⏳ {remaining:.1f}s</div>" if show_left_timer else ""
    timer_right_html = f"<div class='timer-right'>⏳ {remaining:.1f}s</div>" if show_right_timer else ""
    # Name with effect class
    name_html = f"<div class='winner-name {style}'>{name}</div>"
    # Render frame
    scroll_ph.markdown(
        f"<div class='draw-container'>{bg_html}{logo_html}{timer_left_html}{timer_right_html}" +
        f"<div class='winner-backdrop'>{name_html}</div></div>",
        unsafe_allow_html=True
    )
    time.sleep(0.1)

# Final winners
    winners = df.sample(n=winner_count)
    audio_ph.empty()
    if not mute_audio and cr_path and os.path.exists(cr_path):
        cdata = base64.b64encode(open(cr_path,'rb').read()).decode()
        st.markdown(f"<audio autoplay><source src='data:audio/mp3;base64,{cdata}' type='audio/mp3'></audio>", unsafe_allow_html=True)
    if not mute_audio and ap_path and os.path.exists(ap_path):
        adata = base64.b64encode(open(ap_path,'rb').read()).decode()
        st.markdown(f"<audio autoplay><source src='data:audio/mp3;base64,{adata}' type='audio/mp3'></audio>", unsafe_allow_html=True)

    # Display winners
    final_html = "<br>".join([
        (str(r[id_col]) + " | " if show_id and id_col else "") +
        (str(r[name_col]) if show_name else "") +
        (" | " + str(r[acc_col]) if show_account and acc_col else "")
        for _, r in winners.iterrows()
    ])
    scroll_ph.markdown(
        f"<div class='draw-container'>{bg_html}{logo_html}" +
        (f"<div class='timer-left'></div>" if show_left_timer else "") +
        (f"<div class='timer-right'></div>" if show_right_timer else "") +
        f"<div class='winner-backdrop'><div class='winner-name'>{final_html}</div></div></div>",
        unsafe_allow_html=True
    )
    left_timer_ph.empty()
    right_timer_ph.empty()
    winners.to_csv(WINNERS_FILE, index=False)(WINNERS_FILE, index=False)
