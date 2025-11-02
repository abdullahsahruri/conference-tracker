# Setup Guide - Track Your Own Conferences

**Simple guide to set up automated conference deadline tracking for your research area.**

No need to find URLs - just add conference names and the system does everything automatically!

## What This System Does

1. **Automatically finds** conference websites by searching (you just provide conference names)
2. **Extracts deadlines** using intelligent scraping or AI
3. **Updates daily** via GitHub Actions (works 24/7, even when your computer is off)
4. **Sends notifications** when deadlines change
5. **Syncs to Google Calendar** automatically
6. **Displays on website** with color-coded deadlines

## Quick Start (5 minutes)

### Step 1: Fork This Repository

1. Go to this repository on GitHub
2. Click "Fork" button (top right)
3. You now have your own copy!

### Step 2: Add Your Conferences

**This is all you need to do!** Edit `conferences_to_track.txt` and add your conference acronyms:

```txt
# Computer Architecture
ISCA
MICRO
HPCA

# VLSI & Circuits
DAC
ICCAD
VLSI

# Add your conferences here (one per line)
YOUR_CONFERENCE
ANOTHER_CONFERENCE
```

**That's it! No URLs needed!** The system will automatically:
- Search for "ISCA 2025", "ISCA 2026", etc.
- Find the official conference website
- Extract paper submission deadlines
- Detect submission types (Regular/Abstract/Late Breaking/etc.)
- Update your database daily

### Step 3: Enable GitHub Actions

1. Go to your forked repo on GitHub
2. Click "Actions" tab
3. Click "I understand my workflows, enable them"

The system will now run automatically every day at 9 AM UTC!

### Step 4: Set Up GitHub Pages (Optional - for website)

1. Go to Settings → Pages
2. Source: Deploy from a branch
3. Branch: `main`, Folder: `/` (root)
4. Click Save

Your conference tracker website will be live at:
```
https://YOUR_USERNAME.github.io/conference-tracker/conferences.html
```

**You're done!** The system will automatically track all your conferences daily.

---

## How to Add/Remove Conferences

### Adding New Conferences

Simply edit `conferences_to_track.txt` and add the conference acronym:

```txt
# Existing conferences
ISCA
MICRO
DAC

# Add new ones here
CVPR          # Computer Vision
NeurIPS       # Machine Learning
EMNLP         # Natural Language Processing
```

Commit and push:
```bash
git add conferences_to_track.txt
git commit -m "Add CVPR, NeurIPS, EMNLP"
git push
```

The next automated run (daily at 9 AM UTC) will:
1. Search for "CVPR 2025" on the web
2. Find the official website
3. Extract the paper deadline
4. Add to your database
5. Update your website
6. Send you a notification (if configured)

### Removing Conferences

Just delete the line from `conferences_to_track.txt` and commit.

### Conference Name Tips

Use the **official acronym** as it appears in search results:

✅ **Good Examples:**
```txt
ISCA          # Not "International Symposium on Computer Architecture"
DAC           # Not "Design Automation Conference"
NeurIPS       # Not "NIPS" (old name)
CVPR          # Not "Computer Vision and Pattern Recognition"
ICCV          # Not "International Conference on Computer Vision"
```

