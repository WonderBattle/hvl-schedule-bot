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
        response.raise_for_status()
        calendar = Calendar.from_ical(response.content)
        
        tz = pytz.timezone("Europe/Oslo")
        now = datetime.now(tz)
        
        # WEEKEND MODE: 
        # If today is Friday (4) or Saturday (5), we don't look for classes for tomorrow.
        # Weekday returns 0 for Monday, 4 for Friday, 5 for Saturday.
        if now.weekday() in [4, 5]:
            print("Weekend Mode Active: No reminders sent on Friday/Saturday.")
            return "WEEKEND_MODE"

        tomorrow = (now + timedelta(days=1)).date()
        events = []
        
        for component in calendar.walk('VEVENT'):
            start_dt = component.get('dtstart').dt
            end_dt = component.get('dtend').dt
            
            # Handle timezone and time formatting
            if isinstance(start_dt, datetime):
                start_local = start_dt.astimezone(tz)
                end_local = end_dt.astimezone(tz)
                event_date = start_local.date()
                
                # Calculate duration
                duration = end_local - start_local
                hours, remainder = divmod(duration.seconds, 3600)
                minutes = remainder // 60
                dur_str = f"{hours}h {minutes}m" if minutes > 0 else f"{hours}h"
                
                time_info = f"{start_local.strftime('%H:%M')} - {end_local.strftime('%H:%M')} ({dur_str})"
            else:
                event_date = start_dt
                time_info = "All day"

            if event_date == tomorrow:
                summary = str(component.get('summary'))
                location = component.get('location', 'No room specified')
                
                # Clean the summary to find the Course Code (e.g., DAT151)
                parts = summary.split(',')
                course_title = parts[-1].replace("Emne: ", "").strip() if "Emne:" in summary else parts[0]
                
                events.append(f"📚 *{course_title}*\n⏰ {time_info}\n📍 {location}")
        
        return events
    except Exception as e:
        print(f"Error: {e}")
        return None

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, data=payload)

if __name__ == "__main__":
    result = get_tomorrow_classes()
    
    if result == "WEEKEND_MODE":
        # Do nothing, bot stays silent on weekends
        pass
    elif result is None:
        print("Failed to fetch schedule.")
    elif len(result) > 0:
        result.sort() # Sort by time
        header = "🗓 **Classes for Tomorrow:**\n\n"
        send_telegram(header + "\n\n".join(result))
    else:
        send_telegram("🎉 **No classes tomorrow!** Have fun! 🏖️")