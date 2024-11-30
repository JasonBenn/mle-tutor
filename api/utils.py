import asyncio
from functools import wraps
import json
from datetime import datetime
from datetime import datetime, timedelta
from icalendar import Calendar
import requests
import pytz
import requests


def get_open_mics(start_date=None, end_date=None, city="San Francisco"):
    # Set default date range to next 7 days if not specified
    pacific = pytz.timezone("America/Los_Angeles")
    now = datetime.now(pacific)

    if start_date is None:
        start_date = now
    if end_date is None:
        end_date = now + timedelta(days=7)

    # Convert string dates to datetime if needed
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=pacific)
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=pacific)

    # Fetch calendar data
    url = "https://calendar.google.com/calendar/ical/sfbaycomedycalendar%40gmail.com/public/basic.ics"
    response = requests.get(url)
    cal = Calendar.from_ical(response.text)

    # Process events
    events = []

    for event in cal.walk("VEVENT"):
        # Parse start time
        start = event.get("dtstart").dt
        if isinstance(start, datetime):
            start = start.astimezone(pacific)
        else:
            # If it's a date without time, convert to datetime at midnight
            start = pacific.localize(datetime.combine(start, datetime.min.time()))

        # Skip if outside date range
        if start < start_date or start > end_date:
            continue

        location = str(event.get("location", ""))

        # Skip if not in specified city
        if not location or city.lower() not in location.lower():
            continue

        title = str(event.get("summary", "No Title"))
        description = str(event.get("description", ""))

        events.append(
            {"title": title, "datetime": start.strftime("%Y-%m-%d %I:%M %p %Z"), "venue": location, "description": description}
        )

    # Sort by date
    events.sort(key=lambda x: x["datetime"])

    # Create structured output
    llm_friendly_output = {
        "metadata": {
            "total_events": len(events),
            "city": city,
            "date_range": {"start": start_date.strftime("%Y-%m-%d"), "end": end_date.strftime("%Y-%m-%d")},
            "generated_at": now.strftime("%Y-%m-%d %I:%M %p %Z"),
        },
        "events": events,
    }

    return json.dumps(llm_friendly_output, indent=2)


def async_route(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapped
