#!/usr/bin/env python3
"""
One-Click Conference Add
========================

Usage:
    python3 add.py <conference_name> <year> <url>

Example:
    python3 add.py ISCA 2026 https://iscaconf.org/isca2026/submit/papers.php

Does everything:
- AI extracts deadline from URL
- Adds to database
- Pushes to website
"""

import sys
import json
import os
import subprocess
from datetime import datetime
from ai_conference_extractor_ollama import extract_conference_info_with_ollama


DATABASE_FILE = 'conference_database.json'
WEBSITE_REPO = '/home/asahruri/abdullahsahruri.github.io'


def load_database():
    """Load existing database."""
    if not os.path.exists(DATABASE_FILE):
        return {}
    with open(DATABASE_FILE, 'r') as f:
        try:
            return json.load(f)
        except:
            return {}


def save_database(data):
    """Save database."""
    with open(DATABASE_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def sync_to_website():
    """Copy to website and push."""
    print("📤 Syncing to website...", flush=True)

    # Copy database
    subprocess.run(['cp', DATABASE_FILE, f'{WEBSITE_REPO}/assets/conference_database.json'],
                   check=True)

    # Git operations
    subprocess.run(['git', '-C', WEBSITE_REPO, 'add', 'assets/conference_database.json'],
                   check=True)
    subprocess.run(['git', '-C', WEBSITE_REPO, 'commit', '-m',
                   f'Update conferences - {datetime.now().strftime("%Y-%m-%d %H:%M")}'],
                   capture_output=True)  # Ignore if no changes
    subprocess.run(['git', '-C', WEBSITE_REPO, 'pull', '--rebase'],
                   check=True, capture_output=True)
    subprocess.run(['git', '-C', WEBSITE_REPO, 'push'],
                   check=True)

    print("✅ Pushed to website!", flush=True)
    print("   https://abdullahsahruri.github.io/conferences/", flush=True)


def add_conference(conf_name, year, url):
    """Extract, add, and push in one go."""
    conf_name = conf_name.upper()
    year = int(year)
    conf_key = f"{conf_name}_{year}"

    # Load database
    database = load_database()

    # Check if exists
    if conf_key in database:
        print(f"⚠️  {conf_key} exists (deadline: {database[conf_key].get('paper_deadline', 'TBD')})")
        print(f"   Updating with new data from URL...", flush=True)
    else:
        print(f"🆕 Adding {conf_key}...", flush=True)

    # Extract with AI
    print(f"🤖 Extracting from: {url}", flush=True)
    full_name = f"{conf_name} {year}"
    info = extract_conference_info_with_ollama(url, full_name)

    if not info:
        print("❌ AI extraction failed - URL may be blocked or have no deadline info")
        return False

    # Show what was extracted
    print(f"✅ Extracted:", flush=True)
    print(f"   Deadline: {info.get('paper_deadline', 'N/A')}", flush=True)
    print(f"   Type: {info.get('submission_type', 'N/A')}", flush=True)
    print(f"   Dates: {info.get('conference_date', 'N/A')}", flush=True)
    print(f"   Location: {info.get('location', 'N/A')}", flush=True)

    # Add to database
    info['last_checked'] = datetime.now().isoformat()
    info['extracted_with_ai'] = True
    info['ai_model'] = info.get('ai_model', 'llama3.1:latest')

    database[conf_key] = info
    save_database(database)
    print(f"✅ Saved to database", flush=True)

    # Push to website
    sync_to_website()

    return True


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 add.py <conference_name> <year> <url>")
        print("Example: python3 add.py ISCA 2026 https://iscaconf.org/isca2026/submit/papers.php")
        sys.exit(1)

    conf_name = sys.argv[1]
    year = sys.argv[2]
    url = sys.argv[3]

    add_conference(conf_name, year, url)
