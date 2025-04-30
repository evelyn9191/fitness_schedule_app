import datetime

import requests
from bs4 import BeautifulSoup

from helpers import get_next_schedule_start_date, DATE_FORMAT_CZ

SCHEDULE_URL = "https://liberec.imfit.cz/SkupinoveLekce.aspx"
GYM = "I'm Fit"
IGNORED_LESSONS = ["Maminky", "Ladies Jumping"]

def get_schedule():
    parse_from = get_next_schedule_start_date(GYM)
    response = requests.get(SCHEDULE_URL)
    parsed_schedules = parse_schedule(response.text, parse_from)
    return parsed_schedules

def parse_schedule(html: str, parse_from: datetime.date) -> list:
    soup = BeautifulSoup(html, "html.parser")
    days = []

    # Find all class cards
    class_cards = soup.find_all('div', class_='mycard_skupinovky2')

    for card in class_cards:
        class_name_tag = card.find('span', id=lambda x: x and 'lblSkupPopis' in x)
        class_name = class_name_tag.text.strip() if class_name_tag else "Unknown Class"

        if class_name in IGNORED_LESSONS or "zrušeno" in class_name.lower():
            continue

        date_tag = card.find('input', {'name': lambda x: x and 'hfDatum2' in x})
        date = date_tag['value'].split()[0] if date_tag else "Unknown Date"

        if datetime.datetime.strptime(date, DATE_FORMAT_CZ).date() < parse_from:
            continue

        time_tag = card.find('span', id=lambda x: x and 'lblSkupCasOdDo' in x)
        time = time_tag.text.strip().replace(" ", "") if time_tag else "Unknown Time"

        trainer_tag = card.find('span', id=lambda x: x and 'lblSkupTrener' in x)
        trainer = trainer_tag.text.strip() if trainer_tag else "Unknown Trainer"

        spots_tag = card.find('span', id=lambda x: x and 'obsazenost' in x)
        spots = spots_tag.text.strip() if spots_tag else "Unknown Spots"

        day_entry = {'date': date, "gym": GYM, 'lessons': []}

        # Add the lesson to the respective day
        day_entry['lessons'].append({
            'name': class_name,
            'spots': spots,
            'time': time,
            'trainer': [trainer],
        })
        days.append(day_entry)

    return days
