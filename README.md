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
./csv template               # Create empty CSV template
./csv export                 # Export current database to CSV
./csv import <file>          # Import CSV and push to website
./clear                      # Clear all conferences
python3 suggest_conferences.py  # Get AI suggestions for related conferences
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

```bash
python3 suggest_conferences.py
```

Shows related computer architecture and VLSI conferences not yet tracked. Output is in CSV format - just copy the rows you want and paste into `my_conferences.csv`.

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
