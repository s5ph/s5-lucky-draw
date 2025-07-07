import streamlit as st
import pandas as pd
import random
import time
import base64
import os

st.set_page_config("S5 Lucky Draw", layout="wide")

# --- Sidebar controls ---
st.sidebar.title("S5 Lucky Draw Controls")
uploaded_logo = st.sidebar.file_uploader("Upload Logo", type=["png", "jpg", "jpeg"])
uploaded_bg = st.sidebar.file_uploader("Upload Background (Image/Video)", type=["png", "jpg", "jpeg", "gif", "mp4"])
uploaded_csv = st.sidebar.file_uploader("Upload CSV", type=["csv"])

with st.sidebar.expander("Animation & Appearance", expanded=True):
    animation = st.selectbox("Draw Animation Style", [
        "Scrolling", "Rolodex", "Letter-by-Letter", "Fade In", "Slide In"
    ])
    font_size = st.slider("Font Size", 30, 120, 60)
    font_color = st.color_picker("Font Color", "#FFFFFF")
    backdrop_color = st.color_picker("Backdrop Color", "#000000")
    backdrop_opacity = st.slider("Backdrop Opacity", 0.0, 1.0, 0.5)
    logo_width = st.slider("Logo Width (px)", 80, 600, 200)
    winner_count = st.number_input("Number of Winners", 1, 10, 1)
    draw_time = st.slider("Draw Duration (s)", 5, 60, 10)
    show_timer_left = st.checkbox("Show Timer Left", value=True)
    show_timer_right = st.checkbox("Show Timer Right", value=True)
    winner_offset = st.slider("Winner Vertical Offset", -200, 200, 0)

if animation == "Rolodex":
    with st.sidebar.expander("Rolodex Settings", expanded=True):
        rolodex_speed = st.slider("Rolodex Marquee Scrollamount", 1, 50, 10)
        rolodex_interval = st.slider("Rolodex Name Interval (ms)", 10, 500, 100)

display_cols = st.sidebar.multiselect(
    "Display Columns", ["ID", "Name", "Account"],
    default=["Name", "Account"],
    key="display_cols"
)

start_draw = st.sidebar.button("🎲 Start Draw")

# --- Utility for backgrounds ---
def get_b64(file):
    return base64.b64encode(file.read()).decode()

def inject_background(bg_file):
    ext = bg_file.name.split(".")[-1].lower()
    b64 = get_b64(bg_file)
    if ext == "mp4":
        st.markdown(
            f"""<video autoplay loop muted playsinline
                style="position:fixed;right:0;bottom:0;min-width:100vw;min-height:100vh;z-index:0;object-fit:cover;">
                <source src="data:video/mp4;base64,{b64}" type="video/mp4">
            </video>""", unsafe_allow_html=True)
    else:
        st.markdown(
            f"""<div style="position:fixed;top:0;left:0;width:100vw;height:100vh;z-index:0;
            background: url('data:image/{ext};base64,{b64}') no-repeat center center fixed;
            background-size:cover;opacity:1;"></div>""", unsafe_allow_html=True)

def inject_logo(logo_file, width):
    ext = logo_file.name.split(".")[-1].lower()
    b64 = get_b64(logo_file)
    st.markdown(
        f"""<img src="data:image/{ext};base64,{b64}"
        style="position:absolute;top:30px;left:50%;transform:translateX(-50%);
        z-index:3;width:{width}px;max-width:40vw;">""", unsafe_allow_html=True)

def get_column(df, options):
    for o in options:
        c = next((col for col in df.columns if col.lower() == o.lower()), None)
        if c: return c
    return None

