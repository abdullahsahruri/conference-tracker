#!/usr/bin/env python3
"""
AI-Powered Conference Suggestion Tool
======================================

Uses web search and AI to discover related computer architecture and VLSI
conferences based on your existing conference list.

Usage:
    python3 ai_suggest_conferences.py
    python3 ai_suggest_conferences.py my_conferences.csv
"""

import csv
import sys
import json
import subprocess
from datetime import datetime
import requests
from urllib.parse import quote_plus


def load_existing_conferences(filename='my_conferences.csv'):
    """Load existing conferences from CSV."""
    existing = []
    try:
        with open(filename, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('conference_name'):
                    existing.append(row['conference_name'])
    except FileNotFoundError:
        pass
    return existing


def search_conferences(query):
    """Search for conferences using DuckDuckGo."""
    try:
        # Use DuckDuckGo Instant Answer API
        url = f"https://api.duckduckgo.com/?q={quote_plus(query)}&format=json"
        response = requests.get(url, timeout=10)
        return response.json()
    except Exception as e:
        print(f"Search error: {e}")
        return None


def ask_ollama_for_suggestions(existing_conferences):
    """Use Ollama to suggest related conferences."""

    prompt = f"""You are a computer architecture and VLSI conference expert.

I currently track these conferences: {', '.join(existing_conferences)}

Please suggest 10-15 OTHER major computer architecture, VLSI, circuits, and hardware design conferences that I'm not tracking yet.

For each conference, provide ONLY:
- Conference acronym (e.g., "HPCA", "DAC")
- Full name
- Category (Architecture/VLSI/Design Automation/etc.)

Output as JSON array:
[
  {{"acronym": "HPCA", "name": "High-Performance Computer Architecture", "category": "Architecture"}},
  ...
]

Only output the JSON, nothing else."""

    try:
        result = subprocess.run(
            ['ollama', 'run', 'llama3.2'],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=30
        )

        output = result.stdout.strip()

        # Try to extract JSON from output
        if '```json' in output:
            output = output.split('```json')[1].split('```')[0].strip()
        elif '```' in output:
            output = output.split('```')[1].split('```')[0].strip()

        suggestions = json.loads(output)
        return suggestions

    except subprocess.TimeoutExpired:
        print("⏱️  Ollama timeout - using fallback list")
        return None
    except FileNotFoundError:
        print("⚠️  Ollama not found - using fallback list")
        return None
    except json.JSONDecodeError as e:
        print(f"⚠️  Failed to parse AI response: {e}")
        print(f"Raw output: {output[:200]}")
        return None
    except Exception as e:
        print(f"⚠️  Ollama error: {e}")
        return None


def search_web_for_conference_lists():
    """Search web for conference ranking lists."""
    queries = [
        "computer architecture conference rankings",
        "VLSI conference list top tier",
        "hardware design conferences 2025 2026",
        "semiconductor conference deadlines"
    ]

    print("\n🌐 Searching web for conference information...\n")

    found_conferences = set()

    for query in queries:
        print(f"   Searching: {query}")
        result = search_conferences(query)

        if result and 'AbstractText' in result:
            text = result['AbstractText']
            # Simple extraction - look for common conference acronyms
            words = text.upper().split()
            for word in words:
                # Common conference acronyms are 3-7 uppercase letters
                if word.isalpha() and 3 <= len(word) <= 7 and word.isupper():
                    found_conferences.add(word)

    print(f"   Found {len(found_conferences)} potential conferences from web\n")
    return list(found_conferences)


def generate_suggestions(existing_file='my_conferences.csv'):
    """Generate conference suggestions using AI."""

    existing = load_existing_conferences(existing_file)

    print("=" * 80)
    print("AI-POWERED CONFERENCE SUGGESTIONS")
    print("=" * 80)
    print(f"\nYou currently track: {', '.join(existing) if existing else 'No conferences yet'}")
    print("\n🤖 Using AI to find related conferences...\n")

    # Try Ollama first
    suggestions = ask_ollama_for_suggestions(existing)

    if not suggestions:
        # Fallback: Use web search
        web_results = search_web_for_conference_lists()

        # Combine with known conferences
        from suggest_conferences import KNOWN_CONFERENCES

        suggestions = []
        for acronym, info in KNOWN_CONFERENCES.items():
            if acronym not in existing:
                suggestions.append({
                    'acronym': acronym,
                    'name': info['name'],
                    'category': info['category']
                })

        print("📋 Using fallback conference database\n")

    if not suggestions:
        print("❌ No suggestions found")
        return

    # Current and next year
    current_year = datetime.now().year
    years = [current_year, current_year + 1]

    # Group by category
    by_category = {}
    for conf in suggestions:
        cat = conf.get('category', 'Other')
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(conf)

    print("\n" + "=" * 80)
    print("SUGGESTED CONFERENCES (CSV format)")
    print("=" * 80)
    print("\nCopy the rows you want and paste into my_conferences.csv\n")

    total = 0

    for category in sorted(by_category.keys()):
        print(f"\n## {category}")
        print("#" * 80)

        for conf in by_category[category]:
            acronym = conf['acronym']
            name = conf.get('name', '')

            for year in years:
                csv_line = f"{acronym},{year},TBD,TBD,Regular Paper,,,"
                print(f"{csv_line}  # {name}")
                total += 1

    print("\n" + "=" * 80)
    print(f"Total: {total} conference-year combinations suggested")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Copy the CSV rows you want from above")
    print("2. Paste into my_conferences.csv")
    print("3. Fill in actual deadlines and URLs")
    print("4. Run: ./csv import my_conferences.csv")
    print()


if __name__ == "__main__":
    input_file = sys.argv[1] if len(sys.argv) > 1 else 'my_conferences.csv'
    generate_suggestions(input_file)
