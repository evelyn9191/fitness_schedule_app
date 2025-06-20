import requests
from bs4 import BeautifulSoup

from helpers import get_next_schedule_start_date, get_date_string

SCHEDULE_URL = "https://karlin.formfactory.cz/calendar/"
GYM = "Form Factory Karlin"
IGNORED_LESSONS = ["CYCLING", "BARRE workout", "Cvičení pro těhotné"]


def get_schedule():
    print(f"Getting schedule from {GYM}...")
    parse_from = get_next_schedule_start_date(GYM)
    if not parse_from:
        return []

    dates_to_parse_from = [get_date_string(parse_from)]
    parsed_schedules = []
    for _ in dates_to_parse_from:
        response = requests.get(SCHEDULE_URL, verify=False)
        parsed_schedules.extend(parse_schedule(response.text))
    return parsed_schedules

def parse_schedule(html):
    soup = BeautifulSoup(html, "html.parser")
    days = []

    # Find all rows with lessons
    week_chooser = soup.find("div", class_="week_chooser")
    week_dates = None
    if week_chooser:
        week_dates = week_chooser.find("span").text.strip()

    # Find all day columns
    day_columns = soup.select("table.calendar_table > thead > tr > td")
    day_content_columns = soup.select("table.calendar_table > tr > td")

    for i, (day_header, day_content) in enumerate(zip(day_columns, day_content_columns)):
        day_info = {}

        # Get the date from the day header
        date_elem = day_header.find("a", class_="scheduler-go-to-day")
        if date_elem and date_elem.has_attr("meta:date"):
            day_info["date"] = date_elem["meta:date"]
        else:
            continue

        day_info["gym"] = GYM

        # Extract lessons from the day column
        lessons = []
        event_divs = day_content.find_all("div", class_="event")

        for event_div in event_divs:
            lesson_info = {}

            # Extract lesson name
            name_elem = event_div.find("p", class_="event_name")
            if name_elem:
                lesson_info["name"] = name_elem.text.strip()
                if lesson_info["name"] in IGNORED_LESSONS:
                    continue

            # Extract time
            time_elem = event_div.find("span", class_="eventlength")
            if time_elem:
                lesson_info["time"] = time_elem.text.strip()

            # Extract instructor (might be empty)
            instructor_elem = event_div.find("p", class_="instructor")
            if instructor_elem:
                lesson_info["trainer"] = instructor_elem.text.strip()

            # Extract room
            room_elem = event_div.find("p", class_="room")
            if room_elem:
                lesson_info["room"] = room_elem.text.strip()

            # Extract availability (might not have specific numbers)
            availability_elem = event_div.find("span", class_="availability")
            if availability_elem:
                lesson_info["spots"] = availability_elem.text.strip()
            else:
                lesson_info["spots"] = ""

            lessons.append(lesson_info)

        if lessons:
            day_info["lessons"] = lessons
            days.append(day_info)
    return days
