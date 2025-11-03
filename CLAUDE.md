# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an **automated conference deadline tracking system for Computer Architecture and VLSI conferences** that:
1. Discovers conference websites through web search
2. Extracts paper submission deadlines using Ollama AI (90% accuracy, 100% FREE)
3. Validates deadline years to prevent duplicates
4. Maintains a local JSON database of conferences
5. Detects deadline changes daily via GitHub Actions
6. Sends email notifications for changes
7. Pushes updated data to a separate website repository

**Target Conferences**: Tracks major computer architecture, VLSI, circuits, design automation, and hardware security conferences including ISCA, MICRO, HPCA, ASPLOS, ISSCC, DAC, DATE, ICCAD, FPGA, and others listed in `conferences_to_track.txt`.

## Core Architecture

### Two-Stage Pipeline

The system runs daily in this order (orchestrated by `.github/workflows/tracker.yml`):

```
conference_tracker.py → Git commit & push
```

1. **Stage 1: conference_tracker.py** - Discovery & Change Detection
   - Reads `conferences_to_track.txt` (conference acronyms like "ISCA", "DAC")
   - For each conference, searches DuckDuckGo for "{NAME} {YEAR}" (current + next year)
   - Uses Ollama AI to extract deadlines from discovered URLs:
     - Sends website content to local Ollama instance
     - AI understands context and extracts correct deadlines
     - Detects submission types (Regular/Late Breaking/Poster/Workshop/Abstract)
     - **Validates deadline year matches expected conference year**
   - Dual validation prevents duplicates:
     - AI prompt instructs model to check year before extraction
     - Python safety net validates year after extraction
   - Compares with `conference_database.json` to detect changes
   - Logs changes to `deadline_changes.log`
   - Generates `conference_table.html` for viewing
   - Sends email notifications via `email_notifier.py` (if configured)

2. **Stage 2: Git Operations**
   - Commits updated files to this repository
   - Clones `abdullahsahruri/abdullahsahruri.github.io`
   - Copies `conference_database.json` to site's `assets/` folder
   - Pushes to website repository (using `SITE_GITHUB_TOKEN`)

### Key Data Flow

```
conferences_to_track.txt
    ↓ (read by)
conference_tracker.py + Ollama AI
    ↓ (validates year, writes)
conference_database.json + conference_table.html + deadline_changes.log
    ↓ (commits)
Git Commit → Website Repo Push
```

## Essential Commands

### Local Development & Testing

```bash
# Install and start Ollama (one-time)
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve  # Keep running in background

# Download AI model (one-time, ~2GB)
ollama pull llama3.1

# Install Python dependencies
pip install -r requirements.txt

# Test conference discovery and AI extraction
python conference_tracker.py

# Test AI extraction module directly
python ai_conference_extractor_ollama.py

# Test email notifications (requires EMAIL_* env vars)
python email_notifier.py
```

### Testing Individual Components

```bash
# Test only the AI-powered tracking system
python conference_tracker.py

# Check what conferences are being tracked
cat conferences_to_track.txt

# View recent deadline changes
cat deadline_changes.log

# Check database contents
cat conference_database.json | python -m json.tool
```

## Critical Files

### Configuration Files
- **conferences_to_track.txt** - List of conference acronyms to monitor (one per line)
- **credentials.json** - Google OAuth client credentials (DO NOT COMMIT)
- **token.json** - Google Calendar API token (DO NOT COMMIT)

### Data Files (Generated)
- **conference_database.json** - Source of truth for all tracked conferences
- **conference_table.html** - Human-readable HTML table
- **deadline_changes.log** - Timestamped change history

### Core Scripts
- **conference_tracker.py** - Main discovery & monitoring logic with AI extraction
- **ai_conference_extractor_ollama.py** - Ollama AI extraction module
- **date_normalizer.py** - Normalizes dates to consistent format
- **email_notifier.py** - Email notification system

## AI Extraction Strategy

The system uses **Ollama AI (100% FREE)** for intelligent deadline extraction:

### How It Works

1. **Website Discovery**
   - Searches DuckDuckGo for "{CONFERENCE} {YEAR} conference computer architecture"
   - Finds official conference website
   - Downloads HTML content

