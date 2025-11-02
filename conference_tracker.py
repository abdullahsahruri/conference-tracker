#!/usr/bin/env python3
"""
Intelligent Conference Discovery & Monitoring System
====================================================

This system automatically:
1. Searches for conferences by keyword (e.g., "ISCA 2026")
2. Discovers conference websites (handles changing URLs)
3. Extracts deadlines from any conference website
4. Maintains a local database of conferences
5. Detects deadline changes daily
6. Updates Google Calendar and generates HTML table

Built to handle dynamic URLs and deadline updates.
"""

import os
import json
import csv
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import requests
from bs4 import BeautifulSoup
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Import email notifier
try:
    from email_notifier import EmailNotifier
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False
    print("⚠️  Email notifier not available")


# Configuration
DATABASE_FILE = 'conference_database.json'
HTML_OUTPUT = 'conference_table.html'
CHANGES_LOG = 'deadline_changes.log'
CURRENT_YEAR = datetime.now().year
NEXT_YEAR = CURRENT_YEAR + 1


def load_conference_list(filename='conferences_to_track.txt') -> List[str]:
    """
    Load list of conference acronyms to track.

    Returns:
        List of conference names
    """
    conferences = []

    if not os.path.exists(filename):
        print(f"⚠️  Warning: {filename} not found. Using empty list.")
        return conferences

    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if line and not line.startswith('#'):
                conferences.append(line)

    return conferences


def search_conference(conference_name: str, year: int) -> Optional[str]:
    """
    Search the web for a conference and return the official website URL.

    Uses DuckDuckGo HTML search (no API key required).

    Args:
        conference_name: Conference acronym (e.g., "ISCA")
        year: Conference year (e.g., 2026)

    Returns:
        URL of the conference website, or None if not found
    """
    try:
        # Build search query
        query = f"{conference_name} {year} conference"

        # Use DuckDuckGo HTML search (no API required)
        search_url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Find search result links
        results = soup.find_all('a', class_='result__url')

        if not results:
            # Try alternative parsing
            results = soup.find_all('a', href=True)

        # Filter for conference-related URLs
        for link in results[:10]:  # Check first 10 results
            href = link.get('href', '')
            text = link.get_text().lower()

            # Clean DuckDuckGo redirect URLs
            if 'uddg=' in href:
                # Extract the actual URL from DuckDuckGo redirect
                import urllib.parse
                parsed = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
                if 'uddg' in parsed:
                    href = parsed['uddg'][0]

            # Look for conference-related URLs
            if any(indicator in href.lower() or indicator in text for indicator in
                   [conference_name.lower(), 'conference', str(year)]):
                # Clean the URL
                if href.startswith('http'):
                    return href
                elif href.startswith('//'):
                    return 'https:' + href

        print(f"  ⚠️  Could not find website for {conference_name} {year}")
        return None

    except Exception as e:
        print(f"  ❌ Search error for {conference_name} {year}: {e}")
        return None


