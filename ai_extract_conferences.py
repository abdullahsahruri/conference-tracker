#!/usr/bin/env python3
"""
AI Conference Deadline Extractor
=================================

Uses AI to search the web and extract actual conference deadlines.

Usage:
    python3 ai_extract_conferences.py
    python3 ai_extract_conferences.py --conferences "HPCA,DAC,ASPLOS"
"""

import subprocess
import json
import sys
import argparse
import requests
from datetime import datetime
from urllib.parse import quote_plus


def search_conference_website(conference_name, year):
    """Search for conference website using DuckDuckGo."""
    query = f"{conference_name} {year} conference computer architecture"
    try:
        url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)

        # Extract first result URL (simple parsing)
        if 'uddg=' in response.text:
            # Find first result
            start = response.text.find('uddg=') + 5
            end = response.text.find('"', start)
            if start > 5 and end > start:
                encoded_url = response.text[start:end]
                # Decode URL
                import urllib.parse
                result_url = urllib.parse.unquote(encoded_url)
                if result_url.startswith('http'):
                    return result_url

        # Fallback: construct likely URL
        common_patterns = {
            'ISCA': f'https://iscaconf.org/isca{year}',
            'MICRO': f'https://microarch.org/micro{int(year)-1967}',
            'HPCA': f'https://hpca-conf.org/{year}',
            'ASPLOS': f'https://asplos-conference.org/asplos{year}',
            'DAC': f'https://dac.com/{year}',
            'ISSCC': f'https://isscc.org',
        }

        return common_patterns.get(conference_name.upper(), f'https://{conference_name.lower()}.org')

    except Exception as e:
        print(f"   Search error for {conference_name}: {e}")
        return None


def fetch_website_content(url):
    """Fetch website content."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15)
        return response.text[:10000]  # First 10KB
    except Exception as e:
        print(f"   Fetch error: {e}")
        return None


def extract_with_ollama(conference_name, year, website_content, model='qwen2.5'):
    """Use Ollama to extract deadline from website."""

    prompt = f"""Extract paper submission deadline for {conference_name} {year} from this website content.

Website text:
{website_content[:5000]}

Return ONLY valid JSON:
{{
  "paper_deadline": "Month Day, Year" or "TBD",
  "abstract_deadline": "Month Day, Year" or null,
  "conference_date": "Month Day-Day, Year" or null,
  "location": "City, Country" or null
}}

Rules:
- Deadline must be in {year-1} or {year} (not earlier years)
- Use format: "November 17, 2025"
- If not found, use "TBD"
- No explanations, ONLY the JSON"""

    try:
        result = subprocess.run(
            ['ollama', 'run', model],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=60
        )

        output = result.stdout.strip()

        # Extract JSON
        if '```json' in output:
            output = output.split('```json')[1].split('```')[0].strip()
        elif '```' in output:
            output = output.split('```')[1].split('```')[0].strip()
        elif '{' in output:
            # Find first { and last }
            start = output.find('{')
            end = output.rfind('}') + 1
            output = output[start:end]

        data = json.loads(output)
        return data

    except subprocess.TimeoutExpired:
        print(f"   Timeout extracting {conference_name}")
        return None
    except json.JSONDecodeError as e:
        print(f"   JSON parse error for {conference_name}: {e}")
        print(f"   Raw: {output[:200]}")
        return None
    except Exception as e:
        print(f"   Error: {e}")
        return None


def extract_conferences(conference_list, year, model='qwen2.5'):
    """Extract deadlines for multiple conferences."""

    print("=" * 80)
    print("AI CONFERENCE DEADLINE EXTRACTOR")
    print("=" * 80)
    print(f"\n🤖 Using model: {model}")
    print(f"📅 Target year: {year}")
    print(f"📋 Conferences: {', '.join(conference_list)}\n")

    results = []

    for conf_name in conference_list:
        print(f"\n{'='*80}")
        print(f"Processing {conf_name} {year}...")
        print(f"{'='*80}")

        # Step 1: Search for website
        print(f"1️⃣  Searching for {conf_name} {year} website...")
        url = search_conference_website(conf_name, year)
        if not url:
            print(f"   ❌ Could not find website")
            continue
        print(f"   ✅ Found: {url}")

        # Step 2: Fetch content
        print(f"2️⃣  Fetching website content...")
        content = fetch_website_content(url)
        if not content:
            print(f"   ❌ Could not fetch content")
            continue
        print(f"   ✅ Fetched {len(content)} characters")

        # Step 3: Extract with AI
        print(f"3️⃣  Extracting deadlines with AI...")
        info = extract_with_ollama(conf_name, year, content, model=model)

        if info:
            print(f"   ✅ Paper deadline: {info.get('paper_deadline', 'TBD')}")
            if info.get('abstract_deadline'):
                print(f"   ✅ Abstract deadline: {info['abstract_deadline']}")
            if info.get('conference_date'):
                print(f"   ✅ Conference date: {info['conference_date']}")
            if info.get('location'):
                print(f"   ✅ Location: {info['location']}")

            results.append({
                'conference_name': conf_name,
                'year': year,
                'url': url,
                **info
            })
        else:
            print(f"   ❌ Extraction failed")

    # Output CSV
    print(f"\n\n{'='*80}")
    print("RESULTS - Copy and paste into my_conferences.csv")
    print(f"{'='*80}\n")

    if results:
        print("conference_name,year,paper_deadline,url,submission_type,conference_date,abstract_deadline,location")
        for r in results:
            csv_line = f"{r['conference_name']},{r['year']},{r.get('paper_deadline', 'TBD')},{r['url']},Regular Paper,{r.get('conference_date', '')},{r.get('abstract_deadline', '')},{r.get('location', '')}"
            print(csv_line)

        print(f"\n✅ Successfully extracted {len(results)}/{len(conference_list)} conferences")
    else:
        print("❌ No conferences extracted")

    print("\nNext steps:")
    print("1. Copy the CSV lines above")
    print("2. Paste into my_conferences.csv")
    print("3. Run: ./csv import my_conferences.csv\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='AI-powered conference deadline extraction')
    parser.add_argument('--conferences', '-c',
                        default='HPCA,ASPLOS,DAC,ISSCC,VLSI',
                        help='Comma-separated conference names (default: HPCA,ASPLOS,DAC,ISSCC,VLSI)')
    parser.add_argument('--year', '-y', type=int,
                        default=datetime.now().year + 1,
                        help='Target year (default: next year)')
    parser.add_argument('--model', '-m', default='qwen2.5',
                        choices=['qwen2.5', 'mistral', 'llama3.1', 'llama3.2'],
                        help='Ollama model (default: qwen2.5)')

    args = parser.parse_args()

    conferences = [c.strip() for c in args.conferences.split(',')]

    extract_conferences(conferences, args.year, args.model)
