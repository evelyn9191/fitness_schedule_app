import datetime
import json
import logging

from gcal_updater import get_calendar_service, sync_lessons_to_calendar
from helpers import DATE_FORMAT
from schedules import goodfellas, bevondrsfull, imfit, yogaholick, siddha_yoga, moony_yoga, myfitness


def run():
    all_schedules = get_all_schedules()
    if not all_schedules:
        logging.info("No schedules to update.")
        return

    service = get_calendar_service()
    sync_lessons_to_calendar(service, all_schedules)
    save_run_details(all_schedules)

def save_run_details(all_schedules: list) -> None:
    gym_last_lesson_pair = get_last_lesson_date(all_schedules)
    last_run = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open('run_details.json', 'r+w') as file:
        previous_run_details = json.load(file)
        for gym, last_lesson in gym_last_lesson_pair.items():
            previous_run_details[gym]["start"] = last_run
            if last_lesson:
                previous_run_details[gym]["end"] = last_lesson
            else:
                previous_run_details[gym]["end"] = last_run
        json.dump(previous_run_details, file, indent=4)
    print(f"Run details saved:\n", previous_run_details)

def get_last_lesson_date(all_schedules: list) -> dict:
    gym_last_lesson_pair = {}
    for lesson in all_schedules:
        gym = ""
        last_lesson_date = ""
        if not gym:
            gym = lesson['gym']
            last_lesson_date = lesson['date']
        elif gym != lesson['gym']:
            gym_last_lesson_pair = {gym: last_lesson_date}
        else:
            if datetime.datetime.strptime(lesson['date'], DATE_FORMAT) > datetime.datetime.strptime(last_lesson_date, DATE_FORMAT):
                last_lesson_date = lesson['date']
        gym_last_lesson_pair[gym] = last_lesson_date
    return gym_last_lesson_pair

def get_all_schedules():
    schedule_functions = [
        goodfellas.get_schedule,
        bevondrsfull.get_schedule,
        imfit.get_schedule,
        myfitness.get_schedule,
        yogaholick.get_schedule,
        siddha_yoga.get_schedule,
        moony_yoga.get_schedule
    ]
    all_schedules = [schedule() for schedule in schedule_functions]
    return sum(all_schedules, [])

if __name__ == "__main__":
    run()