# --- Main draw logic ---
if start_draw:
    if uploaded_bg:
        inject_background(uploaded_bg)
    if uploaded_logo:
        inject_logo(uploaded_logo, logo_width)

    # --- Data prep ---
    if not uploaded_csv:
        st.error("Please upload a CSV with player info.")
        st.stop()
    df = pd.read_csv(uploaded_csv)
    name_col = get_column(df, ["name"])
    id_col = get_column(df, ["id"])
    acc_col = get_column(df, ["account", "account id", "account name"])

    if not name_col:
        st.error("CSV must contain a 'name' column (case-insensitive).")
        st.stop()

    display_cols_found = []
    if "ID" in display_cols and id_col: display_cols_found.append(id_col)
    if "Name" in display_cols: display_cols_found.append(name_col)
    if "Account" in display_cols and acc_col: display_cols_found.append(acc_col)

    names = df[name_col].dropna().astype(str).tolist()
    winners_df = df.sample(n=winner_count)
    winner_lines = []
    for _, row in winners_df.iterrows():
        line = " | ".join(str(row[c]) for c in display_cols_found)
        winner_lines.append(line)
    winners_str = "<br>".join(winner_lines)

    # --- Placeholders ---
    container = st.empty()
    timer_left_ph = st.empty() if show_timer_left else None
    timer_right_ph = st.empty() if show_timer_right else None

    # --- Animation logic ---
    t_end = time.time() + draw_time
    last_time = None
    name_i = 0
    while time.time() < t_end:
        t_remain = t_end - time.time()
        show_time = f"<div style='color:#FFD700;font-size:2em;font-weight:bold;text-shadow:2px 2px 4px #000'>{t_remain:.1f}s</div>"

        # Timer left/right
        if timer_left_ph: timer_left_ph.markdown(
            f"<div style='position:fixed;left:20px;top:50%;transform:translateY(-50%);z-index:4'>{show_time}</div>", unsafe_allow_html=True)
        if timer_right_ph: timer_right_ph.markdown(
            f"<div style='position:fixed;right:20px;top:50%;transform:translateY(-50%);z-index:4'>{show_time}</div>", unsafe_allow_html=True)

        # Animation styles
        if animation == "Scrolling":
            display_name = random.choice(names)
            draw_html = f"""
            <div style="position:relative;height:100vh;display:flex;align-items:center;justify-content:center;z-index:2;">
                <div style="background:rgba({int(backdrop_color[1:3],16)},{int(backdrop_color[3:5],16)},{int(backdrop_color[5:],16)},{backdrop_opacity});padding:24px 48px;border-radius:12px;">
                    <span style="font-size:{font_size}px;color:{font_color};font-weight:bold;">{display_name}</span>
                </div>
            </div>
            """
        elif animation == "Rolodex":
            # Cycle through names at custom speed/interval
            display_name = names[name_i % len(names)]
            draw_html = f"""
            <div style="position:relative;height:100vh;display:flex;align-items:center;justify-content:center;z-index:2;">
                <div style="background:rgba({int(backdrop_color[1:3],16)},{int(backdrop_color[3:5],16)},{int(backdrop_color[5:],16)},{backdrop_opacity});padding:24px 48px;border-radius:12px;">
                    <span style="font-size:{font_size}px;color:{font_color};font-weight:bold;">{display_name}</span>
                </div>
            </div>
            """
            name_i += 1
            time.sleep(rolodex_interval/1000)
            container.markdown(draw_html, unsafe_allow_html=True)
            continue  # Only update interval
        elif animation == "Letter-by-Letter":
            # Random name, reveal char by char
            target = random.choice(names)
            chars = int(((draw_time-t_remain)/draw_time)*len(target))
            display = target[:max(1,chars)]
            draw_html = f"""
            <div style="position:relative;height:100vh;display:flex;align-items:center;justify-content:center;z-index:2;">
                <div style="background:rgba({int(backdrop_color[1:3],16)},{int(backdrop_color[3:5],16)},{int(backdrop_color[5:],16)},{backdrop_opacity});padding:24px 48px;border-radius:12px;">
                    <span style="font-size:{font_size}px;color:{font_color};font-weight:bold;">{display}</span>
                </div>
            </div>
            """
        elif animation == "Fade In":
            display_name = random.choice(names)
            draw_html = f"""
            <div style="position:relative;height:100vh;display:flex;align-items:center;justify-content:center;z-index:2;">
                <div style="background:rgba({int(backdrop_color[1:3],16)},{int(backdrop_color[3:5],16)},{int(backdrop_color[5:],16)},{backdrop_opacity});padding:24px 48px;border-radius:12px;animation:fadein 0.5s;">
                    <span style="font-size:{font_size}px;color:{font_color};font-weight:bold;">{display_name}</span>
                </div>
            </div>
            <style>@keyframes fadein{{from{{opacity:0}}to{{opacity:1}}}}</style>
            """
        elif animation == "Slide In":
            display_name = random.choice(names)
            draw_html = f"""
            <div style="position:relative;height:100vh;display:flex;align-items:center;justify-content:center;z-index:2;">
                <div style="background:rgba({int(backdrop_color[1:3],16)},{int(backdrop_color[3:5],16)},{int(backdrop_color[5:],16)},{backdrop_opacity});padding:24px 48px;border-radius:12px;animation:slidein 0.5s;">
                    <span style="font-size:{font_size}px;color:{font_color};font-weight:bold;">{display_name}</span>
                </div>
            </div>
            <style>@keyframes slidein{{from{{transform:translateX(-100vw)}}to{{transform:translateX(0)}}}}</style>
            """
        container.markdown(draw_html, unsafe_allow_html=True)
        time.sleep(0.1)

    # --- Reveal winners ---
    winner_html = f"""
    <div style="position:relative;height:100vh;display:flex;align-items:center;justify-content:center;z-index:2;">
        <div style="background:rgba({int(backdrop_color[1:3],16)},{int(backdrop_color[3:5],16)},{int(backdrop_color[5:],16)},{backdrop_opacity});padding:28px 56px;border-radius:16px;">
            <span style="font-size:{font_size+12}px;color:{font_color};font-weight:bold;">🎉<br>{winners_str}<br>🎉</span>
        </div>
    </div>
    """
    container.markdown(winner_html, unsafe_allow_html=True)
    st.balloons()
uploaded_drumroll = st.sidebar.file_uploader("Upload Drumroll Sound", type=["mp3", "wav"])
uploaded_crash = st.sidebar.file_uploader("Upload Crash Sound", type=["mp3", "wav"])
uploaded_applause = st.sidebar.file_uploader("Upload Applause Sound", type=["mp3", "wav"])
mute_audio = st.sidebar.checkbox("Mute Audio", value=False)
def inject_audio(audio_file, loop=False):
    ext = audio_file.name.split('.')[-1]
    b64 = base64.b64encode(audio_file.read()).decode()
    loop_attr = "loop" if loop else ""
    st.markdown(
        f"""<audio autoplay {loop_attr}>
            <source src="data:audio/{ext};base64,{b64}" type="audio/{ext}">
        </audio>""",
        unsafe_allow_html=True
    )
if uploaded_drumroll and not mute_audio:
    inject_audio(uploaded_drumroll, loop=True)
st.markdown("""<script>
var auds = document.getElementsByTagName('audio');
for (var i=0; i<auds.length; i++) {{ auds[i].pause(); auds[i].currentTime = 0; }}
</script>""", unsafe_allow_html=True)

if uploaded_crash and not mute_audio:
    inject_audio(uploaded_crash)
if uploaded_applause and not mute_audio:
    inject_audio(uploaded_applause)
