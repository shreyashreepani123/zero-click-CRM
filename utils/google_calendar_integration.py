from dateutil import parser
import urllib.parse

def generate_calendar_link(summary, description, date):
    """
    Creates a Google Calendar event link that requires no authentication.
    """
    try:
        # Parse date into datetime
        dt = parser.parse(date)

        # Start time
        start = dt.strftime("%Y%m%dT%H%M%S")

        # End time = +1 hour
        end_dt = dt.replace(hour=dt.hour + 1)
        end = end_dt.strftime("%Y%m%dT%H%M%S")

        # Encode text for URL
        summary_encoded = urllib.parse.quote(summary)
        description_encoded = urllib.parse.quote(description or "")

        # Build link
        link = (
            "https://calendar.google.com/calendar/render?action=TEMPLATE"
            f"&text={summary_encoded}"
            f"&dates={start}/{end}"
            f"&details={description_encoded}"
        )

        return link

    except Exception as e:
        return f"Error generating calendar link: {str(e)}"
