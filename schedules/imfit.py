import datetime

import requests
from bs4 import BeautifulSoup

from helpers import get_next_schedule_start_date

SCHEDULE_URL = "https://liberec.imfit.cz/SkupinoveLekce.aspx"

def get_schedule(last_run_date: datetime.datetime):
    if not get_next_schedule_start_date(last_run_date, 4):
        return []

    response = requests.get(SCHEDULE_URL)
    parsed_schedules = parse_schedule(response.text)
    return parsed_schedules

def parse_schedule(html):
    soup = BeautifulSoup(html, "html.parser")
    days = []

    # Find all class cards
    class_cards = soup.find_all('div', class_='mycard_skupinovky2')

    for card in class_cards:
        time_tag = card.find('span', id=lambda x: x and 'lblSkupCasOdDo' in x)
        time = time_tag.text.strip().replace(" ", "") if time_tag else "Unknown Time"

        class_name_tag = card.find('span', id=lambda x: x and 'lblSkupPopis' in x)
        class_name = class_name_tag.text.strip() if class_name_tag else "Unknown Class"

        trainer_tag = card.find('span', id=lambda x: x and 'lblSkupTrener' in x)
        trainer = trainer_tag.text.strip() if trainer_tag else "Unknown Trainer"

        spots_tag = card.find('span', id=lambda x: x and 'obsazenost' in x)
        spots = spots_tag.text.strip() if spots_tag else "Unknown Spots"

        date_tag = card.find('input', {'name': lambda x: x and 'hfDatum2' in x})
        date = date_tag['value'].split()[0] if date_tag else "Unknown Date"

        day_entry = {'date': date, "gym": "I'm Fit", 'lessons': []}

        # Add the lesson to the respective day
        day_entry['lessons'].append({
            'name': class_name,
            'spots': spots,
            'time': time,
            'trainer': [trainer],
        })
        days.append(day_entry)

    return days
