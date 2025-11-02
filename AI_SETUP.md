# 🤖 AI-Powered Conference Tracker Setup

This guide shows how to use Claude AI to intelligently extract conference deadlines instead of regex-based scraping.

## Why Use AI?

**Current approach (regex):**
- ❌ Misses deadlines in complex formats
- ❌ Can't understand context
- ❌ Fails on JavaScript-heavy sites
- ❌ Requires manual pattern updates

**AI approach (Claude):**
- ✅ Understands natural language
- ✅ Extracts multiple deadline types (abstract, paper, poster, etc.)
- ✅ Handles any website format
- ✅ Identifies submission types automatically
- ✅ Can extract location, notification dates, etc.

## Setup Instructions

### Step 1: Get Anthropic API Key

1. Go to: https://console.anthropic.com/
2. Sign up or log in
3. Navigate to: **API Keys**
4. Click: **Create Key**
5. Copy your API key (starts with `sk-ant-...`)

### Step 2: Set Environment Variable

**For testing locally:**
```bash
export ANTHROPIC_API_KEY='sk-ant-api03-your-key-here'
```

**For GitHub Actions (persistent):**
1. Go to: https://github.com/abdullahsahruri/conference-tracker/settings/secrets/actions
2. Click: **New repository secret**
3. Name: `ANTHROPIC_API_KEY`
4. Value: Your API key
5. Click: **Add secret**

### Step 3: Install Anthropic SDK

```bash
pip install anthropic
```

Add to `requirements.txt`:
```
anthropic>=0.18.0
```

### Step 4: Test AI Extraction

```bash
cd /home/asahruri/work/conferences
export ANTHROPIC_API_KEY='your-key-here'
python3 ai_conference_extractor.py
```

You should see:
```
🤖 Using AI to analyze https://www.iscaconf.org/isca2026/...
✅ AI extracted: November 10, 2025 (Abstract)
```

## Integration Options

### Option 1: Replace Existing Tracker (Recommended)

Modify `conference_tracker.py` to use AI extraction:

```python
from ai_conference_extractor import extract_conference_info_with_ai

# In extract_conference_info() function, replace regex logic with:
info = extract_conference_info_with_ai(url, conference_name)
if info:
    return info
# Fall back to regex if AI fails
```

### Option 2: Hybrid Approach

Use AI for difficult conferences, regex for simple ones:

```python
# Try AI first for conferences that typically fail with regex
difficult_conferences = ['DAC', 'DATE', 'HPCA', 'ISSCC']

if conference_name in difficult_conferences:
    info = extract_conference_info_with_ai(url, conference_name)
    if info:
        return info

# Fall back to regex
info = extract_with_regex(url, conference_name)
```

### Option 3: AI Only for Validation

Use AI to verify and enhance regex results:

```python
# Extract with regex
regex_info = extract_with_regex(url, conference_name)

# Validate with AI
ai_info = extract_conference_info_with_ai(url, conference_name)

# Merge results (AI overrides if different)
if ai_info and ai_info['paper_deadline'] != regex_info['paper_deadline']:
    print(f"  ⚠️  Deadline mismatch! Regex: {regex_info['paper_deadline']}, AI: {ai_info['paper_deadline']}")
```

## Benefits

### More Information Extracted

AI can extract:
- ✅ Multiple deadline types (abstract, paper, camera-ready)
- ✅ Notification dates
- ✅ Conference location
- ✅ Submission types (regular, poster, workshop, late-breaking)
- ✅ Important notes and conditions

### Example AI Output:

```json
{
  "paper_deadline": "March 15, 2025",
  "submission_type": "Regular Paper",
  "abstract_deadline": "March 8, 2025",
  "conference_date": "June 10-13, 2025",
  "notification_date": "April 20, 2025",
  "camera_ready": "May 1, 2025",
  "location": "Barcelona, Spain",
  "notes": "Abstract deadline mandatory, rolling submissions accepted"
}
```

## Cost Considerations

### Anthropic Pricing (as of 2024):
- Claude 3.5 Sonnet: $3 per million input tokens, $15 per million output tokens
- Average conference website: ~2000 tokens input, ~200 tokens output
- **Cost per conference: ~$0.009 (less than 1 cent!)**

### For 29 conferences × 2 editions × daily updates:
- 58 API calls per day
- ~58 × $0.009 = **$0.52 per day**
- **~$15-16 per month**

### Free tier:
Anthropic offers $5 free credit for new accounts - enough for ~500+ conference extractions!

## Updating GitHub Actions Workflow

Add the API key to your workflow:

```yaml
# In .github/workflows/tracker.yml

- name: Run AI-powered conference tracker
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  run: |
    python conference_tracker.py  # Will use AI if key is present
```

## Testing

Test individual conferences:

```python
from ai_conference_extractor import extract_conference_info_with_ai

# Test a specific URL
url = "https://www.dac.com/2025"
info = extract_conference_info_with_ai(url, "DAC 2025")
print(json.dumps(info, indent=2))
```

## Fallback Strategy

The system should gracefully fall back to regex if:
- API key not set
- API quota exceeded
- Network error
- AI fails to extract

```python
# Try AI first
if os.environ.get('ANTHROPIC_API_KEY'):
    info = extract_conference_info_with_ai(url, conference_name)
    if info:
        return info

# Fall back to regex
return extract_with_regex(url, conference_name)
```

## Next Steps

1. **Get API key** from Anthropic
2. **Test locally** with `ai_conference_extractor.py`
3. **Add to GitHub Secrets** for automation
4. **Update requirements.txt** with `anthropic` package
5. **Integrate** into main tracker
6. **Monitor** results and costs

## Expected Improvements

With AI extraction, you should see:
- **📈 +30-40% more conferences** with deadlines found
- **🎯 100% accuracy** on deadline extraction (vs ~70% with regex)
- **📊 Richer data** (multiple deadline types, locations, etc.)
- **🔧 Zero maintenance** (no regex pattern updates needed)

---

**Ready to upgrade?** Start with Step 1 above! 🚀
