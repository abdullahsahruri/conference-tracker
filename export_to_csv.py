#!/usr/bin/env python3
"""
Export conference database to CSV for editing
==============================================

Usage:
    python3 export_to_csv.py [output_file.csv]

Default output: conferences.csv
"""

import json
import csv
import sys


DATABASE_FILE = 'conference_database.json'


def export_to_csv(output_file='conferences.csv'):
    """Export database to CSV."""

    # Load database
    with open(DATABASE_FILE, 'r') as f:
        data = json.load(f)

    if not data:
        print("❌ Database is empty, nothing to export")
        return

    # Write CSV
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)

        # Header
        writer.writerow([
            'conference_name',
            'year',
            'paper_deadline',
            'url',
            'submission_type',
            'conference_date',
            'abstract_deadline',
            'location'
        ])

        # Data rows
        for key, conf in sorted(data.items()):
            # Extract name and year from key (e.g., "ISCA_2026")
            name, year = key.rsplit('_', 1)

            writer.writerow([
                name,
                year,
                conf.get('paper_deadline', ''),
                conf.get('url', ''),
                conf.get('submission_type', 'Regular Paper'),
                conf.get('conference_date', ''),
                conf.get('abstract_deadline', ''),
                conf.get('location', '')
            ])

    print(f"✅ Exported {len(data)} conferences to {output_file}")
    print(f"\nEdit the CSV, then import with:")
    print(f"  python3 import_manual_conferences.py {output_file}")


if __name__ == "__main__":
    output_file = sys.argv[1] if len(sys.argv) > 1 else 'conferences.csv'
    export_to_csv(output_file)
