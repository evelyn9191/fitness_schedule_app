import requests
from bs4 import BeautifulSoup

SCHEDULE_URL = "https://goodfellasgym.inrs.cz/rs"

def get_schedule():
    response = requests.get(SCHEDULE_URL)
    parsed_schedules = parse_schedule(response.text)
    return parsed_schedules

def parse_schedule(html):
    soup = BeautifulSoup(html, "html.parser")
    days = []

    # Find all rows with lessons
    rows = soup.find_all("tr", id=lambda x: x and x.startswith("wk-otoceny-jeden-radek-id"))

    for row in rows:
        day_info = {}
        # Extract date
        date_div = row.find("div", class_="wk-day-popis")
        if date_div:
            day_info["day"] = date_div.find("span", class_="aktualni-den").text.strip()
            day_info["date"] = date_div.text.rstrip().split()[-1]

        day_info["gym"] = "GoodFellas"

        lessons = []
        lesson_divs = row.find_all("div", class_="jedna-lekce-vypis")
        for lesson_div in lesson_divs:
            lesson_info = {}
            lesson_info["time"] = lesson_div.find("div", class_="lekce-telo-cas").get_text(strip=True)
            lesson_info["name"] = lesson_div.find("a", class_="lekce-telo-aktivita").text.strip()
            lesson_info["trainer"] = lesson_div.find("div", class_="lekve-telo-instruktor").text.strip()
            occupancy = lesson_div.find("span", class_="cisla").get_text(strip=True)
            lesson_info["spots"] = occupancy.replace("\n", "").replace("\t", "").replace(" ", "")
            lessons.append(lesson_info)

        if lessons:
            day_info["lessons"] = lessons
            days.append(day_info)

    return days
