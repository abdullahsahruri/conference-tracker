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
    """Search for conference website using DuckDuckGo with improved URL filtering."""

    # Comprehensive fallback URLs (use these first for known conferences)
    common_patterns = {
        # Architecture
        'ISCA': f'https://iscaconf.org/isca{year}',
        'MICRO': f'https://microarch.org/micro{int(year)-1967}',
        'HPCA': f'https://hpca-conf.org/{year}',
        'ASPLOS': f'https://asplos-conference.org/asplos{year}',

        # VLSI/Circuits
        'ISSCC': f'https://isscc.org',
        'VLSI': f'https://vlsisymposium.org',

        # Design Automation
        'DAC': f'https://www.dac.com',
        'ICCAD': f'https://iccad.com',
        'DATE': f'https://www.date-conference.com',

        # FPGA
        'FPGA': f'https://www.isfpga.org',

        # Other
        'ISQED': f'https://www.isqed.org',
        'ISLPED': f'https://islped.org',
    }

    # Try fallback URL first for known conferences
    if conference_name.upper() in common_patterns:
        return common_patterns[conference_name.upper()]

    # Otherwise search the web
    query = f"{conference_name} {year} conference official website"
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

                # Clean URL - remove tracking parameters
                if '&amp;rut=' in result_url:
                    result_url = result_url.split('&amp;rut=')[0]
                if '&rut=' in result_url:
                    result_url = result_url.split('&rut=')[0]

                # Filter out PDFs, wikis, and other non-official URLs
                bad_patterns = ['.pdf', 'wikipedia.org', 'wikicfp.com', 'conferencealerts.com',
                               'conferenceindex.org', 'guide2research.com']

                if result_url.startswith('http') and not any(bad in result_url.lower() for bad in bad_patterns):
                    return result_url

        # Final fallback
        return f'https://{conference_name.lower()}.org'

    except Exception as e:
        print(f"   Search error for {conference_name}: {e}")
        return common_patterns.get(conference_name.upper(), f'https://{conference_name.lower()}.org')


def fetch_website_content(url):
    """Fetch website content from main page and common subpages."""
    headers = {'User-Agent': 'Mozilla/5.0'}
    all_content = []

    # Common subpages where deadlines are posted
    subpages = [
        '',  # Main page
        '/cfp/',
        '/cfp',
        '/call-for-papers/',
        '/call-for-papers',
        '/important-dates/',
        '/important-dates',
        '/submissions/',
        '/submissions',
    ]

    for subpage in subpages:
        try:
            # Construct URL - handle trailing slashes
            if url.endswith('/'):
                fetch_url = url.rstrip('/') + subpage
            else:
                fetch_url = url + subpage

            response = requests.get(fetch_url, headers=headers, timeout=15, allow_redirects=True)
            if response.status_code == 200:
                content = response.text[:20000]  # First 20KB per page
                all_content.append(f"\n=== Content from {fetch_url} ===\n{content}")
                print(f"      - Fetched {len(content)} chars from {subpage if subpage else 'main page'}")
        except Exception as e:
            # Silently skip failed subpages
            continue

    if not all_content:
        # Fallback: try just the main URL
        try:
            response = requests.get(url, headers=headers, timeout=15)
            return response.text[:50000]
        except Exception as e:
            print(f"   Fetch error: {e}")
            return None

    # Combine all content
    combined = '\n\n'.join(all_content)
    return combined[:80000]  # Max 80KB total


