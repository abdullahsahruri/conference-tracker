#!/usr/bin/env python3
"""
Date Normalizer
===============

Normalizes various date formats to a consistent format: "Month Day, Year"
Example: "November 10, 2025"
"""

from datetime import datetime
import re
from typing import Optional


def normalize_date(date_str: str) -> str:
    """
    Normalize a date string to consistent format: "Month Day, Year"

    Handles formats like:
    - "November 10, 2025" -> "November 10, 2025"
    - "Nov 10, 2025" -> "November 10, 2025"
    - "2025-11-10" -> "November 10, 2025"
    - "10 November 2025" -> "November 10, 2025"
    - "11/10/2025" -> "November 10, 2025"
    - "Fri 7 Nov 2025" -> "November 7, 2025"
    - "April 11, 2025 at 11:59 PM EDT" -> "April 11, 2025"
    - "October 28, 2024 (FIRM)" -> "October 28, 2024"

    Args:
        date_str: Date string to normalize

    Returns:
        Normalized date string in format "Month Day, Year"
    """
    if not date_str or date_str == 'TBD':
        return date_str

    # Remove extra info like time, timezone, notes in parentheses
    cleaned = re.sub(r'\s+at\s+\d+:\d+.*$', '', date_str, flags=re.IGNORECASE)
    cleaned = re.sub(r'\s*\([^)]*\)', '', cleaned)  # Remove (FIRM), (No Extensions), etc.
    cleaned = re.sub(r'\s*;.*$', '', cleaned)  # Remove ; 23:59 PT
    cleaned = cleaned.strip()

    # Try various date formats
    date_formats = [
        '%B %d, %Y',           # November 10, 2025
        '%b %d, %Y',           # Nov 10, 2025
        '%Y-%m-%d',            # 2025-11-10
        '%d %B %Y',            # 10 November 2025
        '%d %b %Y',            # 10 Nov 2025
        '%m/%d/%Y',            # 11/10/2025
        '%B %d %Y',            # November 10 2025 (no comma)
        '%b %d %Y',            # Nov 10 2025
        '%d %B, %Y',           # 10 November, 2025
        '%d %b, %Y',           # 10 Nov, 2025
    ]

    # Try to parse with different formats
    for fmt in date_formats:
        try:
            # Remove day names like "Fri", "Monday", etc.
            date_only = re.sub(r'^(Mon|Tue|Wed|Thu|Fri|Sat|Sun|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\s+', '', cleaned, flags=re.IGNORECASE)
            date_only = date_only.strip()

            dt = datetime.strptime(date_only, fmt)
            # Return in consistent format
            return dt.strftime('%B %d, %Y')
        except ValueError:
            continue

    # If no format matched, try to extract date parts manually
    # Look for patterns like "November 10, 2025" with variations
    match = re.search(r'(\w+)\s+(\d+),?\s+(\d{4})', cleaned)
    if match:
        month_str, day_str, year_str = match.groups()

        # Try to parse month name
        month_map = {
            'jan': 'January', 'feb': 'February', 'mar': 'March', 'apr': 'April',
            'may': 'May', 'jun': 'June', 'jul': 'July', 'aug': 'August',
            'sep': 'September', 'oct': 'October', 'nov': 'November', 'dec': 'December',
            'january': 'January', 'february': 'February', 'march': 'March',
            'april': 'April', 'june': 'June', 'july': 'July', 'august': 'August',
            'september': 'September', 'october': 'October', 'november': 'November',
            'december': 'December'
        }

        month_lower = month_str.lower()
        if month_lower in month_map:
            return f"{month_map[month_lower]} {day_str}, {year_str}"

    # Return original if we can't parse it
    return date_str


def normalize_conference_dates(info: dict) -> dict:
    """
    Normalize all date fields in conference info dictionary.

    Args:
        info: Conference info dictionary

    Returns:
        Updated dictionary with normalized dates
    """
    date_fields = ['paper_deadline', 'abstract_deadline', 'notification_date', 'camera_ready']

    for field in date_fields:
        if field in info and info[field] and info[field] != 'TBD':
            # Handle dict deadlines (multi-track conferences)
            if isinstance(info[field], dict):
                normalized_dict = {}
                for track, date in info[field].items():
                    normalized_dict[track] = normalize_date(date)
                info[field] = normalized_dict
            else:
                info[field] = normalize_date(info[field])

    return info


if __name__ == '__main__':
    # Test cases
    test_dates = [
        "November 10, 2025",
        "Nov 10, 2025",
        "Fri 7 Nov 2025",
        "April 11, 2025 at 11:59 PM EDT",
        "October 28, 2024 (FIRM)",
        "January 17, 2026 (No Extensions)",
        "April 17, 2025; 23:59 PT",
        "Thursday, December 11, 2025",
        "14 April 2025",
        "2025-11-10",
    ]

    print("Testing date normalizer...\n")
    for date in test_dates:
        normalized = normalize_date(date)
        print(f"'{date}' -> '{normalized}'")

    print("\n✅ All dates normalized to consistent format!")
