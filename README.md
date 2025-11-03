# Conference Tracker - Simple Commands

## Add Conference (AI Extraction)

```bash
./add ISCA 2026 https://iscaconf.org/isca2026/submit/papers.php
```

AI extracts → Database updated → Website pushed!

## Edit with CSV

```bash
# Export to CSV
./csv export

# Edit conferences.csv in Excel/etc

# Import and push to website
./csv import conferences.csv
```

## Other Commands

```bash
./add -h              # Show help
./clear               # Clear all conferences  
./csv template        # Create CSV template
```

## CSV Format

```csv
conference_name,year,paper_deadline,url,submission_type,conference_date,abstract_deadline,location
ISCA,2026,November 17 2025,https://iscaconf.org/isca2026,Regular Paper,June 27-July 1 2026,November 10 2025,Raleigh NC
MICRO,2026,April 11 2026,https://microarch.org/micro59,Regular Paper,,,Seoul Korea
```

Website: https://abdullahsahruri.github.io/conferences/
