import os
import google.generativeai as genai
import json

def extract_email_details(email_text):
    """
    Uses Gemini AI to extract CRM data from plain email content.
    Returns structured JSON with: Name, Company, Follow_up_Date, Notes.
    """
    try:
        if not email_text or email_text.strip() == "":
            return {
                "Name": None,
                "Company": None,
                "Follow_up_Date": None,
                "Notes": "No content provided."
            }

        # Configure Gemini API
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

        # Create a smart structured prompt
        prompt = f"""
        You are an intelligent CRM Data Extractor.
        Analyze the email content below and extract:
        - Name (sender or mentioned contact)
        - Company (organization name)
        - Follow_up_Date (if any date, day, or time is mentioned)
        - Notes (short summary of the email purpose)

        Return response in VALID JSON format ONLY as below:
        {{
            "Name": "Person Name",
            "Company": "Company Name",
            "Follow_up_Date": "Date/Day/Time",
            "Notes": "Short summary of the email"
        }}

        Email Content:
        {email_text}
        """

        # Use Gemini (fast & reliable version)
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        text = response.text.strip()

        # Remove markdown formatting if added by Gemini
        if text.startswith("```json"):
            text = text[7:-3].strip()
        elif text.startswith("```"):
            text = text[3:-3].strip()

        # Try parsing JSON safely
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            data = {
                "Name": None,
                "Company": None,
                "Follow_up_Date": None,
                "Notes": email_text
            }

        # Ensure all keys exist
        for key in ["Name", "Company", "Follow_up_Date", "Notes"]:
            data.setdefault(key, None)

        return data

    except Exception as e:
        print(f"[Error: extract_email_details] {e}")
        return {"error": str(e)}
