import datetime
import json
import logging

from gcal_updater import get_calendar_service, sync_lessons_to_calendar
from schedules import goodfellas, bevondrsfull, imfit, yogaholick, siddha_yoga, moony_yoga, myfitness


def run():
    all_schedules = get_all_schedules()
    if not all_schedules:
        logging.info("No schedules to update.")
        return

    service = get_calendar_service()
    sync_lessons_to_calendar(service, all_schedules)
    gym_schedules_synced = set(schedule['gym'] for schedule in all_schedules)
    save_run_details(gym_schedules_synced)

def save_run_details(gyms: set) -> None:
    last_run_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    this_run_details = {gym: last_run_time for gym in gyms}
    with open('run_details.json', 'r+w') as file:
        previous_run_details = json.load(file)
        run_details = {**previous_run_details, **this_run_details}
        json.dump(run_details, file, indent=4)
    print(f"Run details saved: {last_run_time}")


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
