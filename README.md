# 🤖 HVL Class Reminder Bot

> **Never miss a lecture at HVL Bergen again.**

An automated Telegram bot designed for students at **Høgskulen på Vestlandet (HVL)**. This bot fetches your personal or course schedule from **TimeEdit**, saves your preferences in a cloud database, and sends you a beautifully formatted reminder every evening.

---

## ✨ Features

* **One-Time Setup:** Just send your TimeEdit `.ics` link once; the bot remembers you forever.
* **Daily Reminders:** Automatic messages every night at **21:00** (Bergen time).
* **On-Demand Checking:** Use the `/tomorrow` command to see your next classes instantly.
* **Smart Filtering:** * Calculates class **duration** (e.g., 2h 45m).
* Cleans messy TimeEdit codes into readable course names (e.g., *DAT151*).
* **Weekend Mode:** Automatically stays silent on Friday and Saturday nights.


* **Cloud Hosted:** Runs 24/7 on Render.com with a custom heartbeat to prevent sleeping.

---

## 🛠️ How it Works (The Tech Stack)

* **Language:** Python 3.12
* **Bot Framework:** `pyTelegramBotAPI` (Telebot)
* **Database:** Google Sheets API (used as a lightweight, visible NoSQL database)
* **Hosting:** Render.com (Web Service)
* **Automation:** `schedule` library + `cron-job.org` (to keep the service awake)

---

## 📖 User Guide (For Students)

1. **Find the Bot:** Search for `[@HVLSchedule_bot]` on Telegram.
2. **Get your Link:**
* Go to [HVL TimeEdit](https://www.google.com/search?q=https://cloud.timeedit.net/hvl/web/open/).
* Search for your courses and click **Vis timeplan**.
* Click **Abbonér** (top right) and copy the `.ics` link.


3. **Register:** Paste the link into the Telegram chat. The bot will confirm: `🚀 Registered!`.
4. **Commands:**
* `/start`: Welcome message and instructions.
* `/tomorrow`: Get a summary of tomorrow's date and classes immediately.



`[Insert Screenshot of the bot replying with a schedule for February 26th]`

---

## 🚀 Setup Guide (For Developers)

If you want to host your own version of this bot, follow these steps:

### 1. Prerequisites

* A Telegram Bot token from **@BotFather**.
* A Google Cloud Project with **Google Sheets** and **Google Drive** APIs enabled.
* A Service Account JSON key.

### 2. Local Environment

1. Clone the repo and create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt

```


2. Create a `.env` file:
```text
TELEGRAM_TOKEN=your_token_here

```


3. Place your Google JSON key in the root folder.

### 3. Deployment (Render)

1. Fork this repository.
2. Create a new **Web Service** on Render connected to your fork.
3. Add the following **Environment Variables** in the Render dashboard:
* `TELEGRAM_TOKEN`: Your bot token.
* `GOOGLE_CREDS_JSON`: The **entire contents** of your Service Account JSON file.


4. Set up a pinger on `cron-job.org` to hit your Render URL every 10 minutes to prevent the Free Tier from sleeping.


---

## 📄 License

Distributed under the MIT License. Feel free to fork and adapt for other universities!

---
