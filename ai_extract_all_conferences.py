#!/usr/bin/env python3
"""
AI Conference Deadline Extractor - Comprehensive Edition
=========================================================

Automatically extracts deadlines for ALL major computer architecture,
VLSI, circuits, design automation, and hardware conferences.

Uses AI to search the web and extract actual conference deadlines.

Usage:
    python3 ai_extract_all_conferences.py
    python3 ai_extract_all_conferences.py --year 2025
    python3 ai_extract_all_conferences.py --category "Architecture"
    python3 ai_extract_all_conferences.py --conferences "ISCA,DAC,MICRO"
"""

import subprocess
import json
import sys
import argparse
import requests
from datetime import datetime
from urllib.parse import quote_plus


# Comprehensive conference database covering all major venues
KNOWN_CONFERENCES = {
    # Computer Architecture - Top Tier
    "ISCA": {"name": "International Symposium on Computer Architecture", "category": "Architecture"},
    "MICRO": {"name": "International Symposium on Microarchitecture", "category": "Architecture"},
    "HPCA": {"name": "International Symposium on High-Performance Computer Architecture", "category": "Architecture"},
    "ASPLOS": {"name": "Architectural Support for Programming Languages and Operating Systems", "category": "Architecture"},
    "ICCD": {"name": "International Conference on Computer Design", "category": "Architecture"},
    "ICS": {"name": "International Conference on Supercomputing", "category": "Architecture"},
    "PACT": {"name": "International Conference on Parallel Architectures and Compilation Techniques", "category": "Architecture"},
    "CGO": {"name": "International Symposium on Code Generation and Optimization", "category": "Architecture"},

    # VLSI & Circuits - Top Tier
    "ISSCC": {"name": "International Solid-State Circuits Conference", "category": "VLSI/Circuits"},
    "VLSI": {"name": "VLSI Symposia (Circuits and Technology)", "category": "VLSI/Circuits"},
    "CICC": {"name": "Custom Integrated Circuits Conference", "category": "VLSI/Circuits"},
    "ESSCIRC": {"name": "European Solid-State Circuits Conference", "category": "VLSI/Circuits"},
    "GLSVLSI": {"name": "Great Lakes Symposium on VLSI", "category": "VLSI/Circuits"},
    "ISCAS": {"name": "International Symposium on Circuits and Systems", "category": "VLSI/Circuits"},
    "A-SSCC": {"name": "Asian Solid-State Circuits Conference", "category": "VLSI/Circuits"},
    "RFIC": {"name": "Radio Frequency Integrated Circuits Symposium", "category": "VLSI/Circuits"},

    # Design Automation - Top Tier
    "DAC": {"name": "Design Automation Conference", "category": "Design Automation"},
    "ICCAD": {"name": "International Conference on Computer-Aided Design", "category": "Design Automation"},
    "DATE": {"name": "Design, Automation & Test in Europe", "category": "Design Automation"},
    "ASPDAC": {"name": "Asia and South Pacific Design Automation Conference", "category": "Design Automation"},
    "ISPD": {"name": "International Symposium on Physical Design", "category": "Design Automation"},
    "CODES+ISSS": {"name": "International Conference on Hardware/Software Codesign and System Synthesis", "category": "Design Automation"},

    # Power & Energy
    "ISLPED": {"name": "International Symposium on Low Power Electronics and Design", "category": "Power/Energy"},

    # FPGA & Reconfigurable Computing
    "FPGA": {"name": "ACM/SIGDA International Symposium on Field-Programmable Gate Arrays", "category": "FPGA"},
    "FCCM": {"name": "IEEE Symposium on Field-Programmable Custom Computing Machines", "category": "FPGA"},
    "FPL": {"name": "International Conference on Field Programmable Logic and Applications", "category": "FPGA"},
    "FPT": {"name": "International Conference on Field-Programmable Technology", "category": "FPGA"},

    # Testing & Verification
    "ITC": {"name": "International Test Conference", "category": "Testing"},
    "VTS": {"name": "VLSI Test Symposium", "category": "Testing"},
    "ATS": {"name": "Asian Test Symposium", "category": "Testing"},
    "ETS": {"name": "European Test Symposium", "category": "Testing"},
    "DATE-TEST": {"name": "DATE Test Track", "category": "Testing"},

    # Systems - Top Tier
    "SOSP": {"name": "Symposium on Operating Systems Principles", "category": "Systems"},
    "OSDI": {"name": "USENIX Symposium on Operating Systems Design and Implementation", "category": "Systems"},
    "EUROSYS": {"name": "European Conference on Computer Systems", "category": "Systems"},
    "ATC": {"name": "USENIX Annual Technical Conference", "category": "Systems"},
    "FAST": {"name": "USENIX Conference on File and Storage Technologies", "category": "Systems"},
    "NSDI": {"name": "USENIX Symposium on Networked Systems Design and Implementation", "category": "Systems"},

    # Hardware Security
    "HOST": {"name": "Hardware Oriented Security and Trust", "category": "Security"},
    "CHES": {"name": "Cryptographic Hardware and Embedded Systems", "category": "Security"},

    # Emerging Technologies & Hot Topics
    "HOTCHIPS": {"name": "Hot Chips: A Symposium on High Performance Chips", "category": "Emerging"},
    "HOTOS": {"name": "Workshop on Hot Topics in Operating Systems", "category": "Emerging"},
    "ISPASS": {"name": "IEEE International Symposium on Performance Analysis of Systems and Software", "category": "Performance"},
    "IISWC": {"name": "IEEE International Symposium on Workload Characterization", "category": "Performance"},

    # Memory & Storage
    "MEMSYS": {"name": "International Symposium on Memory Systems", "category": "Memory/Storage"},
    "IMW": {"name": "IEEE International Memory Workshop", "category": "Memory/Storage"},

    # AI/ML Hardware
    "MLSys": {"name": "Conference on Machine Learning and Systems", "category": "AI/ML Hardware"},
    "MLCAD": {"name": "International Workshop on Machine Learning for CAD", "category": "AI/ML Hardware"},

    # Embedded Systems
    "EMSOFT": {"name": "International Conference on Embedded Software", "category": "Embedded"},
    "RTAS": {"name": "Real-Time and Embedded Technology and Applications Symposium", "category": "Embedded"},
    "RTSS": {"name": "Real-Time Systems Symposium", "category": "Embedded"},
    "CASES": {"name": "International Conference on Compilers, Architecture, and Synthesis for Embedded Systems", "category": "Embedded"},

    # Additional Important Venues
    "ISQED": {"name": "International Symposium on Quality Electronic Design", "category": "Design Automation"},
    "ISVLSI": {"name": "IEEE Computer Society Annual Symposium on VLSI", "category": "VLSI/Circuits"},
    "PATMOS": {"name": "International Workshop on Power and Timing Modeling, Optimization and Simulation", "category": "Power/Energy"},
}


