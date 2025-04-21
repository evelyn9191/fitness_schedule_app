import logging
import os
import datetime

import pytz
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from dotenv import load_dotenv

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/calendar.events']

class GoogleCalendarClient:
    def __init__(self):
        self.calendar_id = os.getenv("GOOGLE_CALENDAR_ID")
        self.service = self.get_calendar_service()

    @staticmethod
    def get_calendar_service():
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        return build('calendar', 'v3', credentials=creds)

    def delete_event(self, event: dict) -> None:
        print(f"Deleting event {event['summary']} of gym {event['location']}, id {event['id']}...")
        self.service.events().delete(calendarId=self.calendar_id, eventId=event['id']).execute()

    def list_events(self, query=None, start_from=None) -> list:
        event_items = []
        page_token = None
        while True:
            events = self.service.events().list(calendarId=os.getenv("GOOGLE_CALENDAR_ID"),
                                          timeMin=start_from,
                                          singleEvents=True,
                                          orderBy='startTime',
                                          q=query).execute()
            event_items.extend(events["items"])
            page_token = events.get('nextPageToken')
            if not page_token:
                break
        return event_items

    def sync_lessons_to_calendar(self, all_schedules: list) -> None:
        for day in all_schedules:
            logging.info("Creating calendar events for gym %s on %s", day.get("gym"), day["date"])
            print(day)
            for lesson in day['lessons']:
                print(lesson)
                start_iso, end_iso = self._to_rfc_datetime(day['date'], lesson['time'])
                event_body = {
                    'summary': lesson['name'],
                    'location': lesson.get('gym', day['gym']),
                    'description': f"Trainer: {lesson['trainer']}\nSpots: {lesson['spots']}",
                    'start': {'dateTime': start_iso, 'timeZone': 'Europe/Prague'},
                    'end': {'dateTime': end_iso, 'timeZone': 'Europe/Prague'},
                }
                self.service.events().insert(
                    calendarId=self.calendar_id,
                    body=event_body
                ).execute()
                print(f"Created: {lesson['name']} on {day['date']}")

    @staticmethod
    def _to_rfc_datetime(date_str, time_str):
        start_str, end_str = time_str.replace("–", '-').split('-')
        start = datetime.datetime.strptime(f"{date_str} {start_str}", "%d.%m.%Y %H:%M")
        end = datetime.datetime.strptime(f"{date_str} {end_str}", "%d.%m.%Y %H:%M")
        tz = pytz.timezone("Europe/Prague")
        return tz.localize(start).isoformat(), tz.localize(end).isoformat()
