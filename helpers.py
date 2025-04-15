import datetime
import json
import os


def get_next_schedule_start_date(gym_name: str) -> datetime.datetime | None:
    last_run_date, last_lesson_date = load_last_run_details(gym_name)
    current_date = datetime.datetime.now().date()
    days_to_parse = current_date - last_lesson_date
    if days_to_parse > datetime.timedelta(days=0):
        print("Time to parse the schedule...")
        start_parsing_from = last_lesson_date + datetime.timedelta(days=1)
        future_date = max(start_parsing_from, current_date)
        return future_date.strftime("%Y-%m-%d")
    print(f"Skipping the parsing for {gym_name}")
    return None


def load_last_run_details(gym_name: str) -> tuple[datetime.datetime | None, datetime.date | None]:
    if os.path.exists('run_details.json'):
        with open('run_details.json', 'r') as file:
            run_details = json.load(file)
            last_run_string = run_details[gym_name]["start"].split(" ")[0]
            last_lesson_string = run_details[gym_name]["end"].split(" ")[0]
            return datetime.datetime.strptime(last_run_string, "%Y-%m-%d"), datetime.datetime.strptime(last_lesson_string, "%Y-%m-%d").date()
    return None, None
