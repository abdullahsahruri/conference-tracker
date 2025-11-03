#!/usr/bin/env python3
"""
Manual Conference Entry Tool
=============================

Use this tool to manually add or edit conference entries when the AI
extraction fails or produces incorrect results.

Usage:
    python3 manual_add_conference.py

Or import as module:
    from manual_add_conference import add_manual_entry
"""

import json
import os
from datetime import datetime
from typing import Dict, Optional


DATABASE_FILE = 'conference_database.json'


def load_database() -> Dict:
    """Load existing database."""
    if not os.path.exists(DATABASE_FILE):
        return {}

    with open(DATABASE_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def save_database(data: Dict):
    """Save database to file."""
    with open(DATABASE_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"✅ Saved to {DATABASE_FILE}")


def add_manual_entry(
    conference_name: str,
    year: int,
    paper_deadline: str,
    url: str,
    submission_type: str = "Regular Paper",
    conference_date: Optional[str] = None,
    abstract_deadline: Optional[str] = None,
    location: Optional[str] = None,
    force: bool = False
) -> None:
    """
    Add a manual conference entry to the database.

    Args:
        conference_name: Conference acronym (e.g., "ISCA")
        year: Conference year (e.g., 2026)
        paper_deadline: Paper submission deadline (e.g., "November 17, 2025")
        url: Conference website URL
        submission_type: Type of submission (default: "Regular Paper")
        conference_date: Conference dates (optional)
        abstract_deadline: Abstract deadline (optional)
        location: Conference location (optional)
        force: If True, automatically overwrite existing entries (default: False)
    """
    database = load_database()

    conf_key = f"{conference_name}_{year}"

    entry = {
        "paper_deadline": paper_deadline,
        "submission_type": submission_type,
        "conference_date": conference_date,
        "abstract_deadline": abstract_deadline,
        "location": location,
        "name": f"{conference_name} {year}",
        "url": url,
        "last_checked": datetime.now().isoformat(),
        "extracted_with_ai": False,  # Mark as manually entered
        "ai_model": "manual"
    }

    # Check if already exists
    if conf_key in database and not force:
        print(f"⚠️  {conf_key} already exists in database")
        print(f"   Old deadline: {database[conf_key].get('paper_deadline')}")
        print(f"   New deadline: {paper_deadline}")
        response = input("   Overwrite? (y/n): ")
        if response.lower() != 'y':
            print("❌ Cancelled")
            return

    database[conf_key] = entry
    save_database(database)
    print(f"✅ Added {conf_key}")


def interactive_add():
    """Interactive mode to add a conference."""
    print("=" * 70)
    print("Manual Conference Entry")
    print("=" * 70)
    print()

    # Get conference details
    conference_name = input("Conference acronym (e.g., ISCA): ").strip().upper()
    year = int(input("Year (e.g., 2026): ").strip())
    paper_deadline = input("Paper deadline (e.g., November 17, 2025): ").strip()
    url = input("Conference URL: ").strip()

    print("\nOptional fields (press Enter to skip):")
    submission_type = input("Submission type [Regular Paper]: ").strip() or "Regular Paper"
    conference_date = input("Conference dates: ").strip() or None
    abstract_deadline = input("Abstract deadline: ").strip() or None
    location = input("Location: ").strip() or None

    # Confirm
    print("\n" + "=" * 70)
    print("Confirm entry:")
    print(f"  Conference: {conference_name} {year}")
    print(f"  Deadline: {paper_deadline}")
    print(f"  URL: {url}")
    if conference_date:
        print(f"  Dates: {conference_date}")
    if location:
        print(f"  Location: {location}")
    print("=" * 70)

    response = input("\nAdd this entry? (y/n): ")
    if response.lower() == 'y':
        add_manual_entry(
            conference_name=conference_name,
            year=year,
            paper_deadline=paper_deadline,
            url=url,
            submission_type=submission_type,
            conference_date=conference_date,
            abstract_deadline=abstract_deadline,
            location=location
        )
        print("\n✅ Conference added successfully!")
    else:
        print("\n❌ Cancelled")


def list_conferences():
    """List all conferences in the database."""
    database = load_database()

    if not database:
        print("Database is empty")
        return

    print(f"\nTotal conferences: {len(database)}\n")
    print(f"{'Conference':<20} {'Deadline':<25} {'Source':<10}")
    print("-" * 70)

    for key, conf in sorted(database.items()):
        deadline = conf.get('paper_deadline', 'TBD')[:24]
        source = "Manual" if not conf.get('extracted_with_ai', True) else "AI"
        print(f"{key:<20} {deadline:<25} {source:<10}")


def delete_conference():
    """Delete a conference from the database."""
    database = load_database()

    if not database:
        print("Database is empty")
        return

    list_conferences()
    print()

    conf_key = input("Enter conference key to delete (e.g., ISCA_2026): ").strip()

    if conf_key not in database:
        print(f"❌ {conf_key} not found in database")
        return

    print(f"\nDeleting {conf_key}:")
    print(f"  Name: {database[conf_key].get('name')}")
    print(f"  Deadline: {database[conf_key].get('paper_deadline')}")
    print(f"  URL: {database[conf_key].get('url')}")

    response = input("\nConfirm deletion? (y/n): ")
    if response.lower() == 'y':
        del database[conf_key]
        save_database(database)
        print(f"✅ Deleted {conf_key}")
    else:
        print("❌ Cancelled")


if __name__ == "__main__":
    while True:
        print("\n" + "=" * 70)
        print("Manual Conference Management")
        print("=" * 70)
        print("1. Add new conference")
        print("2. List all conferences")
        print("3. Delete conference")
        print("4. Exit")
        print()

        choice = input("Choose option (1-4): ").strip()

        if choice == '1':
            interactive_add()
        elif choice == '2':
            list_conferences()
        elif choice == '3':
            delete_conference()
        elif choice == '4':
            print("Goodbye!")
            break
        else:
            print("Invalid choice")
