import datetime
import re
import requests
from bs4 import BeautifulSoup

from helpers import get_next_schedule_start_date

GYM = "Elite Athletics"


def parse_duration_minutes(duration_text):
    """Parse a duration string like '55m', '1h' or '1h 30m' into a number of minutes"""
    hours_match = re.search(r'(\d+)\s*h', duration_text)
    minutes_match = re.search(r'(\d+)\s*m', duration_text)
    hours = int(hours_match.group(1)) if hours_match else 0
    minutes = int(minutes_match.group(1)) if minutes_match else 0
    return hours * 60 + minutes


def resolve_full_date(day, month):
    """Turn a day/month pair from the site (which omits the year) into a full date,
    assuming the schedule always refers to the current or upcoming year"""
    today = datetime.date.today()
    year = today.year
    candidate = datetime.date(year, month, day)
    if candidate < today - datetime.timedelta(days=3):
        candidate = datetime.date(year + 1, month, day)
    return candidate


def parse_elite_athletics_schedule(html):
    """Parse Elite Athletics schedule from Reservanto's appointment list HTML"""
    soup = BeautifulSoup(html, 'html.parser')

    groups = soup.select('div.appointment-list-group')
    if not groups:
        print("No appointment groups found")
        return []

    days = []
    for group in groups:
        header = group.select_one('.appointment-list-group-header')
        day_span = header.find('span').get_text(strip=True) if header else ''
        date_match = re.match(r'(\d+)\.\s*(\d+)\.', day_span)
        if not date_match:
            continue
        day, month = int(date_match.group(1)), int(date_match.group(2))
        current_date = resolve_full_date(day, month).strftime("%d.%m.%Y")

        lessons = []
        for appointment in group.select('.appointment-list-group-appointment'):
            onclick = appointment.get('onclick', '')
            id_match = re.search(r'selectAppointment\((\d+)', onclick)
            appointment_id = id_match.group(1) if id_match else ''

            time_element = appointment.select_one('.appointment-list-group-appointment-time')
            start_time_text = time_element.get_text(strip=True) if time_element else ''
            start_time = datetime.datetime.strptime(start_time_text, "%H:%M")

            duration_element = appointment.select_one('.appointment-list-group-appointment-right-pane div')
            duration_minutes = parse_duration_minutes(duration_element.get_text(strip=True)) if duration_element else 0
            end_time = start_time + datetime.timedelta(minutes=duration_minutes)

            info = appointment.select_one('.appointment-list-group-appointment-info')
            name_element = info.find('h4') if info else None
            lesson_name = name_element.get_text(strip=True) if name_element else 'Class'

            trainer_element = info.select_one('div:not(.appointment-list-group-appointment-availability)') if info else None
            trainer = trainer_element.get_text(strip=True) if trainer_element else ''

            spots_element = info.select_one('.appointment-list-group-appointment-availability') if info else None
            spots = spots_element.get_text(strip=True) if spots_element else 'unknown'

            lessons.append({
                'name': lesson_name,
                'date': current_date,
                'time': f"{start_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')}",
                'trainer': trainer,
                'spots': spots,
                'appointment_id': appointment_id
            })

        if lessons:
            days.append({"date": current_date, "gym": GYM, "lessons": lessons})

    return days