def search_conference_website(conference_name, year):
    """Search for conference website using DuckDuckGo with improved URL filtering."""

    # Comprehensive fallback URLs (use these first for known conferences)
    common_patterns = {
        # Architecture
        'ISCA': f'https://iscaconf.org/isca{year}',
        'MICRO': f'https://microarch.org/micro{int(year)-1967}',
        'HPCA': f'https://hpca-conf.org/{year}',
        'ASPLOS': f'https://asplos-conference.org/asplos{year}',
        'ICCD': f'https://www.iccd-conf.com',
        'ICS': f'https://ics-conference.org',
        'PACT': f'https://pactconf.org',
        'CGO': f'https://{year}.cgo.org',

        # VLSI/Circuits
        'ISSCC': f'https://isscc.org',
        'VLSI': f'https://vlsisymposium.org',
        'CICC': f'https://ieee-cicc.org',
        'ESSCIRC': f'https://www.esscirc-essderc{year}.org',
        'GLSVLSI': f'https://www.glsvlsi.org',
        'ISCAS': f'https://iscas{year}.org',

        # Design Automation
        'DAC': f'https://www.dac.com',
        'ICCAD': f'https://iccad.com',
        'DATE': f'https://www.date-conference.com',
        'ASPDAC': f'https://www.aspdac.com/aspdac{year}',
        'ISPD': f'https://ispd.cc',

        # FPGA
        'FPGA': f'https://www.isfpga.org',
        'FCCM': f'https://www.fccm.org',

        # Systems
        'SOSP': f'https://sigops.org/s/conferences/sosp/{year}',
        'OSDI': f'https://www.usenix.org/conference/osdi{year % 100}',
        'EUROSYS': f'https://{year}.eurosys.org',

        # Testing
        'ITC': f'https://www.itctestweek.org',
        'VTS': f'https://tttc-vts.org',

        # Security
        'HOST': f'https://www.hostsymposium.org',
        'CHES': f'https://ches.iacr.org/{year}',

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
    print("AI CONFERENCE DEADLINE EXTRACTOR - COMPREHENSIVE EDITION")
    print("=" * 80)
    print(f"\n🤖 Using model: {model}")
    print(f"📅 Target year: {year}")
    print(f"📋 Conferences: {len(conference_list)} total\n")

    results = []
    success_count = 0
    failed_count = 0

    for conf_name in conference_list:
        conf_info = KNOWN_CONFERENCES.get(conf_name, {})
        category = conf_info.get('category', 'Unknown')
        full_name = conf_info.get('name', conf_name)

        print(f"\n{'='*80}")
        print(f"Processing {conf_name} {year} - {category}")
        print(f"{full_name}")
        print(f"{'='*80}")

        # Step 1: Search for website
        print(f"1️⃣  Searching for {conf_name} {year} website...")
        url = search_conference_website(conf_name, year)
        if not url:
            print(f"   ❌ Could not find website")
            failed_count += 1
            continue
        print(f"   ✅ Found: {url}")

        # Step 2: Fetch content
        print(f"2️⃣  Fetching website content...")
        content = fetch_website_content(url)
        if not content:
            print(f"   ❌ Could not fetch content")
            failed_count += 1
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
                'category': category,
                'full_name': full_name,
                **info
            })
            success_count += 1
        else:
            print(f"   ❌ Extraction failed")
            failed_count += 1

    # Output CSV grouped by category
    print(f"\n\n{'='*80}")
    print("RESULTS - Grouped by Category")
    print(f"{'='*80}\n")

    if results:
        # Group by category
        conferences_by_category = {}
        for conference_result in results:
            category_name = conference_result.get('category', 'Other')
            if category_name not in conferences_by_category:
                conferences_by_category[category_name] = []
            conferences_by_category[category_name].append(conference_result)

        # Print by category
        for category_name in sorted(conferences_by_category.keys()):
            print(f"\n## {category_name}")
            print("#" * 80)
            print()

            for conference in conferences_by_category[category_name]:
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
                    # Simplify location: keep city and state/country abbreviation
                    location = location.replace(', ', ' ')
                else:
                    location = ''

                csv_line = f"{conference['conference_name']},{conference['year']},{paper_deadline},{conference['url']},Regular Paper,{conference_date},{abstract_deadline},{location}"
                print(f"{csv_line}  # {conference['full_name']}")

        print(f"\n\n{'='*80}")
        print(f"SUMMARY")
        print(f"{'='*80}")
        print(f"✅ Successfully extracted: {success_count}/{len(conference_list)} conferences")
        print(f"❌ Failed: {failed_count}/{len(conference_list)} conferences")
        print(f"{'='*80}\n")
    else:
        print("❌ No conferences extracted")

    print("\nNext steps:")
    print("1. Copy the CSV lines from the categories you want above")
    print("2. Paste into my_conferences.csv")
    print("3. Run: ./csv import my_conferences.csv\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='AI-powered conference deadline extraction for ALL major conferences',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract all conferences for next year (default)
  python3 ai_extract_all_conferences.py

  # Extract all conferences for 2025
  python3 ai_extract_all_conferences.py --year 2025

  # Extract only Architecture conferences
  python3 ai_extract_all_conferences.py --category Architecture

  # Extract only VLSI/Circuits conferences
  python3 ai_extract_all_conferences.py --category "VLSI/Circuits"

  # Extract specific conferences
  python3 ai_extract_all_conferences.py --conferences "ISCA,DAC,MICRO,ISSCC"

Available categories:
  Architecture, VLSI/Circuits, Design Automation, Power/Energy, FPGA,
  Testing, Systems, Security, Emerging, Performance, Memory/Storage,
  AI/ML Hardware, Embedded
        """
    )

    parser.add_argument('--conferences', '-c',
                        help='Comma-separated conference names (default: all conferences)')
    parser.add_argument('--category', '-cat',
                        help='Extract only conferences from this category')
    parser.add_argument('--year', '-y', type=int,
                        default=datetime.now().year + 1,
                        help='Target year (default: next year)')
    parser.add_argument('--model', '-m', default='qwen2.5',
                        choices=['qwen2.5', 'qwen3:4b', 'qwen3:8b', 'qwen3:14b', 'mistral', 'llama3.1', 'llama3.2'],
                        help='Ollama model (default: qwen2.5)')
    parser.add_argument('--list-categories', action='store_true',
                        help='List all available categories and exit')
    parser.add_argument('--list-conferences', action='store_true',
                        help='List all conferences by category and exit')

    args = parser.parse_args()

    # List categories
    if args.list_categories:
        categories = sorted(set(info['category'] for info in KNOWN_CONFERENCES.values()))
        print("\nAvailable Categories:")
        print("=" * 80)
        for cat in categories:
            count = sum(1 for info in KNOWN_CONFERENCES.values() if info['category'] == cat)
            print(f"  {cat:<25} ({count} conferences)")
        print()
        sys.exit(0)

    # List all conferences
    if args.list_conferences:
        by_category = {}
        for acronym, info in KNOWN_CONFERENCES.items():
            cat = info['category']
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append((acronym, info['name']))

        print("\nAll Conferences by Category:")
        print("=" * 80)
        for cat in sorted(by_category.keys()):
            print(f"\n{cat}:")
            print("-" * 80)
            for acronym, name in sorted(by_category[cat]):
                print(f"  {acronym:<15} {name}")
        print()
        sys.exit(0)

    # Determine conference list
    if args.conferences:
        conferences = [c.strip() for c in args.conferences.split(',')]
    elif args.category:
        conferences = [
            acronym for acronym, info in KNOWN_CONFERENCES.items()
            if info['category'] == args.category
        ]
        if not conferences:
            print(f"❌ No conferences found in category '{args.category}'")
            print("\nRun with --list-categories to see available categories")
            sys.exit(1)
    else:
        # Default: all conferences
        conferences = list(KNOWN_CONFERENCES.keys())

    extract_conferences(conferences, args.year, args.model)
