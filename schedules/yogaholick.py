import datetime

import pytz
import requests

from helpers import get_next_schedule_start_date, get_date_string

SCHEDULE_API_URL = "https://yogaholick.reenio.cz/cs/api/Term/List"
GYM = "Yogaholick"

def get_schedule():
    print(f"Getting schedule from {GYM}...")
    parse_from = get_next_schedule_start_date(GYM)
    if not parse_from:
        return []

    dates_to_parse_from = [get_date_string(parse_from), get_date_string(parse_from + datetime.timedelta(days=7))]
    parsed_schedules = []
    for date_to_parse_from in dates_to_parse_from:
        view_mode = "7-days"
        response = requests.post(SCHEDULE_API_URL, files=[
            ("date", (None, date_to_parse_from)),
            ("viewMode", (None, view_mode)),
            ("page", (None, "0")),
            ("filter.resource[0].id", (None, "25")),
            ("filter.resource[0].type", (None, "1")),
            ("includeColors", (None, "false")),
        ])
        parsed_schedules.extend(parse_schedule(response.json()))
    return parsed_schedules

def parse_schedule(schedules: dict):
    try:
        events = schedules["data"]["events"]
    except KeyError:
        return

    days = []
    lessons_by_dates = {}
    for event in events:
        current_date = _get_lesson_date(event)
        if current_date not in lessons_by_dates:
            lessons_by_dates[current_date] = []

        if not accepts_multisport:
            continue

        lesson = {}

        start_time = _convert_to_prague_time(event["start"])
        end_time = _convert_to_prague_time(event["end"])
        lesson["time"] = f"{start_time}-{end_time}"
        lesson["name"] = event["eventResources"][0]["name"]
        lesson["trainer"] = event["eventResources"][0]["employee"]["name"]
        try:
            lesson["spots"] = f"{event["reservations"][0]["capacity"]}/{event["maxCapacity"]}"
        except IndexError:
            lesson["spots"] = ""
        lessons_by_dates[current_date].append(lesson)

    for date, lessons in lessons_by_dates.items():
        days.append({"date": date, "gym": GYM, "lessons": lessons})

    return days

def _convert_to_prague_time(utc_str: str) -> str:
    utc_dt = datetime.datetime.strptime(utc_str, '%Y-%m-%dT%H:%M:%SZ')
    utc_dt = utc_dt.replace(tzinfo=pytz.utc)
    prague_tz = pytz.timezone('Europe/Prague')
    prague_dt = utc_dt.astimezone(prague_tz)
    time_str = prague_dt.strftime('%H:%M')
    return time_str

def _get_lesson_date(event: dict) -> str:
    lesson_date = event["start"].split("T")[0]
    year, month, day = lesson_date.split("-")
    return f"{day}.{month}.{year}"

def accepts_multisport(event: dict) -> bool:
    for priceVariant in event["priceVariants"]:
        if priceVariant["price"] == 0:
            return True
    return False
