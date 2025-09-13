import datetime

import requests

from helpers import get_next_schedule_start_date, get_date_string, DATE_FORMAT_CZ
from schedules.form_factory import FormFactorySchedulesHandler

GYM = "Form Factory Karlin"


def get_schedule(*args):
    print(f"Getting schedule from {GYM}...")
    parse_from = get_next_schedule_start_date(GYM)
    if not parse_from:
        return []

    dates_to_parse_from = ["", get_date_string(parse_from + datetime.timedelta(days=7), DATE_FORMAT_CZ)]
    parsed_schedules = []
    for date in dates_to_parse_from:
        handler = FormFactorySchedulesHandler(GYM, "karlin", date)
        response = requests.get(handler.schedule_url, params=handler.get_params(), verify=False)
        parsed_schedules.extend(handler.parse_schedule(response.text))
    return parsed_schedules
