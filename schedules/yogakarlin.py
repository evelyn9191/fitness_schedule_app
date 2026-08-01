import datetime

import requests
from bs4 import BeautifulSoup

from helpers import get_next_schedule_start_date
from schedules.isportsystem import ISportSystemSchedulesHandler, IGNORED_LESSONS

GYM = "Yoga Karlin"


def parse_yogakarlin_schedule(html):
    """Custom parser for Yoga Karlin's new HTML structure"""
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.find_all('a', id=lambda x: x and x.startswith("id_activity_term_"))

    days = []
    lessons_by_dates = {}
    for row in rows:
        # Check if lesson is cancelled
        capacity_text = row.get_text()
        if 'zrušeno' in capacity_text.lower():
            continue
        
        # Extract data from data-tooltip attribute (new structure)
        raw_tooltip = row.get('data-tooltip')
        if not raw_tooltip:
            continue
            
        # Decode HTML entities in the tooltip
        decoded_tooltip = html.unescape(raw_tooltip)
        inner_soup = BeautifulSoup(decoded_tooltip, 'html.parser')
        
        name_tag = inner_soup.select_one('.activityTooltipName')
        name = name_tag.get_text(strip=True) if name_tag else None
        if name in IGNORED_LESSONS:
            continue

        labels = inner_soup.select('.tItem1')
        values = inner_soup.select('.tItem2')

        info = {label.get_text(strip=True): value.get_text(" ", strip=True)
                for label, value in zip(labels, values)}

        capacity = 'free' if 'volno' in capacity_text.lower() else 'full'

        if "Datum" not in info:
            continue

        current_date = info["Datum"].split("\xa0")[1]
        if not current_date:
            continue

        lesson = {
            'name': name,
            'date': current_date,
            'time': info.get('Čas'),
            'trainer': info.get('Lektor', ''),
            'spots': capacity,
        }

        if current_date not in lessons_by_dates:
            lessons_by_dates[current_date] = []

        lessons_by_dates[current_date].append(lesson)

    for date, lessons in lessons_by_dates.items():
        days.append({"date": date, "gym": GYM, "lessons": lessons})

    return days


def get_schedule(*args):
    print(f"Getting schedule from {GYM}...")
    parse_from = get_next_schedule_start_date(GYM)
    if not parse_from:
        return []

    dates_to_parse_from = [parse_from, parse_from + datetime.timedelta(days=7)]
    parsed_schedules = []
    
    # Create session and get cookies from main page first
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    })
    
    # Visit main page to get cookies
    session.get("https://yk.isportsystem.cz/")
    
    for date in dates_to_parse_from:
        handler = ISportSystemSchedulesHandler(GYM, "yk", date)
        post_data = {
            "id_sport": 5,
            "day": date.day,
            "month": date.month,
            "year": date.year,
            "event": "init",
            "timetableWidth": 1058
        }
        headers = handler.generate_client_headers()
        headers["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"
        response = session.post(handler.schedule_url, data=post_data, headers=headers)
        parsed = parse_yogakarlin_schedule(response.text)
        parsed_schedules.extend(parsed)
    return parsed_schedules