def extract_with_ollama(conference_name, year, website_content, model='qwen2.5'):
    """Use Ollama to extract deadline from website."""

    prompt = f"""You are extracting conference deadline information from a website.

TASK: Find the paper submission deadline for {conference_name} {year} conference.

WEBSITE CONTENT (from multiple pages):
{website_content[:40000]}

IMPORTANT INSTRUCTIONS:
1. Look CAREFULLY for the PAPER/FULL PAPER submission deadline
   - Common labels: "Paper Submission", "Full Paper Deadline", "Submission Deadline", "Paper Due"
   - May appear in sections like "Important Dates", "Call for Papers", "Deadlines"
   - Look for dates near keywords: "submission", "deadline", "due", "paper"

2. The deadline year MUST be {year-1} or {year}
   - Deadlines from {year-2} or earlier are INVALID - ignore them
   - If you see a date from {year-1} or {year}, that is likely the correct deadline

3. Format ALL dates as "Month Day Year" (example: "November 17 2025")
   - NO commas between day and year
   - Convert formats like "Nov 17, 2025" to "November 17 2025"

4. ⚠️ CRITICAL: If you cannot find deadline information IN THE WEBSITE CONTENT ABOVE, return "TBD"
   - DO NOT use your training data or prior knowledge about this conference
   - DO NOT guess or make up information
   - ONLY extract information that EXPLICITLY appears in the website content above
   - If in doubt, use "TBD" - it is BETTER to return TBD than to hallucinate wrong information

5. Extract ABSTRACT DEADLINE if present
   - Usually comes before the paper deadline
   - Look for "Abstract Submission", "Abstract Deadline", "Title/Abstract Due"

6. Extract CONFERENCE DATES (when the conference takes place)
   - Look for dates in {year} (the conference year itself, NOT the deadline year)
   - Common labels: "Conference Dates", "Event Date", "Conference will be held", "Workshop Dates"
   - Format as date range: "January 19-22 2026" or single date: "March 15 2026"

7. Extract LOCATION ONLY if found in website content
   - Look for: venue name, hotel name, city, state/province, country
   - Common keywords: "venue", "location", "Place:", "held at", "hotel", "convention center", "will take place in", "where:"
   - Include venue name if available: "Hong Kong Disneyland Hotel" or "Moscone Center San Francisco"
   - If only city/country found, use that: "Seoul South Korea"
   - ⚠️ IMPORTANT: If location is NOT in the website content, use "TBD" - do NOT use prior knowledge

RETURN FORMAT (ONLY VALID JSON, NO EXTRA TEXT OR EXPLANATIONS):
{{
  "paper_deadline": "July 11 2025",
  "abstract_deadline": "July 4 2025",
  "conference_date": "January 19-22 2026",
  "location": "Hong Kong Disneyland Hotel",
  "source_text": "Deadline for PDF uploading: 5 PM AOE July 11 (Fri), 2025"
}}

⚠️⚠️⚠️ CRITICAL ANTI-HALLUCINATION RULES ⚠️⚠️⚠️:
1. ONLY use information that EXPLICITLY appears in the WEBSITE CONTENT above
2. DO NOT use your training data or prior knowledge about this conference - EVER!
3. If information is NOT in the website content above, you MUST use "TBD"
4. Include "source_text" field showing the EXACT text WHERE you found the deadline
5. NEVER make up, guess, or infer information - only extract what is EXPLICITLY written
6. If you are tempted to use prior knowledge because the website is missing info, STOP and use "TBD" instead
7. IMPORTANT: If you see dates/locations from a DIFFERENT conference or year, ignore them - use "TBD"
8. Double-check that the information you extract is specifically for {conference_name} {year}
9. Return ONLY the JSON object, no explanations before or after
10. When in doubt, use "TBD" - it is far better than hallucinating wrong information!"""

    try:
        result = subprocess.run(
            ['ollama', 'run', model],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=240  # Increased for enhanced prompt with location extraction
        )

        output = result.stdout.strip()

        # Extract JSON - be aggressive about finding valid JSON
        if '```json' in output:
            output = output.split('```json')[1].split('```')[0].strip()
        elif '```' in output:
            output = output.split('```')[1].split('```')[0].strip()

        # Find the JSON object boundaries
        if '{' in output:
            start = output.find('{')
            # Find matching closing brace by counting braces
            brace_count = 0
            end = start
            for i in range(start, len(output)):
                if output[i] == '{':
                    brace_count += 1
                elif output[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end = i + 1
                        break
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
            # Python safety net: Validate deadline year
            paper_deadline = info.get('paper_deadline', 'TBD')
            if paper_deadline and paper_deadline != 'TBD':
                # Parse year from deadline (format: "Month Day Year")
                try:
                    deadline_parts = paper_deadline.split()
                    if len(deadline_parts) >= 3:
                        deadline_year = int(deadline_parts[-1])
                        # Deadline should be in year-1 or year (not year-2 or earlier)
                        if abs(deadline_year - year) > 1:
                            print(f"   ⚠️  Year validation failed: deadline {paper_deadline} invalid for {year} conference")
                            print(f"   ⚠️  Setting deadline to TBD (expected {year-1} or {year}, got {deadline_year})")
                            info['paper_deadline'] = 'TBD'
                            info['abstract_deadline'] = ''
                except (ValueError, IndexError):
                    # If we can't parse the year, keep the deadline as-is
                    pass

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
        for conference in results:
            # Clean up dates - remove commas before year
            paper_deadline = conference.get('paper_deadline', 'TBD')
            if paper_deadline and paper_deadline != 'TBD':
                paper_deadline = paper_deadline.replace(', ', ' ')

            abstract_deadline = conference.get('abstract_deadline', '')
            if abstract_deadline and abstract_deadline not in ['None', 'null']:
                abstract_deadline = abstract_deadline.replace(', ', ' ')
            else:
                abstract_deadline = ''

            conference_date = conference.get('conference_date', '')
            if conference_date and conference_date not in ['None', 'null']:
                conference_date = conference_date.replace(', ', ' ')
            else:
                conference_date = ''

            location = conference.get('location', '')
            if location and location not in ['None', 'null']:
                location = location.replace(', ', ' ')
            else:
                location = ''

            csv_line = f"{conference['conference_name']},{conference['year']},{paper_deadline},{conference['url']},Regular Paper,{conference_date},{abstract_deadline},{location}"
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
                        choices=['qwen2.5', 'qwen3:4b', 'qwen3:8b', 'qwen3:14b', 'mistral', 'llama3.1', 'llama3.2'],
                        help='Ollama model (default: qwen2.5)')

    args = parser.parse_args()

    conferences = [c.strip() for c in args.conferences.split(',')]

    extract_conferences(conferences, args.year, args.model)
