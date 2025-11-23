from __future__ import print_function
import datetime
import os.path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from dateutil import parser  # <-- new import for flexible date parsing

SCOPES = ['https://www.googleapis.com/auth/calendar']

def parse_followup_date(date_str):
    """
    Try to convert natural language or informal date strings into ISO format.
    Fallback to today's date if parsing fails.
    """
    try:
        parsed = parser.parse(date_str, fuzzy=True)
        # Force the time to 10:00 AM
        return parsed.strftime("%Y-%m-%dT10:00:00+05:30")
    except Exception:
        today = datetime.datetime.now() + datetime.timedelta(days=1)
        return today.strftime("%Y-%m-%dT10:00:00+05:30")

def add_event_to_calendar(summary, description, date):
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)

        # Ensure proper date format
        start_time = parse_followup_date(date)
        end_time = (parser.parse(start_time) + datetime.timedelta(hours=1)).strftime("%Y-%m-%dT11:00:00+05:30")

        event = {
            'summary': summary,
            'description': description if description else "No additional notes",
            'start': {'dateTime': start_time, 'timeZone': 'Asia/Kolkata'},
            'end': {'dateTime': end_time, 'timeZone': 'Asia/Kolkata'},
        }

        event = service.events().insert(calendarId='primary', body=event).execute()
        return f"✅ Event created successfully: {event.get('htmlLink')}"
    except Exception as e:
        return f"❌ Error: {str(e)}"
