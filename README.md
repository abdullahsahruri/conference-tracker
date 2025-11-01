# Conference Deadline Scraper & Calendar Automation

Automatically scrape conference deadlines from websites and add them as all-day events to Google Calendar using GitHub Actions.

## Project Structure

```
conference-automator/
│
├── .github/
│   └── workflows/
│       └── main.yml           # GitHub Actions scheduler
│
├── main_scraper.py            # Main script that runs on schedule
├── gcal_setup.py              # One-time script to get Google API credentials
├── requirements.txt           # Python dependencies
├── .gitignore                 # Ignores secret files
└── README.md                  # This file
```

## Setup Instructions

### Part 1: Get Google Calendar API Credentials

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/

2. **Create a New Project** (or select an existing one)
   - Click "Select a project" → "New Project"
   - Name it (e.g., "Conference Scraper")
   - Click "Create"

3. **Enable Google Calendar API**
   - In the left sidebar, go to "APIs & Services" → "Library"
   - Search for "Google Calendar API"
   - Click on it and press "Enable"

4. **Create OAuth 2.0 Credentials**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - If prompted, configure the OAuth consent screen:
     - Choose "External" (unless you have a workspace)
     - Fill in app name, user support email, and developer email
     - Click "Save and Continue"
   - Choose "Desktop app" as the application type
   - Name it (e.g., "Conference Scraper Desktop")
   - Click "Create"

5. **Download credentials.json**
   - Click the download icon next to your newly created OAuth client
   - Save the JSON file as `credentials.json` in your project directory

### Part 2: Local Setup and Testing

1. **Clone/Create the repository**
   ```bash
   # If not already in your project directory
   cd /path/to/conference-automator
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the one-time setup script**
   ```bash
   python gcal_setup.py
   ```
   - This will open your browser for authorization
   - Sign in with your Google account
   - Grant the requested permissions
   - This creates `token.json` in your directory

4. **Test the scraper locally** (optional)
   ```bash
   python main_scraper.py
   ```

### Part 3: GitHub Actions Setup (CRITICAL SECURITY STEPS)

**WARNING: NEVER commit `credentials.json` or `token.json` to Git!**

The `.gitignore` file already prevents this, but be extra careful.

#### Step-by-Step: Setting Up GitHub Secrets

1. **Prepare credentials.json content**
   - Open `credentials.json` in a text editor
   - Copy the **entire contents** of the file (it should be a JSON object)

2. **Create GOOGLE_CREDS secret**
   - Go to your GitHub repository
   - Click "Settings" → "Secrets and variables" → "Actions"
   - Click "New repository secret"
   - Name: `GOOGLE_CREDS`
   - Value: Paste the entire contents of `credentials.json`
   - Click "Add secret"

3. **Prepare token.json content**
   - Open `token.json` in a text editor (created by `gcal_setup.py`)
   - Copy the **entire contents** of the file

4. **Create GOOGLE_TOKEN secret**
   - Click "New repository secret" again
   - Name: `GOOGLE_TOKEN`
   - Value: Paste the entire contents of `token.json`
   - Click "Add secret"

#### How the GitHub Action Uses These Secrets

The workflow file (`.github/workflows/main.yml`) contains these steps:

```yaml
# Recreate credentials.json from the secret
- name: Create Google credentials file
  run: |
    echo '${{ secrets.GOOGLE_CREDS }}' > credentials.json

# Recreate token.json from the secret
- name: Create Google token file
  run: |
    echo '${{ secrets.GOOGLE_TOKEN }}' > token.json
```

These commands securely reconstruct the credential files on the GitHub Actions runner before running `main_scraper.py`.

### Part 4: Supported Conference Site Types

The scraper includes built-in support for multiple conference website formats:

#### 1. Conference Aggregator Tables (e.g., Chalmers VLSI)
Automatically scrapes table-based aggregators with columns like:
| Conference | Home Page | Paper Deadline | Conference Date |

**Supported sites:**
- Chalmers VLSI Conference List: https://www.cse.chalmers.se/research/group/vlsi/conference/
- Similar aggregator tables with conference names and deadlines

#### 2. ISCA-Style Conference Sites
Handles individual conference websites with deadline tables (Main Track/Industry Track format).

**Example:** https://iscaconf.org/isca2026/

#### 3. Adding Your Own Sites

1. **Update CONFERENCE_SITES list** in `main_scraper.py`:
   ```python
   CONFERENCE_SITES = [
       "https://iscaconf.org/isca2026/",
       "https://www.cse.chalmers.se/research/group/vlsi/conference/",
       "https://your-conference.com/deadlines",  # Add here
   ]
   ```

2. **For custom formats:**
   - Inspect the HTML using browser DevTools (F12)
   - Create a new scraping function (see `scrape_isca_style()` or `scrape_conference_aggregator_table()` as examples)
   - Add URL detection logic in `process_conference_site()`

3. **Inspect website HTML**
   - Find the elements containing deadline information
   - Update BeautifulSoup selectors accordingly

## Schedule Configuration

The scraper runs **daily at 9:00 AM UTC** by default.

**Why daily?** Conference aggregators frequently update their deadlines, and new conferences are added regularly. Daily scraping ensures your calendar stays current with minimal delay.

To change the schedule, edit `.github/workflows/main.yml`:

```yaml
schedule:
  - cron: '0 9 * * *'  # minute hour day month day-of-week
```

Examples:
- Every day at 8 AM UTC: `'0 8 * * *'` (current setting)
- Twice daily (9 AM & 9 PM): Add a second cron line `'0 21 * * *'`
- Every Monday only: `'0 9 * * 1'`
- First day of each month: `'0 0 1 * *'`

Use [crontab.guru](https://crontab.guru/) to help create cron expressions.

## Manual Triggering

You can manually trigger the workflow from GitHub:
1. Go to "Actions" tab in your repository
2. Select "Conference Deadline Scraper" workflow
3. Click "Run workflow" → "Run workflow"

## How It Works

1. **GitHub Actions triggers** on schedule (daily at 9 AM UTC) or manual run
2. **Environment is set up**: Python + dependencies installed
3. **Credentials are created** from GitHub Secrets
4. **main_scraper.py runs**:
   - Authenticates with Google Calendar API
   - Scrapes each conference website using the appropriate scraper:
     - Conference aggregator tables (like Chalmers VLSI)
     - Individual conference sites (like ISCA)
     - Custom scrapers for specific formats
   - Parses deadline dates (supports multiple date formats)
   - Checks if events already exist (prevents duplicates)
   - Creates new all-day calendar events
5. **Credentials are cleaned up** for security

**Result:** Your Google Calendar stays automatically updated with ~40+ conference deadlines from multiple sources!

## Troubleshooting

### "No valid credentials found" error
- Make sure you ran `gcal_setup.py` locally first
- Verify `GOOGLE_TOKEN` secret is set correctly in GitHub

### Scraper finds no deadlines
- Check if the website structure has changed
- Inspect the HTML using browser DevTools
- Update the scraping logic in `scrape_example_conf()`

### Date parsing errors
- Add new date formats to `parse_date_string()` function
- Common formats are already included

### GitHub Actions workflow fails
- Check the Actions logs for specific errors
- Verify both secrets are set correctly
- Ensure repository has Actions enabled

## Security Best Practices

- **credentials.json** and **token.json** are in `.gitignore` - never commit them
- GitHub Secrets are encrypted and only exposed during workflow runs
- Credentials are cleaned up after each run
- Use least-privilege OAuth scopes (only Calendar access)
- Regularly rotate your OAuth tokens if needed

## License

MIT License - feel free to modify and use for your own projects!
