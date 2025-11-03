#!/usr/bin/env python3
"""
AI-Powered Conference Tracker
==============================

Uses Ollama AI (100% FREE) for intelligent conference deadline extraction.

This system automatically:
1. Searches for conferences by keyword (e.g., "ISCA 2026")
2. Discovers conference websites (handles changing URLs)
3. Extracts deadlines using AI (90% accuracy)
4. Maintains a local database of conferences
5. Detects deadline changes
6. Generates HTML table for website display

Requirements:
- Ollama installed and running (ollama serve)
- Model downloaded (ollama pull llama3.1 or llama3.2)

Usage:
    python3 conference_tracker.py
"""

import os
import json
import sys
from datetime import datetime
from typing import List, Dict, Optional
import requests

# Import email notifier
try:
    from email_notifier import EmailNotifier
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False

# Import date normalizer
try:
    from date_normalizer import normalize_conference_dates
except ImportError:
    normalize_conference_dates = None


# Configuration
DATABASE_FILE = 'conference_database.json'
HTML_OUTPUT = 'conference_table.html'
CHANGES_LOG = 'deadline_changes.log'
CURRENT_YEAR = datetime.now().year
NEXT_YEAR = CURRENT_YEAR + 1

# Conference full names (to help distinguish similar acronyms)
CONFERENCE_FULL_NAMES = {
    # Computer Architecture
    'ISCA': 'International Symposium on Computer Architecture',
    'MICRO': 'International Symposium on Microarchitecture',
    'HPCA': 'High-Performance Computer Architecture',
    'ASPLOS': 'Architectural Support for Programming Languages and Operating Systems',

    # VLSI & Circuits
    'ISSCC': 'International Solid-State Circuits Conference',
    'VLSI': 'VLSI Technology and Circuits Symposium',
    'ICCAD': 'International Conference on Computer-Aided Design',
    'DAC': 'Design Automation Conference',
    'DATE': 'Design Automation and Test in Europe',
    'ASPDAC': 'Asia and South Pacific Design Automation Conference',
    'ISLPED': 'International Symposium on Low Power Electronics and Design',
    'GLSVLSI': 'Great Lakes Symposium on VLSI',
    'CICC': 'Custom Integrated Circuits Conference',
    'ESSCIRC': 'European Solid-State Circuits Conference',
    'ISQED': 'International Symposium on Quality Electronic Design',
    'VLSI-SOC': 'VLSI System on Chip Conference',

    # Design Automation
    'ISCAS': 'International Symposium on Circuits and Systems',
    'ICCD': 'International Conference on Computer Design',
    'ISPD': 'International Symposium on Physical Design',

    # FPGA & Reconfigurable Computing
    'FPGA': 'ACM/SIGDA International Symposium on Field-Programmable Gate Arrays',
    'FCCM': 'Field-Configurable Custom Computing Machines',

    # Testing & Verification
    'ITC': 'International Test Conference',
    'VTS': 'VLSI Test Symposium',
    'ATS': 'Asian Test Symposium',

    # Systems & Architecture
    'SOSP': 'Symposium on Operating Systems Principles',
    'OSDI': 'Operating Systems Design and Implementation',
    'EUROSYS': 'European Conference on Computer Systems',

    # Hardware Security
    'HOST': 'Hardware Oriented Security and Trust',
    'CHES': 'Cryptographic Hardware and Embedded Systems',

    # Emerging Technologies
    'HOTCHIPS': 'Hot Chips Symposium on High-Performance Chips',
}


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


