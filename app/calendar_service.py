import datetime
import json
from dateutil import parser
from dateutil import tz
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

service_account_info = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT"])

credentials = service_account.Credentials.from_service_account_info(
    service_account_info,
    scopes=["https://www.googleapis.com/auth/calendar"]
)

service = build("calendar", "v3", credentials=credentials)

IST = tz.gettz("Asia/Kolkata")

# ─── DATE NORMALIZER ──────────────────────────────────────────────────────────
# AI sometimes passes relative dates like "next Monday", "tomorrow", "February 25th"
# We resolve them relative to today in IST.
RELATIVE_MAP = {
    "today":     0,
    "tomorrow":  1,
    "day after tomorrow": 2,
}

WEEKDAY_MAP = {
    "monday": 0, "tuesday": 1, "wednesday": 2,
    "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6,
}

def resolve_date(date_str: str) -> str:
    """
    Converts relative or natural language dates to YYYY-MM-DD.
    Falls back to dateutil.parser for absolute dates.
    """
    today = datetime.datetime.now(IST).date()
    normalized = date_str.strip().lower()

    # Check simple relative words
    if normalized in RELATIVE_MAP:
        resolved = today + datetime.timedelta(days=RELATIVE_MAP[normalized])
        print(f"[resolve_date] '{date_str}' → {resolved} (relative)")
        return resolved.strftime("%Y-%m-%d")

    # Check "next <weekday>" or just "<weekday>"
    for prefix in ("next ", ""):
        for day_name, day_num in WEEKDAY_MAP.items():
            if normalized == prefix + day_name:
                days_ahead = (day_num - today.weekday()) % 7
                if days_ahead == 0 and prefix == "next ":
                    days_ahead = 7
                elif days_ahead == 0:
                    days_ahead = 7  # assume future if same day
                resolved = today + datetime.timedelta(days=days_ahead)
                print(f"[resolve_date] '{date_str}' → {resolved} (weekday)")
                return resolved.strftime("%Y-%m-%d")

    # Fallback: parse absolute date with dateutil
    try:
        parsed = parser.parse(date_str, ignoretz=True, default=datetime.datetime(today.year, today.month, today.day))
        print(f"[resolve_date] '{date_str}' → {parsed.date()} (parsed)")
        return parsed.strftime("%Y-%m-%d")
    except Exception as e:
        print(f"[resolve_date] ERROR parsing '{date_str}': {e}")
        raise ValueError(f"Could not parse date: '{date_str}'")


def create_event(name: str, date: str, time: str, title: str = None) -> dict:
    print(f"[create_event] RAW INPUT → name={name!r}, date={date!r}, time={time!r}, title={title!r}")

    # Resolve relative dates to YYYY-MM-DD
    resolved_date = resolve_date(date)

    # Parse time — dateutil handles "10:00 AM", "3:30 PM", "15:30", "15:30:00"
    # Strip any timezone labels from the time string (e.g. "10 AM IST" → "10 AM")
    clean_time = time.replace("IST", "").replace("UTC", "").strip()

    try:
        naive_dt = parser.parse(f"{resolved_date} {clean_time}", ignoretz=True)
    except Exception as e:
        print(f"[create_event] ERROR parsing datetime: {e}")
        raise ValueError(f"Could not parse date/time: '{resolved_date} {clean_time}'")

    start_datetime = naive_dt.replace(tzinfo=IST)
    end_datetime   = start_datetime + datetime.timedelta(hours=1)

    print(f"[create_event] start_datetime = {start_datetime.isoformat()}")
    print(f"[create_event] end_datetime   = {end_datetime.isoformat()}")

    event_body = {
        "summary":     title or f"Meeting with {name}",
        "description": f"Scheduled meeting with {name} via Vikara AI",
        "start": {
            "dateTime": start_datetime.isoformat(),
            "timeZone": "Asia/Kolkata",
        },
        "end": {
            "dateTime": end_datetime.isoformat(),
            "timeZone": "Asia/Kolkata",
        },
        "attendees": [],
        "reminders": {
            "useDefault": False,
            "overrides": [
                {"method": "popup", "minutes": 15},
            ],
        },
    }

    print(f"[create_event] Inserting event to Google Calendar...")
    result = service.events().insert(
        calendarId="1mp22cs021@gmail.com",
        body=event_body
    ).execute()

    print(f"[create_event] SUCCESS — id={result.get('id')}, link={result.get('htmlLink')}")
    return result