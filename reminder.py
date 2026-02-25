import os
import telebot
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 1. Setup Google Sheets
# Use the EXACT name of your downloaded JSON file here
JSON_FILE = 'hvl-bot-project-8e665288849f.json'

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(JSON_FILE, scope)
client = gspread.authorize(creds)
# Make sure this matches the name of your Google Sheet exactly
sheet = client.open("HVL_Bot_Data").sheet1

# 2. Setup Bot
# Use your Telegram Token from BotFather
TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "👋 Hi! I'm your HVL Class Reminder Bot.\n\n"
        "To get started, please paste your TimeEdit iCal link here.\n"
        "It should look like: https://cloud.timeedit.net/.../....ics"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: ".ics" in message.text)
def handle_link(message):
    chat_id = str(message.chat.id)
    url = message.text.strip()
    username = message.from_user.username or "Unknown"

    try:
        # Check if user already exists in the sheet
        cell = sheet.find(chat_id)
        if cell:
            # Update existing user's link (Column B is index 2)
            sheet.update_cell(cell.row, 2, url)
            bot.reply_to(message, "✅ Your link has been updated!")
        else:
            # Add new user: [chat_id, url, username]
            sheet.append_row([chat_id, url, username])
            bot.reply_to(message, "🚀 Success! You are now registered. I will send you reminders every evening.")
    except Exception as e:
        bot.reply_to(message, "❌ Oops! Something went wrong while saving your data.")
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Bot is listening for messages...")
    bot.infinity_polling()