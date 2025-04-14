import freezegun
import pytest
from unittest.mock import patch, Mock
from schedules.goodfellas import get_schedule

MOCK_SCHEDULE_URL = "https://goodfellasgym.testurl.abc/rs/kalendar_vypis/kalendar_vypis"
TODAY = "2025-01-10"

@pytest.fixture
def mock_schedule_url(monkeypatch):
    monkeypatch.setattr("schedules.goodfellas.SCHEDULE_URL", MOCK_SCHEDULE_URL)

@pytest.fixture
def mock_html():
    return """
    <tr id="wk-otoceny-jeden-radek-id-123">
        <div class="wk-day-popis">Monday 10.01.2025</div>
        <div class="jedna-lekce-vypis">
            <div class="lekce-telo-cas">18:00</div>
            <a class="lekce-telo-aktivita">CrossFit</a>
            <div class="lekve-telo-instruktor">John Doe</div>
            <span class="cisla">10/15</span>
        </div>
    </tr>
    """
@freezegun.freeze_time(TODAY)
def test_get_schedule_success(mock_html, mock_schedule_url):
    with patch('requests.post') as mock_post:

        # Setup mocks
        mock_response = Mock()
        mock_response.text = mock_html
        mock_post.return_value = mock_response

        # Call function
        result = get_schedule()

        # Verify results
        assert len(result) == 1
        assert result[0]["gym"] == "GoodFellas"
        assert result[0]["date"] == "10.01.2025"
        
        lesson = result[0]["lessons"][0]
        assert lesson["time"] == "18:00"
        assert lesson["name"] == "CrossFit"
        assert lesson["trainer"] == "John Doe"
        assert lesson["spots"] == "10/15"

        # Verify mock calls
        mock_post.assert_called_once_with(f"{MOCK_SCHEDULE_URL}/{TODAY}/1")
