import streamlit as st
import sqlite3
import os
import pandas as pd
from utils.speech_to_text import voice_to_text, extract_crm_details
from utils.email_to_crm import extract_email_details

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Zero-Click CRM", layout="wide")

# ---------- GALAXY BACKGROUND WITH STARS + METEOR ANIMATION ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&display=swap');

body {
    font-family: 'Poppins', sans-serif;
    color: #fff;
    overflow-x: hidden;
}

/* === Gradient Sky Background === */
[data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at top, #0b0f2e, #0f2027, #203a43, #2c5364);
    background-size: 400% 400%;
    animation: gradientFlow 20s ease infinite;
    position: relative;
    overflow: hidden;
}

@keyframes gradientFlow {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

/* === Twinkling Stars === */
[data-testid="stAppViewContainer"]::before {
    content: "";
    position: fixed;
    top: 0; left: 0;
    width: 200%; height: 200%;
    background: transparent url("https://www.transparenttextures.com/patterns/stardust.png") repeat;
    opacity: 0.3;
    animation: starsTwinkle 200s linear infinite;
    z-index: 0;
}

@keyframes starsTwinkle {
    from {background-position: 0 0;}
    to {background-position: 10000px 10000px;}
}

/* === Shooting Meteors === */
[data-testid="stAppViewContainer"]::after {
    content: "";
    position: fixed;
    top: -10%;
    left: -10%;
    width: 120%;
    height: 120%;
    background-image: radial-gradient(ellipse at top, rgba(255,255,255,0.7) 1px, transparent 1px);
    background-size: 3px 3px;
    animation: meteorRain 8s linear infinite;
    opacity: 0.2;
    z-index: 0;
}

@keyframes meteorRain {
    0% {transform: translate(0, 0) rotate(45deg);}
    100% {transform: translate(-100vw, 100vh) rotate(45deg);}
}

/* === Glassmorphic Cards === */
.stCard {
    background: rgba(255,255,255,0.07);
    backdrop-filter: blur(12px);
    border-radius: 20px;
    padding: 25px;
    margin-bottom: 30px;
    box-shadow: 0 0 25px rgba(0,255,255,0.2);
    transition: all 0.4s ease;
    position: relative;
    z-index: 1;
}
.stCard:hover {
    box-shadow: 0 0 40px rgba(0,255,255,0.5);
    transform: scale(1.02);
}

/* === Buttons === */
.stButton>button {
    background: linear-gradient(90deg, #00f7ff, #00b3b3);
    border: none;
    color: black;
    font-weight: 700;
    border-radius: 12px;
    padding: 0.6em 1.4em;
    transition: all 0.3s ease-in-out;
}
.stButton>button:hover {
    transform: scale(1.08);
    box-shadow: 0 0 25px #00ffff;
}

/* === Sidebar === */
div[data-testid="stSidebar"] {
    background: rgba(0,0,0,0.55);
    border-right: 2px solid rgba(0,255,255,0.4);
    box-shadow: 4px 0 15px rgba(0,255,255,0.2);
}

/* === Headers === */
h1, h2, h3 {
    text-align: center;
    color: #00f7ff;
    text-shadow: 0 0 15px #00e6e6;
}

/* === Footer === */
footer {
    position: fixed;
    bottom: 0;
    width: 100%;
    background: rgba(0, 0, 0, 0.35);
    color: #00e6e6;
    text-align: center;
    padding: 10px;
    font-size: 14px;
    border-top: 1px solid #00e6e6;
    backdrop-filter: blur(5px);
    z-index: 2;
}
</style>
""", unsafe_allow_html=True)

# ---------- DATABASE SETUP ----------
def init_db():
    conn = sqlite3.connect('crm.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS crm_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Name TEXT,
                    Company TEXT,
                    Follow_up_Date TEXT,
                    Notes TEXT
                );''')
    conn.commit()
    return conn

conn = init_db()

# ---------- HEADER ----------
st.markdown("<h1>🚀 Zero-Click AI-Powered CRM System</h1>", unsafe_allow_html=True)

# ---------- SIDEBAR ----------
st.sidebar.title("🧭 Navigation")
page = st.sidebar.radio("Go to", ["🎤 Voice to CRM", "📧 Email to CRM", "📊 Dashboard"])

# ---------- VOICE TO CRM ----------
if page == "🎤 Voice to CRM":
    st.markdown('<div class="stCard">', unsafe_allow_html=True)
    st.header("🎙 Voice to CRM Entry")

    st.write("Upload a recorded **voice note (MP3/WAV)** — the system will transcribe it using Whisper and extract CRM details using Gemini AI.")

    audio_file = st.file_uploader("🎧 Upload your voice note:", type=["mp3", "wav"])

    if audio_file:
        temp_audio_path = "uploaded_audio.wav"
        with open(temp_audio_path, "wb") as f:
            f.write(audio_file.read())

        with st.spinner("🧠 Transcribing your audio with Whisper..."):
            transcribed_text = voice_to_text(temp_audio_path)

        st.subheader("🗣 Transcribed Text:")
        st.info(transcribed_text)

        with st.spinner("🤖 Extracting CRM details using Gemini..."):
            crm_data = extract_crm_details(transcribed_text)

        if "error" in crm_data:
            st.error(crm_data["error"])
        else:
            st.subheader("🧩 Extracted CRM Data:")
            st.json(crm_data)

            if st.button("💾 Save to CRM Dashboard"):
                conn.execute(
                    "INSERT INTO crm_data (Name, Company, Follow_up_Date, Notes) VALUES (?, ?, ?, ?)",
                    (crm_data["Name"], crm_data["Company"], crm_data["Follow_up_Date"], crm_data["Notes"]),
                )
                conn.commit()
                st.success("✅ Voice data saved successfully to CRM!")
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- EMAIL TO CRM ----------
elif page == "📧 Email to CRM":
    st.markdown('<div class="stCard">', unsafe_allow_html=True)
    st.header("📨 Email to CRM Entry")

    email_content = st.text_area("✉️ Paste email or text content here:")

    if "email_data" not in st.session_state:
        st.session_state.email_data = None

    if st.button("🔍 Extract Details"):
        if not email_content.strip():
            st.warning("⚠️ Please paste some content before extracting.")
        else:
            with st.spinner("🧠 Extracting CRM data from text..."):
                crm_data = extract_email_details(email_content)
                st.session_state.email_data = crm_data

    if st.session_state.email_data:
        st.subheader("🧾 Extracted Data:")
        st.json(st.session_state.email_data)

        if "error" in st.session_state.email_data:
            st.error(st.session_state.email_data["error"])
        else:
            if st.button("💾 Save Email Data to CRM"):
                conn.execute(
                    "INSERT INTO crm_data (Name, Company, Follow_up_Date, Notes) VALUES (?, ?, ?, ?)",
                    (
                        st.session_state.email_data["Name"],
                        st.session_state.email_data["Company"],
                        st.session_state.email_data["Follow_up_Date"],
                        st.session_state.email_data["Notes"],
                    ),
                )
                conn.commit()
                st.success("✅ Email data saved successfully!")
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- DASHBOARD ----------
elif page == "📊 Dashboard":
    st.markdown('<div class="stCard">', unsafe_allow_html=True)
    st.header("📈 CRM Dashboard")

    cursor = conn.execute("SELECT id, Name, Company, Follow_up_Date, Notes FROM crm_data")
    rows = cursor.fetchall()

    if len(rows) == 0:
        st.info("📭 No CRM data available yet. Add entries via Voice or Email tabs.")
    else:
        df = pd.DataFrame(rows, columns=["ID", "Name", "Company", "Follow Up Date", "Notes"])
        st.dataframe(df, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- FOOTER ----------
st.markdown("""
<footer>
    © 2025 | Built with ❤️| <b>ZERO-CLICK CRM AI</b>
</footer>
""", unsafe_allow_html=True)
