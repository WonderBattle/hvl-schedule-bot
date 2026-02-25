# 🤖 HVL Class Reminder Bot

This bot automatically fetches your **HVL (Høgskulen på Vestlandet)** schedule from TimeEdit and sends a summary of tomorrow's classes directly to your **Telegram**. No more logging into Feide every morning!

## ✨ Features

* **Daily Alerts:** Runs every night at 21:00 (Bergen time).
* **Detailed Info:** Shows class name, start/end times, duration, and room location.
* **Weekend Mode:** Stays quiet on Friday and Saturday nights.
* **Smart Cleaning:** Removes messy TimeEdit codes to show only the course name (e.g., *DAT151*).
* **Free & Automatic:** Hosted on GitHub Actions—no server required.

---

## 🚀 Setup Instructions (Step-by-Step)

### 1. Create your Telegram Bot

1. Open Telegram and search for **@BotFather**.
2. Send `/newbot`, follow the instructions, and copy the **API Token**.
3. Search for **@userinfobot** and send any message to get your **Chat ID**.
4. **Important:** Send a message to your new bot (press "Start") so it has permission to talk to you.

### 2. Get your TimeEdit Link

1. Go to the [HVL TimeEdit Public Portal](https://www.google.com/search?q=https://cloud.timeedit.net/hvl/web/open/).
2. Search for your courses (Emnenavn/Emnekode) and click **Vis timeplan**.
3. Click **Abbonér** in the top right corner.
4. Set the time range to "Hele semesteret" or "Rulling 4 uker".
5. **Copy the link** that ends in `.ics`.

`[Insert Screenshot of the TimeEdit 'Abbonér' window here]`

### 3. Fork this Repository

1. Click the **Fork** button at the top right of this page to create your own copy.
2. In **your** new repository, go to **Settings** > **Secrets and variables** > **Actions**.

`[Insert Screenshot of GitHub Secrets menu here]`

### 4. Add your Secrets

Add the following three **Repository Secrets**:

* `TIMEEDIT_URL`: Your `.ics` link from Step 2.
* `TELEGRAM_TOKEN`: Your API Token from BotFather.
* `TELEGRAM_CHAT_ID`: Your personal ID from userinfobot.

---

## 🛠 Manual Test

Want to see it work right now?

1. Go to the **Actions** tab in your repository.
2. Select **Send Daily Reminder**.
3. Click **Run workflow** > **Run workflow**.

`[Insert Screenshot of the 'Run workflow' button here]`

---

## 🤝 Contributing

If you have ideas for new features, feel free to open a Pull Request!

---
