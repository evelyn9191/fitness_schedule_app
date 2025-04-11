import datetime

def get_next_schedule_start_date(last_run_date: datetime.datetime, days_stored: int = 6) -> datetime.datetime | None:
    current_date = datetime.datetime.now().date()
    stored_schedules_till = last_run_date.date() + datetime.timedelta(days=days_stored)
    days_to_parse = current_date - stored_schedules_till
    if days_to_parse > datetime.timedelta(days=0):
        start_parsing_from = stored_schedules_till + datetime.timedelta(days=1)
        future_date = max(start_parsing_from, current_date)
        return future_date.strftime("%Y-%m-%d")
    return None
