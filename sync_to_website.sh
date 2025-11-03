#!/bin/bash
# Sync conference database to website

set -e

WEBSITE_REPO="/home/asahruri/abdullahsahruri.github.io"
WEBSITE_ASSETS="$WEBSITE_REPO/assets"

echo "📤 Syncing conference database to website..."

# Copy database
cp conference_database.json "$WEBSITE_ASSETS/conference_database.json"
echo "   ✅ Copied database"

# Commit and push
cd "$WEBSITE_REPO"

git add assets/conference_database.json
git commit -m "Update conferences - $(date '+%Y-%m-%d %H:%M')" || echo "   (No changes to commit)"
git pull --rebase
git push

echo ""
echo "✅ Synced! View at: https://abdullahsahruri.github.io/conferences/"
