import datetime

import requests

from helpers import get_next_schedule_start_date
from schedules.isportsystem import ISportSystemSchedulesHandler, parse_new_isportsystem_html

GYM = "Yoga Karlin"


def get_schedule(*args):
    print(f"Getting schedule from {GYM}...")
    parse_from = get_next_schedule_start_date(GYM)
    if not parse_from:
        return []

    dates_to_parse_from = [parse_from, parse_from + datetime.timedelta(days=7)]
    parsed_schedules = []
    
    # Create session and get cookies from main page first
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    })
    
    # Visit main page to get cookies
    session.get("https://yk.isportsystem.cz/")
    
    for date in dates_to_parse_from:
        handler = ISportSystemSchedulesHandler(GYM, "yk", date)
        post_data = {
            "id_sport": 5,
            "day": date.day,
            "month": date.month,
            "year": date.year,
            "event": "init",
            "timetableWidth": 1058
        }
        headers = handler.generate_client_headers()
        headers["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"
        response = session.post(handler.schedule_url, data=post_data, headers=headers)
        parsed = parse_new_isportsystem_html(response.text, GYM)
        parsed_schedules.extend(parsed)
    return parsed_schedules
