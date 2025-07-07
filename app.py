import streamlit as st
import pandas as pd
import random
import time
import base64
import os

st.set_page_config("🎰 S5.COM Lucky Draw", layout="wide")
st.title("🎰 S5.COM Lucky Draw")

# ── Sidebar controls ──
st.sidebar.header("🎨 Upload Assets")
logo_up = st.sidebar.file_uploader("Logo", type=["png","jpg","jpeg"], key="logo_up")
bg_up   = st.sidebar.file_uploader("Background (img/gif/mp4)", type=["png","jpg","jpeg","gif","mp4","webm"], key="bg_up")
csv_up  = st.sidebar.file_uploader("Names CSV", type=["csv"], key="csv_up")
drum_up = st.sidebar.file_uploader("Drumroll", type=["mp3","wav"], key="drum_up")
crash_up= st.sidebar.file_uploader("Crash FX", type=["mp3","wav"], key="crash_up")
ap_up   = st.sidebar.file_uploader("Applause", type=["mp3","wav"], key="applause_up")

st.sidebar.header("🎯 Draw Controls")
winner_count    = st.sidebar.number_input("Number of Winners", 1, 10, 3, key="winner_count")
draw_duration   = st.sidebar.number_input("Duration (sec)", 1.0, 60.0, 10.0, step=0.1, format="%.1f", key="draw_duration")
animation       = st.sidebar.selectbox("Animation Style", ["Scrolling","Rolodex"], key="animation")
rolodex_interval= st.sidebar.slider("Rolodex Interval (s)", 0.05, 1.0, 0.15, 0.01, key="rolodex_interval")

st.sidebar.header("🔤 Appearance")
font_size       = st.sidebar.slider("Font Size (px)", 20, 100, 48, key="font_size")
font_color      = st.sidebar.color_picker("Font Color", "#FFFFFF", key="font_color")
backdrop_color  = st.sidebar.color_picker("Backdrop Color", "#000000", key="backdrop_color")
backdrop_op     = st.sidebar.slider("Backdrop Opacity", 0.0, 1.0, 0.5, key="backdrop_opacity")
backdrop_pad    = st.sidebar.slider("Backdrop Padding", 0, 50, 10, key="backdrop_padding")
show_left       = st.sidebar.checkbox("Show Left Timer", value=True, key="show_left")
show_right      = st.sidebar.checkbox("Show Right Timer", value=True, key="show_right")
confetti        = st.sidebar.checkbox("Show Confetti", value=True, key="confetti")
mute            = st.sidebar.checkbox("Mute All Audio", value=False, key="mute")

start_btn       = st.sidebar.button("🎲 Start Draw", key="start")
export_btn      = st.sidebar.button("📥 Export Winners", key="export")

WINNERS_FILE = "winners.csv"

def encode_upload(upload):
    if upload:
        data = upload.getvalue()
        ext = upload.name.split(".")[-1].lower()
        return base64.b64encode(data).decode(), ext
    return None, None

# Store base64s on every run (to refresh buffers)
logo_b64, logo_ext = encode_upload(logo_up)
bg_b64, bg_ext = encode_upload(bg_up)
drum_b64, drum_ext = encode_upload(drum_up)
crash_b64, crash_ext = encode_upload(crash_up)
appl_b64, appl_ext = encode_upload(ap_up)

draw_ph  = st.empty()
audio_ph = st.empty()

if start_btn:
    if not csv_up:
        st.error("Please upload a Names CSV.")
        st.stop()
    df = pd.read_csv(csv_up)
    name_col = next((c for c in df.columns if c.lower() == "name"), None)
    id_col   = next((c for c in df.columns if c.lower() in ("id","uid")), None)
    acc_col  = next((c for c in df.columns if "account" in c.lower()), None)
    if name_col is None:
        st.error("CSV must contain a 'name' column.")
        st.stop()
    names = df[name_col].dropna().tolist()
    if not names:
        st.error("No names found in CSV.")
        st.stop()

    # --- HTML blocks
    if bg_b64:
        if bg_ext in ("mp4","webm"):
            bg_html = f"""<video autoplay loop muted style="position:absolute;top:0;left:0;width:100vw;height:100vh;object-fit:cover;opacity:{backdrop_op};z-index:0;"><source src="data:video/{bg_ext};base64,{bg_b64}"></video>"""
        else:
            bg_html = f"""<div style="position:absolute;top:0;left:0;width:100vw;height:100vh;background:url('data:image/{bg_ext};base64,{bg_b64}') center/cover;opacity:{backdrop_op};z-index:0;"></div>"""
    else:
        bg_html = ""
    logo_html = f"""<img src="data:image/{logo_ext};base64,{logo_b64}" style="position:absolute;top:10px;left:10px;width:120px;z-index:2;">""" if logo_b64 else ""

    # --- Audio start
    if not mute and drum_b64:
        audio_ph.markdown(f"""<audio autoplay loop><source src="data:audio/{drum_ext};base64,{drum_b64}"></audio>""", unsafe_allow_html=True)

    # --- Draw effect
    start_t = time.time()
    elapsed = 0
    frame = 0
    while elapsed < draw_duration:
        elapsed = time.time() - start_t
        rem = max(0, draw_duration - elapsed)
        if animation == "Scrolling":
            show_name = random.choice(names)
        elif animation == "Rolodex":
            idx = (frame // max(1,int(rolodex_interval/0.1))) % len(names)
            show_name = names[idx]
        else:
            show_name = random.choice(names)

        left_t = f"<div style='position:absolute;left:10px;top:50%;transform:translateY(-50%);font-size:24px;color:{font_color};'>{int(rem)}</div>" if show_left else ""
        right_t= f"<div style='position:absolute;right:10px;top:50%;transform:translateY(-50%);font-size:24px;color:{font_color};'>{int(rem)}</div>" if show_right else ""
        draw_ph.markdown(f"""
        <div style="position:relative;width:100vw;height:100vh;display:flex;align-items:center;justify-content:center;">
            {bg_html}
            {logo_html}
            {left_t}{right_t}
            <div style="position:relative;z-index:3;padding:{backdrop_pad}px;background:{backdrop_color};color:{font_color};font-size:{font_size}px;border-radius:10px;">
                {show_name}
            </div>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(0.1)
        frame += 1

    # --- End: clear drum, play crash & applause
    audio_ph.empty()
    if not mute and crash_b64:
        audio_ph.markdown(f"""<audio autoplay><source src="data:audio/{crash_ext};base64,{crash_b64}"></audio>""", unsafe_allow_html=True)
    if not mute and appl_b64:
        audio_ph.markdown(f"""<audio autoplay><source src="data:audio/{appl_ext};base64,{appl_b64}"></audio>""", unsafe_allow_html=True)

    # --- Winners and confetti
    winners = df.sample(n=winner_count)
    if confetti: st.balloons()
    final_html = "<br>".join(
        " | ".join(str(row[col]) for col in (id_col, name_col, acc_col) if col)
        for _, row in winners.iterrows()
    )
    draw_ph.markdo_
