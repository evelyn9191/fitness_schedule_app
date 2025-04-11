import datetime
import json
import os
from requests_html import HTMLSession

from helpers import get_next_schedule_start_date
from dotenv import load_dotenv

load_dotenv()

LOGIN_URL = "https://www.supersaas.cz/schedule/login/jumping-broumovska/rezervace"
SCHEDULE_URL = "https://www.supersaas.cz/schedule/jumping-broumovska/rezervace"

def get_schedule(last_run_date: datetime.datetime):
    if not get_next_schedule_start_date(last_run_date):
        return []

    session = HTMLSession()
    session.get(LOGIN_URL)
    login_data = {
        "name": os.getenv("MYFITNESS_USERNAME"),
        "password": os.getenv("MYFITNESS_PASSWORD"),
        "remember": "K",
        "button": ""
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "Referer": "https://www.supersaas.cz/schedule/login/jumping-broumovska/rezervace",
        "Origin": "https://www.supersaas.cz",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    response = session.post(
        LOGIN_URL,
        data=login_data,
        headers=headers
    )
    parsed_schedules = parse_schedule(response.text)
    return parsed_schedules

def parse_schedule(response_text: str):
    body = response_text.split("var app=")[1].split("var busy_color")[0]
    all_sessions = json.loads(body)

    days = []
    lessons_by_dates = {}
    for session in all_sessions:
        start, end, _, max_spots, booked_spots, _, _, name, trainer, _, _, _ = session
        start_datetime = datetime.datetime.fromtimestamp(start)
        current_date = start_datetime.date().strftime("%d.%m.%Y")
        if current_date not in lessons_by_dates:
            lessons_by_dates[current_date] = []

        spots = f"{booked_spots}/{max_spots}"
        end_datetime = datetime.datetime.fromtimestamp(end)
        time = f"{start_datetime.strftime('%-H:%M')}-{end_datetime.strftime('%-H:%M')}"
        lessons_by_dates[current_date].append({"time": time,
                                               "name": name,
                                               "trainer": trainer,
                                               "spots": spots
                                               })

    for date, lessons in lessons_by_dates.items():
        days.append({"date": date, "gym": "MyFitness", "lessons": lessons})

    return days
