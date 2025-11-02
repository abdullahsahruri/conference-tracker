# 🤖 Extraction Methods Comparison

Comparison of the two extraction methods available in this tracker.

## TL;DR - Quick Recommendations

| Your Situation | Best Choice |
|---------------|-------------|
| **Want better accuracy (90% vs 66%)** | 🆓 **Ollama AI** |
| **Want 100% free** | 🆓 **Ollama** or 🔧 Regex (both free!) |
| **Have limited compute (<4GB RAM)** | 🔧 Regex |
| **Want fastest extraction (2 min vs 8 min)** | 🔧 Regex |
| **Need submission types extracted** | 🆓 **Ollama** |
| **No setup hassle** | 🔧 Regex (already working!) |

---

## Detailed Comparison

### 1. 🆓 Ollama (Local AI) - RECOMMENDED

**File:** `ai_conference_extractor_ollama.py`
**Setup Guide:** [OLLAMA_SETUP.md](OLLAMA_SETUP.md)

#### Pros:
- ✅ **90% success rate** - Finds 26/29 conferences
- ✅ **100% FREE** - No costs whatsoever
- ✅ **Unlimited usage** - Extract as many times as you want
- ✅ **Privacy** - All data stays on your machine
- ✅ **No API keys** - Simple setup
- ✅ **Works offline** - After initial model download
- ✅ **Extracts submission types** - Regular/Abstract/Late Breaking/etc.
- ✅ **Multi-track deadlines** - Handles conferences with Spring/Fall tracks

#### Cons:
- ❌ Slower (~8 min for 29 conferences vs 2 min with regex)
- ❌ Requires local compute (4GB+ RAM)
- ❌ Initial setup needed (~5 minutes)
- ❌ Slightly lower accuracy than paid cloud AI

#### Cost:
- **Setup**: $0
- **Monthly**: $0
- **Annual**: $0
- **Forever**: **$0** 🎉

#### Best For:
- Users who want better accuracy than regex
- Privacy-conscious users
- Those with decent local hardware (4GB+ RAM)
- Projects with no budget

---

### 2. 🔧 Regex - DEFAULT METHOD

**File:** `conference_tracker.py`

#### Pros:
- ✅ **100% FREE**
- ✅ **Fastest** - ~2 min for 29 conferences (4x faster than AI)
- ✅ **No dependencies** - Just Python + requests
- ✅ **Works offline**
- ✅ **No setup** - Already working!
- ✅ **Runs on GitHub Actions** - Works 24/7 even when computer is off
- ✅ **Very lightweight** - Minimal RAM/CPU usage

#### Cons:
- ❌ **66% success rate** - Finds only 19/29 conferences
- ❌ Misses complex date formats
- ❌ Can't understand context
- ❌ Requires manual pattern updates
- ❌ No submission type detection

#### Cost:
- **Everything**: $0

#### Best For:
- Users who want zero setup
- Those satisfied with current results
- Projects where missing some deadlines is OK
- Automatic daily monitoring (GitHub Actions)

---

## Performance Comparison

### Success Rate (29 conferences tested)

| Method | Found | Success Rate | Missed |
|--------|-------|--------------|---------  |
| **Ollama (llama3.2)** | 26/29 | **90%** | 3 |
| Regex | 19/29 | 66% | 10 |

**Winner:** Ollama finds **36% more conferences** (7 additional deadlines)!

### Speed (time to process all 29 conferences)

| Method | Time | Speed Rating |
|--------|------|--------------  |
| Regex | ~2 min | ⚡⚡⚡ Fastest |
| **Ollama** | **~8 min** | **⚡⚡ Moderate** |

**Winner:** Regex is **4x faster**, but Ollama finds more deadlines.

### Cost (forever)

| Method | Annual Cost |
|--------|-------------|
| **Ollama** | **$0** 🆓 |
| Regex | $0 🆓 |

**Winner:** **Both are 100% FREE!** 🎉

---

## Feature Comparison

