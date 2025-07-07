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
        st.error("CSV must contain a
