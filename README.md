# Fitness Schedule App

A Python application that aggregates fitness class schedules from various gyms and automatically syncs them with Google Calendar.

## Features

- Fetches class schedules from multiple fitness centers
- Syncs class schedules to Google Calendar
- Creates a browsable HTML timetable
- Supports multiple gym providers:
  - GoodFellas
  - Bevondrsfull
  - ImFit
  - YogaHolick
  - Siddha Yoga
  - Moony Yoga
  - MyFitness

## Setup

1. Clone the repository
2. Create a virtual environment and activate it:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Unix/macOS
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.sample` to `.env` and fill in your configuration
5. Set up Google Calendar API credentials:
   - Place your `credentials.json` in the root directory

## Usage

Run the main script to fetch schedules and sync with Google Calendar:
```bash
python run.py
```
Use with care, don't overload the gyms with requests! :pray:

## Requirements

- Python 3.x
- Google Calendar API credentials
- Dependencies listed in `requirements.txt`

## Project Structure

- `run.py` - Main application entry point
- `gcal_updater.py` - Google Calendar integration
- `schedules/` - Individual gym schedule scrapers
- `tests/` - Test suite
- `helpers.py` - Utility functions

## Environment Variables

Create a `.env` file with the following variables:
- Google Calendar configuration
- API credentials
- Other configuration parameters

## License

This project is proprietary and confidential.