import datetime

from gcal_updater import GoogleCalendarClient

def delete_gym_events(gym: str) -> None:
    service = GoogleCalendarClient()
    today = datetime.datetime.now(datetime.timezone.utc).isoformat()
    gym_events = service.list_events(query=gym, start_from=today)
    for event in gym_events:
        print(event)
        service.delete_event(event)

if __name__ == '__main__':
    GYM = ""
    if not GYM:
        print("Set a gym to avoid deleting all events")
    else:
        delete_gym_events(gym=GYM)