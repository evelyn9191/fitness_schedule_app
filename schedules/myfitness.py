import datetime
import json
import os
from requests_html import HTMLSession

from helpers import get_next_schedule_start_date
from dotenv import load_dotenv

load_dotenv()

LOGIN_URL = "https://www.supersaas.cz/schedule/login/jumping-broumovska/rezervace"
SCHEDULE_URL = "https://www.supersaas.cz/schedule/jumping-broumovska/rezervace"
GYM = "MyFitness"
IGNORED_LESSONS = ["CARDIO STEP", "JUMPING", "CARDIO STEP"]
USERNAME = os.getenv("MYFITNESS_USERNAME")
PASSWORD = os.getenv("MYFITNESS_PASSWORD")

def get_schedule():
    parse_from = get_next_schedule_start_date(GYM)
    if not parse_from:
        return []

    session = HTMLSession()
    session.get(LOGIN_URL)
    login_data = {
        "name": USERNAME,
        "password": PASSWORD,
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
    print(all_sessions)

    days = []
    lessons_by_dates = {}
    for session in all_sessions:
        start, end, _, max_spots, booked_spots, _, _, name, trainer, _, _, _ = session
        if name in IGNORED_LESSONS:
            continue

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
        days.append({"date": date, "gym": GYM, "lessons": lessons})

    return days
