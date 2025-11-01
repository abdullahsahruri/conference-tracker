#!/usr/bin/env python3
"""
Official Conference Source Scrapers
====================================

Scrapes conference deadlines from official aggregator sites:
- ACM: https://www.acm.org/conferences/upcoming-submission-deadlines
- IEEE: https://conferences.ieee.org/

These are more reliable than web search since they're maintained
by the professional organizations.
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
from typing import List, Dict, Optional


def scrape_acm_conferences() -> List[Dict]:
    """
    Scrape upcoming conferences from ACM's official deadlines page.

    Returns:
        List of conference dictionaries with name, url, deadline
    """
    conferences = []

    try:
        # ACM upcoming submission deadlines page
        url = 'https://www.acm.org/conferences/upcoming-submission-deadlines'

        print("  → Scraping ACM conferences...")

        response = requests.get(url, timeout=15, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # ACM uses <div class="event"> for each conference
        events = soup.find_all('div', class_='event')

        print(f"  → Found {len(events)} ACM events")

        for event in events:
            try:
                # Extract conference name
                title_elem = event.find('h5') or event.find('h4') or event.find('a')
                if not title_elem:
                    continue

                conf_name = title_elem.get_text().strip()

                # Extract URL
                link = event.find('a', href=True)
                conf_url = link['href'] if link else None
                if conf_url and not conf_url.startswith('http'):
                    conf_url = 'https://www.acm.org' + conf_url

                # Extract deadline - look in event-time or event-desc
                deadline_elem = event.find('div', class_='event-time')
                if not deadline_elem:
                    deadline_elem = event.find('div', class_='event-desc')

                if deadline_elem:
                    deadline_text = deadline_elem.get_text().strip()

                    # Try to extract date from text
                    date_patterns = [
                        r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4}\b',
                        r'\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b',
                        r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
                    ]

                    paper_deadline = None
                    for pattern in date_patterns:
                        match = re.search(pattern, deadline_text, re.IGNORECASE)
                        if match:
                            paper_deadline = match.group()
                            break

                    if paper_deadline and conf_name:
                        conferences.append({
                            'name': conf_name,
                            'url': conf_url or url,
                            'paper_deadline': paper_deadline,
                            'conference_date': None,
                            'source': 'ACM',
                            'last_checked': datetime.now().isoformat()
                        })

            except Exception as e:
                print(f"    ⚠️  Error parsing ACM event: {str(e)[:50]}")
                continue

        print(f"  ✓ Extracted {len(conferences)} ACM conferences with deadlines")

    except Exception as e:
        print(f"  ❌ Error scraping ACM: {str(e)[:100]}")

    return conferences


def scrape_ieee_conferences() -> List[Dict]:
    """
    Scrape upcoming conferences from IEEE's conference calendar.

    Returns:
        List of conference dictionaries with name, url, deadline
    """
    conferences = []

    try:
        # IEEE conference calendar
        url = 'https://conferences.ieee.org/conferences/calendar/'

        print("  → Scraping IEEE conferences...")

        response = requests.get(url, timeout=15, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # IEEE may use various structures - try multiple approaches

        # Approach 1: Look for conference listings in tables
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')[1:]  # Skip header

            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 3:
                    # Typical format: [Conference Name, Date, Location, ...]
                    conf_name_cell = cells[0]
                    conf_name = conf_name_cell.get_text().strip()

                    # Get conference URL
                    link = conf_name_cell.find('a', href=True)
                    conf_url = link['href'] if link else None
                    if conf_url and not conf_url.startswith('http'):
                        conf_url = 'https://conferences.ieee.org' + conf_url

                    # Try to find deadline in other cells
                    deadline = None
                    for cell in cells[1:]:
                        cell_text = cell.get_text().strip()
                        # Look for "deadline" keyword
                        if 'deadline' in cell_text.lower() or 'submission' in cell_text.lower():
                            # Extract date
                            date_patterns = [
                                r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4}\b',
                                r'\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b',
                            ]
                            for pattern in date_patterns:
                                match = re.search(pattern, cell_text, re.IGNORECASE)
                                if match:
                                    deadline = match.group()
                                    break

                    if conf_name and conf_url:
                        conferences.append({
                            'name': conf_name,
                            'url': conf_url,
                            'paper_deadline': deadline or 'TBD',
                            'conference_date': None,
                            'source': 'IEEE',
                            'last_checked': datetime.now().isoformat()
                        })

        # Approach 2: Look for div-based listings
        conf_divs = soup.find_all('div', class_=lambda x: x and ('conference' in str(x).lower() or 'event' in str(x).lower()))

        for div in conf_divs[:50]:  # Limit to first 50
            try:
                # Extract name
                title = div.find(['h2', 'h3', 'h4', 'h5', 'a'])
                if not title:
                    continue

                conf_name = title.get_text().strip()

                # Extract URL
                link = div.find('a', href=True)
                conf_url = link['href'] if link else None
                if conf_url and not conf_url.startswith('http'):
                    if conf_url.startswith('/'):
                        conf_url = 'https://conferences.ieee.org' + conf_url
                    else:
                        conf_url = 'https://' + conf_url

                # Look for deadline
                div_text = div.get_text()
                deadline = None

                if 'deadline' in div_text.lower() or 'submission' in div_text.lower():
                    date_patterns = [
                        r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4}\b',
                        r'\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b',
                    ]
                    for pattern in date_patterns:
                        match = re.search(pattern, div_text, re.IGNORECASE)
                        if match:
                            deadline = match.group()
                            break

                if conf_name and conf_url and deadline:
                    # Check if not duplicate
                    if not any(c['name'] == conf_name for c in conferences):
                        conferences.append({
                            'name': conf_name,
                            'url': conf_url,
                            'paper_deadline': deadline,
                            'conference_date': None,
                            'source': 'IEEE',
                            'last_checked': datetime.now().isoformat()
                        })

            except Exception as e:
                continue

        print(f"  ✓ Extracted {len(conferences)} IEEE conferences")

    except Exception as e:
        print(f"  ❌ Error scraping IEEE: {str(e)[:100]}")

    return conferences


def scrape_all_official_sources() -> List[Dict]:
    """
    Scrape conferences from all official sources.

    Returns:
        Combined list of conferences from ACM and IEEE
    """
    print("\n" + "=" * 70)
    print("Scraping Official Conference Sources")
    print("=" * 70)

    all_conferences = []

    # Scrape ACM
    print("\n→ ACM Conferences")
    acm_confs = scrape_acm_conferences()
    all_conferences.extend(acm_confs)

    # Scrape IEEE
    print("\n→ IEEE Conferences")
    ieee_confs = scrape_ieee_conferences()
    all_conferences.extend(ieee_confs)

    print("\n" + "=" * 70)
    print(f"Total conferences from official sources: {len(all_conferences)}")
    print("=" * 70)

    return all_conferences


if __name__ == '__main__':
    # Test the scrapers
    conferences = scrape_all_official_sources()

    print("\nSample conferences found:")
    for conf in conferences[:10]:
        print(f"  • {conf['name']}")
        print(f"    Deadline: {conf['paper_deadline']}")
        print(f"    URL: {conf['url'][:60]}...")
        print()
