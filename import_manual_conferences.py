#!/usr/bin/env python3
"""
Import Manual Conferences from CSV
===================================

Imports conference data from manual_conferences.csv into the database.

CSV Format:
conference_name,year,paper_deadline,url,submission_type,conference_date,abstract_deadline,location

Usage:
    python3 import_manual_conferences.py
    python3 import_manual_conferences.py my_conferences.csv
"""

import csv
import sys
from manual_add_conference import add_manual_entry, list_conferences


def import_from_csv(filename='manual_conferences.csv'):
    """Import conferences from CSV file."""
    try:
        with open(filename, 'r') as f:
            reader = csv.DictReader(f)

            count = 0
            for row in reader:
                # Skip empty rows and comments
                if not row.get('conference_name') or row['conference_name'].startswith('#'):
                    continue

                print(f"\nImporting {row['conference_name']} {row['year']}...")

                add_manual_entry(
                    conference_name=row['conference_name'].strip(),
                    year=int(row['year']),
                    paper_deadline=row['paper_deadline'].strip(),
                    url=row['url'].strip(),
                    submission_type=row.get('submission_type', 'Regular Paper').strip() or "Regular Paper",
                    conference_date=row.get('conference_date', '').strip() or None,
                    abstract_deadline=row.get('abstract_deadline', '').strip() or None,
                    location=row.get('location', '').strip() or None
                )
                count += 1

            print(f"\n{'='*70}")
            print(f"✅ Imported {count} conferences")
            print(f"{'='*70}\n")

            list_conferences()

    except FileNotFoundError:
        print(f"❌ Error: File '{filename}' not found")
        print(f"\nCreate a CSV file with this format:")
        print("conference_name,year,paper_deadline,url,submission_type,conference_date,abstract_deadline,location")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv) > 1 else 'manual_conferences.csv'
    import_from_csv(filename)
