import datetime

import requests
from bs4 import BeautifulSoup

from helpers import get_next_schedule_start_date

SCHEDULE_URL = "https://moonyyoga.isportsystem.cz/ajax/ajax.schema.php"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Referer": "https://moony-yoga.isportsystem.cz/",
    "X-Requested-With": "XMLHttpRequest",
}

def get_schedule(last_run_date: datetime.datetime):
    if not get_next_schedule_start_date(last_run_date):
        return []

    start_date = datetime.datetime.today()
    params = {
        "day": start_date.day,
        "month": start_date.month,
        "year": start_date.year,
        "id_sport": 5,
        "event": "pageLoad",
        "tab_type": "activity",
        "timetableWidth": 956,
    }

    response = requests.get(SCHEDULE_URL, params=params, headers=HEADERS)
    parsed_schedules = parse_schedule(response.text)
    return parsed_schedules

def parse_schedule(html):
    soup = BeautifulSoup(html, "html.parser")

    rows = soup.find_all('a', id=lambda x: x and x.startswith("id_activity_term_"))

    days = []
    lessons_by_dates = {}
    for row in rows:
        raw_title = row.get('title')
        inner_soup = BeautifulSoup(raw_title, 'html.parser')
        name_tag = inner_soup.select_one('.activityTooltipName')
        name = name_tag.get_text(strip=True) if name_tag else None

        labels = inner_soup.select('.tItem1')
        values = inner_soup.select('.tItem2')

        info = {label.get_text(strip=True): value.get_text(" ", strip=True)
                for label, value in zip(labels, values)}

        capacity = 'free' if 'volno' in row.get_text().lower() else 'full'

        current_date = info.get('Datum', "").split("\xa0")[1]
        if not current_date:
            continue

        lesson = {
            'name': name,
            'date': current_date,
            'time': info.get('Čas'),
            'trainer': info.get('Instruktor', ''),
            'spots': capacity
        }

        if current_date not in lessons_by_dates:
            lessons_by_dates[current_date] = []

        lessons_by_dates[current_date].append(lesson)

    for date, lessons in lessons_by_dates.items():
        days.append({"date": date, "gym": "Moony Yoga", "lessons": lessons})

    print(days)
    return days
