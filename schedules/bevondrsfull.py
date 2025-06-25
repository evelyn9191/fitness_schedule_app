import datetime
import re
from typing import Any

import requests
from bs4 import BeautifulSoup

from helpers import get_next_schedule_start_date, DATE_FORMAT_CZ

SCHEDULE_URL = "https://bevondrsfull.clubspire.cz/timeline/week?criteriaTimestamp&resetFilter=true#timelineCalendar"
GYM = "Be Vondrsfull"
IGNORED_LESSONS = ["PRONÁJEM SÁLU", "BARRE BODY", "PILATES S ROLLERY"]

def get_schedule():
    print(f"Getting schedule from {GYM}...")
    parse_from = get_next_schedule_start_date(GYM)
    if not parse_from:
        return []

    parsed_schedules = []
    response = requests.get(SCHEDULE_URL)

    parsed_schedules.extend(parse_schedule(response.text, parse_from))
    return parsed_schedules


def parse_schedule(html: str, parse_from: datetime.date) -> list[dict[str, Any]]:
    soup = BeautifulSoup(html, 'html.parser')
    days_section = soup.find('div', {'id': 'days_halls'})
    if not days_section:
        return []

    day_elements = days_section.find_all('li', id=re.compile(r'^day_hall_\w{3}$'))
    date_map = {}

    for day_elem in day_elements:
        day_abbr = day_elem['id'].split('_')[-1]  # mon, tue, etc.
        date_text = day_elem.find('span', class_='day').get_text(strip=True)
        # Extract date from text like "Mon 30.6."
        date_str = re.search(r'\d+\.\d+\.', date_text).group(0)
        day, month, _ = date_str.split('.')
        year = datetime.date.today().year
        date_map[day_abbr] = datetime.date(year, int(month), int(day))

    schedule = []
    lesson_rows = soup.select('tr[data-parent-row-id]')

    for row in lesson_rows:
        day_abbr = row['data-parent-row-id'].split('_')[-1]  # mon, tue, etc.
        if day_abbr not in date_map:
            continue

        date = date_map[day_abbr]
        if date < parse_from:
            continue

        lesson_cells = row.find_all('td', class_=lambda c: c and 'a_' in c)

        for cell in lesson_cells:
            lesson = {
                'date': date.strftime(DATE_FORMAT_CZ),
                'gym': GYM,
                'lessons': []
            }

            # Extract time from the tooltip
            tooltip = cell.find('div', class_='schedule_tooltip')
            if not tooltip:
                continue

            time_info = tooltip.find('div', class_='info top')
            if not time_info:
                continue

            time_start = time_info.find('div', class_='time start')
            time_end = time_info.find('div', class_='time end')

            if not time_start or not time_end:
                continue

            start_time = time_start.get_text(strip=True).strip(':')
            end_time = time_end.get_text(strip=True).strip(':')

            description = tooltip.find('div', class_='description')
            if not description:
                continue

            name_elem = description.find('div', class_='lesson_name')
            if not name_elem:
                continue

            lesson_name = name_elem.get_text(strip=True)
            if any(ignored in lesson_name for ignored in IGNORED_LESSONS) or "Nelze využít kartu Multisport" in lesson_name:
                continue

            # Extract trainer
            trainer_elem = description.find('a', class_='ajax_popup_trigger')
            trainer = trainer_elem.get_text(strip=True).replace("\xa0", " ") if trainer_elem else ""

            # Extract available spots
            availability = tooltip.find('div', class_='availability')
            spots = "N/A"
            if availability and availability.strong:
                spots = availability.strong.get_text(strip=True)

            lesson['lessons'].append({
                'name': lesson_name,
                'time': f"{start_time}-{end_time}",
                'trainer': [trainer] if trainer else [],
                'spots': spots
            })

            if lesson['lessons']:
                schedule.append(lesson)

    return schedule
