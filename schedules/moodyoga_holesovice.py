import datetime

import requests

from helpers import get_next_schedule_start_date
from schedules.isportsystem import ISportSystemSchedulesHandler

GYM = "Mood Yoga Holesovice"
ID_SPORT = 15


def get_schedule(*args):
    print(f"Getting schedule from {GYM}...")
    parse_from = get_next_schedule_start_date(GYM)
    if not parse_from:
        return []

    dates_to_parse_from = [parse_from, parse_from + datetime.timedelta(days=7)]
    parsed_schedules = []
    for date in dates_to_parse_from:
        handler = ISportSystemSchedulesHandler(GYM, "mood", date)
        response = requests.get(handler.schedule_url, params=handler.get_params(ID_SPORT), headers=handler.generate_client_headers())
        parsed_schedules.extend(handler.parse_schedule(response.text))
    return parsed_schedules