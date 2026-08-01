import datetime

from bs4 import BeautifulSoup

IGNORED_LESSONS = [
    "Pronájem sálu", "PetsYoga", "Individuální lekce", "Jóga MAMI & MIMI", "Open shala", "Jóga pro těhotné",
    "Pravidelné jógové hry pro rodiče a děti 4 - 8 let", "Jógové hry pro rodiče a děti 4 - 8 let",
    "Jógové hry pro rodiče a děti 5 - 12 let", "Těhotenská jóga", "Létající jóga v sítích", "Jóga & pilates",
    "Lunch jóga"
    ]
SIDDHA_YOGA_FUGNEROVA_VENUE_COLOR = "#f2b825"


def parse_new_isportsystem_html(html, gym_name, venue_color_filter=None):
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.find_all('a', id=lambda x: x and x.startswith("id_activity_term_"))

    days = []
    lessons_by_dates = {}
    for row in rows:
        # Check if lesson is cancelled
        capacity_text = row.get_text()
        if 'zrušeno' in capacity_text.lower():
            continue
        
        # Filter by venue color if specified
        if venue_color_filter:
            style = row.get('style', '').lower()
            if venue_color_filter not in style:
                continue
        
        # Extract data from data-tooltip attribute (new structure)
        raw_tooltip = row.get('data-tooltip')
        if not raw_tooltip:
            continue
            
        # Decode HTML entities in the tooltip
        decoded_tooltip = raw_tooltip.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&').replace('&quot;', '"')
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
        days.append({"date": date, "gym": gym_name, "lessons": lessons})

    return days


class ISportSystemSchedulesHandler:
    def __init__(self, gym: str, domain_name: str, parse_from: datetime.date):
        self.gym = gym
        self.domain_name = domain_name
        self.parse_from = parse_from
        self.schedule_url = f"https://{domain_name}.isportsystem.cz/ajax/ajax.schema.php"

    def generate_client_headers(self) -> dict:
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Referer": f"https://{self.domain_name}.isportsystem.cz/",
            "X-Requested-With": "XMLHttpRequest",
        }

    def get_params(self, id_sport: int = 5) -> dict:
        return {
            "day": self.parse_from.day,
            "month": self.parse_from.month,
            "year": self.parse_from.year,
            "id_sport": id_sport,
            "event": "pageLoad",
            "tab_type": "activity",
            "timetableWidth": 956,
        }

    def parse_schedule(self, html):
        soup = BeautifulSoup(html, "html.parser")

        rows = soup.find_all('a', id=lambda x: x and x.startswith("id_activity_term_"))

        days = []
        lessons_by_dates = {}
        for row in rows:
            raw_title = row.get('title')
            inner_soup = BeautifulSoup(raw_title, 'html.parser')
            name_tag = inner_soup.select_one('.activityTooltipName')
            name = name_tag.get_text(strip=True) if name_tag else None
            if name in IGNORED_LESSONS:
                continue

            labels = inner_soup.select('.tItem1')
            values = inner_soup.select('.tItem2')

            info = {label.get_text(strip=True): value.get_text(" ", strip=True)
                    for label, value in zip(labels, values)}

            capacity = 'free' if 'volno' in row.get_text().lower() else 'full'

            if "Datum" not in info:
                continue

            if capacity == 'full' and self.gym == "Siddha Yoga":
                continue

            current_date = info["Datum"].split("\xa0")[1]
            if not current_date:
                continue

            if self.gym == "Siddha Yoga":
                style = row.get('style', '').lower()
                is_fugnerova = SIDDHA_YOGA_FUGNEROVA_VENUE_COLOR in style
                if not is_fugnerova:
                    continue

            lesson = {
                'name': name,
                'date': current_date,
                'time': info.get('Čas'),
                'trainer': info.get('Instruktor', ''),
                'spots': capacity,
            }

            if current_date not in lessons_by_dates:
                lessons_by_dates[current_date] = []

            lessons_by_dates[current_date].append(lesson)

        for date, lessons in lessons_by_dates.items():
            days.append({"date": date, "gym": self.gym, "lessons": lessons})

        return days