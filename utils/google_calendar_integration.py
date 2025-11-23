from __future__ import print_function
import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dateutil import parser

# Google Calendar SCOPES
SCOPES = ['https://www.googleapis.com/auth/calendar']


def parse_followup_date(date_str):
    """
    Convert natural language date strings into standard RFC3339 format for Google Calendar.
    """
    try:
        parsed = parser.parse(date_str, fuzzy=True)
        return parsed.strftime("%Y-%m-%dT10:00:00+05:30")
    except:
        tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
        return tomorrow.strftime("%Y-%m-%dT10:00:00+05:30")


def get_calendar_service():
    """
    Creates a Google Calendar API service using a Service Account.
    Reads credentials from Streamlit Secrets.
    """
    import streamlit as st

    # Load service account key from Streamlit Secrets
    service_account_info = st.secrets["gcp_service_account"]

    creds = service_account.Credentials.from_service_account_info(
        service_account_info,
        scopes=SCOPES
    )

    # Build calendar service
    service = build("calendar", "v3", credentials=creds)
    return service


def add_event_to_calendar(summary, description, date):
    """
    Create a Google Calendar event using Service Account credentials.
    """
    try:
        service = get_calendar_service()

        start_time = parse_followup_date(date)
        end_dt = parser.parse(start_time) + datetime.timedelta(hours=1)
        end_time = end_dt.strftime("%Y-%m-%dT11:00:00+05:30")

        event = {
            "summary": summary,
            "description": description if description else "No additional notes",
            "start": {"dateTime": start_time, "timeZone": "Asia/Kolkata"},
            "end": {"dateTime": end_time, "timeZone": "Asia/Kolkata"},
        }

        created_event = service.events().insert(calendarId="primary", body=event).execute()
        return f"✅ Event created: {created_event.get('htmlLink')}"

    except Exception as e:
        return f"❌ Error adding event: {str(e)}"
