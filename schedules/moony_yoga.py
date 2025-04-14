import requests

from helpers import get_next_schedule_start_date
from schedules.isportsystem import ISportSystemSchedulesHandler

GYM = "Moony Yoga"


def get_schedule():
    parse_from = get_next_schedule_start_date(GYM)
    if not parse_from:
        return []

    handler = ISportSystemSchedulesHandler(GYM, "moonyyoga", parse_from)
    response = requests.get(handler.schedule_url, params=handler.get_params(), headers=handler.generate_client_headers())
    parsed_schedules = handler.parse_schedule(response.text)
    return parsed_schedules
