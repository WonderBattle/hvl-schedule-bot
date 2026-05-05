import os
import telebot
import gspread
import requests
import pytz
import schedule
import time
import threading
from flask import Flask
from threading import Thread
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

def get_date_info(tz, target="tomorrow"):
    """Generates the date string and the raw date object for today or tomorrow"""
    if target == "today":
        target_obj = datetime.now(tz)
    else:
        target_obj = (datetime.now(tz) + timedelta(days=1))
        
    day = target_obj.day
    # Adding the English suffix (1st, 2nd, 3rd, 4th...)
    if 11 <= day <= 13:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
    date_str = target_obj.strftime(f"{day}{suffix} %B")
    
    return target_obj.date(), date_str

def fetch_classes(url, target="tomorrow"):
    try:
        response = requests.get(url)
        calendar = Calendar.from_ical(response.content)
        tz = pytz.timezone("Europe/Oslo")
        
        # Use our new flexible date function!
        target_date, date_text = get_date_info(tz, target)
        
        events = []
        for component in calendar.walk('VEVENT'):
            start_dt = component.get('dtstart').dt
            end_dt = component.get('dtend').dt
            
            if isinstance(start_dt, datetime):
                start_local = start_dt.astimezone(tz)
                # Check against our target_date instead of just 'tomorrow'
                if start_local.date() == target_date:
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
        
        # Dynamically change the prefix based on what we asked for
        prefix = "TODAY" if target == "today" else "TOMORROW"
        
        if events:
            return f"📅 **{prefix}: {date_text}**\nYou have these classes:\n\n" + "\n\n".join(sorted(events))
        else:
            return f"📅 **{prefix}: {date_text}**\nYou don't have classes! Enjoy! 🎉"
            
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
    schedule.every().day.at("21:00", "Europe/Oslo").do(send_daily_reminders)
    while True:
        schedule.run_pending()
        time.sleep(30)

# --- BOT COMMANDS ---

@bot.message_handler(commands=['start'])
def welcome(message):
    welcome_text = (
        "👋 **Welcome to the HVL Schedule Bot!**\n\n"
        "Send me your TimeEdit `.ics` link to register for daily reminders at 21:00.\n\n"
        "**Commands:**\n"
        "📅 /today - Check today's classes\n"
        "📅 /tomorrow - Check tomorrow's classes\n"
        "🔄 `/update [link]` - Change your schedule link"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

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

@bot.message_handler(commands=['today'])
def manual_check_today(message):
    try:
        ws = get_sheet()
        cell = ws.find(str(message.chat.id))
        if cell:
            url = ws.cell(cell.row, 2).value
            # We pass target="today" to force it to look at today's schedule!
            msg = fetch_classes(url, target="today")
            bot.send_message(message.chat.id, msg, parse_mode="Markdown")
        else:
            bot.reply_to(message, "⚠️ You are not registered yet. Please send your .ics link first!")
    except Exception as e:
        print(f"Manual check error: {e}")

@bot.message_handler(commands=['update'])
def update_link(message):
    chat_id = str(message.chat.id)
    
    # 1. Split the message into two parts: the command and the link
    # maxsplit=1 ensures we only split at the first space
    text_parts = message.text.split(maxsplit=1) 
    
    # 2. Validation: Check if they provided a link, and if it's an .ics link
    if len(text_parts) < 2 or ".ics" not in text_parts[1]:
        bot.reply_to(
            message, 
            "⚠️ Please provide your TimeEdit link after the command.\n\n*Format:*\n`/update [your_link.ics]`", 
            parse_mode="Markdown"
        )
        return

    # 3. Extract the clean URL
    new_url = text_parts[1].strip()
    username = message.from_user.username or "User"
    
    try:
        ws = get_sheet()
        # Look for existing user
        try:
            cell = ws.find(chat_id)
            # update_cell takes (row, column, new_value). URL is in column 2!
            ws.update_cell(cell.row, 2, new_url)
            bot.reply_to(message, "✅ Your schedule has been successfully updated! Try /today to see your new classes.")
        except: 
            # If they use /update but aren't in the database yet, we register them anyway
            ws.append_row([chat_id, new_url, username])
            bot.reply_to(message, "🚀 Registered and updated! You will get daily reminders at 21:00. Try /today now!")
    except Exception as e:
        bot.reply_to(message, "❌ Error saving to database. Please try again later.")
        print(f"Update command error: {e}")

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

app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run_web_server():
    # Render provides a PORT environment variable automatically
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    # 1. Start the Web Server (to keep Render awake)
    Thread(target=run_web_server).start()
    
    # 2. Start the Scheduler (for 21:00 reminders)
    threading.Thread(target=run_scheduler, daemon=True).start()
    
    print("🚀 Bot is live and listening...")
    # 3. Start the Telegram Listener
    bot.infinity_polling()