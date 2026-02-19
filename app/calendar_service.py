import os
import json
import datetime
from dateutil import parser
from dateutil import tz
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar"]

# Load credentials from environment variable
service_account_info = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT"])
credentials = service_account.Credentials.from_service_account_info(
    service_account_info, scopes=SCOPES
)

service = build("calendar", "v3", credentials=credentials)

IST = tz.gettz("Asia/Kolkata")

def create_event(name, date, time, title=None):
    print(f"[DEBUG] RAW INPUT → date={date!r}  time={time!r}")

    # ignoretz=True strips any tz info from the string (e.g. if AI passes "10:00 AM IST")
    # dateutil handles both 12hr ("10:00 AM", "3:30 PM") and 24hr ("15:30:00") automatically
    naive_dt = parser.parse(f"{date} {time}", ignoretz=True)
    start_datetime = naive_dt.replace(tzinfo=IST)  # attach IST explicitly
    end_datetime   = start_datetime + datetime.timedelta(hours=1)

    print(f"[DEBUG] start_datetime = {start_datetime.isoformat()}")  # must show +05:30

    event = {
        "summary":     title or "Scheduled Meeting",
        "description": f"Meeting with {name}",
        "start": {
            "dateTime": start_datetime.isoformat(),
            "timeZone": "Asia/Kolkata",
        },
        "end": {
            "dateTime": end_datetime.isoformat(),
            "timeZone": "Asia/Kolkata",
        },
    }

    result = service.events().insert(
        calendarId="1mp22cs021@gmail.com",
        body=event
    ).execute()

    print(f"[DEBUG] Google returned start = {result.get('start')}")
    return result