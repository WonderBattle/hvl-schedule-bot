<img width="1920" height="1080" alt="1" src="https://github.com/user-attachments/assets/13e5b449-832c-41cb-b141-ee9d88299a4c" />
# 🤖 HVL Class Reminder Bot

> **Never miss a lecture at HVL Bergen again.**

An automated Telegram bot designed for students at **Høgskulen på Vestlandet (HVL)**. This bot fetches your personal or course schedule from **TimeEdit**, saves your preferences in a cloud database, and sends you a beautifully formatted reminder every evening.

---

## ✨ Features

* **One-Time Setup:** Just send your TimeEdit `.ics` link once; the bot remembers you forever.
* **Daily Reminders:** Automatic messages every night at **21:00** (Bergen time).
* **On-Demand Checking:** Use the `/today` or `/tomorrow` commands to see your classes instantly.
* **Update Anytime:** Schedule changed? Just use `/update` with your new link.
* **Smart Filtering:** 
  * Calculates class **duration** (e.g., 2h 45m).
  * Cleans messy TimeEdit codes into readable course names (e.g., *DAT151*).
* **Weekend Mode:** Automatically stays silent on Friday and Saturday nights.
* **Cloud Hosted:** Runs 24/7 in the cloud to ensure reminders are always sent on time.

---

## 🛠️ How it Works (The Tech Stack)

* **Language:** Python 3.12
* **Bot Framework:** `pyTelegramBotAPI` (Telebot)
* **Database:** Google Sheets API (used as a lightweight, visible NoSQL database)
* **Automation:** `schedule` library 

---

## 📖 User Guide (For Students)

### 1. Find the Bot
Search for `[@HVLSchedule_bot]` on Telegram and click **Start**.

### 2. Get your TimeEdit Link
Follow these exact steps to get your personalized schedule link:

1. Go to the [HVL TimeEdit Open Entrance](https://cloud.timeedit.net/hvl/web/open/) and click on **Alle campus**.
<img width="1920" height="1080" alt="1" src="https://github.com/user-attachments/assets/319da405-8ae0-4a07-8aad-56923a86e16f" />
<img width="1920" height="1080" alt="2" src="https://github.com/user-attachments/assets/67d22127-c222-448a-a7db-868af8b6ef60" />
3. In the **Søk** (Search) box, type your course codes.
4. Click your courses in the **Søkeresultat** (Search results) to add them to your **Mine valg** (My choices). 
5. When you have selected all your courses, click the **Vis timeplan** (Show schedule) button at the bottom.
<img width="1920" height="1080" alt="3" src="https://github.com/user-attachments/assets/7068611d-26f3-4d37-beb5-5478423825d1" />
7. On the schedule page, click the **Abonnér** button in the top right corner.
8. In the popup, change the **Tid** (Time) dropdown to select the whole semester (e.g., *Nå - 19.06.2026*) instead of the default 4 weeks.
9. Click the blue **Kopier** (Copy) button to copy your `.ics` link.
<img width="1920" height="1080" alt="4" src="https://github.com/user-attachments/assets/e9542c04-f0a7-4b40-aadd-95bfc266e66a" />

### 3. Register
Paste the link you just copied directly into the Telegram chat. The bot will confirm: `🚀 Registered!`.

### 4. Bot Commands
* `/start` - Welcome message and instructions.
* `/today` - Get a summary of today's date and classes immediately.
* `/tomorrow` - Get a summary of tomorrow's date and classes immediately.
* `/update [link]` - Change your schedule link if your courses change.

---

## 🚀 Setup Guide (For Developers)

If you want to run your own local version of this bot or contribute to the code, follow these steps:

### 1. Prerequisites

* A Telegram Bot token from **@BotFather**.
* A Google Cloud Project with **Google Sheets** and **Google Drive** APIs enabled.
* A Service Account JSON key.

### 2. Local Environment Setup

1. Clone the repo and create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

2. Duplicate the `.env.example` file, rename it to `.env`, and fill in your keys:
```text
TELEGRAM_TOKEN=your_token_here
GOOGLE_CREDS_JSON={"type": "service_account", ...}
```

3. Run the bot:
```bash
python reminder.py
```

**⚠️ IMPORTANT NOTE ON LOCAL TESTING (Error 409 Conflict):**  
Telegram only allows **one** connection to a bot at a time. If the bot is already hosted and running in the cloud (production), and you try to run `python reminder.py` locally on your machine with the same `TELEGRAM_TOKEN`, it will crash with a `409 Conflict: terminated by other getUpdates request` error. To test locally, you must temporarily pause or suspend the cloud-hosted version, or use a separate testing bot token.

---

## 👨‍💻 Author

Created by **Elena Cancho** for the students at Høgskulen på Vestlandet.  
*Connect with me on [LinkedIn](https://www.linkedin.com/in/elena-cancho-94435932a/?skipRedirect=true)*
*Other projects: [WonderBattle](https://github.com/WonderBattle)*

## 📄 License

Distributed under the MIT License. Feel free to fork and adapt for other universities!
