#!/usr/bin/env python3
"""
AI-Powered Conference Information Extractor
===========================================

Uses Claude AI to intelligently extract conference deadlines and information
from websites. Much more accurate than regex-based parsing.
"""

import os
import json
import anthropic
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Optional, Dict

# Initialize Anthropic client
def get_anthropic_client():
    """Get Anthropic API client. Requires ANTHROPIC_API_KEY environment variable."""
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")
    return anthropic.Anthropic(api_key=api_key)


def fetch_conference_website(url: str) -> Optional[str]:
    """Fetch conference website HTML."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        # Extract text content (Claude doesn't need HTML tags)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Get text
        text = soup.get_text()

        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)

        # Limit to first 8000 characters to stay within token limits
        return text[:8000]
    except Exception as e:
        print(f"  ❌ Error fetching {url}: {str(e)[:100]}")
        return None


def extract_conference_info_with_ai(url: str, conference_name: str) -> Optional[Dict]:
    """
    Use Claude AI to extract conference information from website.

    Args:
        url: Conference website URL
        conference_name: Expected conference name

    Returns:
        Dictionary with extracted information or None
    """
    print(f"  🤖 Using AI to analyze {url[:60]}...")

    # Fetch website content
    website_text = fetch_conference_website(url)
    if not website_text:
        return None

    # Get AI client
    try:
        client = get_anthropic_client()
    except ValueError as e:
        print(f"  ⚠️  {e}")
        print("  ℹ️  Set ANTHROPIC_API_KEY to use AI extraction")
        return None

    # Craft prompt for Claude
    prompt = f"""Analyze this conference website and extract structured information.

Conference: {conference_name}
Website URL: {url}

Website Content:
{website_text}

Please extract the following information and respond ONLY with valid JSON:
{{
    "paper_deadline": "exact deadline date if found (e.g., 'March 15, 2025' or 'TBD' if not found)",
    "submission_type": "type of submission (Regular Paper, Abstract, Late Breaking Results, Poster, Short Paper, Workshop/WIP, or Regular Paper if unclear)",
    "conference_date": "conference dates if found (e.g., 'June 10-13, 2025' or null)",
    "abstract_deadline": "abstract deadline if different from paper deadline (or null)",
    "notification_date": "notification date if found (or null)",
    "camera_ready": "camera ready deadline if found (or null)",
    "location": "conference location/city if found (or null)",
    "notes": "any important notes about deadlines or submission types"
}}

Important:
- Look for keywords like "deadline", "submission", "important dates", "call for papers"
- Distinguish between abstract deadlines and full paper deadlines
- Identify submission type from context (late breaking, poster, workshop, etc.)
- Return ONLY the JSON object, no additional text"""

    try:
        # Call Claude API
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Parse response
        response_text = message.content[0].text.strip()

        # Remove markdown code blocks if present
        if response_text.startswith('```json'):
            response_text = response_text.split('```json')[1].split('```')[0].strip()
        elif response_text.startswith('```'):
            response_text = response_text.split('```')[1].split('```')[0].strip()

        # Parse JSON
        info = json.loads(response_text)

        # Add metadata
        info['name'] = conference_name
        info['url'] = url
        info['last_checked'] = datetime.now().isoformat()
        info['extracted_with_ai'] = True

        # Validate we got at least a deadline
        if info.get('paper_deadline') and info['paper_deadline'] != 'TBD':
            print(f"  ✅ AI extracted: {info['paper_deadline']} ({info.get('submission_type', 'Regular Paper')})")
            return info
        else:
            print(f"  ⚠️  AI could not find deadline in website")
            return None

    except json.JSONDecodeError as e:
        print(f"  ❌ AI response was not valid JSON: {str(e)[:100]}")
        print(f"  Response: {response_text[:200]}")
        return None
    except Exception as e:
        print(f"  ❌ AI extraction error: {str(e)[:100]}")
        return None


def search_conference_with_ai(conference_name: str, year: int) -> Optional[Dict]:
    """
    Search for a conference and extract info using AI.

    Args:
        conference_name: Conference acronym (e.g., "ISCA")
        year: Conference year (e.g., 2026)

    Returns:
        Dictionary with conference information or None
    """
    from conference_tracker import search_conference

    print(f"\n→ Processing: {conference_name} {year}")

    # First, find the conference URL using existing search
    print(f"  🔍 Searching for {conference_name} {year}...")
    url = search_conference(conference_name, year)

    if not url:
        return None

    print(f"  ✓ Found: {url[:60]}...")

    # Use AI to extract information
    return extract_conference_info_with_ai(url, f"{conference_name} {year}")


def main():
    """Test the AI-powered extraction."""
    print("=" * 70)
    print("AI-Powered Conference Information Extractor")
    print("=" * 70)

    # Check for API key
    if not os.environ.get('ANTHROPIC_API_KEY'):
        print("\n⚠️  ANTHROPIC_API_KEY not set!")
        print("\nTo use AI extraction:")
        print("1. Get API key from: https://console.anthropic.com/")
        print("2. Set environment variable:")
        print("   export ANTHROPIC_API_KEY='your-api-key-here'")
        print("\n" + "=" * 70)
        return

    # Test with a few conferences
    test_conferences = [
        ("ISCA", 2026),
        ("MICRO", 2025),
        ("DAC", 2025),
    ]

    results = []
    for conf_name, year in test_conferences:
        result = search_conference_with_ai(conf_name, year)
        if result:
            results.append(result)

    print("\n" + "=" * 70)
    print(f"✅ Successfully extracted {len(results)} conferences using AI")
    print("=" * 70)

    # Show sample result
    if results:
        print("\nSample result:")
        print(json.dumps(results[0], indent=2))


if __name__ == '__main__':
    main()
