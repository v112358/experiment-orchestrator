"""
Google Calendar OAuth Authentication Handler

This file handles logging into Google Calendar using OAuth.
It creates a token.json file after first login so you don't need to log in again.
"""

import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# These are the permissions we're asking Google to give us
# CALENDAR scope means we can read and write to calendars
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_authenticated_service():
    """
    Authenticate with Google Calendar API.
    
    Returns:
        - On first run: Opens browser for you to log in, saves token.json
        - On future runs: Uses saved token.json automatically
    
    Returns:
        service: Authenticated Google Calendar service object
    """
    
    creds = None
    
    # Check if token.json already exists (meaning we've logged in before)
    if os.path.exists('data/token.json'):
        creds = Credentials.from_authorized_user_file('data/token.json', SCOPES)
    
    # If no valid credentials, run OAuth flow (user logs in)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Refresh the token if it expired
            creds.refresh(Request())
        else:
            # First time: open browser for login
            flow = InstalledAppFlow.from_client_secrets_file(
                'data/client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the token so we don't need to log in next time
        os.makedirs('data', exist_ok=True)
        with open('data/token.json', 'w') as token:
            token.write(creds.to_json())
    
    # Now we return the service that can actually talk to Google Calendar
    from googleapiclient.discovery import build
    service = build('calendar', 'v3', credentials=creds)
    return service
