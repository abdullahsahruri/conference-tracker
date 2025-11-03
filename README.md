# Conference Tracker - One Command Add

**One command → AI extracts → Database updated → Website pushed**

## Usage

```bash
./add ISCA 2026 https://iscaconf.org/isca2026/submit/papers.php
```

That's it! Everything happens automatically:
1. ✅ AI extracts deadline from URL
2. ✅ Adds to database (or updates if exists)
3. ✅ Pushes to website
4. ✅ Website updates in 1-2 minutes

## Examples

```bash
# Add ISCA 2026
./add ISCA 2026 https://iscaconf.org/isca2026/submit/papers.php

# Add MICRO 2026
./add MICRO 2026 https://microarch.org/micro58/submit/papers.php

# Add DAC 2026
./add DAC 2026 https://dac.com/2026/cfp

# Update existing entry (runs same command)
./add ISCA 2026 https://iscaconf.org/isca2026/submit/papers.php
```

## What It Extracts

From the URL, AI finds:
- Paper submission deadline
- Abstract deadline (if any)
- Conference dates
- Location
- Submission type

## View/Manage Conferences

**List all:**
```bash
python3 manual_add_conference.py
# Choose option 2
```

**Delete one:**
```bash
python3 manual_add_conference.py
# Choose option 3
```

**Manual entry (if AI fails):**
```bash
python3 manual_add_conference.py
# Choose option 1
```

## Requirements

Ollama must be running:
```bash
# Check if running
curl -s http://localhost:11434/api/tags

# Start if needed
ollama serve &
```

## Files

- `add` - **Main command (USE THIS!)**
- `add.py` - Python script
- `manual_add_conference.py` - Manual entry fallback
- `conference_database.json` - Your data

## Workflow

Find a conference → Copy CFP URL → Run one command → Done!

Website: https://abdullahsahruri.github.io/conferences/
