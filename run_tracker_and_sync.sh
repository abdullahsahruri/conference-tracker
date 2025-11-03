#!/bin/bash

# Conference Tracker with Auto-Sync to Website
# Runs Ollama-powered tracker and automatically updates website repo

set -e  # Exit on any error

echo "======================================================================="
echo "Conference Tracker with Auto-Sync"
echo "======================================================================="

# Step 1: Run the tracker with Ollama AI
echo ""
echo "Step 1: Running conference tracker with Ollama AI..."
echo "-----------------------------------------------------------------------"
python3 conference_tracker.py

if [ $? -ne 0 ]; then
    echo "❌ Tracker failed! Not syncing to website."
    exit 1
fi

echo ""
echo "✅ Tracker completed successfully!"
echo ""

# Step 2: Copy database to website repo
echo "Step 2: Syncing to website repository..."
echo "-----------------------------------------------------------------------"

WEBSITE_REPO="/home/asahruri/abdullahsahruri.github.io"
WEBSITE_ASSETS="$WEBSITE_REPO/assets"

if [ ! -d "$WEBSITE_REPO" ]; then
    echo "❌ Website repo not found at $WEBSITE_REPO"
    exit 1
fi

# Copy the database
cp conference_database.json "$WEBSITE_ASSETS/conference_database.json"
echo "✅ Copied conference_database.json to website assets/"

# Step 3: Commit and push to website repo
echo ""
echo "Step 3: Committing and pushing to website..."
echo "-----------------------------------------------------------------------"

cd "$WEBSITE_REPO"

# Check if there are changes
if git diff --quiet assets/conference_database.json; then
    echo "ℹ️  No changes detected in conference database"
    echo ""
    echo "======================================================================="
    echo "✅ Sync complete! No updates needed."
    echo "======================================================================="
    exit 0
fi

# Add and commit changes
git add assets/conference_database.json
git commit -m "Auto-update conference database

- Updated by conference tracker
- Extracted with Ollama AI (llama3.1:latest)
- $(date '+%Y-%m-%d %H:%M:%S')"

# Push to GitHub
echo ""
echo "Pushing to GitHub..."
git push

if [ $? -eq 0 ]; then
    echo ""
    echo "======================================================================="
    echo "✅ SUCCESS! Conference database synced to website!"
    echo "======================================================================="
    echo ""
    echo "Your website will update in 1-2 minutes:"
    echo "https://abdullahsahruri.github.io/conferences/"
    echo ""
else
    echo ""
    echo "❌ Push failed! You may need to push manually:"
    echo "   cd $WEBSITE_REPO && git push"
    exit 1
fi