def get_schedule():
    print(f"Getting schedule from {GYM}...")
    parse_from = get_next_schedule_start_date(GYM)
    if not parse_from:
        return []

    # Note: The Reservanto API only returns the current week's schedule
    # regardless of the date parameter. This is a limitation of the API.
    
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Origin": "https://booking.reservanto.cz",
        "Referer": "https://booking.reservanto.cz/Modal/?id=13652&seg=6",
        "X-Requested-With": "XMLHttpRequest"
    })
    
    # Visit the modal page first to get cookies
    session.get("https://booking.reservanto.cz/Modal/?id=13652&seg=6", verify=False)
    
    parsed_schedules = []
    
    # Fetch schedule for the current week only (API limitation)
    post_data = {
        "SessionStorage": "",
        "LocalStorage": "",
        "IsLoginOnly": "False",
        "MustBeLogged": "False",
        "FirstAccessUrl": "https%3A%2F%2Fbooking.reservanto.cz%2FModal%2F%3Fid%3D13652%26seg%3D6",
        "Compact": "False",
        "SegmentId": "6",
        "SegmentType": "2",
        "RefreshInsteadOfClose": "False",
        "FirstStep": "2",
        "SegmentSelect": "False",
        "ChangeAppointmentId": "",
        "UseCultureChanger": "False",
        "ShowServiceLengths": "True",
        "HideAccounts": "False",
        "PluginData": "",
        "Mode": "None",
        "AutoClassesSettingsViewModel.SettingsId": "0",
        "AutoClassesSettingsViewModel.Capacity": "0",
        "AutoClassesSettingsViewModel.AutoLength": "0",
        "AutoClassesSettingsViewModel.AutoTimeInterval": "0",
        "AutoClassesSettingsViewModel.FirstChoose": "EveryCustomerService",
        "BookingLocationAppointmentViewModel.LocationId": "12960",
        "BookingLocationAppointmentViewModel.CourseId": "0",
        "BookingLocationAppointmentViewModel.AppointmentId": "0",
        "BookingServiceViewModel.MerchantName": "Elite Athletics training center",
        "BookingServiceViewModel.MerchantId": "13652",
        "BookingServiceViewModel.CalendarId": "14996",
        "BookingServiceViewModel.ResourceAutoSelectState": "Off",
        "BookingServiceViewModel.ResourceAutoSelectCaption": "",
        "BookingServiceViewModel.MaxLightweightCombinations": "0",
        "BookingServiceViewModel.BookingResourceId": "0",
        "BookingServiceViewModel.BookingServiceId": "0",
        "BookingServiceViewModel.PreselectedServiceId": "0",
        "BookingServiceViewModel.UseAppointmentSequences": "False",
        "BookingServiceViewModel.ServicePrice": "0",
        "BookingServiceViewModel.PriceLevelId": "",
        "BookingServiceViewModel.PriceLevelSet": "False",
        "LogoVisibility": "Small",
        "IsFreeSpaceWaitingCustomerEnabled": "False",
        "FreeSpaceWaitingCustomerViewModel.MerchantId": "0",
        "FreeSpaceWaitingCustomerViewModel.CustomerId": "0",
        "FreeSpaceWaitingCustomerViewModel.LocationId": "0",
        "FreeSpaceWaitingCustomerViewModel.BookingResourceId": "",
        "FreeSpaceWaitingCustomerViewModel.BookingServiceId": "0",
        "FreeSpaceWaitingCustomerViewModel.StartsAt": "1.+1.+0001+0%3A00%3A00",
        "FreeSpaceWaitingCustomerViewModel.EndsAt": "",
        "FreeSpaceWaitingCustomerViewModel.MinimalFreeSpaceLength": "00%3A00%3A00",
        "BookingTimeViewModel.DateTimeFrom": "0001-01-01T00%3A00%3A00%2B01%3A00",
        "BookingTimeViewModel.DateTimeToSetter": "",
        "BookingTimeViewModel.LastMondayDay": "0",
        "BookingTimeViewModel.LastMondayMonth": "0",
        "BookingTimeViewModel.LastMondayYear": "0",
        "BookingTimeViewModel.LastSelectedDate": parse_from.strftime("%d.%m.%Y"),
        "BookingTimeViewModel.TimeInterval": "0",
        "BookingTimeViewModel.Length": "0",
        "BookingTimeViewModel.PaddingTime": "0",
        "BookingTimeViewModel.PersonFilterType": "Off",
        "RepetitionViewModel.UseRepetition": "False",
        "RepetitionViewModel.ToRemoveJson": "",
        "BookingLoginModel.SplitNames": "False",
        "BookingLoginModel.FirstName": "",
        "BookingLoginModel.LastName": "",
        "BookingLoginModel.Email": "",
        "BookingLoginModel.Phone": "",
        "BookingLoginModel.Password": "",
        "BookingLoginModel.TryRegister": "False",
        "BookingLoginModel.ValidationCode": "",
        "PaymentModel.PaymentMethod": "",
        "PaymentModel.VoucherId": "",
        "PaymentModel.PassToCustomerId": "0",
        "PaymentModel.PassToBuyId": "",
        "PaymentModel.CreditPartiallyUsed": "0",
        "PaymentModel.LPointsPartiallyUsed": "0",
        "PaymentModel.AnotherCustomersCount": "0",
        "PaymentModel.UsePartialVoucher": "False",
        "PaymentModel.AllCardHolderInfoAvailable": "False",
        "AlternateBookingModel.AlternateBookingsType": "Disabled",
        "AlternateBookingModel.CustomerConfirmedAlternate": "False",
        "AlternateCourseBookingModel.AlternateBookingsType": "Disabled",
        "AlternateCourseBookingModel.CustomerConfirmedAlternate": "False",
        "MerchantGroupViewModel.MerchantGroupId": "",
        "MerchantGroupViewModel.SelectedServiceGroupId": "",
        "TrackingHints": "%7B%22StepName%22%3A%22%2FClasses%2FStep2%22%7D"
    }
    
    headers = session.headers.copy()
    headers["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"
    
    try:
        response = session.post(
            "https://booking.reservanto.cz/Classes/Step2_Calendar",
            data=post_data,
            headers=headers,
            verify=False
        )
        print(f"Response status: {response.status_code}")
        print(f"Response length: {len(response.text)}")
        
        parsed = parse_elite_athletics_schedule(response.text)
        print(f"Parsed {len(parsed)} schedule days")

        parsed_schedules.extend(parsed)
        
    except Exception as e:
        print(f"Error fetching Elite Athletics schedule: {e}")
    
    return parsed_schedules
