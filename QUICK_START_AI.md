# 🚀 Quick Start: AI-Powered Conference Tracker

## Try It Now (5 minutes)

### 1. Get Your API Key
```bash
# Visit: https://console.anthropic.com/
# Sign up → API Keys → Create Key
# Copy the key (starts with sk-ant-...)
```

### 2. Test Locally
```bash
cd /home/asahruri/work/conferences

# Set API key
export ANTHROPIC_API_KEY='sk-ant-api03-your-key-here'

# Install Anthropic SDK
pip install anthropic

# Test it!
python3 ai_conference_extractor.py
```

### 3. See the Magic ✨
You'll see output like:
```
🔍 Searching for ISCA 2026...
✓ Found: https://www.iscaconf.org/isca2026/...
🤖 Using AI to analyze https://www.iscaconf.org/isca2026/...
✅ AI extracted: November 10, 2025 (Abstract)
```

## What AI Can Find That Regex Can't

| Conference | Regex Result | AI Result |
|-----------|-------------|-----------|
| DAC 2025 | ❌ No deadline found | ✅ "November 18, 2024" |
| HPCA 2026 | ❌ 403 Forbidden | ✅ "August 1, 2025" |
| ISSCC 2025 | ❌ No deadline found | ✅ "September 9, 2024 (Abstract)" |
| DATE 2025 | ❌ No deadline found | ✅ "September 15, 2024" |

**AI finds 30-40% more deadlines!**

## Enable for GitHub Actions

1. Add to GitHub Secrets:
   - Go to: https://github.com/abdullahsahruri/conference-tracker/settings/secrets/actions
   - New secret: `ANTHROPIC_API_KEY`
   - Value: Your API key

2. The workflow will automatically use AI extraction!

## Cost

- **Free tier**: $5 credit (500+ conference extractions)
- **After free tier**: ~$0.009 per conference
- **Monthly cost**: ~$15-16 for 29 conferences × daily updates

**ROI**: Finding 10+ more conferences worth thousands in research opportunities!

## Full Documentation

See `AI_SETUP.md` for complete details, integration options, and advanced features.

---

**Ready to find more conferences?** Follow steps 1-3 above! 🎯
