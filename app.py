import streamlit as st
import pandas as pd
import random
import time
from io import StringIO
import base64

st.set_page_config(page_title="🎰 S5.com Lucky Draw", layout="centered")
st.markdown("""
    <h1 style='text-align: center;'>🎰 S5.COM Lucky Draw</h1>
    <hr>
""", unsafe_allow_html=True)

# Upload logo
logo_file = st.file_uploader("Upload Logo (optional)", type=["png", "jpg", "jpeg"])
if logo_file:
    st.image(logo_file, use_column_width=True)

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
scroll_speed = st.sidebar.slider("Scroll Speed (sec per name)", min_value=0.01, max_value=0.5, value=0.1, step=0.01)

winner_log = []

# Countdown effect
def countdown_scroll(df, speed=0.1, rounds=15):
    scroll_placeholder = st.empty()
    for _ in range(rounds):
        random_row = df.sample(1).iloc[0]
        scroll_text = f"🔄 {random_row['Name']} ({random_row['Account Name']})"
        scroll_placeholder.markdown(f"<h3 style='text-align: center;'>{scroll_text}</h3>", unsafe_allow_html=True)
        time.sleep(speed)

# Winner announcement
def show_winner(winner):
    winner_text = f"🎉 **ID:** {winner['ID']}<br>👤 **Name:** {winner['Name']}<br>💼 **Account:** {winner['Account Name']}"
    st.markdown(f"<div style='text-align:center;'>{winner_text}</div>", unsafe_allow_html=True)
    winner_log.append(winner_text)

if df is not None:
    if st.button("🎲 Start Draw"):
        with st.spinner("Spinning the wheel..."):
            winners_df = df.sample(n=winner_count).reset_index(drop=True)
            for i in range(winner_count):
                st.subheader(f"Drawing Winner #{i + 1}...")
                countdown_scroll(df, speed=scroll_speed, rounds=15)
                winner = winners_df.iloc[i]
                show_winner(winner)
                time.sleep(0.5)

    if winner_log:
        st.markdown("---")
        st.subheader("📜 Winner Log")
        for entry in winner_log:
            st.markdown(entry, unsafe_allow_html=True)

        # Export button
        export_csv = df.sample(n=winner_count).to_csv(index=False)
        b64 = base64.b64encode(export_csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="winners.csv">📥 Download Winners CSV</a>'
        st.markdown(href, unsafe_allow_html=True)
else:
    st.info("Please upload a valid CSV file to begin.")
