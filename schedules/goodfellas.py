import datetime

import requests
from bs4 import BeautifulSoup

from helpers import get_next_schedule_start_date, get_date_string

SCHEDULE_URL = "https://goodfellasgym.inrs.cz/rs/kalendar_vypis/kalendar_vypis"
GYM = "GoodFellas"
IGNORED_LESSONS = ["OPEN", "GF Maminky s dětmi", "GF Vzpírání", "Funkční Fit. 2",
                   "GF FF 2 - Ranní", "B-Cross Run Prep", "Běžecký trénink (technika & Intervaly)"]

def get_schedule():
    print(f"Getting schedule from {GYM}...")
    parse_from = get_next_schedule_start_date(GYM)
    if not parse_from:
        return []

    dates_to_parse_from = [get_date_string(parse_from), get_date_string(parse_from + datetime.timedelta(days=7))]
    parsed_schedules = []
    for date in dates_to_parse_from:
        schedule_url = f"{SCHEDULE_URL}/{date}/1"
        response = requests.post(schedule_url)
        parsed_schedules.extend(parse_schedule(response.text))
    return parsed_schedules

def parse_schedule(html):
    soup = BeautifulSoup(html, "html.parser")
    days = []

    # Find all rows with lessons
    rows = soup.find_all("tr", id=lambda x: x and x.startswith("wk-otoceny-jeden-radek-id"))

    for row in rows:
        day_info = {}

        date_div = row.find("div", class_="wk-day-popis")
        if date_div:
            day_info["date"] = date_div.text.rstrip().split()[-1]

        day_info["gym"] = GYM

        lessons = []
        lesson_divs = row.find_all("div", class_="jedna-lekce-vypis")
        for lesson_div in lesson_divs:
            lesson_info = {}
            lesson_info["name"] = lesson_div.find("a", class_="lekce-telo-aktivita").text.strip()
            if lesson_info["name"] in IGNORED_LESSONS:
                continue

            lesson_info["time"] = lesson_div.find("div", class_="lekce-telo-cas").get_text(strip=True).replace(" ", "")
            lesson_info["trainer"] = lesson_div.find("div", class_="lekve-telo-instruktor").text.strip()
            try:
                occupancy = lesson_div.find("span", class_="cisla").get_text(strip=True)
                lesson_info["spots"] = occupancy.replace("\n", "").replace("\t", "").replace(" ", "")
            except AttributeError:
                lesson_info["spots"] = "" # lessons already finished or running
                pass
            lessons.append(lesson_info)

        if lessons:
            day_info["lessons"] = lessons
            days.append(day_info)

    return days
