# Conference Deadline Tracker - Complete Setup Guide

## 🎯 What This System Does

This is an **intelligent conference deadline discovery and monitoring system** that:

1. **🔍 Automatically discovers conferences** by searching the web (e.g., "ISCA 2026", "DAC 2026")
2. **📅 Extracts deadlines** from any conference website intelligently
3. **💾 Maintains a local database** with change history
4. **🔔 Detects deadline changes** daily and sends email alerts
5. **📊 Generates HTML table** (like Chalmers VLSI conference list)
6. **🗓️ Updates Google Calendar** automatically
7. **🤖 Runs automatically** via GitHub Actions daily

### Key Advantages:
- **Handles changing URLs**: Finds ISCA 2026 even if URL changes next year
- **Change detection**: Alerts you when deadlines are postponed/updated
- **No manual maintenance**: Unlike Chalmers, this is fully automated
- **Multiple sources**: Web search + Chalmers aggregator as fallback

---

## 📋 Prerequisites

1. **Python 3.10+**
2. **Google Account** (for Calendar API)
3. **Email Account** (Gmail recommended for notifications)
4. **GitHub Account** (for automation)

---

## 🚀 Quick Start

### Step 1: Clone/Setup Repository

```bash
cd /path/to/conferences
git init
git add .
git commit -m "Initial commit"
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Google Calendar Setup (One-Time)

1. Get Google OAuth credentials:
   - Go to https://console.cloud.google.com/
   - Create project → Enable Google Calendar API
   - Create OAuth 2.0 Client ID (Desktop app)
   - Download as `credentials.json`

2. Run OAuth setup:
```bash
python gcal_setup.py
```
   - This opens your browser for authorization
   - Generates `token.json`

### Step 4: Configure Conferences to Track

Edit `conferences_to_track.txt`:
```
# Add conference acronyms (one per line)
ISCA
MICRO
DAC
DATE
GLSVLSI
ISCAS
# Add more...
```

### Step 5: Test Locally

```bash
python conference_tracker.py
```

This will:
- Search for each conference
- Extract deadlines
- Create `conference_database.json`
- Generate `conference_table.html` (open in browser!)

---

## 📧 Email Notifications Setup

### For Gmail Users:

1. **Enable 2-Step Verification** on your Google Account

2. **Generate App Password**:
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and your device
   - Copy the 16-character password

3. **Set Environment Variables** (Linux/Mac):
```bash
export EMAIL_FROM='your.email@gmail.com'
export EMAIL_PASSWORD='your-app-password'
export EMAIL_TO='recipient@email.com'  # Optional
```

4. **Test Email**:
```bash
python email_notifier.py
```

### For Other Email Providers:

Edit `email_notifier.py` and change:
```python
EmailNotifier(smtp_server='smtp.yourprovider.com', smtp_port=587)
```

---

## ⚙️ GitHub Actions Automation

### Step 1: Push to GitHub

```bash
git remote add origin https://github.com/YOUR_USERNAME/conference-tracker.git
git branch -M main
git push -u origin main
```

### Step 2: Add GitHub Secrets

Go to: **Settings → Secrets and variables → Actions**

Create these secrets:

1. **GOOGLE_CREDS**
   ```bash
   cat credentials.json
   ```
   Copy entire output → New secret

2. **GOOGLE_TOKEN**
   ```bash
   cat token.json
   ```
   Copy entire output → New secret

3. **EMAIL_FROM**
   - Value: `your.email@gmail.com`

4. **EMAIL_PASSWORD**
   - Value: Your Gmail app password

5. **EMAIL_TO** (optional)
   - Value: Recipient email (defaults to EMAIL_FROM)

### Step 3: Enable GitHub Actions

The workflow runs automatically daily at 9 AM UTC!

**Manual trigger**: Actions tab → "Conference Deadline Tracker" → "Run workflow"

---

## 📊 Viewing Your Conference Table

### Option 1: Local HTML File

Open `conference_table.html` in your browser after running tracker.

### Option 2: GitHub Pages (Public)

The workflow automatically deploys to GitHub Pages!

1. Go to **Settings → Pages**
2. Source: Deploy from a branch
3. Branch: `gh-pages` → `/ (root)` → Save
4. Your table will be at: `https://YOUR_USERNAME.github.io/conference-tracker/conference_table.html`

---

## 🔄 How It Works Daily

