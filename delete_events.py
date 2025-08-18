import datetime

from gcal_updater import GoogleCalendarClient

def delete_events(query: str | None = None, timeMin: str | None = None, timeMax: str | None = None) -> None:
    if not (query or timeMin or timeMax):
        return

    service = GoogleCalendarClient()
    gym_events = service.list_events(query=query, timeMin=timeMin, timeMax=timeMax)
    for event in gym_events:
        print(event)
        service.delete_event(event)


if __name__ == '__main__':
    now = datetime.datetime.now()
    two_days_later = now + datetime.timedelta(days=2)
    time_min = two_days_later.replace(hour=0, minute=0, second=0, microsecond=0)
    time_max = two_days_later.replace(hour=23, minute=59, second=59, microsecond=999999)
    time_min_iso = time_min.isoformat() + 'Z'
    time_max_iso = time_max.isoformat() + 'Z'

    print(f"Deleting events from {time_min} to {time_max}")
    delete_events()