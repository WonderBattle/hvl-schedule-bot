import os
import requests
from icalendar import Calendar
from datetime import datetime, timedelta
import pytz

# Load settings from GitHub Secrets
ICAL_URL = os.getenv("TIMEEDIT_URL")
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def get_tomorrow_classes():
    try:
        response = requests.get(ICAL_URL)
        calendar = Calendar.from_ical(response.content)
        
        # Set timezone to Norway
        tz = pytz.timezone("Europe/Oslo")
        tomorrow = (datetime.now(tz) + timedelta(days=1)).date()
        
        events = []
        for component in calendar.walk('VEVENT'):
            start_dt = component.get('dtstart').dt
            
            # Handle both datetime and date-only objects
            if isinstance(start_dt, datetime):
                event_date = start_dt.astimezone(tz).date()
                event_time = start_dt.astimezone(tz).strftime("%H:%M")
            else:
                event_date = start_dt
                event_time = "All day"

            if event_date == tomorrow:
                summary = component.get('summary')
                location = component.get('location', 'No room specified')
                events.append(f"⏰ *{event_time}*\n📚 {summary}\n📍 {location}")
        
        return events
    except Exception as e:
        return [f"Error fetching schedule: {e}"]

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, data=data)

if __name__ == "__main__":
    classes = get_tomorrow_classes()
    if classes:
        header = "🗓 **Classes for Tomorrow:**\n\n"
        send_telegram(header + "\n\n".join(classes))
    else:
        # Optional: send a message saying "No classes tomorrow"
        print("No classes found for tomorrow.")