# Integrating Conference Table with abdullahsahruri.github.io

You have two options for integrating the conference tracker with your existing Beautiful Jekyll site.

---

## ✅ Option 1: Add as a New Tab (Recommended)

This keeps your existing site and adds "Conferences" as a new navigation tab.

### Step 1: Copy the Conference Page

```bash
# Copy the conferences.md file to your site repository
cp conferences.md /path/to/abdullahsahruri.github.io/
```

### Step 2: Update Navigation (Beautiful Jekyll)

Edit `_config.yml` in your abdullahsahruri.github.io repository:

```yaml
navbar-links:
  About Me: "aboutme"
  Resources:
    - Beautiful Jekyll: "https://beautifuljekyll.com"
    - Learn markdown: "https://www.markdowntutorial.com/"
  Conferences: "conferences"  # ADD THIS LINE
  Author's home: "https://deanattali.com"
```

### Step 3: Push Conference Data to Your Site Repo

Update the GitHub Actions workflow to push data to your site:

**Edit `.github/workflows/tracker.yml`**:

```yaml
      # After updating database, push to main site
      - name: Push to main site repository
        run: |
          # Clone your main site repo
          git clone https://github.com/abdullahsahruri/abdullahsahruri.github.io.git site

          # Copy database JSON to site (for the JavaScript to load)
          cp conference_database.json site/assets/

          # Copy updated conferences.md page
          cp conferences.md site/

          # Commit and push to site
          cd site
          git config user.name "GitHub Action"
          git config user.email "action@github.com"
          git add conference_database.json conferences.md
          git commit -m "Update conference deadlines - $(date +'%Y-%m-%d')" || echo "No changes"
          git push https://${{ secrets.SITE_GITHUB_TOKEN }}@github.com/abdullahsahruri/abdullahsahruri.github.io.git main
```

### Step 4: Create GitHub Token for Site Access

1. Go to https://github.com/settings/tokens/new
2. Name: "Conference Tracker"
3. Scopes: Check `repo` (full control)
4. Generate token
5. Copy token

6. Add to conference-tracker repository secrets:
   - Secret name: `SITE_GITHUB_TOKEN`
   - Value: Your token

### Step 5: Create `assets` Directory in Your Site

```bash
cd /path/to/abdullahsahruri.github.io
mkdir -p assets
```

### Step 6: Update conferences.md to Load from Correct Path

Edit the fetch URL in `conferences.md`:

```javascript
// Change this line:
const response = await fetch('https://raw.githubusercontent.com/abdullahsahruri/conference-tracker/main/conference_database.json');

// To this:
const response = await fetch('/assets/conference_database.json');
```

### Step 7: Commit and Push

```bash
cd /path/to/abdullahsahruri.github.io
git add conferences.md assets/ _config.yml
git commit -m "Add conference deadlines tracker page"
git push
```

**Your conference page will be live at:**
`https://abdullahsahruri.github.io/conferences`

---

## 🔥 Option 2: Replace Homepage with Conference Table

If you want the conference table as your main landing page:

### Step 1: Backup Your Site

```bash
cd /path/to/abdullahsahruri.github.io
git branch backup-beautiful-jekyll
git push origin backup-beautiful-jekyll
```

### Step 2: Replace index.html

```bash
# Remove existing index
rm index.html index.md

# Copy conference table as index
cp conference_table.html index.html
```

### Step 3: Clean Up Beautiful Jekyll

```bash
# Remove Beautiful Jekyll files (optional)
rm -rf _posts/ aboutme.md _config.yml
```

### Step 4: Simplify

Just keep:
- `index.html` (your conference table)
- `conference_database.json`
- `assets/` folder

### Step 5: Push

```bash
git add .
git commit -m "Replace site with conference tracker"
git push
```

---

## 🤖 Automated Updates Workflow

Once integrated, here's how it works:

```
Daily at 9 AM UTC
        ↓
conference-tracker repo:
  • Searches conferences
  • Updates database
  • Detects changes
  • Sends emails
        ↓
abdullahsahruri.github.io repo:
  • Receives updated JSON
  • Receives updated page
  • GitHub Pages auto-deploys
        ↓
Your live site updates automatically!
```

---

## 📱 Mobile-Responsive Design

