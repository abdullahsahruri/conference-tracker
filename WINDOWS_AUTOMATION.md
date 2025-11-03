# Windows Automation Guide

Automate conference tracking without manually logging into WSL.

## Option 1: Double-Click to Run (Manual)

### Setup (One-Time)

1. **Copy the .bat file to Windows**:
   - Open Windows Explorer
   - Navigate to: `\\wsl$\Ubuntu\home\asahruri\work\conferences\`
   - Copy `run_tracker.bat` to your Windows Desktop

2. **Run the tracker**:
   - Double-click `run_tracker.bat` on your Desktop
   - The script will automatically:
     - Start WSL
     - Run Ollama tracker
     - Sync to website
     - Push to GitHub
   - Window stays open to show results

**When to use:** Run manually whenever you want to update deadlines.

---

## Option 2: Automatic Daily Updates (Recommended)

Use Windows Task Scheduler to run the tracker automatically every day.

### Setup (One-Time)

1. **Open Task Scheduler**:
   - Press `Win + R`
   - Type: `taskschd.msc`
   - Press Enter

2. **Create a new task**:
   - Click "Create Task" (not "Create Basic Task")
   - **General Tab:**
     - Name: `Conference Tracker`
     - Description: `Automatically update conference deadlines daily`
     - ✅ Run whether user is logged on or not
     - ✅ Run with highest privileges

3. **Triggers Tab:**
   - Click "New"
   - Begin the task: `On a schedule`
   - Settings: `Daily`
   - Start time: `9:00 AM` (or your preferred time)
   - ✅ Enabled

4. **Actions Tab:**
   - Click "New"
   - Action: `Start a program`
   - Program/script: `wsl`
   - Add arguments: `bash -c "cd /home/asahruri/work/conferences && ./run_tracker_and_sync.sh"`

5. **Conditions Tab:**
   - ✅ Start the task only if the computer is on AC power (optional)
   - ✅ Wake the computer to run this task (optional)

6. **Settings Tab:**
   - ✅ Allow task to be run on demand
   - ✅ If the task fails, restart every: `1 hour`
   - ✅ Stop the task if it runs longer than: `3 hours`

7. **Click OK** and enter your Windows password if prompted

### Verify It Works

Test the task immediately:
- In Task Scheduler, right-click "Conference Tracker"
- Click "Run"
- Check the "Last Run Result" column (should say "Success")

### View Results

Check the log:
```cmd
wsl cat /home/asahruri/work/conferences/tracker.log
```

---

## Option 3: GitHub Actions (Semi-Automatic)

**Limitation:** GitHub Actions **cannot** run Ollama (it's local-only).

However, you can create a GitHub Action to:
1. Manually trigger from GitHub website
2. Just sync existing database to website (no new extraction)

### When to use this:
- When you've run the tracker locally
- Want to quickly push to website without WSL

See `.github/workflows/manual-sync.yml` for setup.

---

## Troubleshooting

### "Ollama not running" error

**Problem:** Task Scheduler runs before Ollama starts.

**Solution:** Make Ollama start automatically:

1. **Option A: Make Ollama a Windows Service**
   ```cmd
   wsl sudo systemctl enable ollama
   wsl sudo systemctl start ollama
   ```

2. **Option B: Add Ollama check to script**
   The script already checks if Ollama is running and starts it if needed.

### Task shows "Failed" in Task Scheduler

Check the log:
```cmd
wsl cat /home/asahruri/work/conferences/tracker.log
```

Or run manually:
```cmd
wsl bash -c "cd /home/asahruri/work/conferences && ./run_tracker_and_sync.sh"
```

### Git push authentication fails

The script uses your saved git credentials. If it fails:
```bash
# In WSL:
cd ~/work/conferences
git config credential.helper store
git push  # Enter credentials once
```

---

## Recommended Setup

For fully hands-free automation:

1. ✅ **Set up Task Scheduler** (runs daily automatically)
2. ✅ **Make Ollama auto-start** (via systemd or startup script)
3. ✅ **Keep double-click .bat** (for manual runs when needed)

This way:
- Tracker runs every day at 9 AM (or your chosen time)
- No manual intervention needed
- You can still manually trigger via .bat file

---

## Viewing Logs

### Real-time (while running):
```cmd
wsl tail -f /home/asahruri/work/conferences/tracker.log
```

### Recent runs:
```cmd
wsl tail -100 /home/asahruri/work/conferences/tracker.log
```

### Check what changed:
```cmd
wsl cat /home/asahruri/work/conferences/deadline_changes.log
```

---

## Disabling Automatic Updates

To stop automatic updates:
1. Open Task Scheduler
2. Find "Conference Tracker"
3. Right-click → Disable

---

## Summary

| Method | When to Use | Pros | Cons |
|--------|-------------|------|------|
| **Double-click .bat** | Manual updates | Simple, see output | Must remember to run |
| **Task Scheduler** | Set & forget | Fully automatic | No visual feedback |
| **GitHub Actions** | Remote trigger | Can trigger from phone | Can't run Ollama (sync only) |

**Recommended:** Use Task Scheduler for daily automation + keep .bat file for manual runs.
