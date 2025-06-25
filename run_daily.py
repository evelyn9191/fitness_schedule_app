import datetime
import logging

from gcal_updater import GoogleCalendarClient
from helpers import DATE_FORMAT_CZ
from schedules import moodyoga, yogakarlin, form_factory

DAY_TO_TRACK = datetime.date.today() + datetime.timedelta(days=1)
FROM_TIME = datetime.time(8, 0)
TO_TIME = datetime.time(17, 30)

def run():
    all_schedules = get_all_schedules()
    if not all_schedules:
        logging.info("No schedules to update.")
        return

    day_schedules = filter_schedules_by_day(all_schedules)

    GoogleCalendarClient().sync_lessons_to_calendar(day_schedules)

    print("Schedules saved.")

def filter_schedules_by_day(all_schedules: list) -> list[dict]:
    filtered_schedules = []
    for day_schedule in all_schedules:
        lesson_date = datetime.datetime.strptime(day_schedule['date'], DATE_FORMAT_CZ)
        if lesson_date.date() == DAY_TO_TRACK:
            day_lessons = []
            for day_lesson in day_schedule['lessons']:
                start_time = day_lesson["time"].split("-")[0].split("–")[0]
                hour, minutes = start_time.split(":")
                lesson_time = datetime.time(int(hour), int(minutes))
                if FROM_TIME <= lesson_time <= TO_TIME:
                    day_lessons.append(day_lesson)
            day_schedule['lessons'] = day_lessons
            filtered_schedules.append(day_schedule)
    return filtered_schedules

def get_all_schedules():
    schedule_functions = [
        moodyoga.get_schedule,
        yogakarlin.get_schedule,
        form_factory.get_schedule,
    ]
    all_schedules = [schedule() for schedule in schedule_functions]
    return sum(all_schedules, [])

if __name__ == "__main__":
    run()
