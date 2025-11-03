#!/usr/bin/env python3
"""
AI-Powered Conference Tracker (Manual Run)
==========================================

This version uses Ollama AI for conference extraction.
Run this manually on your computer for best results.

The regular conference_tracker.py (using regex) runs automatically
via GitHub Actions even when your computer is off.

Usage:
    python3 conference_tracker_ai.py

Requirements:
    - Ollama installed and running (ollama serve)
    - Model downloaded (ollama pull llama3.1)
"""

import os
import sys
from datetime import datetime

# Import the Ollama AI extractor
from ai_conference_extractor_ollama import (
    check_ollama_running,
    get_available_models,
    extract_conference_info_with_ollama
)

# Import from the main tracker
from conference_tracker import (
    load_conference_list,
    load_database,
    save_database,
    detect_changes,
    log_change,
    generate_html_table,
    search_conference,
    CURRENT_YEAR,
    NEXT_YEAR
)

# Import email notifier if available
try:
    from email_notifier import EmailNotifier
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False


def main():
    """Run AI-powered conference tracking."""
    print("=" * 70)
    print("AI-Powered Conference Tracker (Ollama - FREE)")
    print("=" * 70)

    # Check Ollama is running
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
        print("\n" + "=" * 70)
        sys.exit(1)

    # Select model
    model = models[0]
    print(f"\n✅ Ollama is running!")
    print(f"📦 Using model: {model}")

    # Load conference list
    print("\n→ Loading conference list...")
    conferences_to_track = load_conference_list()
    print(f"  Found {len(conferences_to_track)} conferences to track")

    # Load existing database
    print("\n→ Loading existing database...")
    database = load_database()
    print(f"  {len(database)} conferences in database")

    # Process each conference with AI
    changes_detected = []
    conferences_found = 0
    conferences_failed = 0

    for conf_name in conferences_to_track:
        print(f"\n→ Processing: {conf_name}")

        # Try both current and next year
        for year in [CURRENT_YEAR, NEXT_YEAR]:
            conf_key = f"{conf_name}_{year}"

            # Search for conference website
            print(f"  🔍 Searching for {conf_name} {year}...")
            url = search_conference(conf_name, year)

            if not url:
                continue

            print(f"  ✓ Found: {url[:60]}...")

            # Extract with AI
            info = extract_conference_info_with_ollama(url, f"{conf_name} {year}", model)

            if not info:
                print(f"  ⚠️  AI could not extract deadline")
                conferences_failed += 1
                continue

            # Validate that deadline year matches search year
            deadline = info.get('paper_deadline', '')
            if deadline and deadline != 'TBD' and not isinstance(deadline, dict):
                import re
                # Extract year from deadline (e.g., "March 17, 2025" -> 2025)
                deadline_year_match = re.search(r'\d{4}', str(deadline))
                if deadline_year_match:
                    deadline_year = int(deadline_year_match.group())
                    # Only accept deadlines in the same year as the search year
                    # This prevents: searching for 2026, finding 2025 site with 2026 deadline
                    if deadline_year != year:
                        print(f"  ⚠️  Skipping: Deadline year ({deadline_year}) doesn't match search year ({year})")
                        continue

            conferences_found += 1
            print(f"  ✅ AI extracted: {info.get('paper_deadline', 'Not found')}")

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
    elif changes_detected:
        print("\n→ Email notifications...")
        print("  ⚠️  Email not configured. Skipping notification.")
        print("     Set EMAIL_FROM, EMAIL_PASSWORD, EMAIL_TO environment variables")

    # Summary
    print("\n" + "=" * 70)
    print("Summary:")
    print(f"  • Total conferences tracked: {len(database)}")
    print(f"  • Conferences found with AI: {conferences_found}")
    print(f"  • Conferences where AI failed: {conferences_failed}")
    print(f"  • Changes detected: {len(changes_detected)}")

    if changes_detected:
        print("\n  Changes:")
        for conf_key, changes in changes_detected:
            if changes['is_new']:
                print(f"    🆕 {conf_key}: New")
            elif changes['deadline_changed']:
                print(f"    🔄 {conf_key}: {changes['old_deadline']} → {changes['new_deadline']}")

    print("\n✅ AI tracking complete!")
    print("\n💡 Next steps:")
    print("   1. Review changes above")
    print("   2. Commit and push to update website:")
    print("      git add conference_database.json")
    print("      git commit -m 'Update conferences with AI extraction'")
    print("      git push")
    print("\n" + "=" * 70)


if __name__ == '__main__':
    main()
