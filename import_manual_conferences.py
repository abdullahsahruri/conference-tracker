#!/usr/bin/env python3
"""
Import Manual Conferences from CSV
===================================

Syncs conference data from CSV into the database.
- Adds new conferences from CSV
- Updates existing conferences from CSV
- Removes manual entries not in CSV (AI-extracted entries are preserved)

CSV Format:
conference_name,year,paper_deadline,url,submission_type,conference_date,abstract_deadline,location

Usage:
    python3 import_manual_conferences.py
    python3 import_manual_conferences.py my_conferences.csv
"""

import csv
import sys
import os
from manual_add_conference import add_manual_entry, list_conferences, load_database, save_database


def import_from_csv(filename='manual_conferences.csv', force=False):
    """Sync conferences from CSV file with database.

    Args:
        filename: CSV file to import
        force: If True, automatically overwrite existing entries without prompting
    """
    try:
        # Read all conferences from CSV
        csv_conferences = {}
        with open(filename, 'r', encoding='utf-8') as f:
            # Skip comment lines at the beginning
            lines = []
            for line in f:
                stripped = line.strip()
                # Skip empty lines and comment lines
                if not stripped or stripped.startswith('#'):
                    continue
                lines.append(line)

            # Parse CSV from the non-comment lines
            reader = csv.DictReader(lines)

            for row in reader:
                # Skip empty rows
                if not row.get('conference_name'):
                    continue

                conf_key = f"{row['conference_name'].strip()}_{row['year'].strip()}"
                csv_conferences[conf_key] = row

        # Load current database
        database = load_database()

        # Track changes
        added = 0
        updated = 0
        removed = 0

        print(f"\n{'='*70}")
        print(f"SYNCING CSV → DATABASE")
        print(f"{'='*70}\n")

        # Add/Update conferences from CSV
        for conf_key, row in csv_conferences.items():
            is_new = conf_key not in database

            print(f"{'➕ Adding' if is_new else '🔄 Updating'}: {row['conference_name']} {row['year']}...")

            add_manual_entry(
                conference_name=row['conference_name'].strip(),
                year=int(row['year']),
                paper_deadline=row['paper_deadline'].strip(),
                url=row['url'].strip(),
                submission_type=row.get('submission_type', 'Regular Paper').strip() or "Regular Paper",
                conference_date=row.get('conference_date', '').strip() or None,
                abstract_deadline=row.get('abstract_deadline', '').strip() or None,
                location=row.get('location', '').strip() or None,
                force=True  # Always force to enable sync
            )

            if is_new:
                added += 1
            else:
                updated += 1

        # Remove manual entries not in CSV
        database = load_database()  # Reload after updates
        to_remove = []

        for conf_key, conf_data in database.items():
            # Only remove manual entries (preserve AI-extracted ones)
            is_manual = conf_data.get('ai_model') == 'manual' or not conf_data.get('extracted_with_ai', True)

            if is_manual and conf_key not in csv_conferences:
                to_remove.append((conf_key, conf_data))

        if to_remove:
            print(f"\n{'='*70}")
            print("REMOVING CONFERENCES NOT IN CSV")
            print(f"{'='*70}\n")

            for conf_key, conf_data in to_remove:
                print(f"🗑️  Removing: {conf_data.get('name', conf_key)}")
                del database[conf_key]
                removed += 1

            save_database(database)

        # Summary
        print(f"\n{'='*70}")
        print("SYNC SUMMARY")
        print(f"{'='*70}")
        print(f"➕ Added:   {added} conferences")
        print(f"🔄 Updated: {updated} conferences")
        print(f"🗑️  Removed: {removed} conferences")
        print(f"{'='*70}\n")

        list_conferences()

    except FileNotFoundError:
        print(f"❌ Error: File '{filename}' not found")
        print(f"\nCreate a CSV file with this format:")
        print("conference_name,year,paper_deadline,url,submission_type,conference_date,abstract_deadline,location")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv) > 1 else 'manual_conferences.csv'

    # Check if running in CI environment (GitHub Actions)
    force = os.getenv('CI') == 'true' or '--force' in sys.argv

    import_from_csv(filename, force=force)
