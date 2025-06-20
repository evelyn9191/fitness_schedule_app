import datetime
import json
import os

from requests_html import HTMLSession
from dotenv import load_dotenv

from helpers import get_next_schedule_start_date, DATE_FORMAT_CZ

load_dotenv()

LOGIN_URL = "https://www.supersaas.cz/schedule/login/jumping-broumovska/rezervace"
SCHEDULE_URL = "https://www.supersaas.cz/schedule/jumping-broumovska/rezervace"
GYM = "MyFitness"
IGNORED_LESSONS = ["CARDIO STEP", "JUMPING", "CARDIO STEP"]
USERNAME = os.getenv("MYFITNESS_USERNAME")
PASSWORD = os.getenv("MYFITNESS_PASSWORD")

def get_schedule():
    print(f"Getting schedule from {GYM}...")
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
    session.post(
        LOGIN_URL,
        data=login_data,
        headers=headers
    )
    start_date, end_date = generate_schedule_dates()
    print("Querying sessions for date range", start_date, end_date)
    response = session.get(
        f"https://www.supersaas.cz/ajax/capacity/27740?token=42786&afrom={start_date}&ato={end_date}&ad=r&efrom={start_date}&eto={end_date}&ed=r")
    parsed_schedules = parse_schedule(response.text)
    return parsed_schedules

def parse_schedule(response_text: str):
    all_sessions = json.loads(response_text)["app"]

    parse_from = get_next_schedule_start_date(GYM)

    days = []
    lessons_by_dates = {}
    for session in all_sessions:
        start, end, _, max_spots, booked_spots, _, _, name, trainer, _, _, _ = session
        if name in IGNORED_LESSONS:
            continue

        start_datetime = datetime.datetime.fromtimestamp(start, tz=datetime.timezone.utc)
        if start_datetime.date() < parse_from:
            continue

        current_date = start_datetime.date().strftime(DATE_FORMAT_CZ)

        if current_date not in lessons_by_dates:
            lessons_by_dates[current_date] = []

        spots = f"{booked_spots}/{max_spots}"
        end_datetime = datetime.datetime.fromtimestamp(end, tz=datetime.timezone.utc)
        time = f"{start_datetime.strftime('%-H:%M')}-{end_datetime.strftime('%-H:%M')}"
        lessons_by_dates[current_date].append({"time": time,
                                               "name": name,
                                               "trainer": trainer,
                                               "spots": spots
                                               })

    for date, lessons in lessons_by_dates.items():
        days.append({"date": date, "gym": GYM, "lessons": lessons})

    return days


def generate_schedule_dates() -> tuple[str, str]:
    today = datetime.date.today()
    first_day_of_month = today.replace(day=1)
    last_day_of_next_month = (first_day_of_month.replace(month=(today.month % 12) + 2, day=1) - datetime.timedelta(days=1))
    start_date = first_day_of_month - datetime.timedelta(days=first_day_of_month.weekday())
    end_date = last_day_of_next_month + datetime.timedelta(days=(6 - last_day_of_next_month.weekday()))
    return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')
