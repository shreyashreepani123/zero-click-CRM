import whisper
import os
import google.generativeai as genai
import json

def voice_to_text(audio_path):
    """
    Converts a recorded or uploaded voice note into text using OpenAI Whisper.
    """
    try:
        # Load Whisper model (base = balanced speed & accuracy)
        model = whisper.load_model("base")
        result = model.transcribe(audio_path, fp16=False)
        text = result.get("text", "").strip()

        if not text:
            return "No speech detected. Please try again."
        return text

    except Exception as e:
        print(f"[Error: voice_to_text] {e}")
        return f"Error transcribing audio: {str(e)}"


def extract_crm_details(transcribed_text):
    """
    Uses Gemini AI to extract structured CRM data from transcribed voice notes.
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

        Output STRICT JSON ONLY, in this format:
        {{
            "Name": "Person Name",
            "Company": "Company Name",
            "Follow_up_Date": "Date or Time",
            "Notes": "Brief summary of the discussion"
        }}

        Conversation Text:
        {transcribed_text}
        """

        # Generate structured response from Gemini
        model = genai.GenerativeModel("gemini-2.0-flash")  # ✅ Stable model
        response = model.generate_content(prompt)
        text = response.text.strip()

        # Handle possible Markdown formatting from Gemini
        if text.startswith("```json"):
            text = text[7:-3].strip()
        elif text.startswith("```"):
            text = text[3:-3].strip()

        # Parse to JSON safely
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            # Fallback if model response isn’t pure JSON
            data = {
                "Name": None,
                "Company": None,
                "Follow_up_Date": None,
                "Notes": transcribed_text
            }

        # Ensure all required keys exist
        for key in ["Name", "Company", "Follow_up_Date", "Notes"]:
            data.setdefault(key, None)

        return data

    except Exception as e:
        print(f"[Error: extract_crm_details] {e}")
        return {"error": str(e)}