def search_conference(conference_name: str, year: int, return_multiple: bool = False):
    """
    Search the web for a conference and return the official website URL(s).

    Uses DuckDuckGo search API (no API key required).

    Args:
        conference_name: Conference acronym (e.g., "ISCA")
        year: Conference year (e.g., 2026)
        return_multiple: If True, return list of candidate URLs; if False, return best single URL

    Returns:
        URL of the conference website, or list of URLs if return_multiple=True, or None if not found
    """
    try:
        from ddgs import DDGS

        # Get full conference name for more specific search
        full_name = CONFERENCE_FULL_NAMES.get(conference_name, conference_name)

        # Try multiple search strategies with full names for specificity
        queries = [
            f'"{conference_name} {year}" call for papers',  # Exact acronym + year in quotes
            f'"{full_name}" {year} CFP',  # Full name search
            f"{conference_name} {year} IEEE ACM deadline",  # IEEE/ACM conferences
            f"{conference_name} {year} conference submission",  # Fallback
        ]

        all_urls = []
        seen_urls = set()

        for query in queries:
            try:
                results = DDGS().text(query, max_results=10)

                for result in results:
                    href = result.get('href', '')
                    title = result.get('title', '').lower()
                    href_lower = href.lower()

                    # Skip duplicates and non-relevant sites
                    if href in seen_urls:
                        continue

                    # Block social media and common wrong matches
                    blocked_domains = [
                        'wikipedia', 'twitter', 'facebook', 'linkedin', 'youtube', 'instagram',
                        'microsoft.com/blog', 'techcommunity.microsoft', 'postgres',  # Block Postgres/database conferences
                        'easychair.org/smart', 'springer', 'semanticscholar',  # Aggregators that confuse search
                        'wikicfp.com', 'conferenceindex.org', 'conference-service.com',  # Generic CFP aggregators (unreliable)
                        'github.com', 'elettronica-tech.it', 'conferencelists.org',  # Wrong domains
                        'microbit.org', 'foodmicro', 'icfmh.org',  # Not tech conferences
                        'callforpaper.org', 'manuscriptlink.com', 'blogspot.com',  # Aggregators
                        'ourglocal.com', 'resurchify.com',  # More aggregators
                    ]
                    if any(skip in href_lower for skip in blocked_domains):
                        continue

                    # Block conferences that sound similar but are different
                    conference_blocklist = {
                        'DAC': ['aspdac'],  # DAC should not match ASPDAC
                        'MICRO': ['microbit', 'foodmicro', 'microbiology'],
                        'VLSI': ['isvlsi'],  # VLSI should not match ISVLSI
                        'ISCA': ['iscas'],  # ISCA should not match ISCAS
                    }
                    if conference_name in conference_blocklist:
                        if any(blocked in href_lower or blocked in title for blocked in conference_blocklist[conference_name]):
                            continue

                    # CRITICAL: Verify URL actually contains the EXACT conference acronym
                    # This prevents matching similar acronyms (e.g., ISCAS vs ISCA)
                    import re
                    conf_lower = conference_name.lower()
                    year_str = str(year)

                    # Extract path components from URL
                    url_parts = re.split(r'[/\-_.]', href_lower)

                    # Check if exact conference acronym appears as a token in URL
                    has_exact_match = (
                        conf_lower in url_parts or  # Exact match as path component
                        f"{conf_lower}{year}" in url_parts or  # conference2026 format
                        f"{year}{conf_lower}" in url_parts or  # 2026conference format
                        f"{conf_lower}{year % 100:02d}" in url_parts  # conference26 format
                    )

                    # Check title contains exact acronym (with word boundaries)
                    title_pattern = r'\b' + re.escape(conf_lower) + r'\b'
                    has_conf_in_title = (
                        re.search(title_pattern, title, re.IGNORECASE) is not None or
                        full_name.lower() in title
                    )

                    # Require EXACT match (not substring) in URL or title
                    if not (has_exact_match or has_conf_in_title):
                        continue

                    # ADDITIONAL CHECK: For short acronyms (<=5 chars), require year nearby
                    # This prevents MICRO matching "food microbiology" or DAC matching "aspdac"
                    if len(conference_name) <= 5:
                        # Check if year appears near conference name in URL or title
                        has_year_in_url = year_str in href_lower
                        has_year_in_title = year_str in title

                        # Also check if full name appears (strongest signal)
                        has_full_name = full_name.lower() in (href_lower + ' ' + title)

                        # Reject if acronym found but NO year and NO full name
                        if not (has_year_in_url or has_year_in_title or has_full_name):
                            continue

                    seen_urls.add(href)

                    # Prioritize CFP/deadline pages
                    cfp_score = 0
                    if any(term in href_lower for term in ['cfp', 'call-for-papers', 'callforpapers', 'submissions', 'submit']):
                        cfp_score += 3
                    if any(term in title for term in ['call for papers', 'cfp', 'deadline', 'submission']):
                        cfp_score += 2
                    if conference_name.lower() in href_lower and str(year) in href_lower:
                        cfp_score += 2
                    elif conference_name.lower() in href_lower:
                        cfp_score += 1

                    if cfp_score > 0:
                        all_urls.append((href, cfp_score))

            except Exception as e:
                continue  # Try next query

        # Sort by score (highest first)
        all_urls.sort(key=lambda x: x[1], reverse=True)

        if return_multiple:
            # Return top 3 URLs
            return [url for url, score in all_urls[:3]] if all_urls else []
        else:
            # Return best single URL
            return all_urls[0][0] if all_urls else None

    except Exception as e:
        print(f"  ❌ Search error for {conference_name} {year}: {e}")
        return [] if return_multiple else None


