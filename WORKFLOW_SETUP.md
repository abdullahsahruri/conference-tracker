# Automatic Website Sync Setup

## How It Works

When you commit changes to `my_conferences.csv`, GitHub Actions automatically:
1. 📥 Syncs the CSV to `conference_database.json`
2. 💾 Commits the updated database to this repo
3. 🌐 Pushes the database to your website repository
4. ✅ Your website updates automatically!

## One-Time Setup Required

The workflow needs a Personal Access Token (PAT) to push to your website repo.

### Steps to Create the Token:

1. **Go to GitHub Settings**
   - Visit: https://github.com/settings/tokens
   - Click "Generate new token" → "Generate new token (classic)"

2. **Configure the Token**
   - **Note**: "Conference Tracker Website Sync"
   - **Expiration**: Choose "No expiration" or "1 year"
   - **Scopes**: Check these boxes:
     - ✅ `repo` (Full control of private repositories)
     - ✅ `workflow` (Update GitHub Action workflows)

3. **Generate and Copy the Token**
   - Click "Generate token"
   - **⚠️ IMPORTANT**: Copy the token immediately (you won't see it again!)

4. **Add the Token to This Repository**
   - Go to: https://github.com/abdullahsahruri/conference-tracker/settings/secrets/actions
   - Click "New repository secret"
   - **Name**: `SITE_GITHUB_TOKEN`
   - **Value**: Paste your token
   - Click "Add secret"

## Testing the Workflow

Once the token is set up:

```bash
# Edit your CSV
vim my_conferences.csv

# Commit and push
git add my_conferences.csv
git commit -m "Add new conference"
git push
```

Then:
1. Go to: https://github.com/abdullahsahruri/conference-tracker/actions
2. Watch the "Sync Conferences CSV to Website" workflow run
3. Your website will update in 1-2 minutes!

## Troubleshooting

**Error: "SITE_GITHUB_TOKEN secret not configured"**
- Follow the setup steps above to create and add the token

**Workflow doesn't trigger:**
- Make sure you're pushing changes to `my_conferences.csv`
- Check that the workflow file is in `.github/workflows/csv_import.yml`

**Website doesn't update:**
- Check the Actions tab for error messages
- Verify the token has `repo` permissions
- Make sure the token hasn't expired
