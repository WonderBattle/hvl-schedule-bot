import os
import telebot
import gspread
import requests
import pytz
import schedule
import time
import threading
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials
from icalendar import Calendar
from datetime import datetime, timedelta

# Load environment variables from .env
load_dotenv()

# 1. Setup Google Sheets
JSON_FILE = 'hvl-bot-project-8e665288849f.json'
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Recreate the JSON credentials file from Environment Variable
if not os.path.exists(JSON_FILE):
    with open(JSON_FILE, "w") as f:
        f.write(os.getenv("GOOGLE_CREDS_JSON"))

def get_sheet():
    creds = ServiceAccountCredentials.from_json_keyfile_name(JSON_FILE, scope)
    client = gspread.authorize(creds)
    # This grabs the very first tab of your 'HVL_Bot_Data' sheet
    return client.open("HVL_Bot_Data").get_worksheet(0)

# 2. Setup Bot
TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)

# --- CORE LOGIC ---

def get_tomorrow_info(tz):
    tomorrow_obj = (datetime.now(tz) + timedelta(days=1))
    day = tomorrow_obj.day
    # Adding the English suffix (1st, 2nd, 3rd, 4th...)
    if 11 <= day <= 13:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
    date_str = tomorrow_obj.strftime(f"{day}{suffix} %B")
    return tomorrow_obj.date(), date_str

def fetch_classes(url):
    try:
        response = requests.get(url)
        calendar = Calendar.from_ical(response.content)
        tz = pytz.timezone("Europe/Oslo")
        tomorrow_date, date_text = get_tomorrow_info(tz)
        
        events = []
        for component in calendar.walk('VEVENT'):
            start_dt = component.get('dtstart').dt
            end_dt = component.get('dtend').dt
            
            if isinstance(start_dt, datetime):
                start_local = start_dt.astimezone(tz)
                if start_local.date() == tomorrow_date:
                    end_local = end_dt.astimezone(tz)
                    duration = end_local - start_local
                    hours, remainder = divmod(duration.seconds, 3600)
                    minutes = remainder // 60
                    dur_str = f"{hours}h {minutes}m" if minutes > 0 else f"{hours}h"
                    
                    summary = str(component.get('summary'))
                    parts = summary.split(',')
                    course = parts[-1].replace("Emne: ", "").strip() if "Emne:" in summary else parts[0]
                    
                    location = component.get('location', 'No room specified')
                    time_info = f"{start_local.strftime('%H:%M')} - {end_local.strftime('%H:%M')} ({dur_str})"
                    events.append(f"📚 *{course}*\n⏰ {time_info}\n📍 {location}")
        
        if events:
            return f"📅 **TOMORROW: {date_text}**\nYou have these classes:\n\n" + "\n\n".join(sorted(events))
        else:
            return f"📅 **TOMORROW: {date_text}**\nYou don't have classes! Enjoy! 🎉"
            
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return "❌ Error: Could not retrieve your schedule."

# --- BACKGROUND TASKS ---

def send_daily_reminders():
    print(f"🔔 [{datetime.now()}] Running programmed broadcast...")
    try:
        ws = get_sheet()
        users = ws.get_all_records()
        tz = pytz.timezone("Europe/Oslo")
        
        if datetime.now(tz).weekday() in [4, 5]: # Friday/Saturday night
            return

        for user in users:
            msg = fetch_classes(user['timeedit_url'])
            bot.send_message(user['chat_id'], msg, parse_mode="Markdown")
    except Exception as e:
        print(f"Broadcast Error: {e}")

def run_scheduler():
    schedule.every().day.at("21:00").do(send_daily_reminders)
    while True:
        schedule.run_pending()
        time.sleep(30)

# --- BOT COMMANDS ---

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "👋 Welcome! Send me your TimeEdit .ics link to get reminders.\nUse /tomorrow anytime to check your next classes.")

@bot.message_handler(commands=['tomorrow'])
def manual_check(message):
    try:
        ws = get_sheet()
        cell = ws.find(str(message.chat.id))
        if cell:
            url = ws.cell(cell.row, 2).value
            msg = fetch_classes(url)
            bot.send_message(message.chat.id, msg, parse_mode="Markdown")
        else:
            bot.reply_to(message, "⚠️ You are not registered yet. Please send your .ics link first!")
    except Exception as e:
        print(f"Manual check error: {e}")

@bot.message_handler(func=lambda m: ".ics" in m.text)
def save_user(message):
    chat_id = str(message.chat.id)
    url = m_url = message.text.strip()
    username = message.from_user.username or "User"
    
    try:
        ws = get_sheet()
        # Look for existing user
        try:
            cell = ws.find(chat_id)
            ws.update_cell(cell.row, 2, m_url)
            bot.reply_to(message, "✅ Schedule updated!")
        except: # gspread version-agnostic "not found" handling
            ws.append_row([chat_id, m_url, username])
            bot.reply_to(message, "🚀 Registered! You will get daily reminders at 21:00. Try /tomorrow now!")
    except Exception as e:
        bot.reply_to(message, "❌ Error saving to database. Check if the Robot has permissions.")
        print(f"DEBUG ERROR: {e}")

if __name__ == "__main__":
    threading.Thread(target=run_scheduler, daemon=True).start()
    print("🚀 Bot is live and listening...")
    bot.infinity_polling()