2. **AI Extraction**
   - Sends website text to local Ollama instance
   - AI prompt includes:
     - Conference name and expected year
     - Instructions to extract paper deadline (not notification dates)
     - **Year validation rules** to prevent duplicates
   - AI extracts:
     - Paper deadline with correct year
     - Submission type (Regular/Abstract/Late Breaking/Poster)
     - Conference dates and location

3. **Dual Year Validation** (Prevents Duplicates)
   - **AI Validation**: Prompt instructs model to check deadline year matches expected year
     - Example: Searching for "GLSVLSI 2026" should have 2025-2026 deadline, not 2024-2025
     - If year mismatch detected, AI returns "TBD"
   - **Python Safety Net**: After extraction, validates `abs(deadline_year - expected_year) <= 1`
     - Rejects entries like GLSVLSI_2026 with March 2025 deadline
     - Prevents duplicates in database

4. **Date Normalization**
   - Normalizes all formats to "Month Day, Year"
   - Handles formats: "Feb 15, 2026", "2026-02-15", "Fri 7 Nov 2025", "April 11, 2025 at 11:59 PM EDT"

**Accuracy**: 90% success rate (finds 26/29 test conferences correctly)

## GitHub Actions Workflow

Runs **daily at 9:00 AM UTC** (`.github/workflows/tracker.yml`):

### Required GitHub Secrets
- **EMAIL_FROM** - Sender email (Gmail recommended, optional)
- **EMAIL_PASSWORD** - App password for email notifications (optional)
- **EMAIL_TO** - Recipient email (optional)
- **SITE_GITHUB_TOKEN** - Personal Access Token for pushing to website repo

**Note**: GitHub Actions cannot run Ollama (requires local installation). The tracker runs on your local machine, and GitHub Actions only handles the git operations.

### Workflow Steps
1. Checkout code
2. Install Python dependencies
3. Run `conference_tracker.py` (discovery with AI extraction)
4. Commit changes to tracker repo
5. Push `conference_database.json` to website repo

## Adding New Conferences

Simply add the conference acronym to `conferences_to_track.txt`:

```
ISCA
DAC
MICRO
YOUR_NEW_CONF  # Add here
```