The table is already mobile-responsive with:
- ✅ Scrollable on small screens
- ✅ Touch-friendly buttons
- ✅ Readable font sizes
- ✅ Clean Beautiful Jekyll integration

---

## 🎨 Customization

### Change Colors to Match Your Site

Edit the `<style>` section in `conferences.md`:

```css
.conference-table th {
    background-color: #2c5aa0;  /* Change this to your site's primary color */
    color: white;
}
```

### Add Your Profile Info

Add to the top of `conferences.md`:

```markdown
---
layout: page
title: Conference Deadlines
subtitle: Tracked and maintained by Abdullah Sahruri
---

<div style="text-align: center; margin: 20px 0;">
    <img src="/assets/img/avatar-icon.png" alt="Avatar" style="border-radius: 50%; width: 100px;">
    <p>PhD Student | Conference Tracker Enthusiast</p>
</div>
```

---

## 🔍 SEO Optimization

Add to `conferences.md` front matter:

```yaml
---
layout: page
title: Conference Deadlines
subtitle: Automatically updated conference submission deadlines
description: Track computer science conference deadlines automatically
keywords: conference deadlines, computer science, submission dates, ISCA, DAC, MICRO
image: /assets/img/conference-preview.png
share-img: /assets/img/conference-preview.png
---
```

---

## 🚀 Quick Start Commands

### Option 1 (Add as Tab):

```bash
# In conference-tracker directory
cp conferences.md ~/path/to/abdullahsahruri.github.io/

# In site directory
cd ~/path/to/abdullahsahruri.github.io
mkdir -p assets
nano _config.yml  # Add "Conferences: conferences" to navbar-links
git add .
git commit -m "Add conference tracker page"
git push
```

### Option 2 (Replace Homepage):

```bash
cd ~/path/to/abdullahsahruri.github.io
git checkout -b backup-beautiful-jekyll
git push origin backup-beautiful-jekyll
git checkout main

# Copy conference files
cp ~/path/to/conference-tracker/conference_table.html ./index.html
cp ~/path/to/conference-tracker/conference_database.json ./

git add .
git commit -m "Replace with conference tracker"
git push
```

---

## 📊 Example Preview

After integration, your site will have:

**Navigation Bar:**
```
[About Me] [Resources ▾] [Conferences] [Author's home]
```

**Conferences Page:**
```
═══════════════════════════════════════════════════
        Conference Deadlines
        Automatically updated daily
═══════════════════════════════════════════════════

🔄 Updated daily at 9 AM UTC | 📧 Email notifications

[🔍 Search conferences...]

[All] [2025] [2026] [Upcoming Deadlines]

╔═══════════════╦═══════════════╦════════════════╗
║ Conference    ║ Paper Deadline║ Website        ║
╠═══════════════╬═══════════════╬════════════════╣
║ ISCA 2026     ║ Nov 10, 2025  ║ iscaconf.org   ║
║ DAC 2026      ║ Nov 18, 2025  ║ dac.com        ║
║ GLSVLSI 2025  ║ Mar 17, 2025  ║ glsvlsi.org    ║
╚═══════════════╩═══════════════╩════════════════╝

Last updated: Oct 31, 2025 | Total: 48 conferences
```

---

## 🎯 Which Option Should You Choose?

### Choose Option 1 (Add as Tab) if:
- ✅ You want to keep your existing Beautiful Jekyll site
- ✅ You have other content (blog posts, about page, etc.)
- ✅ You want conferences as a separate section
- ✅ You like the Beautiful Jekyll theme

### Choose Option 2 (Replace Homepage) if:
- ✅ Your main purpose is the conference tracker
- ✅ You don't need the Beautiful Jekyll theme
- ✅ You want a simple, focused site
- ✅ You prefer minimal setup

---

## 🆘 Need Help?

**Common Issues:**

1. **Page not showing up?**
   - Check `_config.yml` has correct navbar link
   - Verify `conferences.md` is in root directory
   - Wait 2-3 minutes for GitHub Pages to rebuild

2. **Table not loading?**
   - Check browser console for errors
   - Verify `conference_database.json` is accessible
   - Check fetch URL is correct

3. **Styles look wrong?**
   - Beautiful Jekyll may override some CSS
   - Add `!important` to style rules if needed
   - Or use inline styles

---

**Ready to integrate? Pick your option and follow the steps!** 🚀
