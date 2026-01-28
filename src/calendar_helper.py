"""
Google Calendar Helper - Creates events in your Experiments calendar

This file has functions to interact with Google Calendar.
Think of it as a translator between what we want (experiment name + dates)
and what Google Calendar API expects.
"""

from datetime import datetime, timedelta

def create_experiment_event(service, experiment_name, start_date, duration_days):
    """
    Create a new event in the "Experiments" Google Calendar.
    
    Args:
        service: The authenticated Google Calendar service (from auth.py)
        experiment_name: Name of the experiment (string)
        start_date: Start date as string in format "YYYY-MM-DD"
        duration_days: How many days the experiment runs (integer)
    
    Returns:
        event_id: The ID of the created event
    """
    
    # Convert string date to datetime object
    start = datetime.strptime(start_date, "%Y-%m-%d")
    # Calculate end date by adding duration
    end = start + timedelta(days=duration_days)
    
    # Format dates for Google Calendar (it wants ISO format with timezone)
    # All-day event format: dates only (no time)
    event_body = {
        'summary': experiment_name,
        'description': f'Duration: {duration_days} days',
        'start': {
            'date': start.strftime("%Y-%m-%d"),
        },
        'end': {
            'date': end.strftime("%Y-%m-%d"),
        }
    }
    
    # First, we need to find the "Experiments" calendar ID
    calendar_id = get_experiments_calendar_id(service)
    
    if not calendar_id:
        raise Exception("Could not find 'Experiments' calendar. Create it in Google Calendar first.")
    
    # Create the event
    event = service.events().insert(
        calendarId=calendar_id,
        body=event_body
    ).execute()
    
    return event['id']


def get_experiments_calendar_id(service):
    """
    Find the calendar ID for "Experiments" calendar.
    
    Google Calendar API requires a calendar ID to create events.
    This function searches your calendars for one named "Experiments".
    
    Args:
        service: The authenticated Google Calendar service
    
    Returns:
        calendar_id (string) or None if not found
    """
    
    calendars_result = service.calendarList().list().execute()
    calendars = calendars_result.get('items', [])
    
    for calendar in calendars:
        if calendar['summary'] == 'Experiments':
            return calendar['id']
    
    return None
