# Manual Intervention Guide

When the AI tracker fails or produces incorrect results, you can manually add/edit conferences using these tools.

## Option 1: Interactive Script (Recommended)

Add conferences one by one with prompts:

```bash
python3 manual_add_conference.py
```

**Menu options:**
1. **Add new conference** - Interactive prompts for all fields
2. **List all conferences** - View current database (shows which are AI vs Manual)
3. **Delete conference** - Remove incorrect entries
4. **Exit**

### Example Session:

```bash
$ python3 manual_add_conference.py

======================================================================
Manual Conference Management
======================================================================
1. Add new conference
2. List all conferences
3. Delete conference
4. Exit

Choose option (1-4): 1

======================================================================
Manual Conference Entry
======================================================================

Conference acronym (e.g., ISCA): ISCA
Year (e.g., 2026): 2026
Paper deadline (e.g., November 17, 2025): November 17, 2025
Conference URL: https://iscaconf.org/isca2026

Optional fields (press Enter to skip):
Submission type [Regular Paper]:
Conference dates: June 27-July 1, 2026
Abstract deadline: November 10, 2025
Location: Raleigh, NC

======================================================================
Confirm entry:
  Conference: ISCA 2026
  Deadline: November 17, 2025
  URL: https://iscaconf.org/isca2026
  Dates: June 27-July 1, 2026
  Location: Raleigh, NC
======================================================================

Add this entry? (y/n): y

✅ Conference added successfully!
```

## Option 2: Bulk Import via CSV

For adding multiple conferences at once:

### Step 1: Create your CSV file

Copy the template:
```bash
cp manual_conferences_template.csv manual_conferences.csv
```

### Step 2: Edit the CSV

Open `manual_conferences.csv` and add your conferences:

```csv
conference_name,year,paper_deadline,url,submission_type,conference_date,abstract_deadline,location
ISCA,2026,November 17 2025,https://iscaconf.org/isca2026,Regular Paper,June 27-July 1 2026,November 10 2025,Raleigh NC
MICRO,2026,April 11 2026,https://microarch.org/micro59,Regular Paper,October 2026,,Seoul Korea
DAC,2026,November 15 2025,https://dac.com/2026,Regular Paper,June 26-30 2026,,San Francisco CA
```

**Fields:**
- `conference_name` - Required. Conference acronym (e.g., "ISCA")
- `year` - Required. Conference year (e.g., 2026)
- `paper_deadline` - Required. Full deadline (e.g., "November 17 2025")
- `url` - Required. Conference website
- `submission_type` - Optional. Defaults to "Regular Paper"
- `conference_date` - Optional. Conference dates
- `abstract_deadline` - Optional. Abstract deadline
- `location` - Optional. Conference location

### Step 3: Import

```bash
python3 import_manual_conferences.py
```

Or with custom filename:
```bash
python3 import_manual_conferences.py my_conferences.csv
```

## Option 3: Programmatic API

Use in your own scripts:

```python
from manual_add_conference import add_manual_entry

add_manual_entry(
    conference_name="ISCA",
    year=2026,
    paper_deadline="November 17, 2025",
    url="https://iscaconf.org/isca2026",
    submission_type="Regular Paper",
    conference_date="June 27-July 1, 2026",
    abstract_deadline="November 10, 2025",
    location="Raleigh, NC"
)
```

## Hybrid Workflow

You can combine AI and manual entries:

1. **Run AI tracker** to get initial data:
   ```bash
   python3 conference_tracker.py
   ```

2. **Review results**:
   ```bash
   python3 manual_add_conference.py
   # Choose option 2: List all conferences
   ```

3. **Fix incorrect entries**:
   ```bash
   python3 manual_add_conference.py
   # Choose option 3: Delete incorrect entries
   # Choose option 1: Add correct entries
   ```

4. **Sync to website**:
   ```bash
   ./run_tracker_and_sync.sh  # Or just sync step
   ```

## Identifying Manual vs AI Entries

When you list conferences, the source column shows:
- **AI** - Extracted by Ollama
- **Manual** - Manually entered by you

```
Total conferences: 30

Conference           Deadline                  Source
----------------------------------------------------------------------
ISCA_2025            November 22, 2024         AI
ISCA_2026            November 17, 2025         Manual
MICRO_2025           April 11, 2025            AI
MICRO_2026           TBD                       AI
```

## Tips

### When to Use Manual Entry

- AI found completely wrong conference (e.g., MICRO → Postgres blog)
- AI couldn't find the conference website
- Deadline is in unusual format AI can't parse
- Conference website requires authentication
- You have insider information about deadlines

### Batch Operations

To replace all AI entries with manual ones:

1. Export current conferences to CSV
2. Edit deadlines/URLs
3. Clear database: `echo '{}' > conference_database.json`
4. Import from CSV

### Updating Single Conference

```bash
python3 manual_add_conference.py
# It will detect existing entry and ask to overwrite
```

## Troubleshooting

**"Conference already exists"**
- The script will ask if you want to overwrite
- Choose 'y' to replace with your manual entry

**"Database is empty"**
- Normal after clearing - just add your first entry

**CSV import fails**
- Check CSV format matches the template
- Ensure no special characters in deadlines/URLs
- Make sure year is numeric

## Complete Example Workflow

```bash
# 1. Clear corrupted data
echo '{}' > conference_database.json

# 2. Create manual entries CSV
cp manual_conferences_template.csv my_conf.csv
# Edit my_conf.csv with correct data

# 3. Import
python3 import_manual_conferences.py my_conf.csv

# 4. Verify
python3 manual_add_conference.py
# Choose option 2 to list

# 5. Sync to website
cd /home/asahruri/abdullahsahruri.github.io
cp /home/asahruri/work/conferences/conference_database.json assets/
git add assets/conference_database.json
git commit -m "Update conferences with manual data"
git push
```

Website updates in 1-2 minutes!
