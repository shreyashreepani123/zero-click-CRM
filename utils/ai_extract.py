import requests, json, os

# 👉 Paste your MakerSuite Gemini API key here
API_KEY = "AIzaSyAJx42pT-4CVtzWkZogwrfkCGlVVxAuELw"

def extract_crm_fields(text):
    """
    Sends user text (from email or voice note) to Google's free Gemini API via MakerSuite.
    Returns structured CRM data as JSON.
    """
    # Gemini REST API endpoint
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"

    # Construct request payload
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": (
                            f"Extract CRM fields from the following text:\n\n"
                            f"{text}\n\n"
                            "Return output strictly in JSON format with keys:\n"
                            "Name, Company, Follow_up_Date, Notes."
                        )
                    }
                ]
            }
        ]
    }

    # Make API request
    try:
        r = requests.post(f"{url}?key={API_KEY}", headers=headers, json=data)
        r.raise_for_status()
        raw_text = r.json()["candidates"][0]["content"]["parts"][0]["text"]

        # Try to parse as JSON (Gemini sometimes returns plain text)
        try:
            crm_data = json.loads(raw_text)
        except:
            crm_data = {
                "Name": "Unknown",
                "Company": "Unknown",
                "Follow_up_Date": "Not found",
                "Notes": text
            }

        return json.dumps(crm_data, indent=2)

    except Exception as e:
        print("Gemini API error:", e)
        # Fallback basic response
        return json.dumps({
            "Name": "Unknown",
            "Company": "Unknown",
            "Follow_up_Date": "Not found",
            "Notes": text
        }, indent=2)
