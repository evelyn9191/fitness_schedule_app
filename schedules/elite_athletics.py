import datetime
import requests
from bs4 import BeautifulSoup

from helpers import get_next_schedule_start_date

GYM = "Elite Athletics"


def get_schedule():
    print(f"Getting schedule from {GYM}...")
    parse_from = get_next_schedule_start_date(GYM)
    if not parse_from:
        return []

    base_url = "https://booking.reservanto.cz/Modal/?id=13652&seg=6"
    
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    })
    
    try:
        response = session.get(base_url)
        print(f"Response status: {response.status_code}")
        print(f"Response length: {len(response.text)}")
        
        # Parse the HTML response
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # TODO: Parse the actual schedule data from the Reservanto modal
        # This will need to be implemented based on the actual HTML structure
        # For now, return empty list as placeholder
        
        return []
        
    except Exception as e:
        print(f"Error fetching Elite Athletics schedule: {e}")
        return []
