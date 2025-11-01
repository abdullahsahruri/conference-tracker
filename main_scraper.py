#!/usr/bin/env python3
"""
Conference Deadline Scraper & Google Calendar Automation
=========================================================

This script scrapes conference deadlines from websites and automatically
adds them as all-day events to Google Calendar.

Designed to run automatically via GitHub Actions.
"""

import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# List of conference websites to scrape
CONFERENCE_SITES = [
    "https://iscaconf.org/isca2026/",
    "https://www.cse.chalmers.se/research/group/vlsi/conference/",
    # Add more conference URLs here
]

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']


def get_calendar_service():
    """
    Authenticate and return a Google Calendar API service object.

    Returns:
        service: Authorized Google Calendar API service instance
    """
    creds = None

    # Load existing token
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # Refresh token if expired
    if creds and creds.expired and creds.refresh_token:
        print("→ Refreshing expired token...")
        creds.refresh(Request())
        # Save the refreshed credentials
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    if not creds or not creds.valid:
        raise Exception("No valid credentials found. Run gcal_setup.py first.")

    service = build('calendar', 'v3', credentials=creds)
    return service


def scrape_example_conf(url):
    """
    Scrapes deadlines from example-conf.com format.

    Assumes HTML structure like:
    <div>
        <h3>Submission Deadline:</h3>
        <span>February 15, 2026</span>
    </div>

    Args:
        url: The URL to scrape

    Returns:
        list: List of tuples [(event_name, date_string), ...]
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        deadlines = []

        # Find all h3 tags that might contain deadline information
        h3_tags = soup.find_all('h3')

        for h3 in h3_tags:
            # Check if this is a deadline-related heading
            if 'deadline' in h3.get_text().lower():
                event_name = h3.get_text().strip()

                # Look for the date in the next sibling span or div
                sibling = h3.find_next_sibling(['span', 'div', 'p'])
                if sibling:
                    date_string = sibling.get_text().strip()
                    deadlines.append((event_name, date_string))

        return deadlines

    except Exception as e:
        print(f"❌ Error scraping {url}: {e}")
        return []


def scrape_isca_style(url):
    """
    Scrapes deadlines from ISCA-style conference websites.

    Handles table structure with columns:
    | Deadline Name | Main Track Date | Industry Track Date |
    | Abstract Deadline | November 10, 2025 | December 5, 2025 |

    Args:
        url: The URL to scrape

    Returns:
        list: List of tuples [(event_name, date_string), ...]
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        deadlines = []

        # Find the table with deadlines
        table = soup.find('table')
        if not table:
            return deadlines

        rows = table.find_all('tr')

        # Skip header row (first row)
        for row in rows[1:]:
            cells = row.find_all('td')

            # Expect: [Deadline Name, Main Track, Industry Track]
            if len(cells) >= 2:
                deadline_name = cells[0].get_text().strip()

                # Skip if deadline name is empty or just whitespace
                if not deadline_name:
                    continue

                # Get Main Track date (column 2)
                main_track_date = cells[1].get_text().strip()
                if main_track_date and main_track_date.lower() != 'n/a':
                    deadlines.append((f"ISCA 2026 - {deadline_name} (Main Track)", main_track_date))

                # Get Industry Track date (column 3) if exists
                if len(cells) >= 3:
                    industry_track_date = cells[2].get_text().strip()
                    if industry_track_date and industry_track_date.lower() != 'n/a':
                        deadlines.append((f"ISCA 2026 - {deadline_name} (Industry Track)", industry_track_date))

        return deadlines

    except Exception as e:
        print(f"❌ Error scraping {url}: {e}")
        return []


