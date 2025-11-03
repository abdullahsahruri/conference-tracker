#!/usr/bin/env python3
"""
Conference Suggestion Tool
==========================

Scans existing conferences and suggests related computer architecture
and VLSI conferences in CSV format for manual review.

Usage:
    python3 suggest_conferences.py
    python3 suggest_conferences.py my_conferences.csv
"""

import csv
import sys
from datetime import datetime

# Common computer architecture and VLSI conferences
KNOWN_CONFERENCES = {
    # Computer Architecture - Top Tier
    "ISCA": {"name": "International Symposium on Computer Architecture", "category": "Architecture"},
    "MICRO": {"name": "International Symposium on Microarchitecture", "category": "Architecture"},
    "HPCA": {"name": "International Symposium on High-Performance Computer Architecture", "category": "Architecture"},
    "ASPLOS": {"name": "Architectural Support for Programming Languages and Operating Systems", "category": "Architecture"},

    # VLSI & Circuits - Top Tier
    "ISSCC": {"name": "International Solid-State Circuits Conference", "category": "VLSI/Circuits"},
    "VLSI": {"name": "VLSI Symposia (Circuits and Technology)", "category": "VLSI/Circuits"},
    "CICC": {"name": "Custom Integrated Circuits Conference", "category": "VLSI/Circuits"},
    "ESSCIRC": {"name": "European Solid-State Circuits Conference", "category": "VLSI/Circuits"},

    # Design Automation
    "DAC": {"name": "Design Automation Conference", "category": "Design Automation"},
    "ICCAD": {"name": "International Conference on Computer-Aided Design", "category": "Design Automation"},
    "DATE": {"name": "Design, Automation & Test in Europe", "category": "Design Automation"},
    "ASPDAC": {"name": "Asia and South Pacific Design Automation Conference", "category": "Design Automation"},
    "ISPD": {"name": "International Symposium on Physical Design", "category": "Design Automation"},

    # Power & Energy
    "ISLPED": {"name": "International Symposium on Low Power Electronics and Design", "category": "Power/Energy"},

    # FPGA & Reconfigurable Computing
    "FPGA": {"name": "ACM/SIGDA International Symposium on Field-Programmable Gate Arrays", "category": "FPGA"},
    "FCCM": {"name": "IEEE Symposium on Field-Programmable Custom Computing Machines", "category": "FPGA"},

    # Testing & Verification
    "ITC": {"name": "International Test Conference", "category": "Testing"},
    "VTS": {"name": "VLSI Test Symposium", "category": "Testing"},
    "ATS": {"name": "Asian Test Symposium", "category": "Testing"},

    # Systems
    "SOSP": {"name": "Symposium on Operating Systems Principles", "category": "Systems"},
    "OSDI": {"name": "USENIX Symposium on Operating Systems Design and Implementation", "category": "Systems"},
    "EUROSYS": {"name": "European Conference on Computer Systems", "category": "Systems"},

    # Hardware Security
    "HOST": {"name": "Hardware Oriented Security and Trust", "category": "Security"},
    "CHES": {"name": "Cryptographic Hardware and Embedded Systems", "category": "Security"},

    # Emerging Technologies
    "HOTCHIPS": {"name": "Hot Chips: A Symposium on High Performance Chips", "category": "Emerging"},
    "GLSVLSI": {"name": "Great Lakes Symposium on VLSI", "category": "VLSI/Circuits"},
    "ISCAS": {"name": "International Symposium on Circuits and Systems", "category": "Circuits"},
    "ICCD": {"name": "International Conference on Computer Design", "category": "Architecture"},
}


def load_existing_conferences(filename='my_conferences.csv'):
    """Load existing conferences from CSV."""
    existing = set()
    try:
        with open(filename, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('conference_name'):
                    # Store conference name and year
                    existing.add(f"{row['conference_name']}_{row['year']}")
    except FileNotFoundError:
        pass
    return existing


def suggest_conferences(existing_file='my_conferences.csv', output_file=None):
    """Suggest conferences not in the current list."""

    existing = load_existing_conferences(existing_file)

    print("=" * 80)
    print("CONFERENCE SUGGESTIONS - Computer Architecture & VLSI")
    print("=" * 80)
    print(f"\nYou currently have {len(existing)} conferences tracked.")
    print("\nSuggested conferences to add (copy the CSV rows you want):\n")

    # Current and next year
    current_year = datetime.now().year
    years = [current_year, current_year + 1]

    suggestions = []

    for conf_acronym, info in sorted(KNOWN_CONFERENCES.items()):
        for year in years:
            conf_key = f"{conf_acronym}_{year}"

            if conf_key not in existing:
                suggestions.append({
                    'conference_name': conf_acronym,
                    'year': year,
                    'paper_deadline': 'TBD',
                    'url': 'TBD',
                    'submission_type': 'Regular Paper',
                    'conference_date': '',
                    'abstract_deadline': '',
                    'location': '',
                    'full_name': info['name'],
                    'category': info['category']
                })

    if not suggestions:
        print("✅ You already have all known conferences tracked!")
        return

    # Group by category
    by_category = {}
    for s in suggestions:
        cat = s['category']
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(s)

    # Print by category with CSV format
    print("CSV FORMAT (conference_name,year,paper_deadline,url,submission_type,conference_date,abstract_deadline,location)")
    print("-" * 80)

    all_csv_lines = []

    for category in sorted(by_category.keys()):
        print(f"\n## {category}")
        print(f"# Copy the rows below and paste into my_conferences.csv")
        print()

        for conf in by_category[category]:
            csv_line = f"{conf['conference_name']},{conf['year']},{conf['paper_deadline']},{conf['url']},{conf['submission_type']},{conf['conference_date']},{conf['abstract_deadline']},{conf['location']}"
            print(f"{csv_line}  # {conf['full_name']}")
            all_csv_lines.append(csv_line)

    # Optionally save to file
    if output_file:
        with open(output_file, 'w') as f:
            f.write("conference_name,year,paper_deadline,url,submission_type,conference_date,abstract_deadline,location\n")
            for line in all_csv_lines:
                # Remove comment
                line = line.split('#')[0].strip()
                f.write(line + '\n')
        print(f"\n✅ Suggestions saved to {output_file}")

    print("\n" + "=" * 80)
    print(f"Total suggestions: {len(suggestions)} conferences")
    print("=" * 80)
    print("\nTo add conferences:")
    print("1. Copy the CSV rows you want from above")
    print("2. Edit my_conferences.csv and paste them")
    print("3. Run: ./csv import my_conferences.csv")
    print("   OR commit to GitHub and the workflow will auto-import")
    print()


if __name__ == "__main__":
    input_file = sys.argv[1] if len(sys.argv) > 1 else 'my_conferences.csv'
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    suggest_conferences(input_file, output_file)
