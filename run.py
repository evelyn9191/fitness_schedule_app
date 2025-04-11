import datetime
import json
import os
import webbrowser

import pandas as pd

from gcal_updater import get_calendar_service, sync_lessons_to_calendar
from schedules import goodfellas, bevondrsfull, imfit, yogaholick, siddha_yoga, moony_yoga, myfitness


def run():
    last_run_date = load_last_run_details()
    all_schedules = get_all_schedules(last_run_date)
    # service = get_calendar_service()
    # sync_lessons_to_calendar(service, all_schedules)
    # create_timetable_for_browser(all_schedules, date_spec)
    # save_run_details()

def load_last_run_details():
    if os.path.exists('run_details.json'):
        with open('run_details.json', 'r') as file:
            run_details = json.load(file)
            last_run_string = run_details.get('last_run', '').split(" ")[0]
            return datetime.datetime.strptime(last_run_string, "%Y-%m-%d")
    return None

def create_timetable_for_browser(all_schedules: list[dict], date_spec: str | None = None) -> None:
    formatted_data = []

    for gym_schedule in all_schedules:
        if date_spec and gym_schedule['date'] != date_spec:
            continue

        date = gym_schedule['date']
        gym = gym_schedule["gym"]
        for lesson in gym_schedule.get('lessons', []):
            formatted_data.append({
                'Date': date,
                'Class Name': lesson['name'],
                'Time': lesson['time'],
                'Spots': lesson.get("spots", ""),
                'Trainer': lesson['trainer'],
                'Gym': gym,
            })

    df = pd.DataFrame(formatted_data)
    print(df.to_string(index=False))
    html_output = df.to_html(index=False, escape=False)
    html_file_path = 'timetable.html'
    with open(html_file_path, 'w') as f:
        f.write(html_output)
    webbrowser.open('file://' + os.path.realpath(html_file_path))

def save_run_details():
    last_run_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    run_details = {'last_run': last_run_time}
    with open('run_details.json', 'w') as file:
        json.dump(run_details, file, indent=4)
    print(f"Run details saved: {last_run_time}")

def get_all_schedules(last_run_date: datetime.datetime):
    schedule_functions = [
        goodfellas.get_schedule,
        # bevondrsfull.get_schedule,
        # imfit.get_schedule,
        # myfitness.get_schedule,
        # yogaholick.get_schedule,
        # siddha_yoga.get_schedule,
        # moony_yoga.get_schedule
    ]
    all_schedules = [schedule(last_run_date) for schedule in schedule_functions]
    return sum(all_schedules, [])

if __name__ == "__main__":
    run()