def extract_conference_info(url: str, conference_name: str) -> Optional[Dict]:
    """
    Extract conference information from a website using Ollama AI.

    Args:
        url: Conference website URL
        conference_name: Expected conference name

    Returns:
        Dictionary with conference info, or None if extraction fails
    """
    try:
        from ai_conference_extractor_ollama import extract_conference_info_with_ollama

        # Use AI extraction (90% accuracy vs 66% with regex)
        info = extract_conference_info_with_ollama(url, conference_name)

        if info and info.get('paper_deadline'):
            print(f"  ✅ AI extracted: {info['paper_deadline']}")
            return info
        else:
            print(f"  ⚠️  AI could not extract deadline")
            return None

    except Exception as e:
        print(f"  ❌ Error during AI extraction: {str(e)[:100]}")
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
    # Handle both string and dict deadlines (some conferences have multiple deadlines)
    def get_sort_key(conf):
        deadline = conf[1].get('paper_deadline', 'ZZZ')
        if isinstance(deadline, dict):
            # For conferences with multiple deadlines, use the first one
            return str(next(iter(deadline.values()))) if deadline else 'ZZZ'
        return str(deadline) if deadline else 'ZZZ'

    conferences.sort(key=get_sort_key)

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
    print("AI-Powered Conference Tracker (Ollama)")
    print("=" * 70)

    # Check if Ollama is running
    try:
        from ai_conference_extractor_ollama import check_ollama_running, get_available_models

        if not check_ollama_running():
            print("\n❌ Ollama is not running!")
            print("\nPlease start Ollama:")
            print("  1. In a terminal: ollama serve")
            print("  2. Then run this script again")
            print("\n" + "=" * 70)
            sys.exit(1)

        # Get available models
        models = get_available_models()
        if not models:
            print("\n❌ No Ollama models installed!")
            print("\nPlease install a model:")
            print("  ollama pull llama3.1")
            print("  or")
            print("  ollama pull llama3.2")
            print("\n" + "=" * 70)
            sys.exit(1)

        print(f"\n✅ Ollama is running!")
        print(f"📦 Using model: {models[0]}")
    except ImportError:
        print("\n❌ AI extraction module not found!")
        print("Make sure ai_conference_extractor_ollama.py is in the same directory.")
        sys.exit(1)

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

            # Search for conference website (get multiple candidates)
            print(f"  Searching for {conf_name} {year}...")
            candidate_urls = search_conference(conf_name, year, return_multiple=True)

            if not candidate_urls:
                print(f"  ⚠️  Could not find website for {conf_name} {year}")
                continue

            # Try each URL until we successfully extract a deadline
            info = None
            for url in candidate_urls:
                print(f"  ✓ Found: {url[:60]}...")
                print(f"  Extracting deadline information...")

                info = extract_conference_info(url, f"{conf_name} {year}")

                if info:
                    # Successfully extracted!
                    break
                else:
                    print(f"  ⚠️  No deadline found, trying next URL...")

            if not info:
                print(f"  ⚠️  Could not extract deadline from any URL")
                continue

            # Validate that deadline year is reasonable for search year
            # NOTE: It's NORMAL for deadlines to be in the year BEFORE the conference
            # Example: ISCA 2026 (June 2026) has deadline November 2025 - this is CORRECT
            deadline = info.get('paper_deadline', '')
            if deadline and deadline != 'TBD' and not isinstance(deadline, dict):
                import re
                from dateutil import parser

                # Extract year from deadline (e.g., "March 17, 2025" -> 2025)
                deadline_year_match = re.search(r'\d{4}', str(deadline))
                if deadline_year_match:
                    deadline_year = int(deadline_year_match.group())

                    # Check 1: Deadline year validation
                    # Allow deadline within ±1 year of conference year
                    # ISCA 2026 → accept 2025, 2026, 2027 deadlines
                    # Reject: ISCA 2026 → 2024 deadline (means we found wrong year website)
                    if abs(deadline_year - year) > 1:
                        print(f"  ⚠️  Skipping: Deadline year ({deadline_year}) too far from search year ({year})")
                        print(f"      (Deadline should be {year-1}, {year}, or {year+1})")
                        continue

                    # Check 2: Don't accept deadlines that are VERY old (>18 months past)
                    # Allow recently passed deadlines because 2026 CFPs may not be posted yet
                    # This catches old conference websites (e.g., GLSVLSI 2024 site when searching for 2026)
                    try:
                        from dateutil.relativedelta import relativedelta
                        deadline_date = parser.parse(str(deadline), fuzzy=True)
                        months_ago = relativedelta(datetime.now(), deadline_date).months + \
                                     (relativedelta(datetime.now(), deadline_date).years * 12)

                        if months_ago > 18:  # More than 1.5 years old
                            print(f"  ⚠️  Skipping: Deadline too old ({deadline}, {months_ago} months ago)")
                            print(f"      (Likely found very old conference website)")
                            continue
                        elif deadline_date < datetime.now():
                            print(f"  ℹ️  Note: Deadline has passed ({deadline})")
                            print(f"      (But keeping - 2026 CFP may not be posted yet)")
                    except:
                        pass  # If we can't parse the date, continue anyway

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