def extract_conference_info(url: str, conference_name: str) -> Optional[Dict]:
    """
    Extract conference information from a website.

    Intelligently finds:
    - Paper submission deadline
    - Conference dates
    - Conference title

    Args:
        url: Conference website URL
        conference_name: Expected conference name

    Returns:
        Dictionary with conference info, or None if extraction fails
    """
    try:
        response = requests.get(url, timeout=15, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Initialize result
        info = {
            'name': conference_name,
            'url': url,
            'paper_deadline': None,
            'submission_type': 'Regular Paper',
            'conference_date': None,
            'last_checked': datetime.now().isoformat()
        }

        import re

        # Enhanced date patterns
        date_patterns = [
            (r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},?\s+\d{4}\b', re.IGNORECASE),
            (r'\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b', 0),
            (r'\b\d{1,2}\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*,?\s+\d{4}\b', re.IGNORECASE),
            (r'\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b', 0),
        ]

        deadline_keywords = ['paper deadline', 'submission deadline', 'abstract deadline', 'submission due', 'deadline:', 'submissions close']

        # Strategy 1: Look in specific deadline sections
        deadline_sections = soup.find_all(['div', 'section', 'p', 'li', 'td', 'th'],
                                         string=lambda text: text and any(kw in text.lower() for kw in deadline_keywords))

        for section in deadline_sections[:5]:  # Check first 5 matches
            section_text = section.get_text()

            # Try each date pattern
            for pattern, flags in date_patterns:
                if flags:
                    matches = list(re.finditer(pattern, section_text, flags))
                else:
                    matches = list(re.finditer(pattern, section_text))

                if matches:
                    info['paper_deadline'] = matches[0].group()

                    # Detect submission type from context
                    section_lower = section_text.lower()
                    if any(kw in section_lower for kw in ['late breaking', 'late-breaking', 'lbr']):
                        info['submission_type'] = 'Late Breaking Results'
                    elif any(kw in section_lower for kw in ['poster', 'poster session']):
                        info['submission_type'] = 'Poster'
                    elif any(kw in section_lower for kw in ['short paper', 'short-paper']):
                        info['submission_type'] = 'Short Paper'
                    elif any(kw in section_lower for kw in ['workshop', 'wip', 'work in progress', 'work-in-progress']):
                        info['submission_type'] = 'Workshop/WIP'
                    elif any(kw in section_lower for kw in ['abstract', 'abstract deadline']):
                        info['submission_type'] = 'Abstract'
                    break

            if info['paper_deadline']:
                break

        # Strategy 2: Look in tables (like ISCA-style)
        if not info['paper_deadline']:
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        first_cell = cells[0].get_text().strip().lower()

                        # Check if first cell mentions deadline
                        if any(kw in first_cell for kw in ['deadline', 'submission', 'due']):
                            # Second cell likely has the date
                            date_cell_text = cells[1].get_text().strip()

                            for pattern, flags in date_patterns:
                                if flags:
                                    matches = list(re.finditer(pattern, date_cell_text, flags))
                                else:
                                    matches = list(re.finditer(pattern, date_cell_text))

                                if matches:
                                    info['paper_deadline'] = matches[0].group()

                                    # Detect submission type from row context
                                    row_text = row.get_text().lower()
                                    if any(kw in row_text for kw in ['late breaking', 'late-breaking', 'lbr']):
                                        info['submission_type'] = 'Late Breaking Results'
                                    elif any(kw in row_text for kw in ['poster', 'poster session']):
                                        info['submission_type'] = 'Poster'
                                    elif any(kw in row_text for kw in ['short paper', 'short-paper']):
                                        info['submission_type'] = 'Short Paper'
                                    elif any(kw in row_text for kw in ['workshop', 'wip', 'work in progress', 'work-in-progress']):
                                        info['submission_type'] = 'Workshop/WIP'
                                    elif any(kw in row_text for kw in ['abstract', 'abstract deadline']):
                                        info['submission_type'] = 'Abstract'
                                    break

                            if info['paper_deadline']:
                                break

                if info['paper_deadline']:
                    break

        # Strategy 3: Scan entire page text for deadline mentions
        if not info['paper_deadline']:
            full_text = soup.get_text()

            for keyword in deadline_keywords:
                # Find keyword positions
                keyword_lower = keyword.lower()
                text_lower = full_text.lower()
                pos = text_lower.find(keyword_lower)

                if pos != -1:
                    # Get context around keyword (next 150 characters)
                    context = full_text[pos:pos+150]

                    # Find first date in context
                    for pattern, flags in date_patterns:
                        if flags:
                            matches = list(re.finditer(pattern, context, flags))
                        else:
                            matches = list(re.finditer(pattern, context))

                        if matches:
                            info['paper_deadline'] = matches[0].group()
                            break

                    if info['paper_deadline']:
                        break

        # Get conference title
        title_tag = soup.find('title')
        if title_tag:
            info['full_name'] = title_tag.get_text().strip()[:100]

        # Only return if we found a deadline
        if info['paper_deadline']:
            print(f"  ✓ Extracted: {info['paper_deadline']}")
            return info
        else:
            return None

    except Exception as e:
        print(f"  ❌ Error extracting from {url}: {str(e)[:100]}")
        return None


def load_database() -> Dict:
    """Load the conference database from JSON file."""
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_database(database: Dict):
    """Save the conference database to JSON file."""
    with open(DATABASE_FILE, 'w') as f:
        json.dump(database, f, indent=2)
    print(f"\n✓ Database saved to {DATABASE_FILE}")


def detect_changes(old_data: Optional[Dict], new_data: Dict) -> Dict:
    """
    Detect changes between old and new conference data.

    Returns:
        Dictionary describing the changes
    """
    changes = {
        'is_new': old_data is None,
        'deadline_changed': False,
        'old_deadline': None,
        'new_deadline': None,
        'url_changed': False,
    }

    if old_data is None:
        return changes

    # Check deadline change
    if old_data.get('paper_deadline') != new_data.get('paper_deadline'):
        changes['deadline_changed'] = True
        changes['old_deadline'] = old_data.get('paper_deadline')
        changes['new_deadline'] = new_data.get('paper_deadline')

    # Check URL change
    if old_data.get('url') != new_data.get('url'):
        changes['url_changed'] = True
        changes['old_url'] = old_data.get('url')
        changes['new_url'] = new_data.get('url')

    return changes


def log_change(conference_name: str, changes: Dict):
    """Log deadline changes to a file."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    with open(CHANGES_LOG, 'a') as f:
        if changes['is_new']:
            f.write(f"[{timestamp}] NEW: {conference_name} discovered\n")

        if changes['deadline_changed']:
            old = changes['old_deadline'] or 'None'
            new = changes['new_deadline'] or 'None'
            f.write(f"[{timestamp}] DEADLINE CHANGE: {conference_name}: {old} → {new}\n")

        if changes['url_changed']:
            f.write(f"[{timestamp}] URL CHANGE: {conference_name}: {changes['old_url']} → {changes['new_url']}\n")


def generate_html_table(database: Dict):
    """Generate an HTML table like Chalmers VLSI conference list."""
    html = """<!DOCTYPE html>
<html>
<head>
    <title>Conference Deadlines Tracker</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
        }
        h1 {
            color: #333;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin-top: 20px;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: #4CAF50;
            color: white;
        }
        tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        tr:hover {
            background-color: #ddd;
        }
        a {
            color: #1a73e8;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        .deadline-past {
            color: #999;
        }
        .deadline-soon {
            background-color: #fff3cd;
            font-weight: bold;
        }
        .last-updated {
            color: #666;
            font-size: 0.9em;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <h1>Conference Deadlines Tracker</h1>
    <p>Automatically updated daily at 9:00 AM UTC</p>

    <table>
        <tr>
            <th>Conference</th>
            <th>Home Page</th>
            <th>Paper Deadline</th>
            <th>Conference Date</th>
            <th>Last Checked</th>
        </tr>
"""

    # Sort conferences by deadline
    conferences = []
    for key, data in database.items():
        conferences.append((key, data))

    # Sort by paper deadline (if parseable)
    conferences.sort(key=lambda x: x[1].get('paper_deadline', 'ZZZ'))

    for conf_key, data in conferences:
        name = data.get('name', conf_key)
        url = data.get('url', '#')
        deadline = data.get('paper_deadline', 'TBD')
        conf_date = data.get('conference_date', 'TBD')
        last_checked = data.get('last_checked', '')[:10]  # Just the date

        html += f"""        <tr>
            <td>{name}</td>
            <td><a href="{url}" target="_blank">{url[:50]}...</a></td>
            <td>{deadline}</td>
            <td>{conf_date}</td>
            <td>{last_checked}</td>
        </tr>
"""

    html += f"""    </table>

    <p class="last-updated">Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
    <p class="last-updated">Total conferences tracked: {len(database)}</p>
</body>
</html>
"""

    with open(HTML_OUTPUT, 'w') as f:
        f.write(html)

    print(f"✓ HTML table generated: {HTML_OUTPUT}")


def main():
    """Main function to run the conference tracking system."""
    print("=" * 70)
    print("Intelligent Conference Discovery & Monitoring System")
    print("=" * 70)

    # Load conference list
    print("\n→ Loading conference list...")
    conferences_to_track = load_conference_list()
    print(f"  Found {len(conferences_to_track)} conferences to track")

    # Load existing database
    print("\n→ Loading existing database...")
    database = load_database()
    print(f"  {len(database)} conferences in database")

    # Process each conference
    changes_detected = []

    for conf_name in conferences_to_track:
        print(f"\n→ Processing: {conf_name}")

        # Try both current and next year
        for year in [CURRENT_YEAR, NEXT_YEAR]:
            conf_key = f"{conf_name}_{year}"

            # Search for conference website
            print(f"  Searching for {conf_name} {year}...")
            url = search_conference(conf_name, year)

            if not url:
                continue

            print(f"  ✓ Found: {url[:60]}...")

            # Extract conference information
            print(f"  Extracting deadline information...")
            info = extract_conference_info(url, f"{conf_name} {year}")

            if not info:
                print(f"  ⚠️  Could not extract deadline")
                continue

            print(f"  ✓ Deadline: {info.get('paper_deadline', 'Not found')}")

            # Check for changes
            old_data = database.get(conf_key)
            changes = detect_changes(old_data, info)

            if changes['is_new']:
                print(f"  🆕 New conference discovered!")
                changes_detected.append((conf_key, changes))
            elif changes['deadline_changed']:
                print(f"  🔄 Deadline changed: {changes['old_deadline']} → {changes['new_deadline']}")
                changes_detected.append((conf_key, changes))
            elif changes['url_changed']:
                print(f"  🔄 URL changed")
                changes_detected.append((conf_key, changes))
            else:
                print(f"  ✓ No changes")

            # Update database
            database[conf_key] = info

            # Log changes
            if changes['is_new'] or changes['deadline_changed'] or changes['url_changed']:
                log_change(conf_key, changes)

    # Save updated database
    print("\n" + "=" * 70)
    save_database(database)

    # Generate HTML table
    print("\n→ Generating HTML table...")
    generate_html_table(database)

    # Send email notifications for changes
    if changes_detected and EMAIL_AVAILABLE:
        print("\n→ Sending email notifications...")
        notifier = EmailNotifier()
        notifier.notify_changes(changes_detected)

    # Summary
    print("\n" + "=" * 70)
    print("Summary:")
    print(f"  • Total conferences tracked: {len(database)}")
    print(f"  • Changes detected: {len(changes_detected)}")

    if changes_detected:
        print("\n  Changes:")
        for conf_key, changes in changes_detected:
            if changes['is_new']:
                print(f"    🆕 {conf_key}: New")
            elif changes['deadline_changed']:
                print(f"    🔄 {conf_key}: {changes['old_deadline']} → {changes['new_deadline']}")

    print("\n✅ Tracking complete!")
    print("=" * 70)


if __name__ == '__main__':
    main()
