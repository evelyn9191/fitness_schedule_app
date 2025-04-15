import freezegun
import pytest
from unittest.mock import patch, Mock
from schedules.myfitness import get_schedule

MOCK_LOGIN_URL = "https://www.supersaas.test/schedule/login/jumping-broumovska/rezervace"
MOCK_SCHEDULE_URL = "https://www.supersaas.test/schedule/jumping-broumovska/rezervace"
TODAY = "2025-01-10"

@pytest.fixture
def mock_urls(monkeypatch):
    monkeypatch.setattr("schedules.myfitness.LOGIN_URL", MOCK_LOGIN_URL)
    monkeypatch.setattr("schedules.myfitness.SCHEDULE_URL", MOCK_SCHEDULE_URL)

@pytest.fixture
def mock_response_data():
    # Mock the JavaScript app data that contains schedule information
    return """var app=[
        [1736527200,1736530800,null,15,8,null,null,"HIIT",
        "Jane Smith",null,null,null],
        [1736534400,1736538000,null,12,5,null,null,"CARDIO STEP",
        "John Doe",null,null,null],
        [1736541600,1736545200,null,20,15,null,null,"Strength Training",
        "Mike Johnson",null,null,null]
    ]var busy_color"""

@freezegun.freeze_time(TODAY)
def test_get_schedule_success(mock_response_data, mock_urls):
    mock_session = Mock()
    mock_response = Mock()
    mock_response.text = mock_response_data
    mock_session.post.return_value = mock_response
    mock_session.get.return_value = Mock()

    with patch('schedules.myfitness.HTMLSession', return_value=mock_session):
        # Call function
        result = get_schedule()

        # Verify results
        assert len(result) == 1  # One day of schedule
        assert result[0]["gym"] == "MyFitness"
        assert result[0]["date"] == "10.01.2025"
        
        # Should only have 2 lessons as CARDIO STEP is in IGNORED_LESSONS
        assert len(result[0]["lessons"]) == 2
        
        lesson1 = result[0]["lessons"][0]
        assert lesson1["time"] == "16:40-17:40"
        assert lesson1["name"] == "HIIT"
        assert lesson1["trainer"] == "Jane Smith"
        assert lesson1["spots"] == "8/15"

        lesson2 = result[0]["lessons"][1]
        assert lesson2["time"] == "20:40-21:40"
        assert lesson2["name"] == "Strength Training"
        assert lesson2["trainer"] == "Mike Johnson"
        assert lesson2["spots"] == "15/20"