❌ **Avoid:**
- Full conference names (too long, won't match)
- Old/deprecated acronyms
- Unofficial abbreviations

**Quick Test:** Search "{YOUR_CONFERENCE} 2025" on Google. Use whatever acronym appears in the top results.

---

## Understanding Conference List Format

The `conferences_to_track.txt` file is very simple:

```txt
# Lines starting with # are comments (ignored)

# Computer Architecture Conferences
ISCA          # International Symposium on Computer Architecture
MICRO         # IEEE/ACM International Symposium on Microarchitecture
HPCA          # International Symposium on High-Performance Computer Architecture

# VLSI Conferences
DAC           # Design Automation Conference
ICCAD         # International Conference on Computer-Aided Design

# You can organize by category using comments
# Or just list them all:
ASPLOS
ISSCC
DATE
GLSVLSI
```

**Each line = one conference to track**

The system automatically searches for:
- `{CONFERENCE} 2025` (current year)
- `{CONFERENCE} 2026` (next year)

So adding just `ISCA` will find both ISCA 2025 and ISCA 2026!

---

## Extraction Methods

### Method 1: Automatic Regex (Default - Already Working!)

**No setup needed** - works out of the box.

- ✅ Runs automatically via GitHub Actions 24/7
- ✅ Works even when your computer is off
- ✅ Completely free forever
- ✅ Fast (2-3 minutes for all conferences)
- ⚠️ Success rate: ~66% (finds 19/29 test conferences)

**Good for:** Daily automatic monitoring, no effort required

### Method 2: AI-Powered (Better Accuracy)

For higher success rate, use AI extraction:

#### Option A: Ollama (100% FREE Local AI)

**Setup (5 minutes):**

1. Install Ollama:
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

2. Start Ollama:
```bash
ollama serve
```

3. Download model:
```bash
ollama pull llama3.2
```

4. Run AI tracker:
```bash
python3 conference_tracker_ai.py
```

**Performance:**
- ✅ Success rate: ~90% (finds 26/29 conferences)
- ✅ 100% FREE forever
- ✅ Unlimited usage
- ✅ Privacy (runs on your computer)
- ⚠️ Takes ~8 minutes for all conferences
- ⚠️ Requires 4GB+ RAM

**See [OLLAMA_SETUP.md](OLLAMA_SETUP.md) for detailed instructions**

#### Option B: Claude API (Cloud AI - Costs Money)

- ✅ Success rate: ~93% (finds 27/29 conferences)
- ✅ Fastest (3 minutes)
- ❌ Costs ~$15-20/month for daily updates

**See [AI_SETUP.md](AI_SETUP.md) for setup**

**Comparison:** See [AI_COMPARISON.md](AI_COMPARISON.md) to choose the best method for you.

---

## Optional Features

### Google Calendar Sync

Automatically add deadlines to your Google Calendar.

**Quick Setup:**

1. Run the setup script:
```bash
python3 gcal_setup.py
```

2. Follow the browser OAuth flow

3. Add to GitHub Secrets:
   - Settings → Secrets → Actions
   - Add `GOOGLE_CREDS` (paste contents of `credentials.json`)
   - Add `GOOGLE_TOKEN` (paste contents of `token.json`)

**Detailed guide:** [AUTOMATION_SETUP.md](AUTOMATION_SETUP.md)

### Email Notifications

Get notified when deadlines change.

**Quick Setup:**

1. Get Gmail App Password:
   - Go to https://myaccount.google.com/apppasswords
   - Generate password

2. Add to GitHub Secrets:
   - `EMAIL_FROM`: your.email@gmail.com
   - `EMAIL_PASSWORD`: your-app-password
   - `EMAIL_TO`: recipient@email.com

**You'll receive emails when:**
- New conferences are discovered
- Deadlines change or get extended
- Conference URLs change

---

## How It Works Behind the Scenes

When you add `ISCA` to the conference list:

### 1. Discovery Phase
```
System searches DuckDuckGo for:
→ "ISCA 2025"
→ "ISCA 2026"

Finds official websites:
→ https://iscaconf.org/isca2025/
→ https://www.isca2026.org/
```

### 2. Extraction Phase
```
Downloads webpage HTML
↓
Searches for deadline keywords:
- "paper deadline"
- "submission deadline"
- "important dates"
↓
Extracts date using smart patterns:
- "February 15, 2026"
- "Feb 15, 2026"
- "2026-02-15"
- etc.
↓
Detects submission type:
- Regular Paper
- Abstract
- Late Breaking Results
- Poster/Workshop
```

### 3. Storage Phase
```
Saves to conference_database.json:
{
  "ISCA_2026": {
    "name": "ISCA 2026",
    "url": "https://isca2026.org/",
    "paper_deadline": "November 10, 2025",
    "submission_type": "Abstract",
    "conference_date": "June 13-17, 2026",
    "location": "Seoul, South Korea",
    "last_checked": "2025-11-02T09:00:00"
  }
}
```

### 4. Update Phase
```
Compares with previous data
↓
If changed:
  → Logs to deadline_changes.log
  → Sends email notification
  → Updates Google Calendar
  → Regenerates website table
```

### Why No URLs Required?

Conference websites change every year:
- ISCA 2025: `https://isca2025.github.io`
- ISCA 2026: `https://iscaconf.org/isca2026/`
- ISCA 2027: (will be different)

By searching for `{NAME} {YEAR}`, the system automatically finds the current URL each year!

---

## Example Workflows

### Workflow 1: Minimal Setup (Just Track Deadlines)

```bash
1. Fork repo
2. Edit conferences_to_track.txt (add your conferences)
3. Enable GitHub Actions
4. Done! Automatic daily updates start
```

**Result:** Database updates daily, changes logged

### Workflow 2: With Website Display

```bash
1-3. Same as above
4. Enable GitHub Pages
5. View at https://username.github.io/conference-tracker/
```

**Result:** Public website showing all conferences with color-coded deadlines

### Workflow 3: Full Setup (Everything!)

```bash
1-4. Same as above
5. Set up Google Calendar (run gcal_setup.py)
6. Add GitHub secrets (GOOGLE_CREDS, EMAIL_*, etc.)
7. Optional: Install Ollama for AI extraction
8. Optional: Run AI tracker weekly for better accuracy
```

**Result:** Full automation with calendar sync, email alerts, and high accuracy

---

## Customization

### Change Update Frequency

Edit `.github/workflows/tracker.yml`:

```yaml
on:
  schedule:
    # Daily at 9 AM UTC (default)
    - cron: '0 9 * * *'

    # Other options:
    # - cron: '0 */6 * * *'    # Every 6 hours
    # - cron: '0 9 * * 1'      # Every Monday only
    # - cron: '0 9 1,15 * *'   # 1st and 15th of month
```

### Track Only Current Year (Not Next Year)

Edit `conference_tracker.py` around line 40-41:

```python
# BEFORE (searches both years):
for year in [CURRENT_YEAR, NEXT_YEAR]:

# AFTER (only current year):
for year in [CURRENT_YEAR]:
```

### Customize Website Colors

Edit your website's CSS for deadline colors:

```css
/* Change yellow warning threshold */
.deadline-soon {
    background-color: #fff9c4 !important;
}

/* Change in JavaScript: warning period */
const oneWeek = 14 * 24 * 60 * 60 * 1000; // Change to 2 weeks
```

---

## Troubleshooting

### Problem: No conferences showing on website

**Solution:**
1. Check GitHub Actions ran successfully (Actions tab)
2. Verify `conference_database.json` exists and has data
3. Check browser console for JavaScript errors
4. Make sure GitHub Pages is enabled (Settings → Pages)

### Problem: Conference not being found

**Solution:**
1. Search "{CONFERENCE} 2025" on Google manually
2. If no results, conference might not be announced yet
3. Try different acronym (e.g., "NeurIPS" vs "NIPS")
4. Use AI extraction for better results (`python3 conference_tracker_ai.py`)

### Problem: Deadline not extracted

Some conferences are harder:
- JavaScript-heavy sites → Use AI extraction
- PDF-only deadlines → Can't extract (yet)
- Image-based dates → Can't extract (yet)
- Sites blocking scrapers → Try AI extraction

**Solution:** Run the AI tracker for better accuracy:
```bash
python3 conference_tracker_ai.py
```

### Problem: "Permission denied" in GitHub Actions

**Solution:** Add to `.github/workflows/tracker.yml`:

```yaml
jobs:
  track-conferences:
    permissions:
      contents: write  # Add this line
```

---

## File Structure Explained

```
conference-tracker/
│
├── 📝 conferences_to_track.txt          # YOUR LIST - Edit this!
│
├── 📊 Generated Files (automatic):
│   ├── conference_database.json          # Deadline database
│   ├── conference_table.html             # HTML display
│   └── deadline_changes.log              # Change history
│
├── 🤖 Main Scripts:
│   ├── conference_tracker.py             # Main tracker (regex)
│   ├── conference_tracker_ai.py          # AI tracker (Ollama)
│   ├── main_scraper.py                   # Google Calendar sync
│   └── email_notifier.py                 # Email alerts
│
├── ⚙️ Setup Scripts:
│   ├── gcal_setup.py                     # Google OAuth setup
│   └── requirements.txt                  # Python dependencies
│
├── 🔐 Credentials (not in git):
│   ├── credentials.json                  # Google OAuth client
│   └── token.json                        # Access token
│
├── 📖 Documentation:
│   ├── SETUP_GUIDE.md                    # This file!
│   ├── OLLAMA_SETUP.md                   # Free AI setup
│   ├── AI_SETUP.md                       # Claude API setup
│   ├── AI_COMPARISON.md                  # Method comparison
│   ├── QUICK_START_AI.md                 # AI quick start
│   ├── AUTOMATION_SETUP.md               # GitHub Actions guide
│   └── CLAUDE.md                         # Developer docs
│
└── 🔄 GitHub Actions:
    └── .github/workflows/tracker.yml     # Automated daily runs
```

**You only need to edit:** `conferences_to_track.txt`

---

## Sharing Conference Lists

Help others in your research area! Share your conference list:

### Machine Learning Researchers:
```txt
# Top ML Conferences
NeurIPS
ICML
ICLR
CVPR
ICCV
ECCV
```

### Natural Language Processing:
```txt
# NLP Conferences
ACL
EMNLP
NAACL
COLING
EACL
```

### Computer Systems:
```txt
# Systems Conferences
SOSP
OSDI
NSDI
EUROSYS
ATC
```

### Hardware Security:
```txt
# Security Conferences
HOST
CHES
FDTC
COSADE
```

Create a pull request or issue to share your list!

---

## FAQ

**Q: Do I need to provide conference URLs?**
A: No! Just acronyms. The system finds URLs automatically.

**Q: What if the conference website isn't up yet?**
A: The system keeps searching daily. When it goes live, it'll be found.

**Q: Can I track workshops?**
A: Yes! Add workshop acronyms the same way.

**Q: Does this work for non-CS conferences?**
A: Yes! Any conference with deadlines on their website.

**Q: How accurate is the extraction?**
A: Regex: ~66%, Ollama AI: ~90%, Claude API: ~93%

**Q: Is this free?**
A: Yes! Regex + GitHub Actions is 100% free. Ollama AI is also free.

**Q: Can I run this locally without GitHub?**
A: Yes! Just run `python3 conference_tracker.py` manually.

**Q: Can I use this for medical/biology/physics conferences?**
A: Absolutely! Works for any field.

**Q: What if a conference has multiple tracks?**
A: The system tries to find the main paper deadline. You can manually add specific tracks.

**Q: Can I get notifications on Slack/Discord instead of email?**
A: Yes, but you'll need to modify `email_notifier.py` to add webhooks.

---

## Next Steps

1. ✅ **Add your conferences** to `conferences_to_track.txt`
2. ✅ **Enable GitHub Actions** for automatic daily updates
3. ⚡ **Optional:** Set up GitHub Pages for public website
4. ⚡ **Optional:** Configure Google Calendar sync
5. ⚡ **Optional:** Install Ollama for better accuracy (90% vs 66%)
6. ⚡ **Optional:** Set up email notifications

**That's it! Your conference tracker is now running automatically! 🎓**

---

## Getting Help

- **Extraction methods:** See [AI_COMPARISON.md](AI_COMPARISON.md)
- **AI setup:** See [OLLAMA_SETUP.md](OLLAMA_SETUP.md) or [AI_SETUP.md](AI_SETUP.md)
- **Automation:** See [AUTOMATION_SETUP.md](AUTOMATION_SETUP.md)
- **Developer docs:** See [CLAUDE.md](CLAUDE.md)

Happy conference tracking! 🚀
