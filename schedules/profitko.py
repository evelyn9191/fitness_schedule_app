import datetime

import requests
from bs4 import BeautifulSoup
import logging

from helpers import get_date_string, get_next_schedule_start_date

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SCHEDULE_URL = "https://booking.reservanto.cz/Modal/?id=10578&lId=10469"
GYM = "Profitko"
IGNORED_LESSONS = [
    "ČLEN REGISTRACE", "Seznamovačka", "Team kondička", "Kondička", "Silovka", "Skills"
]


def get_schedule():
    print(f"Getting schedule from {GYM}...")
    parse_from = get_next_schedule_start_date(GYM)
    if not parse_from:
        return []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'https://booking.reservanto.cz/Modal/?id=10578&lId=10469',
    }

    # First, get the main page to set cookies
    session = requests.Session()
    response = session.get('https://booking.reservanto.cz/Modal/?id=10578&lId=10469', headers=headers)
    response.raise_for_status()
    
    # Extract the necessary form fields
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Get all hidden inputs for the form
    form_data = {}
    for input_tag in soup.find_all('input', {'type': 'hidden'}):
        if 'name' in input_tag.attrs and 'value' in input_tag.attrs:
            form_data[input_tag['name']] = input_tag['value']
    
    # Set the calendar ID for group classes (SKUPINOVKY)
    form_data['BookingServiceViewModel.CalendarId'] = '14523'
    
    all_schedules = []
    
    # Get the Monday of the current week
    monday = parse_from - datetime.timedelta(days=parse_from.weekday())
    
    # Fetch three weeks of data (current week and next two weeks)
    for week_offset in [0, 1, 2]:
        week_start = monday + datetime.timedelta(weeks=week_offset)
        week_end = week_start + datetime.timedelta(days=6)
        
        # Update form data with the new date range
        form_data.update({
            'BookingTimeViewModel.DateTimeFrom': week_start.strftime('%Y-%m-%dT00:00:00'),
            'BookingTimeViewModel.DateTimeTo': week_end.strftime('%Y-%m-%dT23:59:59'),
            'BookingTimeViewModel.LastMondayDay': str(week_start.day),
            'BookingTimeViewModel.LastMondayMonth': str(week_start.month),
            'BookingTimeViewModel.LastMondayYear': str(week_start.year)
        })
        
        # Make the AJAX request to get the calendar data
        headers.update({
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://booking.reservanto.cz/Modal/?id=10578&lId=10469'
        })
        
        response = session.post(
            'https://booking.reservanto.cz/Classes/Step2_Calendar',
            headers=headers,
            data=form_data
        )
        response.raise_for_status()
        
        # Parse the schedule for this week
        week_schedule = parse_schedule(response.text)
        
        # Filter out days before parse_from
        filtered_schedule = []
        for day in week_schedule:
            try:
                day_date = datetime.datetime.strptime(day['date'], '%d.%m.%Y').date()
                if day_date >= parse_from:
                    filtered_schedule.append(day)
            except (ValueError, KeyError) as e:
                print(f"Error processing day {day.get('date', 'unknown')}: {e}")
                continue
                
        all_schedules.extend(filtered_schedule)
        
        # Small delay between requests to be nice to the server
        import time
        time.sleep(1)
    
    return all_schedules


def parse_schedule(html):
    soup = BeautifulSoup(html, 'html.parser')
    days = []
    
    # Find all appointment divs
    appointments = soup.find_all('div', class_='appointment')
    
    # Group appointments by date
    date_groups = {}
    
    for appt in appointments:
        # Extract data from the appointment div
        datetime_div = appt.find('div', class_='datetime')
        service_div = appt.find('div', class_='service')
        source_div = appt.find('div', class_='source')
        availability_span = appt.find('span', class_='availability')
        length_div = appt.find('div', class_='length')
        
        if not all([datetime_div, service_div, length_div]):
            continue
            
        # Format: 'neděle 05.10. 18:00'
        datetime_str = datetime_div.text.strip()
        
        # Split into date and time parts
        datetime_parts = datetime_str.split()
        if len(datetime_parts) < 3:
            continue
            
        # Get date in format 'DD.MM.'
        date_str = datetime_parts[1].strip('.')  # '05.10.' -> '05.10'
        
        # Extract time range from the title attribute (format: 'Ouša : Kondička (18:00 - 19:00) 3/14')
        title = appt.get('title', '')
        time_range = ''
        if '(' in title and ')' in title:
            time_part = title.split('(')[1].split(')')[0]  # Gets '18:00 - 19:00'
            time_range = time_part.replace(" ", "")
        
        # Extract class name, trainer, and spots
        class_name = service_div.text.strip()
        trainer = source_div.text.strip() if source_div else ''
        spots = availability_span.text.strip() if availability_span else ''
        
        # Skip ignored lessons
        if class_name in IGNORED_LESSONS:
            continue
            
        # Create day entry if it doesn't exist
        if date_str not in date_groups:
            date_groups[date_str] = []
            
        date_groups[date_str].append({
            'time': time_range,
            'name': class_name,
            'trainer': trainer,
            'spots': spots
        })
    
    # Convert to the required format (DD.MM.YYYY)
    current_year = datetime.datetime.now().year
    for date_str, lessons in date_groups.items():
        try:
            # Format: '05.10' -> '05.10.2025'
            if '.' in date_str:
                # Remove any existing dot at the end
                clean_date = date_str.rstrip('.')
                # Split into day and month
                day, month = clean_date.split('.')[:2]
                # Format with current year and ensure it's in DD.MM.YYYY format
                formatted_date = f"{day.zfill(2)}.{month.zfill(2)}.{current_year}"
                # Ensure the date is valid
                try:
                    # This will raise ValueError if the date is invalid
                    datetime.datetime.strptime(formatted_date, "%d.%m.%Y")
                    
                    days.append({
                        'date': formatted_date,
                        'gym': GYM,
                        'lessons': lessons
                    })
                except ValueError as e:
                    print(f"Invalid date '{formatted_date}': {e}")
        except Exception as e:
            print(f"Error parsing date '{date_str}': {e}")
            continue
    return days
