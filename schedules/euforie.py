import datetime

import requests
from bs4 import BeautifulSoup
from requests_html import HTMLSession

from helpers import get_next_schedule_start_date, get_date_string

SCHEDULE_URL = "https://rezervace.euforie.cz/cs/euforie/rozvrh-hodin"
GYM = "Euforie Karlin"
IGNORED_LESSONS = ["CYCLING", "BARRE workout", "Cvičení pro těhotné", "Trampolínky"]


# ajax=vytvor-tabulku-rozvrh-hodin&limit=0&nacteno=0&pobocka=3&datum=Datum+...&skupina=
def get_schedule():
    parse_from = get_next_schedule_start_date(GYM)
    if not parse_from:
        return []

    parsed_schedules = []
    for results_count in range(0, 100, 10):
        data = {
            "ajax": "vytvor-tabulku-rozvrh-hodin",
            "limit": results_count,
            "nacteno": results_count,
            "pobocka": 3,
            "datum": "Datum ...",
            "skupina": ""
        }
        response = requests.post(SCHEDULE_URL, data=data)
        parsed_schedules.extend(parse_schedule(response.text))
    parsed_schedules = merge_parsed_schedules(parsed_schedules)
    return parsed_schedules


def merge_parsed_schedules(parsed_schedules: list[dict]):
    merged_by_date = {}

    for schedule in parsed_schedules:
        date = schedule["date"]

        if date in merged_by_date:
            merged_by_date[date]['lessons'].extend(schedule.get('lessons', []))
        else:
            merged_by_date[date] = {
                'date': date,
                'gym': schedule.get('gym', GYM),
                'lessons': schedule.get('lessons', [])
            }

    merged_schedules = list(merged_by_date.values())
    return merged_schedules

def parse_schedule(html):
    soup = BeautifulSoup(html, "html.parser")
    lessons_by_date = {}

    # Find all lesson rows (excluding the "load more" row)
    lesson_rows = soup.find_all("tr")
    lesson_rows = [row for row in lesson_rows if not "timetable-more" in row.get("class", [])]

    for row in lesson_rows:
        # Skip header rows or rows without enough cells
        cells = row.find_all("td")
        if len(cells) < 6:
            continue

        # Extract lesson information from cells
        room = cells[0].text.strip()
        lesson_name = cells[1].text.strip()

        # Skip ignored lessons
        if lesson_name in IGNORED_LESSONS:
            continue

        # Parse date (format: "Po  9. 6. 2025")
        date_text = cells[2].text.strip()
        try:
            # Extract just the date part (e.g., "9. 6. 2025")
            date_parts = date_text.split()
            if len(date_parts) >= 3:
                day = date_parts[1].replace(".", "").strip()
                month = date_parts[2].replace(".", "").strip()
                year = date_parts[3].strip()
                date_str = f"{day}.{month}.{year}"  # Format as DD.MM.YYYY
            else:
                continue
        except (IndexError, ValueError):
            continue

        # Extract time
        time = cells[3].text.strip()

        # Extract duration
        duration = cells[4].text.strip()

        # Extract trainer
        trainer = cells[5].text.strip()

        # Format time as "HH:MM-HH:MM" (start time to end time)
        # Calculate end time based on duration (e.g., "60 min.")
        try:
            duration_minutes = int(duration.split()[0]) if duration else 60
            start_time_parts = time.split(":")
            if len(start_time_parts) == 1:  # Handle format like "7:00" vs "7"
                start_hour = int(start_time_parts[0])
                start_minute = 0
            else:
                start_hour = int(start_time_parts[0])
                start_minute = int(start_time_parts[1])

            # Calculate end time
            end_minutes = (start_minute + duration_minutes) % 60
            end_hours = (start_hour + (start_minute + duration_minutes) // 60)

            # Format as "HH:MM-HH:MM"
            time_range = f"{start_hour}:{start_minute:02d}-{end_hours}:{end_minutes:02d}"
        except (ValueError, IndexError):
            time_range = f"{time}-?"

        # Create or get the lessons list for this date
        if date_str not in lessons_by_date:
            lessons_by_date[date_str] = {
                "date": date_str,
                "gym": GYM,
                "lessons": []
            }

        # Add lesson to the appropriate date
        lessons_by_date[date_str]["lessons"].append({
            "name": lesson_name,
            "time": time_range,
            "trainer": trainer,
            "room": room,
            "spots": ""  # No specific availability info in the HTML
        })

    # Convert the dictionary to a list of day schedules
    days = list(lessons_by_date.values())

    return days
