import datetime
import re
from typing import Any
import logging

import requests
from bs4 import BeautifulSoup

from helpers import get_next_schedule_start_date, DATE_FORMAT_CZ

BASE_URL = "https://bevondrsfull.clubspire.cz"
SCHEDULE_URL = f"{BASE_URL}/timeline/week"
GYM = "Be Vondrsfull"
IGNORED_LESSONS = ["PRONÁJEM SÁLU", "BARRE BODY", "PILATES S ROLLERY", "REFORMER PILATES", "POWER PLATE", "KRUHOVÝ TRÉNINK", "FYZIO PILATES"]

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_week_timestamps():
    """Generate timestamps for current week and next two weeks"""
    now = datetime.datetime.now()
    timestamps = []
    
    # Get current week's Monday
    current_week = now - datetime.timedelta(days=now.weekday())
    
    # Generate timestamps for current week and next two weeks
    for week in range(3):
        week_date = current_week + datetime.timedelta(weeks=week)
        timestamp = int(week_date.timestamp()) * 1000
        timestamps.append(timestamp)
    
    return timestamps

def get_schedule():
    print(f"Getting schedule from {GYM}...")
    parse_from = get_next_schedule_start_date(GYM)
    if not parse_from:
        return []

    parsed_schedules = []
    session = requests.Session()
    
    # Set headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Referer': f'{BASE_URL}/',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    # First, get the initial page to set up the session
    session.get(f"{BASE_URL}/timeline", headers=headers)
    
    # Get schedules for current week and next two weeks
    for timestamp in get_week_timestamps():
        params = {
            'criteriaTimestamp': str(timestamp),
            'resetFilter': 'true'
        }

        response = session.get(SCHEDULE_URL, headers=headers, params=params)
        response.raise_for_status()

        parsed = parse_schedule(response.text, parse_from)
        parsed_schedules.extend(parsed)
    
    return parsed_schedules


def parse_schedule(html: str, parse_from: datetime.date) -> list[dict[str, Any]]:
    soup = BeautifulSoup(html, 'html.parser')
    days_section = soup.find('div', {'id': 'days_halls'})
    if not days_section:
        return []

    day_elements = days_section.find_all('li', id=re.compile(r'^day_hall_\w{3}$'))
    date_map = {}

    for day_elem in day_elements:
        day_abbr = day_elem['id'].split('_')[-1]
        date_span = day_elem.find('span', class_='day')
        if not date_span:
            continue
            
        date_text = date_span.get_text(strip=True)
        date_match = re.search(r'(\d+)\.(\d+)\.', date_text)
        if not date_match:
            continue
            
        day, month = date_match.groups()
        year = datetime.date.today().year
        
        current_month = datetime.date.today().month
        if int(month) < current_month and current_month > 10:
            year += 1
            
        try:
            date_map[day_abbr] = datetime.date(year, int(month), int(day))
        except ValueError:
            continue

    schedule = []
    
    lesson_rows = soup.select('tr[data-parent-row-id]')

    for row in lesson_rows:
        parent_row_id = row.get('data-parent-row-id', '')
        day_abbr = parent_row_id.split('_')[-1] if '_' in parent_row_id else ''
        
        if day_abbr not in date_map:
            continue

        date = date_map[day_abbr]
        if date < parse_from:
            continue

        lesson_cells = row.find_all('td', class_=lambda c: c and any(c.startswith(prefix) for prefix in ['a_', 'b_', 'd_']) and 'empty' not in c)

        for cell in lesson_cells:
            if 'disabled' in cell.get('class', []):
                continue
                
            tooltip = cell.find('div', class_='schedule_tooltip')
            if not tooltip:
                continue

            time_info = tooltip.find('div', class_='info top')
            if not time_info:
                continue

            time_start_elem = time_info.find('div', class_='time start')
            time_end_elem = time_info.find('div', class_='time end')

            if not time_start_elem or not time_end_elem:
                continue

            start_time_text = time_start_elem.get_text(strip=True)
            end_time_text = time_end_elem.get_text(strip=True)
            
            start_time = re.sub(r'[^\d:]', '', start_time_text)
            end_time = re.sub(r'[^\d:]', '', end_time_text)

            description = tooltip.find('div', class_='description')
            if not description:
                continue

            name_elem = description.find('div', class_='lesson_name')
            if not name_elem:
                continue

            lesson_name_full = name_elem.get_text(strip=True)
            
            if ' - ' in lesson_name_full:
                lesson_name, trainer_part = lesson_name_full.split(' - ', 1)
            else:
                lesson_name = lesson_name_full
                trainer_part = ""

            if any(ignored in lesson_name for ignored in IGNORED_LESSONS):
                continue

            location_elem = description.find('div', class_='lesson_description')
            location = location_elem.get_text(strip=True) if location_elem else ""

            trainer_link = description.find('a', class_='ajax_popup_trigger')
            if trainer_link:
                trainer = trainer_link.get_text(strip=True).replace("\xa0", " ")
            elif trainer_part:
                trainer = trainer_part
            else:
                trainer = ""

            availability_elem = tooltip.find('div', class_='availability')
            spots = "N/A"
            if availability_elem:
                strong_elem = availability_elem.find('strong')
                if strong_elem:
                    spots = strong_elem.get_text(strip=True)

            lesson_entry = {
                'date': date.strftime(DATE_FORMAT_CZ),
                'gym': GYM,
                'lessons': [{
                    'name': lesson_name,
                    'time': f"{start_time}-{end_time}",
                    'trainer': [trainer] if trainer else [],
                    'spots': spots,
                    'location': location
                }]
            }

            schedule.append(lesson_entry)

    return schedule
