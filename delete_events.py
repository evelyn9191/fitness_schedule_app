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
    today = datetime.datetime.now(datetime.timezone.utc)
    delete_events()