The system will automatically:
- Search for "{NAME} {CURRENT_YEAR}" and "{NAME} {NEXT_YEAR}"
- Discover the conference website
- Use AI to extract deadlines with year validation
- Prevent duplicates (won't create CONF_2026 with 2025 deadline)
- Handle changing URLs over time

**Current Categories in `conferences_to_track.txt`**:
- Computer Architecture: ISCA, MICRO, HPCA, ASPLOS
- VLSI & Circuits: ISSCC, VLSI, ICCAD, DAC, DATE, ASPDAC, ISLPED, GLSVLSI, CICC, ESSCIRC
- Design Automation: ISCAS, ICCD, ISPD
- FPGA & Reconfigurable Computing: FPGA, FCCM
- Testing & Verification: ITC, VTS, ATS
- Systems & Architecture: SOSP, OSDI, EUROSYS
- Hardware Security: HOST, CHES
- Emerging Technologies: HOTCHIPS

## Modifying Scraping Logic

### To Support New Website Formats

1. **Inspect the target site's HTML** using browser DevTools
2. **Add detection logic** in `conference_tracker.py::extract_conference_info()`
3. **Consider adding date patterns** if the site uses unusual formats
4. **Test locally** before pushing: `python conference_tracker.py`

### To Add a Dedicated Scraper (like main_scraper.py)

For sites with very specific formats (like ISCA), create a custom function in `main_scraper.py`:
- See `scrape_isca_style()` or `scrape_conference_aggregator_table()` as examples
- Add URL detection in `process_conference_site()`
- Add the URL to `CONFERENCE_SITES` list

## Important Behaviors

### Duplicate Prevention
- **Calendar**: `event_exists()` checks for same title + date before creating
- **Database**: Conference key is `{NAME}_{YEAR}`, naturally prevents duplicates
- **Git**: Commits only if files changed (`git diff --quiet` check)

### URL Handling
- Conferences may change URLs year-to-year (e.g., isca2026 → isca2027)
- Search-based discovery handles this automatically
- URL changes are logged in `deadline_changes.log`

### Deadline Change Detection
- Compares `old_data` vs `new_data` in `detect_changes()`
- Tracks: new conferences, deadline changes, URL changes
- Logs all changes with timestamps

### Submission Type Detection
- Scans context around deadline for keywords
- Types: "Regular Paper", "Late Breaking Results", "Poster", "Short Paper", "Workshop/WIP", "Abstract"
- Stored in `submission_type` field in database

## Email Notifications

Configured via environment variables:
```bash
export EMAIL_FROM='your.email@gmail.com'
export EMAIL_PASSWORD='your-app-password'  # Get from Google App Passwords
export EMAIL_TO='recipient@email.com'
```

**Gmail Users**: Must use App Password, not regular password
- Enable 2-Step Verification
- Generate App Password: https://myaccount.google.com/apppasswords

Notifications sent for:
- New conferences discovered
- Deadline changes
- URL changes

## Integration with Main Website

The workflow pushes to `abdullahsahruri/abdullahsahruri.github.io`:
```bash
cp conference_database.json site/assets/
cd site && git push
```

This allows the main website to consume `assets/conference_database.json` for display at https://abdullahsahruri.github.io/conferences/

### Known Issue: Conference Table Not Displaying

**Problem**: The webpage at https://abdullahsahruri.github.io/conferences/ shows "Loading conference data..." indefinitely, even though `assets/conference_database.json` exists and is accessible.

**Possible Causes**:
1. **JavaScript execution failure** - Check browser console for errors
2. **CORS/fetch issues** - The fetch to `/assets/conference_database.json` may fail silently
3. **JSON parsing error** - Malformed JSON structure could prevent parsing
4. **Path mismatch** - The conferences page might be in a subdirectory causing relative path issues
5. **GitHub Pages caching** - Old version of JS may be cached

**Debugging Steps**:
```bash
# 1. Verify JSON is valid and accessible
curl https://abdullahsahruri.github.io/assets/conference_database.json | python -m json.tool

# 2. Check the JSON structure matches expected format
# Should be: { "CONF_YEAR": { "name": ..., "paper_deadline": ..., ... } }

# 3. Test locally by cloning the website repo
git clone https://github.com/abdullahsahruri/abdullahsahruri.github.io.git
cd abdullahsahruri.github.io
# Open conferences/index.html in browser and check console

# 4. Verify the fetch path in the JavaScript
# Look for: fetch('/assets/conference_database.json')
# May need to change to: fetch('../assets/conference_database.json')
```

**Fix Recommendations**:
1. Add error handling in the website's JavaScript to show specific error messages
2. Check if the conferences page is using the correct relative path for the JSON
3. Add console.log statements to debug where the JavaScript fails
4. Verify the JSON structure matches what the JavaScript expects (object with conference keys)
5. Clear GitHub Pages cache by making a commit to the website repo

## Token Refresh Handling

`main_scraper.py::get_calendar_service()` automatically:
1. Checks if token is expired
2. Refreshes using refresh token
3. Saves updated token back to `token.json`

GitHub Actions workflow must update the `GOOGLE_TOKEN` secret if token is refreshed, but this is typically handled automatically during workflow runs.

## Troubleshooting

### "No valid credentials found"
- Run `gcal_setup.py` locally first to generate `token.json`
- Verify `GOOGLE_TOKEN` and `GOOGLE_CREDS` secrets are set in GitHub

### Scraper finds no deadlines
- Conference site structure may have changed
- Check browser DevTools to inspect HTML
- Update extraction logic in `extract_conference_info()`

### Duplicate events in calendar
- Check `event_exists()` logic in `main_scraper.py`
- Verify event title format matches exactly

### Workflow fails to push to website
- Check `SITE_GITHUB_TOKEN` has write permissions
- Verify target repository path is correct

### Email notifications not working
- Verify all `EMAIL_*` environment variables are set
- For Gmail: ensure App Password is used (not regular password)
- Test locally: `python email_notifier.py`