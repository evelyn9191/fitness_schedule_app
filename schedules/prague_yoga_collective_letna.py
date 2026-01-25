import json
import datetime
import requests
import pytz

from helpers import get_next_schedule_start_date, get_date_string

SCHEDULE_URL = "https://readonly-api.momence.com/host-plugins/host/21663/host-schedule/sessions?locationIds[]=26600&sessionTypes[]=course-class&sessionTypes[]=fitness&sessionTypes[]=retreat&sessionTypes[]=special-event&sessionTypes[]=special-event-new&pageSize=20&page=0"
GYM = "PYC Letna"
IGNORED_LESSONS = []


def get_schedule(day_to_track: datetime.date | None = None):
    print(f"Getting schedule from {GYM}...")
    parse_from = day_to_track or get_next_schedule_start_date(GYM)
    if not parse_from:
        return []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Origin': 'https://pragueyogacollective.com',
        'Referer': 'https://pragueyogacollective.com/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
    }

    dates_to_parse_from = [get_date_string(parse_from)]
    parsed_schedules = []
    for _ in dates_to_parse_from:
        url_with_date = f"{SCHEDULE_URL}&fromDate={parse_from}T00:00:00.000Z&toDate={parse_from}T22:00:00.000Z"
        response = requests.get(url_with_date, headers=headers)
        parsed_schedules.extend(parse_schedule(response.text))
            
    return parsed_schedules

def parse_schedule(html: str):
    data = json.loads(html)
    days = []
    lessons_by_dates = {}

    for session in data["payload"]:
        # Skip cancelled sessions
        if session.get("isCancelled"):
            continue

        # Parse the start time (UTC) and convert to Prague timezone
        start_time_utc = datetime.datetime.fromisoformat(session["startsAt"].replace('Z', '+00:00'))
        end_time_utc = datetime.datetime.fromisoformat(session["endsAt"].replace('Z', '+00:00'))
        
        # Convert to Prague timezone
        prague_tz = pytz.timezone('Europe/Prague')
        start_time = start_time_utc.astimezone(prague_tz)
        end_time = end_time_utc.astimezone(prague_tz)
        
        # Format date and time
        date_str = start_time.strftime("%d.%m.%Y")
        time_str = f"{start_time.strftime('%-H:%M')}-{end_time.strftime('%-H:%M')}"

        # Prepare lesson info
        lesson = {
            "name": session["sessionName"],
            "time": time_str,
            "trainer": session["teacher"],
            "spots": f"{session.get('ticketsSold', 0)}/{session.get('capacity', 0)}",
            "location": session.get("location", "")
        }

        # Group lessons by date
        if date_str not in lessons_by_dates:
            lessons_by_dates[date_str] = []
        lessons_by_dates[date_str].append(lesson)

    # Convert to the required format
    for date, lessons in lessons_by_dates.items():
        days.append({
            "date": date,
            "gym": GYM,
            "lessons": lessons
        })

    return days
