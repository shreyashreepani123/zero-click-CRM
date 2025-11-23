import streamlit as st
import sqlite3
import os
import pandas as pd
from utils.speech_to_text import voice_to_text, extract_crm_details
from utils.email_to_crm import extract_email_details
from utils.google_calendar_integration import generate_calendar_link
from gtts import gTTS
import playsound
import matplotlib.pyplot as plt
from textblob import TextBlob
import google.generativeai as genai

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Zero-Click CRM AI", layout="wide")

# ---------- AI VOICE FEEDBACK FUNCTION ----------
def speak_confirmation(message="Contact added to CRM successfully!"):
    try:
        tts = gTTS(text=message, lang='en')
        tts.save("voice_feedback.mp3")
        playsound.playsound("voice_feedback.mp3")
        os.remove("voice_feedback.mp3")
    except Exception as e:
        st.warning(f"🔇 Voice feedback failed: {e}")

# ---------- CSS ----------
st.markdown("""
<style>
/* Your CSS remains unchanged */
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
page = st.sidebar.radio("Go to", ["🎤 Voice to CRM", "📧 Email to CRM", "📊 Dashboard", "🤖 Chat with CRM"])

# =====================================================================
# 🎤 VOICE TO CRM PAGE
# =====================================================================
if page == "🎤 Voice to CRM":
    st.title("🎙 Voice to CRM Entry")
    st.write("Upload your recorded voice note (MP3/WAV). AI will transcribe, extract CRM details, and save automatically.")

    audio_file = st.file_uploader("🎧 Upload Voice Note", type=["mp3", "wav"])

    if audio_file:
        temp_audio_path = "uploaded_audio.wav"
        with open(temp_audio_path, "wb") as f:
            f.write(audio_file.read())

        with st.spinner("🧠 Transcribing your audio..."):
            transcribed_text = voice_to_text(temp_audio_path)

        st.subheader("🗣 Transcribed Text:")
        st.write(transcribed_text)

        with st.spinner("🤖 Extracting CRM details..."):
            crm_data = extract_crm_details(transcribed_text)

        if "error" in crm_data:
            st.error(crm_data["error"])
        else:
            st.subheader("🧩 Extracted CRM Data:")
            st.json(crm_data)

            # SAVE BUTTON —— FIXED INDENTATION
            if st.button("💾 Save to CRM + Calendar"):
                conn.execute(
                    "INSERT INTO crm_data (Name, Company, Follow_up_Date, Notes) VALUES (?, ?, ?, ?)",
                    (crm_data["Name"], crm_data["Company"], crm_data["Follow_up_Date"], crm_data["Notes"]),
                )
                conn.commit()
                st.success("✅ Voice data saved successfully!")

                calendar_link = generate_calendar_link(
                    summary=f"Follow-up with {crm_data['Name']}",
                    description=crm_data["Notes"],
                    date=crm_data["Follow_up_Date"]
                )
                st.markdown(f"[📅 Click here to add event to Google Calendar]({calendar_link})")

                speak_confirmation(f"{crm_data['Name']} from {crm_data['Company']} added to CRM successfully!")

# =====================================================================
# 📧 EMAIL TO CRM PAGE
# =====================================================================
elif page == "📧 Email to CRM":
    st.title("📨 Email to CRM Entry")
    email_content = st.text_area("✉ Paste email or text content here:")

    if "email_data" not in st.session_state:
        st.session_state.email_data = None

    if st.button("🔍 Extract Details"):
        if not email_content.strip():
            st.warning("⚠ Please paste some content before extracting.")
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
            if st.button("💾 Save Email Data to CRM + Calendar"):
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

                calendar_link = generate_calendar_link(
                    summary=f"Follow-up with {st.session_state.email_data['Name']}",
                    description=st.session_state.email_data["Notes"],
                    date=st.session_state.email_data["Follow_up_Date"]
                )
                st.markdown(f"[📅 Click here to add event to Google Calendar]({calendar_link})")

                speak_confirmation(f"{st.session_state.email_data['Name']} added to CRM successfully!")

# =====================================================================
# 📊 DASHBOARD PAGE
# =====================================================================
elif page == "📊 Dashboard":
    st.title("📈 CRM Dashboard")

    cursor = conn.execute("SELECT id, Name, Company, Follow_up_Date, Notes FROM crm_data")
    rows = cursor.fetchall()

    if len(rows) == 0:
        st.info("📭 No CRM data available yet. Add entries via Voice or Email tabs.")
    else:
        df = pd.DataFrame(rows, columns=["ID", "Name", "Company", "Follow Up Date", "Notes"])

        st.subheader("🧠 Smart Sentiment Analysis")
        df["Sentiment"] = df["Notes"].apply(lambda x: TextBlob(str(x)).sentiment.polarity)
        df["Sentiment_Label"] = df["Sentiment"].apply(
            lambda x: "😊 Positive" if x > 0 else ("😐 Neutral" if x == 0 else "☹ Negative")
        )

        st.subheader("📋 Complete CRM Data (with Sentiments)")
        st.dataframe(df[["Name", "Company", "Follow Up Date", "Notes", "Sentiment_Label"]],
                     use_container_width=True, height=350)

        st.subheader("📊 Analytics Overview")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Contacts", len(df))
        with col2:
            st.metric("Positive Clients", len(df[df["Sentiment_Label"] == "😊 Positive"]))
        with col3:
            st.metric("Companies Tracked", df["Company"].nunique())

        st.markdown("### 📈 Leads by Company")
        company_counts = df["Company"].value_counts()

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(company_counts.index, company_counts.values)
        ax.set_facecolor("#111111")
        fig.patch.set_alpha(0)
        st.pyplot(fig)

        st.subheader("🧩 AI Summary Generator")
        if st.button("🧠 Generate AI Summary"):
            with st.spinner("Generating summary..."):
                try:
                    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
                    prompt = f"Summarize this CRM dataset briefly:\n{df.to_string(index=False)}"
                    model = genai.GenerativeModel("gemini-2.0-flash")
                    response = model.generate_content(prompt)
                    st.info(response.text.strip())
                except Exception as e:
                    st.error(f"Error generating summary: {e}")

# =====================================================================
# 🤖 CHAT WITH CRM PAGE
# =====================================================================
elif page == "🤖 Chat with CRM":
    st.title("🤖 AI Chat Assistant for CRM")
    cursor = conn.execute("SELECT Name, Company, Follow_up_Date, Notes FROM crm_data")
    rows = cursor.fetchall()

    if len(rows) == 0:
        st.info("No CRM data found.")
    else:
        df = pd.DataFrame(rows, columns=["Name", "Company", "Follow_up_Date", "Notes"])
        user_query = st.text_area("💬 Ask your CRM:")

        if st.button("Ask AI"):
            with st.spinner("🤖 Thinking..."):
                try:
                    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
                    prompt = f"""
                    Use the CRM data below to answer the user's question:
                    {df.to_string(index=False)}

                    Question: {user_query}
                    """
                    model = genai.GenerativeModel("gemini-2.0-flash")
                    response = model.generate_content(prompt)
                    st.success(response.text.strip())
                    speak_confirmation(response.text.strip())
                except Exception as e:
                    st.error(f"Error: {str(e)}")

# ---------- FOOTER ----------
st.markdown("""
<footer style="text-align:center; color:#00e6e6; margin-top:40px;">
    © 2025 | Built with ❤ | <b>ZERO-CLICK CRM AI</b>
</footer>
""", unsafe_allow_html=True)

