import datetime
import json
import logging
import os


def get_next_schedule_start_date(gym_name: str, days_stored: int = 6) -> datetime.datetime | None:
    last_run_date = load_last_run_details(gym_name)
    current_date = datetime.datetime.now().date()
    stored_schedules_till = last_run_date.date() + datetime.timedelta(days=days_stored)
    days_to_parse = current_date - stored_schedules_till
    if days_to_parse > datetime.timedelta(days=0):
        logging.info("Time to parse the schedule...")
        start_parsing_from = stored_schedules_till + datetime.timedelta(days=1)
        future_date = max(start_parsing_from, current_date)
        return future_date.strftime("%Y-%m-%d")
    logging.info("Skipping the parsing.")
    return None


def load_last_run_details(gym_name: str) -> datetime.datetime | None:
    if os.path.exists('run_details.json'):
        with open('run_details.json', 'r') as file:
            run_details = json.load(file)
            last_run_string = run_details.get(gym_name, '').split(" ")[0]
            return datetime.datetime.strptime(last_run_string, "%Y-%m-%d")
    return None
