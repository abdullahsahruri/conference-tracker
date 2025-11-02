#!/usr/bin/env python3
"""
AI-Powered Conference Information Extractor (Ollama Version)
============================================================

Uses Ollama with local LLM models for FREE conference deadline extraction.
No API keys, no costs, unlimited usage!

Supported models:
- llama3.2 (recommended - fast and accurate)
- llama3.1 (larger, more capable)
- mistral (good alternative)
- qwen2.5 (multilingual support)
"""

import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Optional, Dict

# Import deadline validator
try:
    from deadline_validator import validate_extracted_info, check_deadline_context
except ImportError:
    # Validator not available, continue without validation
    validate_extracted_info = None
    check_deadline_context = None

# Ollama API endpoint (runs locally)
OLLAMA_API = "http://localhost:11434/api/generate"


def check_ollama_running() -> bool:
    """Check if Ollama is running locally."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False


def get_available_models() -> list:
    """Get list of installed Ollama models."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            data = response.json()
            return [model['name'] for model in data.get('models', [])]
        return []
    except:
        return []


def fetch_conference_website(url: str) -> Optional[str]:
    """Fetch conference website HTML."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        # Extract text content
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

        # Limit to first 6000 characters (local models have smaller context)
        return text[:6000]
    except Exception as e:
        print(f"  ❌ Error fetching {url}: {str(e)[:100]}")
        return None


def extract_with_ollama(website_text: str, conference_name: str, url: str,
                       model: str = "llama3.2") -> Optional[Dict]:
    """
    Use Ollama to extract conference information.

    Args:
        website_text: Website content
        conference_name: Conference name
        url: Conference URL
        model: Ollama model to use (default: llama3.2)

    Returns:
        Dictionary with extracted information or None
    """
    prompt = f"""Analyze this conference website and extract deadline information.

Conference: {conference_name}
Website: {url}

Website Content:
{website_text}

Extract the following information and respond with ONLY valid JSON (no other text):
{{
    "paper_deadline": "exact deadline date if found (e.g., 'March 15, 2025') or 'TBD'",
    "submission_type": "Regular Paper, Abstract, Late Breaking Results, Poster, or Workshop",
    "conference_date": "conference dates or null",
    "abstract_deadline": "abstract deadline or null",
    "location": "city/country or null"
}}

IMPORTANT:
- Extract the PAPER SUBMISSION deadline, NOT notification/acceptance/camera-ready dates
- Look for keywords: "paper deadline", "submission deadline", "abstract deadline", "call for papers"
- IGNORE keywords: "notification", "acceptance", "camera ready", "final version", "author notification"
- If multiple deadlines exist, choose the EARLIEST submission-related deadline
Return ONLY the JSON object."""

    try:
        # Call Ollama API
        response = requests.post(
            OLLAMA_API,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,  # Low temperature for factual extraction
                    "num_predict": 300,  # Limit response length
                }
            },
            timeout=60  # Local models can be slower
        )

        if response.status_code != 200:
            print(f"  ❌ Ollama API error: {response.status_code}")
            return None

        # Parse response
        result = response.json()
        response_text = result.get('response', '').strip()

        # Extract JSON from response (model might add extra text)
        # Find JSON object between { and }
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1

        if json_start == -1 or json_end == 0:
            print(f"  ⚠️  No JSON found in response")
            return None

        json_str = response_text[json_start:json_end]

        # Parse JSON
        info = json.loads(json_str)

        # Add metadata
        info['name'] = conference_name
        info['url'] = url
        info['last_checked'] = datetime.now().isoformat()
        info['extracted_with_ai'] = True
        info['ai_model'] = model

        # Validate deadline is not notification/camera-ready date
        if validate_extracted_info:
            is_valid, reason, corrected = validate_extracted_info(info)
            if not is_valid:
                print(f"  ⚠️  Validation failed: {reason}")
                if corrected:
                    print(f"  🔧 Using corrected info")
                    info = corrected
                else:
                    print(f"  ❌ Cannot auto-correct, skipping")
                    return None

        # Validate we got at least a deadline
        if info.get('paper_deadline') and info['paper_deadline'] != 'TBD':
            return info
        else:
            return None

    except json.JSONDecodeError as e:
        print(f"  ❌ Invalid JSON from model: {str(e)[:100]}")
        return None
    except Exception as e:
        print(f"  ❌ Ollama extraction error: {str(e)[:100]}")
        return None


def extract_conference_info_with_ollama(url: str, conference_name: str,
                                       model: str = "llama3.2") -> Optional[Dict]:
    """
    Use Ollama to extract conference information from website.

    Args:
        url: Conference website URL
        conference_name: Expected conference name
        model: Ollama model to use

    Returns:
        Dictionary with extracted information or None
    """
    # Check Ollama is running
    if not check_ollama_running():
        print("  ⚠️  Ollama not running!")
        print("  ℹ️  Start Ollama: ollama serve")
        return None

    print(f"  🤖 Using Ollama ({model}) to analyze {url[:60]}...")

    # Fetch website content
    website_text = fetch_conference_website(url)
    if not website_text:
        return None

    # Extract with Ollama
    info = extract_with_ollama(website_text, conference_name, url, model)

    if info:
        print(f"  ✅ Ollama extracted: {info['paper_deadline']} ({info.get('submission_type', 'Regular Paper')})")
        return info
    else:
        print(f"  ⚠️  Ollama could not find deadline")
        return None


def search_conference_with_ollama(conference_name: str, year: int,
                                 model: str = "llama3.2") -> Optional[Dict]:
    """
    Search for a conference and extract info using Ollama.

    Args:
        conference_name: Conference acronym
        year: Conference year
        model: Ollama model to use

    Returns:
        Dictionary with conference information or None
    """
    from conference_tracker import search_conference

    print(f"\n→ Processing: {conference_name} {year}")

    # Find the conference URL
    print(f"  🔍 Searching for {conference_name} {year}...")
    url = search_conference(conference_name, year)

    if not url:
        return None

    print(f"  ✓ Found: {url[:60]}...")

    # Use Ollama to extract information
    return extract_conference_info_with_ollama(url, f"{conference_name} {year}", model)


def main():
    """Test Ollama-powered extraction."""
    print("=" * 70)
    print("AI-Powered Conference Extractor (Ollama - FREE VERSION)")
    print("=" * 70)

    # Check Ollama
    if not check_ollama_running():
        print("\n❌ Ollama is not running!")
        print("\nTo start Ollama:")
        print("  1. Install: https://ollama.ai/")
        print("  2. Run: ollama serve")
        print("  3. Pull model: ollama pull llama3.2")
        print("\n" + "=" * 70)
        return

    # List available models
    models = get_available_models()
    print(f"\n✅ Ollama is running!")
    print(f"📦 Available models: {', '.join(models) if models else 'None'}")

    if not models:
        print("\n⚠️  No models installed!")
        print("Install a model: ollama pull llama3.2")
        return

    # Select model (prefer llama3.2)
    model = "llama3.2" if "llama3.2" in models else models[0]
    print(f"🤖 Using model: {model}")

    # Test with a few conferences
    test_conferences = [
        ("ISCA", 2026),
        ("MICRO", 2025),
    ]

    results = []
    for conf_name, year in test_conferences:
        result = search_conference_with_ollama(conf_name, year, model)
        if result:
            results.append(result)

    print("\n" + "=" * 70)
    print(f"✅ Successfully extracted {len(results)} conferences (100% FREE!)")
    print("=" * 70)

    # Show sample result
    if results:
        print("\nSample result:")
        print(json.dumps(results[0], indent=2))


if __name__ == '__main__':
    main()
