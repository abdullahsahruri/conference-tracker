#!/usr/bin/env python3
"""
Deadline Validation Utility
============================

Validates extracted conference deadlines to prevent common errors:
- Extracting notification dates instead of submission deadlines
- Extracting camera-ready dates instead of submission deadlines
- Extracting conference dates instead of deadlines
"""

from datetime import datetime
from typing import Dict, Optional, Tuple
import re


# Keywords that indicate this is NOT a submission deadline
EXCLUDE_KEYWORDS = [
    'notification',
    'acceptance',
    'camera ready',
    'camera-ready',
    'final version',
    'final manuscript',
    'author notification',
    'decision notification',
    'registration deadline',
    'early bird',
    'hotel reservation'
]

# Keywords that indicate this IS a submission deadline
INCLUDE_KEYWORDS = [
    'paper deadline',
    'submission deadline',
    'abstract deadline',
    'full paper',
    'paper submission',
    'abstract submission',
    'manuscript submission',
    'call for papers'
]


def validate_deadline(
    deadline: str,
    context: str = '',
    conference_date: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Validate if an extracted deadline is actually a submission deadline.

    Args:
        deadline: Extracted deadline string
        context: Surrounding text context (helps identify if it's notification/camera-ready)
        conference_date: Conference date if known (deadline should be before this)

    Returns:
        (is_valid, reason) tuple
    """
    if not deadline or deadline == 'TBD':
        return True, "No deadline to validate"

    # Check if context contains exclude keywords
    if context:
        context_lower = context.lower()
        for keyword in EXCLUDE_KEYWORDS:
            if keyword in context_lower:
                # Check if this is near the deadline
                deadline_lower = deadline.lower()
                # Look for the keyword within 100 chars of the deadline
                if keyword in context_lower:
                    pattern = f'.{{0,100}}{re.escape(deadline_lower)}.{{0,100}}'
                    matches = re.finditer(pattern, context_lower, re.DOTALL)
                    for match in matches:
                        if keyword in match.group():
                            return False, f"Deadline appears near '{keyword}' - likely not a submission deadline"

    # If we have conference date, deadline should be before it
    if conference_date:
        try:
            # Simple date parsing - extract year and month
            deadline_match = re.search(r'(\w+)\s+(\d+),?\s+(\d{4})', deadline)
            conf_match = re.search(r'(\w+)\s+(\d+),?\s+(\d{4})', conference_date)

            if deadline_match and conf_match:
                deadline_dt = datetime.strptime(deadline_match.group(), '%B %d, %Y')
                conf_dt = datetime.strptime(conf_match.group(), '%B %d, %Y')

                # Deadline should be at least 30 days before conference
                days_before = (conf_dt - deadline_dt).days
                if days_before < 30:
                    return False, f"Deadline is only {days_before} days before conference - suspicious"
        except:
            pass  # Date parsing failed, skip this check

    return True, "Appears to be a valid submission deadline"


def validate_extracted_info(info: Dict) -> Tuple[bool, str, Optional[Dict]]:
    """
    Validate extracted conference information and suggest corrections.

    Args:
        info: Extracted conference info dictionary

    Returns:
        (is_valid, reason, corrected_info) tuple
    """
    if not info:
        return True, "No info to validate", None

    paper_deadline = info.get('paper_deadline', '')
    notification_date = info.get('notification_date', '')
    camera_ready = info.get('camera_ready', '')
    conference_date = info.get('conference_date', '')

    # Check if paper_deadline looks like notification/camera-ready
    if paper_deadline and notification_date:
        # If they're the same, that's wrong!
        if paper_deadline.strip() == notification_date.strip():
            return False, "paper_deadline same as notification_date - extracted wrong field", None

    if paper_deadline and camera_ready:
        if paper_deadline.strip() == camera_ready.strip():
            return False, "paper_deadline same as camera_ready - extracted wrong field", None

    # Try to parse dates and check chronological order
    try:
        # Expected order: abstract < paper < notification < camera_ready < conference
        dates = []

        if info.get('abstract_deadline'):
            dates.append(('abstract', info['abstract_deadline']))
        if paper_deadline:
            dates.append(('paper', paper_deadline))
        if notification_date:
            dates.append(('notification', notification_date))
        if camera_ready:
            dates.append(('camera_ready', camera_ready))
        if conference_date:
            # Extract first date from conference date range
            conf_match = re.search(r'(\w+ \d+, \d{4})', conference_date)
            if conf_match:
                dates.append(('conference', conf_match.group()))

        # Parse and check order
        parsed_dates = []
        for name, date_str in dates:
            try:
                # Try common date formats
                for fmt in ['%B %d, %Y', '%b %d, %Y', '%Y-%m-%d']:
                    try:
                        dt = datetime.strptime(date_str.strip(), fmt)
                        parsed_dates.append((name, dt, date_str))
                        break
                    except:
                        continue
            except:
                continue

        # Check chronological order
        if len(parsed_dates) >= 2:
            for i in range(len(parsed_dates) - 1):
                name1, dt1, str1 = parsed_dates[i]
                name2, dt2, str2 = parsed_dates[i + 1]

                if dt1 > dt2:
                    # Dates are out of order!
                    if name1 == 'paper' and name2 == 'notification':
                        return False, f"Paper deadline ({str1}) is AFTER notification ({str2}) - dates swapped!", None
                    if name1 == 'notification' and name2 == 'paper':
                        # Suggest swapping
                        corrected = info.copy()
                        corrected['paper_deadline'] = str2
                        corrected['notification_date'] = str1
                        return False, f"Dates appear swapped - notification before paper deadline", corrected

    except Exception as e:
        pass  # Date validation failed, skip

    return True, "Extracted info appears valid", None


def check_deadline_context(website_text: str, deadline: str) -> Optional[str]:
    """
    Find the context around a deadline in website text to verify it's a submission deadline.

    Args:
        website_text: Full website text
        deadline: Deadline string to search for

    Returns:
        Context string if found, None otherwise
    """
    if not website_text or not deadline:
        return None

    # Find deadline in text
    pattern = re.escape(deadline)
    match = re.search(pattern, website_text, re.IGNORECASE)

    if match:
        # Get 200 chars before and after
        start = max(0, match.start() - 200)
        end = min(len(website_text), match.end() + 200)
        context = website_text[start:end]
        return context

    return None


if __name__ == '__main__':
    # Test cases
    print("Testing deadline validator...\n")

    # Test 1: Valid submission deadline
    valid, reason = validate_deadline("November 10, 2025", "Paper submission deadline: November 10, 2025")
    print(f"Test 1 - Valid submission: {valid} - {reason}")

    # Test 2: Notification date (should fail)
    valid, reason = validate_deadline("January 31, 2026", "Author notification: January 31, 2026")
    print(f"Test 2 - Notification date: {valid} - {reason}")

    # Test 3: Camera ready (should fail)
    valid, reason = validate_deadline("February 28, 2026", "Camera ready deadline: February 28, 2026")
    print(f"Test 3 - Camera ready: {valid} - {reason}")

    # Test 4: Validate full info
    info = {
        'paper_deadline': 'January 31, 2026',
        'notification_date': 'January 31, 2026',  # Same as paper - wrong!
    }
    valid, reason, corrected = validate_extracted_info(info)
    print(f"\nTest 4 - Duplicate dates: {valid} - {reason}")

    print("\n✅ Validation tests complete!")
