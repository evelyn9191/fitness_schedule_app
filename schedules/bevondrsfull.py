import requests
from bs4 import BeautifulSoup

from helpers import get_next_schedule_start_date

SCHEDULE_URL = "https://cz.boofit.net/bevondrsfull/rozvrh-a-rezervace/aktualni-rozvrh/1071/"
GYM = "Be Vondrsfull"

def get_schedule():
    parse_from = get_next_schedule_start_date(GYM)
    if not parse_from:
        return []

    response = requests.get(SCHEDULE_URL + parse_from)
    parsed_schedules = parse_schedule(response.text)
    return parsed_schedules

def parse_schedule(html):
    soup = BeautifulSoup(html, "html.parser")

    # Extract lessons for each day
    days = []
    day_containers = soup.find_all("div", class_="col7-sm-7")
    for day_container in day_containers:
        day = {}

        # Find the date for the day
        date_heading = day_container.find("dt")
        if date_heading:
            day["date"] = date_heading.find("strong").text.strip()

        # Find lessons for the day
        lessons = []
        lesson_elements = day_container.find_all("p", class_="lesson")
        for lesson_element in lesson_elements:
            lesson = {}

            # Parse time, name, trainers, and spots
            time_and_name = lesson_element.find("span").get_text(" ", strip=True).split()
            lesson["time"] = f"{time_and_name[0]}-{time_and_name[2]}"
            lesson["name"] = lesson_element.find("em").text.strip()
            lesson["trainer"] = [trainer.get_text(strip=True) for trainer in lesson_element.find_all("b")]

            # Extract available spots
            spots_element = lesson_element.find("span", class_="places")
            lesson["spots"] = spots_element.text.strip().replace(" ", "") if spots_element else "N/A"

            lessons.append(lesson)

        day["lessons"] = lessons
        day["gym"] = GYM
        days.append(day)
    print(days)
    return days
