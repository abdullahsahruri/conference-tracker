#!/usr/bin/env python3
"""
One-Time Google Calendar API Setup Script
==========================================

This script handles the OAuth 2.0 authentication flow to generate
the token.json file needed for Google Calendar API access.

Run this ONCE locally before setting up GitHub Actions.
"""

import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']


def main():
    """
    Main function to handle Google Calendar API authentication.

    This will:
    1. Check if token.json already exists
    2. If not, prompt for OAuth authorization using credentials.json
    3. Generate and save token.json for future use
    """
    creds = None

    # The file token.json stores the user's access and refresh tokens
    if os.path.exists('token.json'):
        print("✓ Found existing token.json")
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("→ Refreshing expired token...")
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                print("\n❌ ERROR: credentials.json not found!")
                print("\nPlease follow these steps to get credentials.json:")
                print("1. Go to https://console.cloud.google.com/")
                print("2. Create a new project (or select existing)")
                print("3. Enable the Google Calendar API")
                print("4. Go to 'Credentials' → 'Create Credentials' → 'OAuth client ID'")
                print("5. Choose 'Desktop app' as application type")
                print("6. Download the JSON file and save it as 'credentials.json'")
                print("7. Place credentials.json in the same directory as this script")
                return

            print("→ Starting OAuth 2.0 authorization flow...")
            print("→ Your browser will open for authorization...")
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
        print("✓ Successfully created token.json")

    # Test the credentials by accessing the Calendar API
    try:
        service = build('calendar', 'v3', credentials=creds)
        print("\n→ Testing Calendar API access...")

        # Get the primary calendar
        calendar = service.calendars().get(calendarId='primary').execute()
        print(f"✓ Successfully connected to calendar: {calendar['summary']}")

        print("\n✅ Setup complete!")
        print("\nNext steps:")
        print("1. Keep credentials.json and token.json safe (DO NOT commit to Git)")
        print("2. Add their contents as GitHub Secrets")
        print("3. Run main_scraper.py to test locally")
        print("4. Set up GitHub Actions to run automatically")

    except Exception as e:
        print(f"\n❌ Error testing Calendar API: {e}")


if __name__ == '__main__':
    main()
