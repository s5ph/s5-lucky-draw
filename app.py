import streamlit as st
import pandas as pd
import random
import time
from io import StringIO
import base64

st.set_page_config(page_title="🎰 S5.com Lucky Draw", layout="wide")

st.markdown("""
    <style>
        .draw-area {
            position: relative;
            text-align: center;
            color: white;
        }
        .logo-overlay {
            position: absolute;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 10;
        }
        .background {
            position: absolute;
            width: 100%;
            height: 100%;
            top: 0;
            left: 0;
            object-fit: cover;
            z-index: 0;
            opacity: 0.3;
        }
        .winner-text {
            font-size: 2rem;
            font-weight: bold;
            z-index: 5;
        }
        .timer {
            font-size: 1.5rem;
            color: yellow;
            margin-top: 10px;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>🎰 S5.COM Lucky Draw</h1><hr>", unsafe_allow_html=True)

# Upload logo and background
logo_file = st.file_uploader("Upload Logo (optional)", type=["png", "jpg", "jpeg"])
background_file = st.file_uploader("Upload Background Image (optional)", type=["png", "jpg", "jpeg"])

# Upload CSV
df = None
csv_file = st.file_uploader("Upload CSV File", type=["csv"])
if csv_file:
    df = pd.read_csv(csv_file)
    if not {"ID", "Name", "Account Name"}.issubset(df.columns):
        st.error("CSV must contain columns: ID, Name, Account Name")
        df = None

# Controls
st.sidebar.header("Draw Settings")
winner_count = st.sidebar.slider("Number of Winners", min_value=1, max_value=10, value=3)
total_draw_time = st.sidebar.number_input("Total Draw Time (in seconds)", min_value=1.0, max_value=300.0, value=15.0, step=1.0)

winner_log = []

# Countdown effect with visual timer and animation
def countdown_scroll(df, total_time):
    scroll_placeholder = st.empty()
    rounds = int(total_time / 0.1)
    logo_b64 = base64.b64encode(logo_file.read()).decode() if logo_file else ""
    bg_b64 = base64.b64encode(background_file.read()).decode() if background_file else ""
    for i in range(rounds):
        random_row = df.sample(1).iloc[0]
        scroll_text = f"🔄 {random_row['Name']} ({random_row['Account Name']})"
        remaining = total_time - (i * 0.1)
        html = f"""
        <div class='draw-area'>
            {f'<img src="data:image/png;base64,{logo_b64}" class="logo-overlay">' if logo_b64 else ''}
            {f'<img src="data:image/png;base64,{bg_b64}" class="background">' if bg_b64 else ''}
            <div class='winner-text'>{scroll_text}</div>
            <div class='timer'>⏳ Time Remaining: {remaining:.1f} sec</div>
        </div>
        """
        scroll_placeholder.markdown(html, unsafe_allow_html=True)
        time.sleep(0.1)

# Winner announcement
def show_winner(winner):
    winner_text = f"🎉 <b>ID:</b> {winner['ID']}<br><b>👤 Name:</b> {winner['Name']}<br><b>💼 Account:</b> {winner['Account Name']}"
    st.markdown(f"<div style='text-align:center; font-size: 1.8rem;'>{winner_text}</div>", unsafe_allow_html=True)
    winner_log.append(winner_text)

if df is not None:
    if st.button("🎲 Start Draw"):
        with st.spinner("Spinning the wheel..."):
            winners_df = df.sample(n=winner_count).reset_index(drop=True)
            for i in range(winner_count):
                st.subheader(f"Drawing Winner #{i + 1}...")
                countdown_scroll(df, total_time=total_draw_time)
                winner = winners_df.iloc[i]
                show_winner(winner)
                time.sleep(0.5)

    if winner_log:
        st.markdown("---")
        st.subheader("📜 Winner Log")
        for entry in winner_log:
            st.markdown(entry, unsafe_allow_html=True)

        export_csv = df.sample(n=winner_count).to_csv(index=False)
        b64 = base64.b64encode(export_csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="winners.csv">📥 Download Winners CSV</a>'
        st.markdown(href, unsafe_allow_html=True)
else:
    st.info("Please upload a valid CSV file to begin.")
