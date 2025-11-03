# Conference Deadline Tracker - Interactive Mode

**You provide URLs → AI extracts details → Auto-syncs to website**

## Quick Start

```bash
python3 interactive_add.py
```

Then paste conference URLs one by one. AI extracts everything automatically!

## Example Session

```bash
$ python3 interactive_add.py

======================================================================
Interactive Conference Entry with AI Extraction
======================================================================

You provide the URL, AI extracts the details.

======================================================================
Enter conference URL (or 'quit' to exit): https://iscaconf.org/isca2026/submit/papers.php

Conference acronym (e.g., ISCA): ISCA
Year (e.g., 2026): 2026

🤖 Extracting conference info from URL using AI...
   URL: https://iscaconf.org/isca2026/submit/papers.php

✅ AI extracted:
   Conference: ISCA 2026
   Paper Deadline: November 17, 2025
   Submission Type: Regular Paper
   Conference Dates: June 27-July 1, 2026
   Location: Raleigh, NC
   Abstract Deadline: November 10, 2025

   Add this to database? (y/n): y

✅ Added ISCA_2026 to database!

📤 Syncing to website...
✅ Synced to website!
   View at: https://abdullahsahruri.github.io/conferences/
```

## Features

✅ **You provide URL** - No wrong conference matching!
✅ **AI extracts deadline** - No manual typing!
✅ **Duplicate detection** - Warns if conference already exists
✅ **Auto-sync to website** - Updates in 1-2 minutes
✅ **Confirmation before adding** - Review before saving

## Requirements

Start Ollama if needed:
```bash
ollama serve &
```

## Files

- `interactive_add.py` - Main tool (USE THIS!)
- `manual_add_conference.py` - Fallback for manual entry
- `sync_to_website.sh` - Sync to website
