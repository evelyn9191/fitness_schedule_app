import datetime

from run import get_last_lesson_date

ALL_SCHEDULES = [
        {'date': '1.5.2025', 'time': '8:30-9:30', 'name': 'PILATES', 'trainer': 'Lucie', 'spots': '0/-3',
         'gym': 'MyFitness'},
]
def test_get_last_lesson_date():
    result = get_last_lesson_date(ALL_SCHEDULES)
    assert result == {'MyFitness': '2025-05-01'}