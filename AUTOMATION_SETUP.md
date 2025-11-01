# 🤖 Automation Setup - Final Steps

Your conference tracker is ready to go! Follow these steps to enable daily automatic updates.

---

## Step 1: Create GitHub Repository

1. **Go to GitHub**: https://github.com/new

2. **Repository settings**:
   - Repository name: `conference-tracker`
   - Description: `Intelligent conference deadline tracker with auto-updates`
   - Visibility: **Public** (or Private if you prefer)
   - ❌ **DO NOT** initialize with README, .gitignore, or license (we already have these)

3. **Click "Create repository"**

---

## Step 2: Push Your Code

Copy the commands GitHub shows you, or use these:

```bash
cd /home/asahruri/work/conferences

# Add remote
git remote add origin https://github.com/abdullahsahruri/conference-tracker.git

# Rename branch to main (optional, if you prefer main over master)
git branch -M main

# Push
git push -u origin main
```

**✅ Your code is now on GitHub!**

---

## Step 3: Create Personal Access Token (PAT)

This allows the tracker to automatically update your main website.

1. **Go to**: https://github.com/settings/tokens/new

2. **Token settings**:
   - Note: `Conference Tracker - Site Access`
   - Expiration: `No expiration` (or 1 year)
   - Scopes: Check **`repo`** (Full control of private repositories)

3. **Click "Generate token"**

4. **COPY THE TOKEN** - You won't see it again!
   - It looks like: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

---

## Step 4: Add GitHub Secrets

### In the `conference-tracker` Repository:

Go to: https://github.com/abdullahsahruri/conference-tracker/settings/secrets/actions

Click **"New repository secret"** for each of these:

### Secret 1: GOOGLE_CREDS
```bash
# Get the content:
cat /home/asahruri/work/conferences/credentials.json

# Copy the ENTIRE output (including { and })
# Paste as secret value
```
- Name: `GOOGLE_CREDS`
- Value: Entire contents of credentials.json

### Secret 2: GOOGLE_TOKEN
```bash
# Get the content:
cat /home/asahruri/work/conferences/token.json

# Copy the ENTIRE output
# Paste as secret value
```
- Name: `GOOGLE_TOKEN`
- Value: Entire contents of token.json

### Secret 3: SITE_GITHUB_TOKEN
- Name: `SITE_GITHUB_TOKEN`
- Value: The Personal Access Token you created in Step 3
  (Starts with `ghp_...`)

### Secret 4: EMAIL_FROM (Optional)
- Name: `EMAIL_FROM`
- Value: `your.email@gmail.com`

### Secret 5: EMAIL_PASSWORD (Optional)
- Name: `EMAIL_PASSWORD`
- Value: Your Gmail App Password (16 characters)
  - Get it from: https://myaccount.google.com/apppasswords
  - Enable 2-Step Verification first

### Secret 6: EMAIL_TO (Optional)
- Name: `EMAIL_TO`
- Value: `recipient@email.com` (can be same as EMAIL_FROM)

---

## Step 5: Verify Setup

### Check Secrets:
Go to: https://github.com/abdullahsahruri/conference-tracker/settings/secrets/actions

You should see:
- ✅ GOOGLE_CREDS
- ✅ GOOGLE_TOKEN
- ✅ SITE_GITHUB_TOKEN
- ✅ EMAIL_FROM (optional)
- ✅ EMAIL_PASSWORD (optional)
- ✅ EMAIL_TO (optional)

---

## Step 6: Test the Automation

### Manual Trigger:

1. Go to: https://github.com/abdullahsahruri/conference-tracker/actions

2. Click **"Conference Deadline Tracker"** workflow

3. Click **"Run workflow"** → **"Run workflow"**

4. Wait 2-3 minutes

5. **Check the logs** to see if it worked!

### What Should Happen:

1. ✅ Searches for conferences (ISCA, DAC, GLSVLSI, etc.)
2. ✅ Extracts deadlines
3. ✅ Updates `conference_database.json`
4. ✅ Sends email (if configured)
5. ✅ Updates Google Calendar
6. ✅ Pushes updated JSON to `abdullahsahruri.github.io/assets/`
7. ✅ Your website auto-updates!

---

## Step 7: Verify Your Site Updated

Wait 2-3 minutes after the workflow completes, then:

1. Visit: https://abdullahsahruri.github.io/conferences

2. Check if the data looks correct

3. Check the "Last updated" timestamp at the bottom

---

## 🎉 You're Done!

Your system is now **fully automated**!

### Daily Schedule:

**Every day at 9:00 AM UTC**, the system will:
1. Search for conferences
2. Extract deadlines
3. Detect changes
4. Send email if changes found
5. Update Google Calendar
6. Update your website
7. Commit changes to both repos

---

## 🔧 Troubleshooting

### Workflow Failed?

1. **Check Actions logs**: https://github.com/abdullahsahruri/conference-tracker/actions
2. Look for error messages
3. Common issues:
   - ❌ Missing secrets → Add them in Step 4
   - ❌ Invalid token → Regenerate PAT with `repo` scope
   - ❌ Email auth → Check Gmail app password

### Site not updating?

1. Check that workflow completed successfully
2. Verify `SITE_GITHUB_TOKEN` is correct
3. Check that token has `repo` scope
4. Look at the "Push to main site repository" step in logs

### No email notifications?

- Email secrets are **optional**
- If you don't want emails, that's fine - system still works!
- To enable: Set EMAIL_FROM, EMAIL_PASSWORD, EMAIL_TO

---

## 📊 Monitoring

### View Workflow Runs:
https://github.com/abdullahsahruri/conference-tracker/actions

### View Change Log:
Check `deadline_changes.log` in your repo

### View Database:
https://github.com/abdullahsahruri/conference-tracker/blob/main/conference_database.json

---

## 🎯 Adding More Conferences

Edit `conferences_to_track.txt`:

```bash
# Computer Architecture
ISCA
MICRO
HPCA
ASPLOS

# VLSI & Circuits
DAC
ICCAD
DATE
GLSVLSI
ISSCC

# Add your favorites!
SOSP
OSDI
NSDI
```

Commit and push:
```bash
git add conferences_to_track.txt
git commit -m "Add more conferences to track"
git push
```

Next run will track the new conferences!

---

## ⚙️ Advanced Configuration

### Change Schedule:

Edit `.github/workflows/tracker.yml`:
```yaml
schedule:
  - cron: '0 9 * * *'   # Daily 9 AM UTC
  - cron: '0 21 * * *'  # Add: Daily 9 PM UTC
```

### Customize Email Template:

Edit `email_notifier.py` → `notify_changes()` function

---

## 📞 Need Help?

**Checklist before asking:**
- ✅ All secrets are set correctly
- ✅ PAT has `repo` scope
- ✅ Workflow logs show specific error
- ✅ credentials.json and token.json are valid

**Common commands:**
```bash
# Re-run OAuth setup
python gcal_setup.py

# Test email
export EMAIL_FROM='your@email.com'
export EMAIL_PASSWORD='app-password'
python email_notifier.py

# Test tracker locally
python conference_tracker.py
```

---

**Ready? Start with Step 1!** 🚀
