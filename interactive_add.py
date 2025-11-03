#!/usr/bin/env python3
"""
Interactive Conference Entry with AI Extraction
================================================

You provide the URL, AI extracts the deadline and details.

Usage:
    python3 interactive_add.py
    python3 interactive_add.py https://iscaconf.org/isca2026/submit/papers.php
"""

import sys
import json
import os
from datetime import datetime
from ai_conference_extractor_ollama import extract_conference_info_ollama


DATABASE_FILE = 'conference_database.json'


def load_database():
    """Load existing database."""
    if not os.path.exists(DATABASE_FILE):
        return {}

    with open(DATABASE_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def save_database(data):
    """Save database to file."""
    with open(DATABASE_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def sync_to_website():
    """Sync database to website and push."""
    import subprocess

    print("\n📤 Syncing to website...")

    try:
        # Run sync script
        result = subprocess.run(['./sync_to_website.sh'],
                              capture_output=True,
                              text=True,
                              timeout=60)

        if result.returncode == 0:
            print("✅ Synced to website!")
            print("   View at: https://abdullahsahruri.github.io/conferences/")
        else:
            print(f"⚠️  Sync had issues: {result.stderr}")

    except FileNotFoundError:
        print("⚠️  sync_to_website.sh not found, syncing manually...")

        # Manual sync
        website_repo = "/home/asahruri/abdullahsahruri.github.io"
        subprocess.run(['cp', DATABASE_FILE, f'{website_repo}/assets/conference_database.json'])

        subprocess.run(['git', '-C', website_repo, 'add', 'assets/conference_database.json'])
        subprocess.run(['git', '-C', website_repo, 'commit', '-m',
                       f'Update conferences - {datetime.now().strftime("%Y-%m-%d")}'])
        subprocess.run(['git', '-C', website_repo, 'pull', '--rebase'])
        subprocess.run(['git', '-C', website_repo, 'push'])

        print("✅ Synced to website!")


def extract_and_add(url, conference_name=None, year=None, auto_sync=True):
    """
    Extract conference info from URL and add to database.

    Args:
        url: Conference website URL
        conference_name: Optional conference acronym (extracted from user if not provided)
        year: Optional year (extracted from user if not provided)
        auto_sync: Auto-sync to website after adding (default: True)
    """
    database = load_database()

    # If name/year not provided, ask user
    if not conference_name:
        conference_name = input("Conference acronym (e.g., ISCA): ").strip().upper()
    if not year:
        year = int(input("Year (e.g., 2026): ").strip())

    conf_key = f"{conference_name}_{year}"

    # Check if already exists
    if conf_key in database:
        print(f"\n⚠️  {conf_key} already exists in database")
        print(f"   Current deadline: {database[conf_key].get('paper_deadline', 'TBD')}")
        print(f"   Current URL: {database[conf_key].get('url', 'N/A')}")

        response = input("\n   Update with new data from this URL? (y/n): ")
        if response.lower() != 'y':
            print("❌ Skipped")
            return False

    # Extract info using AI
    print(f"\n🤖 Extracting conference info from URL using AI...")
    print(f"   URL: {url}")

    info = extract_conference_info_ollama(url, conference_name, year)

    if not info:
        print("❌ AI could not extract conference information")
        print("   The URL may be invalid, blocked, or not contain deadline info")
        return False

    # Display extracted info
    print(f"\n✅ AI extracted:")
    print(f"   Conference: {info.get('name', 'N/A')}")
    print(f"   Paper Deadline: {info.get('paper_deadline', 'N/A')}")
    print(f"   Submission Type: {info.get('submission_type', 'N/A')}")
    print(f"   Conference Dates: {info.get('conference_date', 'N/A')}")
    print(f"   Location: {info.get('location', 'N/A')}")
    print(f"   Abstract Deadline: {info.get('abstract_deadline', 'N/A')}")

    # Confirm before adding
    response = input("\n   Add this to database? (y/n): ")
    if response.lower() != 'y':
        print("❌ Cancelled")
        return False

    # Add to database
    info['last_checked'] = datetime.now().isoformat()
    info['extracted_with_ai'] = True
    info['ai_model'] = info.get('ai_model', 'llama3.1:latest')

    database[conf_key] = info
    save_database(database)

    print(f"\n✅ Added {conf_key} to database!")

    # Auto-sync to website
    if auto_sync:
        sync_to_website()

    return True


def interactive_mode():
    """Interactive mode - keep asking for URLs."""
    print("=" * 70)
    print("Interactive Conference Entry with AI Extraction")
    print("=" * 70)
    print("\nYou provide the URL, AI extracts the details.")
    print()

    while True:
        print("\n" + "=" * 70)
        url = input("Enter conference URL (or 'quit' to exit): ").strip()

        if url.lower() in ['quit', 'exit', 'q']:
            print("\nGoodbye!")
            break

        if not url.startswith('http'):
            print("⚠️  URL must start with http:// or https://")
            continue

        try:
            extract_and_add(url)
        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    # Check if URL provided as argument
    if len(sys.argv) > 1:
        url = sys.argv[1]

        # Optional: conference name and year as args
        conf_name = sys.argv[2] if len(sys.argv) > 2 else None
        year = int(sys.argv[3]) if len(sys.argv) > 3 else None

        extract_and_add(url, conf_name, year)
    else:
        # Interactive mode
        interactive_mode()
