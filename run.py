import datetime
import json
import logging

from gcal_updater import GoogleCalendarClient
from helpers import DATE_FORMAT_US, DATE_FORMAT_CZ
from schedules import goodfellas, bevondrsfull, imfit, yogaholick, siddha_yoga, moony_yoga, myfitness


def run():
    all_schedules = get_all_schedules()
    if not all_schedules:
        logging.info("No schedules to update.")
        return

    GoogleCalendarClient().sync_lessons_to_calendar(all_schedules)

    save_run_details(all_schedules)

def save_run_details(all_schedules: list) -> None:
    gym_last_lesson_pair = get_last_lesson_date(all_schedules)
    last_run = datetime.datetime.now().strftime("%Y-%m-%d")
    with open('run_details.json', 'r') as file:
        previous_run_details = json.load(file)

    for gym, last_lesson in gym_last_lesson_pair.items():
        previous_run_details[gym]["start"] = last_run
        if last_lesson:
            previous_run_details[gym]["end"] = last_lesson
        else:
            previous_run_details[gym]["end"] = last_run

    with open('run_details.json', 'w') as file:
        json.dump(previous_run_details, file, indent=4)

    print(f"Run details saved:\n", previous_run_details)

def get_last_lesson_date(all_schedules: list) -> dict:
    gym_last_lesson_pair = {}
    for lesson in all_schedules:
        gym = ""
        last_lesson_date = ""
        lesson_date = datetime.datetime.strptime(lesson['date'], DATE_FORMAT_CZ)
        if not gym:
            gym = lesson['gym']
            last_lesson_date = lesson_date
        elif gym != lesson['gym']:
            gym_last_lesson_pair = {gym: last_lesson_date}
        else:
            if lesson_date > last_lesson_date:
                last_lesson_date = lesson_date
        gym_last_lesson_pair[gym] = datetime.datetime.strftime(last_lesson_date, DATE_FORMAT_US)
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