| Feature | Regex | Ollama |
|---------|-------|--------|
| Paper deadline | ✅ | ✅ |
| Submission type | ❌ | ✅ |
| Abstract deadline | ❌ | ✅ |
| Conference dates | ❌ | ✅ |
| Location | ❌ | ✅ |
| Context understanding | ❌ | ✅ |
| Multi-track deadlines | ❌ | ✅ |
| Speed | ⚡⚡⚡ | ⚡⚡ |
| Success rate | 66% | 90% |

---

## Hybrid Approach (RECOMMENDED)

**Best of both worlds:** Use Ollama for better accuracy, with Regex as backup.

### Option 1: Regex Auto + Ollama Manual

**How it works:**
1. Regex runs automatically daily via GitHub Actions (even when computer is off)
2. Run Ollama manually once a week/month for better accuracy
3. Commit Ollama results to update database

**Benefits:**
- ✅ Automatic daily monitoring (regex)
- ✅ High accuracy when you run AI (90%)
- ✅ 100% FREE
- ✅ No computer needed for daily updates

**How to use:**
```bash
# Automatic (already running):
# - GitHub Actions runs conference_tracker.py daily at 9 AM UTC

# Manual AI update (when you want better results):
ollama serve &
python3 conference_tracker_ai.py
git add conference_database.json
git commit -m "Update with AI extraction"
git push
```

**Result:** Best success rate, zero cost! 🎯

### Option 2: Ollama with Regex Fallback

**For advanced users:** Modify `conference_tracker.py` to try Ollama first.

```python
# Try Ollama first (requires computer on + Ollama running)
info = extract_conference_info_with_ollama(url, name)
if info:
    return info

# Fall back to regex if Ollama fails
return extract_with_regex(url, name)
```

**Result:** 90% success rate, but only works when computer is on.

---

## Our Recommendation

### For Most Users: 🎯 **Hybrid Approach**

Use the **Regex Auto + Ollama Manual** approach:
- ✅ Automatic daily updates continue (even when computer off)
- ✅ Run AI manually once a week for better accuracy
- ✅ 100% FREE forever
- ✅ Best of both worlds

**Setup:**
1. Regex is already running automatically (no setup needed)
2. Follow [OLLAMA_SETUP.md](OLLAMA_SETUP.md) to install Ollama (5 minutes)
3. Run `python3 conference_tracker_ai.py` when you want AI accuracy

### For Minimal Setup: 🔧 **Regex Only**

Stick with regex if you:
- Are satisfied with current 66% success rate
- Want zero setup
- Don't have 4GB+ RAM for Ollama
- Can't run Ollama locally

**No setup needed** - already working!

### For Maximum Accuracy: 🆓 **Ollama Only**

Use Ollama if you:
- Need 90% accuracy (vs 66% with regex)
- Want submission types automatically detected
- Have 4GB+ RAM available
- Can run tracker manually when computer is on

**Setup:** See [OLLAMA_SETUP.md](OLLAMA_SETUP.md)

---

## Quick Start Guides

- **Ollama (FREE AI)**: See [OLLAMA_SETUP.md](OLLAMA_SETUP.md)
- **Regex**: Already running! No setup needed.
- **Hybrid Approach**: Install Ollama, run manually as needed

---

## Questions?

**Q: Which is most accurate?**
A: Ollama (90%) > Regex (66%)

**Q: Which is fastest?**
A: Regex (2 min) > Ollama (8 min)

**Q: Which is cheapest?**
A: Both are $0 - 100% FREE!

**Q: Can Ollama run on GitHub Actions?**
A: Technically yes, but it's complex. Easier to run locally and commit results.

**Q: Does Ollama work on my machine?**
A: If you have 4GB+ RAM, yes! Works on Linux, Mac, Windows (WSL).

**Q: Why not use paid cloud AI?**
A: This project focuses on 100% free solutions. Ollama gives 90% accuracy for $0!

---

**Ready to choose?** Pick your method and follow the respective setup guide! 🚀