def scrape_conference_aggregator_table(url):
    """
    Scrapes deadlines from conference aggregator tables.

    Works with sites like Chalmers VLSI that have tables with columns:
    | Conference | Home Page | Paper Deadline | Conference Date |

    Args:
        url: The URL to scrape

    Returns:
        list: List of tuples [(event_name, date_string), ...]
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        deadlines = []

        # Find the main table
        table = soup.find('table')
        if not table:
            return deadlines

        rows = table.find_all('tr')

        # Skip header row
        for row in rows[1:]:
            cells = row.find_all('td')

            # Expected format: [Conference Name, Home Page, Paper Deadline, Conference Date]
            if len(cells) >= 3:
                conf_name = cells[0].get_text().strip()
                paper_deadline = cells[2].get_text().strip()

                # Skip if no conference name or deadline
                if not conf_name or not paper_deadline:
                    continue

                # Skip if deadline is TBD or empty
                if paper_deadline.lower() in ['tbd', 'tba', 'n/a', '-', '']:
                    continue

                # Create event name
                event_name = f"{conf_name} - Paper Deadline"
                deadlines.append((event_name, paper_deadline))

        return deadlines

    except Exception as e:
        print(f"❌ Error scraping {url}: {e}")
        return []


def parse_date_string(date_string):
    """
    Parse various date formats into a datetime object.

    Args:
        date_string: Date string to parse (e.g., "February 15, 2026")

    Returns:
        datetime object or None if parsing fails
    """
    # Common date formats
    date_formats = [
        "%B %d, %Y",       # February 15, 2026
        "%b %d, %Y",       # Feb 15, 2026
        "%Y-%m-%d",        # 2026-02-15
        "%d %B %Y",        # 15 February 2026
        "%d %b %Y",        # 15 Feb 2026
        "%m/%d/%Y",        # 02/15/2026
    ]

    for fmt in date_formats:
        try:
            return datetime.strptime(date_string.strip(), fmt)
        except ValueError:
            continue

    print(f"⚠️  Could not parse date: {date_string}")
    return None


def event_exists(service, event_title, event_date):
    """
    Check if an event with the exact same title and date already exists.

    Args:
        service: Google Calendar API service object
        event_title: Title of the event to check
        event_date: Date of the event (datetime object)

    Returns:
        bool: True if event exists, False otherwise
    """
    try:
        # For all-day events, we need to search a broader range
        # Google Calendar's date filtering for all-day events needs the start of the month
        month_start = event_date.replace(day=1, hour=0, minute=0, second=0)
        # Search the entire month to ensure we capture all-day events
        if event_date.month == 12:
            month_end = event_date.replace(year=event_date.year + 1, month=1, day=1, hour=0, minute=0, second=0)
        else:
            month_end = event_date.replace(month=event_date.month + 1, day=1, hour=0, minute=0, second=0)

        time_min = month_start.isoformat() + 'Z'
        time_max = month_end.isoformat() + 'Z'

        events_result = service.events().list(
            calendarId='primary',
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            maxResults=500  # Get more events to avoid pagination issues
        ).execute()

        events = events_result.get('items', [])
        target_date_str = event_date.strftime('%Y-%m-%d')

        # Check if any event has the exact same title and date
        for event in events:
            event_summary = event.get('summary', '').strip()
            if event_summary == event_title.strip():
                # Check if the date matches (for all-day events)
                event_date_str = event['start'].get('date', '')
                if not event_date_str:  # Handle datetime events
                    event_datetime_str = event['start'].get('dateTime', '')
                    if event_datetime_str:
                        event_date_str = event_datetime_str[:10]

                if event_date_str == target_date_str:
                    return True

        return False

    except HttpError as e:
        print(f"❌ Error checking for existing event: {e}")
        return False


def create_all_day_event(service, event_title, event_date):
    """
    Create an all-day event in Google Calendar.

    Args:
        service: Google Calendar API service object
        event_title: Title of the event
        event_date: Date of the event (datetime object)

    Returns:
        bool: True if event was created, False otherwise
    """
    try:
        # Format date for all-day event (YYYY-MM-DD)
        date_str = event_date.strftime('%Y-%m-%d')

        event = {
            'summary': event_title,
            'start': {
                'date': date_str,
            },
            'end': {
                'date': date_str,
            },
            'description': 'Conference deadline added automatically by scraper',
        }

        created_event = service.events().insert(
            calendarId='primary',
            body=event
        ).execute()

        print(f"✓ Created event: {event_title} on {date_str}")
        return True

    except HttpError as e:
        print(f"❌ Error creating event '{event_title}': {e}")
        return False


def process_conference_site(service, url):
    """
    Process a single conference website: scrape, parse, and add to calendar.

    Args:
        service: Google Calendar API service object
        url: URL to scrape
    """
    print(f"\n→ Processing: {url}")

    # Choose the appropriate scraper based on the URL
    if 'iscaconf.org' in url or 'isca' in url.lower():
        deadlines = scrape_isca_style(url)
    elif 'chalmers.se' in url or 'conference' in url:
        # Conference aggregator tables (like Chalmers VLSI)
        deadlines = scrape_conference_aggregator_table(url)
    else:
        # Use the generic scraper as fallback
        deadlines = scrape_example_conf(url)

    if not deadlines:
        print("  No deadlines found")
        return

    print(f"  Found {len(deadlines)} deadline(s)")

    # Process each deadline
    for event_name, date_string in deadlines:
        # Parse the date
        event_date = parse_date_string(date_string)
        if not event_date:
            continue

        # Check if event already exists
        if event_exists(service, event_name, event_date):
            print(f"  ⊘ Skipped (already exists): {event_name}")
            continue

        # Create the event
        create_all_day_event(service, event_name, event_date)


def main():
    """
    Main function to run the conference deadline scraper.
    """
    print("=" * 60)
    print("Conference Deadline Scraper")
    print("=" * 60)

    try:
        # Authenticate with Google Calendar
        print("\n→ Authenticating with Google Calendar...")
        service = get_calendar_service()
        print("✓ Authentication successful")

        # Process each conference site
        for site_url in CONFERENCE_SITES:
            try:
                process_conference_site(service, site_url)
            except Exception as e:
                print(f"❌ Error processing {site_url}: {e}")
                continue

        print("\n" + "=" * 60)
        print("✅ Scraping complete!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        raise


if __name__ == '__main__':
    main()