```
9:00 AM UTC (Daily)
        ↓
┌───────────────────────────────┐
│  GitHub Actions Triggers      │
└───────────────────────────────┘
        ↓
┌───────────────────────────────┐
│  conference_tracker.py        │
│  • Searches for conferences   │
│  • Extracts deadlines          │
│  • Detects changes             │
│  • Updates database            │
│  • Generates HTML table        │
└───────────────────────────────┘
        ↓
┌───────────────────────────────┐
│  Email Notifications          │
│  Sent if changes detected      │
└───────────────────────────────┘
        ↓
┌───────────────────────────────┐
│  main_scraper.py              │
│  • Updates Google Calendar    │
│  • Adds new deadlines          │
└───────────────────────────────┘
        ↓
┌───────────────────────────────┐
│  Commits & Pushes Updates     │
│  • Updated database            │
│  • New HTML table              │
│  • Change log                  │
└───────────────────────────────┘
```

---

## 📁 File Structure

```
conference-tracker/
│
├── conference_tracker.py       # Intelligent discovery system
├── main_scraper.py             # Google Calendar integration
├── gcal_setup.py               # One-time OAuth setup
├── email_notifier.py           # Email alert system
├── official_sources.py         # ACM/IEEE scrapers (optional)
│
├── conferences_to_track.txt    # Your conference list
├── conference_database.json    # Auto-updated database
├── conference_table.html       # Generated HTML table
├── deadline_changes.log        # Change history
│
├── credentials.json            # Google OAuth (NOT in git)
├── token.json                  # Google token (NOT in git)
│
├── requirements.txt            # Python dependencies
├── .gitignore                  # Protects secrets
│
└── .github/
    └── workflows/
        ├── main.yml            # Legacy calendar sync
        └── tracker.yml         # New intelligent tracker
```

---

## 🔧 Customization

### Add More Conferences

Edit `conferences_to_track.txt`:
```
# Architecture
ISCA
MICRO
HPCA

# VLSI
DAC
ICCAD
DATE
```

### Change Run Schedule

Edit `.github/workflows/tracker.yml`:
```yaml
schedule:
  - cron: '0 9 * * *'   # Daily at 9 AM UTC
  - cron: '0 21 * * *'  # Add: Daily at 9 PM UTC
```

### Customize Email Template

Edit `email_notifier.py` → `notify_changes()` function

### Add Custom Conference Sources

Edit `conference_tracker.py` → add new scraping functions

---

## 🐛 Troubleshooting

### "No deadlines found"

- Conference website may have changed structure
- Check `conference_database.json` for URL
- Manually verify deadline is visible on the page

### Email not sending

```bash
# Test configuration
python email_notifier.py

# Check environment variables
echo $EMAIL_FROM
echo $EMAIL_PASSWORD
```

### GitHub Actions failing

- Check Actions logs for errors
- Verify all secrets are set correctly
- Ensure credentials.json and token.json are valid

### Calendar not updating

```bash
# Test locally
python main_scraper.py

# Regenerate token if expired
python gcal_setup.py
```

---

## 📈 Advanced Features

### Monitor Specific Conference Patterns

```python
# In conference_tracker.py, modify search:
def search_conference(conference_name, year):
    # Add specific domain filtering
    query = f"{conference_name} {year} site:iscaconf.org OR site:dac.com"
```

### Add Slack Notifications

Install `slack-sdk` and add to `email_notifier.py`:
```python
from slack_sdk import WebClient

def notify_slack(self, changes):
    client = WebClient(token=os.environ['SLACK_TOKEN'])
    # Send to Slack channel
```

### Export to CSV

```python
# Add to conference_tracker.py
import csv

def export_to_csv(database):
    with open('conferences.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['name', 'url', 'paper_deadline'])
        writer.writeheader()
        for conf in database.values():
            writer.writerow(conf)
```

---

## 📝 What Gets Tracked

For each conference:
- **Name**: e.g., "ISCA 2026"
- **URL**: Official website
- **Paper Deadline**: Submission deadline
- **Last Checked**: Timestamp
- **Full Name**: Complete conference title
- **Change History**: Logged in `deadline_changes.log`

---

## 🎓 Example Output

### HTML Table
![Conference Table Example](https://i.imgur.com/example.png)

### Email Notification
```
🔔 Conference Deadlines Update - 3 changes detected

🆕 NEW: ISCA 2026
   Deadline: November 10, 2025

🔄 UPDATED: DAC 2026
   November 15, 2025 → November 22, 2025 (EXTENDED!)

🔄 UPDATED: GLSVLSI 2026
   March 10, 2025 → March 17, 2025
```

### Google Calendar
All deadlines appear as all-day events with conference name!

---

## 🤝 Contributing

Feel free to:
- Add more conference acronyms
- Improve deadline extraction patterns
- Add new official sources (ACM, IEEE, WikiCFP)
- Submit PRs!

---

## 📄 License

MIT License - Free to use and modify!

---

## 🆘 Support

Issues? Questions?
1. Check the troubleshooting section above
2. Review GitHub Actions logs
3. Test components locally first
4. Check that all secrets are configured

**Happy conference tracking! 🎉**
