import os
import webbrowser

import pandas as pd
from schedules import goodfellas, bevondrsfull, imfit


def run(date_spec=None):
    goodfellas_schedule = goodfellas.get_schedule()
    bevondrsfull_schedule = bevondrsfull.get_schedule(date_spec=date_spec)
    imfit_schedule = imfit.get_schedule()

    # Combine all schedules into one list
    all_schedules = goodfellas_schedule + bevondrsfull_schedule + imfit_schedule

    # Create a list to store formatted data
    formatted_data = []

    for gym_schedule in all_schedules:
        if date_spec and gym_schedule['date'] != date_spec:
            continue

        date = gym_schedule['date']
        day = gym_schedule['day']
        gym = gym_schedule["gym"]
        for lesson in gym_schedule['lessons']:
            formatted_data.append({
                'Date': date,
                'Day': day,
                'Class Name': lesson['name'],
                'Time': lesson['time'],
                'Spots': lesson['spots'],
                'Trainer': lesson['trainer'],
                'Gym': gym,
            })

    df = pd.DataFrame(formatted_data)
    print(df.to_string(index=False))  # Removes index for a cleaner look
    html_output = df.to_html(index=False, escape=False)
    html_file_path = 'timetable.html'
    with open(html_file_path, 'w') as f:
        f.write(html_output)
    webbrowser.open('file://' + os.path.realpath(html_file_path))

if __name__ == "__main__":
    run(date_spec=None)