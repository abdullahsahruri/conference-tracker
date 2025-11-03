# Conference Deadline Tracker

AI-powered conference deadline tracker using **Ollama (100% FREE)** for intelligent extraction.

## Quick Start

### Run Tracker with Auto-Sync

```bash
./run_tracker_and_sync.sh
```

This single command will:
1. Run the conference tracker with Ollama AI
2. Extract deadlines for all conferences in `conferences_to_track.txt`
3. Automatically copy `conference_database.json` to website repo
4. Commit and push changes to GitHub Pages

Your website at https://abdullahsahruri.github.io/conferences/ will update in 1-2 minutes!

## Setup

1. **Install Ollama** (one-time):
   ```bash
   curl -fsSL https://ollama.ai/install.sh | sh
   ollama serve  # Keep running
   ollama pull llama3.1
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Add conferences** to `conferences_to_track.txt`:
   ```
   ISCA
   MICRO
   DAC
   YOUR_CONFERENCE
   ```

4. **Run tracker**:
   ```bash
   ./run_tracker_and_sync.sh
   ```

## Manual Commands

If you prefer to run steps separately:

```bash
# Run tracker only
python3 conference_tracker.py

# Sync to website manually
cp conference_database.json ../abdullahsahruri.github.io/assets/
cd ../abdullahsahruri.github.io
git add assets/conference_database.json
git commit -m "Update conferences"
git push
```

## Features

- **100% FREE**: Uses local Ollama AI (no API costs)
- **90% accuracy**: AI understands context and finds correct deadlines
- **Smart validation**: Prevents duplicates, validates years
- **Auto-sync**: One command updates everything
- **No URLs needed**: Just add conference acronyms

## Documentation

- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Detailed setup instructions
- [CLAUDE.md](CLAUDE.md) - Developer documentation

## Files

- `run_tracker_and_sync.sh` - **Main script** (run this!)
- `conference_tracker.py` - Conference discovery and tracking
- `ai_conference_extractor_ollama.py` - Ollama AI extraction
- `conferences_to_track.txt` - Your conference list
- `conference_database.json` - Generated deadline database

Happy conference tracking! 🚀
