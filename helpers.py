import datetime
import json
import os

DATE_FORMAT = "%Y-%m-%d"

def get_next_schedule_start_date(gym_name: str) -> datetime.date | None:
    last_run_date, last_lesson_date = load_last_run_details(gym_name)
    current_date = datetime.datetime.now().date()
    start_parsing_from = last_lesson_date + datetime.timedelta(days=1)
    future_date = max(start_parsing_from, current_date)
    return future_date

def load_last_run_details(gym_name: str) -> tuple[datetime.datetime | None, datetime.date | None]:
    if os.path.exists('run_details.json'):
        with open('run_details.json', 'r') as file:
            run_details = json.load(file)
            last_run_string = run_details[gym_name]["start"].split(" ")[0]
            last_lesson_string = run_details[gym_name]["end"].split(" ")[0]
            return datetime.datetime.strptime(last_run_string, DATE_FORMAT), datetime.datetime.strptime(last_lesson_string, DATE_FORMAT).date()
    return None, None

def get_date_string(date: datetime.date) -> str:
    return date.strftime(DATE_FORMAT)
