# Whisper removed because Streamlit Cloud cannot run heavy ML models.
# import whisper
import os
import google.generativeai as genai
import json

def voice_to_text(audio_path):
    """
    Whisper STT is disabled for Streamlit deployment.
    Streamlit Cloud cannot run Whisper due to large model size & no GPU.

    This placeholder returns a safe message.
    """
    return "Voice transcription is disabled in the deployed version."


def extract_crm_details(transcribed_text):
    """
    Uses Gemini AI to extract structured CRM data from text.
    Returns JSON with fields: Name, Company, Follow_up_Date, Notes.
    """
    try:
        if not transcribed_text or transcribed_text.strip() == "":
            return {
                "Name": None,
                "Company": None,
                "Follow_up_Date": None,
                "Notes": "No valid text to process."
            }

        # Configure Gemini API
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

        # Prompt for CRM detail extraction
        prompt = f"""
        You are a professional CRM assistant.
        Analyze the following conversation or meeting note and extract:
        - Name (person mentioned)
        - Company (organization or client name)
        - Follow_up_Date (specific or relative time)
        - Notes (main discussion summary)

        If a field is missing, return it as null.

        Output STRICT JSON ONLY in this format:
        {{
            "Name": "Person Name",
            "Company": "Company Name",
            "Follow_up_Date": "Date or Time",
            "Notes": "Brief summary"
        }}

        Conversation Text:
        {transcribed_text}
        """

        # Call Gemini model
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        text = response.text.strip()

        # Clean JSON if wrapped in markdown
        if text.startswith("```json"):
            text = text[7:-3].strip()
        elif text.startswith("```"):
            text = text[3:-3].strip()

        # Parse JSON
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            data = {
                "Name": None,
                "Company": None,
                "Follow_up_Date": None,
                "Notes": transcribed_text
            }

        # Ensure required keys
        for key in ["Name", "Company", "Follow_up_Date", "Notes"]:
            data.setdefault(key, None)

        return data

    except Exception as e:
        print(f"[Error: extract_crm_details] {e}")
        return {"error": str(e)}
