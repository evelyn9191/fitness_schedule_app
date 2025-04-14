import logging
import os
from datetime import datetime

import pytz
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from dotenv import load_dotenv

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/calendar.events']
CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID")

def get_calendar_service():
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    return build('calendar', 'v3', credentials=creds)

def to_rfc_datetime(date_str, time_str):
    start_str, end_str = time_str.replace("–", '-').split('-')
    start = datetime.strptime(f"{date_str} {start_str}", "%d.%m.%Y %H:%M")
    end = datetime.strptime(f"{date_str} {end_str}", "%d.%m.%Y %H:%M")
    tz = pytz.timezone("Europe/Prague")
    return tz.localize(start).isoformat(), tz.localize(end).isoformat()

def sync_lessons_to_calendar(service, data):
    for day in data:
        logging.info("Creating calendar events for gym %s on %s", day.get("gym"), day["date"])
        print(day)
        for lesson in day['lessons']:
            print(lesson)
            start_iso, end_iso = to_rfc_datetime(day['date'], lesson['time'])
            event_body = {
                'summary': lesson['name'],
                'location': lesson.get('gym', day['gym']),
                'description': f"Trainer: {lesson['trainer']}\nSpots: {lesson['spots']}",
                'start': {'dateTime': start_iso, 'timeZone': 'Europe/Prague'},
                'end': {'dateTime': end_iso, 'timeZone': 'Europe/Prague'},
            }
            service.events().insert(
                calendarId=CALENDAR_ID,
                body=event_body
            ).execute()
            print(f"Created: {lesson['name']} on {day['date']}")
