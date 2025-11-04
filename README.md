# Conference Tracker - Manual CSV Management

Simple CSV-based conference deadline tracker.

## Quick Start

### Create CSV with your conferences

```bash
./csv template
```

Edit `my_conferences.csv`:

```csv
conference_name,year,paper_deadline,url,submission_type,conference_date,abstract_deadline,location
ISCA,2026,November 17 2025,https://iscaconf.org/isca2026,Regular Paper,June 27-July 1 2026,November 10 2025,Raleigh NC
MICRO,2026,April 11 2026,https://microarch.org/micro59,Regular Paper,,,Seoul Korea
DAC,2026,November 15 2025,https://dac.com/2026,Regular Paper,June 26-30 2026,,San Francisco CA
```

### Import and push to website

```bash
./csv import my_conferences.csv
```

Done! Website updates in 1-2 minutes.

## All Commands

```bash
./csv template                      # Create empty CSV template
./csv export                        # Export current database to CSV
./csv import <file>                 # Import CSV and push to website
./clear                             # Clear all conferences
python3 ai_extract_conferences.py   # AI extracts real deadlines from web
python3 suggest_conferences.py      # Static curated list (TBD deadlines)
```

## Workflow

### Add/Edit Conferences

1. Export current data (or create template):
   ```bash
   ./csv export          # or: ./csv template
   ```

2. Edit CSV in Excel/LibreOffice

3. Import:
   ```bash
   ./csv import conferences.csv
   ```

### Get Conference Suggestions

**AI Deadline Extraction (Recommended - Extracts Real Data):**
```bash
# Pull Qwen model first (one-time, 4.7GB)
ollama pull qwen2.5

# Extract deadlines for specific conferences
python3 ai_extract_conferences.py --conferences "HPCA,ASPLOS,DAC,ISSCC"

# Or use defaults (HPCA,ASPLOS,DAC,ISSCC,VLSI)
python3 ai_extract_conferences.py
```

**This actually:**
- Searches the web for each conference
- Fetches the conference website
- Uses AI to extract paper deadlines, abstract deadlines, dates, location
- Returns populated CSV with REAL data

**Curated List (Fast but Static):**
```bash
python3 suggest_conferences.py
```

Shows 50+ conferences from a hardcoded list with TBD deadlines. You fill in deadlines manually.

All tools output CSV format - copy the rows and paste into `my_conferences.csv`.

Categories include:
- Computer Architecture (ISCA, MICRO, HPCA, ASPLOS, etc.)
- VLSI & Circuits (ISSCC, VLSI, CICC, ESSCIRC, etc.)
- Design Automation (DAC, ICCAD, DATE, ASPDAC, etc.)
- FPGA, Testing, Security, Systems, and more

### Manual Entry (Alternative)

```bash
python3 manual_add_conference.py
```

Interactive menu for adding/editing/deleting one at a time.

## CSV Format

Required fields:
- `conference_name` - Acronym (ISCA, MICRO, etc.)
- `year` - Conference year
- `paper_deadline` - Submission deadline
- `url` - Conference website

Optional fields:
- `submission_type` (default: "Regular Paper")
- `conference_date`
- `abstract_deadline`
- `location`

Website: https://abdullahsahruri.github.io/conferences/
