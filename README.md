# Fitness Schedule App

A Python application that aggregates fitness class schedules from various gyms and automatically syncs them with Google Calendar.

## Features

- Fetches class schedules from multiple fitness centers
- Syncs class schedules to Google Calendar

It supports multiple gym providers:
  - GoodFellas (inrs.cz)
  - Bevondrsfull (clubspire)
  - ImFit
  - YogaHolick (reenio)
  - Siddha Yoga (isportsystem)
  - MyFitness (supersaas)
  - Mood Yoga (isportsystem)
  - Yoga Karlin (isportsystem)

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

## Environment Variables

Create a `.env` file with envvars you need including those stated in the [.env.sample](.env.sample) file.
