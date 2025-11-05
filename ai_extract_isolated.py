#!/usr/bin/env python3
"""
Isolated Conference Extraction Script
======================================

Extracts conferences ONE AT A TIME to prevent context contamination.
Each conference runs in a completely fresh subprocess with no shared context.

Usage:
    python3 ai_extract_isolated.py --conferences "DAC,ASPDAC,ICCAD"
    python3 ai_extract_isolated.py --category "Design Automation"
"""

import subprocess
import argparse
import sys
import time
from datetime import datetime

# Import conference database from ai_extract_all_conferences
sys.path.insert(0, '/home/asahruri/work/conferences')
from ai_extract_all_conferences import KNOWN_CONFERENCES


def restart_ollama(model='qwen2.5'):
    """Restart Ollama to completely clear context and ensure isolation."""

    print("   🔄 Restarting Ollama to clear context...")

    # Step 1: Kill Ollama completely
    subprocess.run(['pkill', '-9', 'ollama'], stderr=subprocess.DEVNULL, check=False)
    time.sleep(7)  # Wait for full shutdown and cleanup

    # Step 2: Start Ollama in background
    subprocess.Popen(
        ['ollama', 'serve'],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(10)  # Wait for full startup

    # Step 3: Verify Ollama is running
    try:
        result = subprocess.run(
            ['ollama', 'list'],
            capture_output=True,
            timeout=5
        )
        if result.returncode != 0:
            print("   ⚠️  Ollama may not be fully ready")
            return False
    except:
        print("   ⚠️  Could not verify Ollama status")
        return False

    # Step 4: Preload the model to force cache clear
    try:
        subprocess.run(
            ['ollama', 'run', model, 'Hello'],
            input='',
            capture_output=True,
            text=True,
            timeout=30
        )
        print("   ✅ Ollama restarted and model cache cleared")
        return True
    except:
        print("   ⚠️  Model reload may have failed")
        return False


def extract_conference_isolated(conf_name, year, model='qwen2.5', restart_ollama_flag=True):
    """Extract a single conference in complete isolation."""

    print(f"\n{'='*80}")
    print(f"Extracting {conf_name} {year} in isolated process...")
    print(f"{'='*80}\n")

    # Run extraction in completely isolated subprocess
    # This prevents any context leakage between conferences
    cmd = [
        'python3',
        'ai_extract_all_conferences.py',
        '--conferences', conf_name,
        '--year', str(year),
        '--model', model
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout per conference
            cwd='/home/asahruri/work/conferences'
        )

        return {
            'conference': conf_name,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode,
            'success': result.returncode == 0
        }

    except subprocess.TimeoutExpired:
        print(f"⏱️  Timeout extracting {conf_name} (>5 minutes)")
        return {
            'conference': conf_name,
            'success': False,
            'error': 'Timeout'
        }
    except Exception as e:
        print(f"❌ Error extracting {conf_name}: {e}")
        return {
            'conference': conf_name,
            'success': False,
            'error': str(e)
        }


def parse_csv_from_output(output):
    """Extract CSV lines from command output."""
    lines = output.split('\n')
    csv_lines = []
    in_results = False

    for line in lines:
        # Start collecting after "## " category header
        if line.startswith('##'):
            in_results = True
            continue

        # Stop at summary section
        if 'SUMMARY' in line or '=====' in line:
            if csv_lines:  # Only stop if we've collected something
                break

        # Collect CSV lines (they contain commas and start with conference name)
        if in_results and ',' in line and not line.startswith('#'):
            # Extract just the CSV part (before any comment)
            csv_part = line.split('#')[0].strip()
            if csv_part and not csv_part.startswith('conference_name'):
                csv_lines.append(csv_part)

    return csv_lines


def main():
    parser = argparse.ArgumentParser(
        description='Extract conferences in complete isolation (prevents context contamination)'
    )
    parser.add_argument('--conferences', '-c',
                        help='Comma-separated conference names')
    parser.add_argument('--category', '-cat',
                        help='Extract all conferences from this category')
    parser.add_argument('--year', '-y', type=int,
                        default=datetime.now().year + 1,
                        help='Target year (default: next year)')
    parser.add_argument('--model', '-m', default='qwen2.5',
                        choices=['qwen2.5', 'qwen3:4b', 'qwen3:8b', 'qwen3:14b', 'mistral', 'llama3.1', 'llama3.2'],
                        help='Ollama model (default: qwen2.5)')

    args = parser.parse_args()

    # Determine which conferences to extract
    if args.conferences:
        conferences = [c.strip() for c in args.conferences.split(',')]
    elif args.category:
        # Get conferences from category
        conferences = [
            name for name, info in KNOWN_CONFERENCES.items()
            if info['category'] == args.category
        ]
        if not conferences:
            print(f"❌ No conferences found in category '{args.category}'")
            sys.exit(1)
    else:
        print("❌ Must specify --conferences or --category")
        sys.exit(1)

    print("="*80)
    print("ISOLATED CONFERENCE EXTRACTION")
    print("="*80)
    print(f"\n🤖 Model: {args.model}")
    print(f"📅 Year: {args.year}")
    print(f"📋 Conferences: {', '.join(conferences)}")
    print(f"🔒 Mode: Each conference extracted in isolated subprocess\n")

    # Extract each conference in complete isolation
    results = []
    all_csv_lines = []
    successful = 0
    failed = 0

    for i, conf in enumerate(conferences, 1):
        print(f"\n[{i}/{len(conferences)}] Processing {conf}...")

        # Restart Ollama before each conference (except first) for complete isolation
        if i > 1:
            if not restart_ollama(model=args.model):
                print(f"   ⚠️  Warning: Ollama restart may have failed, continuing anyway...")

        result = extract_conference_isolated(conf, args.year, args.model, restart_ollama_flag=False)
        results.append(result)

        if result['success']:
            # Parse CSV from output
            csv_lines = parse_csv_from_output(result['stdout'])
            if csv_lines:
                all_csv_lines.extend(csv_lines)
                successful += 1
                print(f"   ✅ {conf} extracted successfully ({len(csv_lines)} entries)")
            else:
                failed += 1
                print(f"   ⚠️  {conf} extraction succeeded but no CSV data found")
        else:
            failed += 1
            print(f"   ❌ {conf} extraction failed")

    # Print final results
    print("\n\n" + "="*80)
    print("FINAL RESULTS - Copy and paste into my_conferences.csv")
    print("="*80 + "\n")

    if all_csv_lines:
        print("conference_name,year,paper_deadline,url,submission_type,conference_date,abstract_deadline,location")
        for line in all_csv_lines:
            print(line)

        print(f"\n{'='*80}")
        print("SUMMARY")
        print(f"{'='*80}")
        print(f"✅ Successfully extracted: {successful}/{len(conferences)} conferences")
        print(f"❌ Failed: {failed}/{len(conferences)} conferences")
        print(f"{'='*80}")

        print("\nNext steps:")
        print("1. Review the extracted data above")
        print("2. Copy the CSV lines")
        print("3. Paste into my_conferences.csv")
        print("4. Run: ./csv import my_conferences.csv\n")
    else:
        print("❌ No conferences were successfully extracted\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
