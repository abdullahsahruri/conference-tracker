@echo off
REM Conference Tracker - Windows Launcher
REM Double-click this file to run the tracker from Windows

echo ========================================================================
echo Conference Tracker with Auto-Sync
echo ========================================================================
echo.
echo Starting tracker in WSL...
echo.

REM Run the script in WSL
wsl bash -c "cd /home/asahruri/work/conferences && ./run_tracker_and_sync.sh"

echo.
echo ========================================================================
echo Done! Press any key to close...
echo ========================================================================
pause >nul
