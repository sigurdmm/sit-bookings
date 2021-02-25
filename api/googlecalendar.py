import pickle
import os.path
from datetime import timedelta, datetime
import googleapiclient.errors
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/calendar']
CREDENTIALS_FILE = '.credentials.json'
CALENDAR_ID = 'q5diacsindgidfaspn5tb8ug08@group.calendar.google.com'


class Calendar:

    def __init__(self):
        self.service = self.get_calendar_service()

    # If modifying these scopes, delete the file token.pickle.
    def get_calendar_service(self):
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        service = build('calendar', 'v3', credentials=creds)
        return service

    def list_calendars(self):
        # Call the Calendar API
        print('Getting list of calendars')
        calendars_result = self.service.calendarList().list().execute()

        calendars = calendars_result.get('items', [])

        if not calendars:
            print('No calendars found.')
        for calendar in calendars:
            summary = calendar['summary']
            id = calendar['id']
            primary = "Primary" if calendar.get('primary') else ""
            print(f'SUMMARY={summary} ID={id} PRIMARY={primary}')
            # print("%s\t%s\t%s" % (summary, id, primary))

    def list_events(self):
        # Call the Calendar API
        now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        print('Getting List o 10 events')
        events_result = self.service.events().list(
            calendarId=CALENDAR_ID, timeMin=now,
            maxResults=100, singleEvents=True,
            orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])

    def get_events(self):
        # Call the Calendar API
        now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time

        events_result = self.service.events().list(
            calendarId=CALENDAR_ID, timeMin=now,
            maxResults=100, singleEvents=True,
            orderBy='startTime').execute()
        events = events_result.get('items', [])
        return events
        # if not events:
        #     print('No upcoming events found.')
        # for event in events:
        #     start = event['start'].get('dateTime', event['start'].get('date'))
        #     print(start, event['summary'], event['description'])

    def create_event(self, event):
        # creates one hour event tomorrow 10 AM IST
        # d = datetime.now().date()
        # tomorrow = datetime(d.year, d.month, d.day, 10) + timedelta(days=1)
        # start = tomorrow.isoformat()
        # end = (tomorrow + timedelta(hours=1)).isoformat()
        #
        # event = {
        #     "summary": "Summary message",
        #     "description": "Description message",
        #     "start": start,
        #     "end": end
        # }

        event_result = self.service.events().insert(calendarId=CALENDAR_ID,
                                                    body={
                                                        "summary": event['summary'],
                                                        "description": event['description'],
                                                        "start": {"dateTime": event['start'],
                                                                  "timeZone": 'Europe/Oslo'},
                                                        "end": {"dateTime": event['end'], "timeZone": 'Europe/Oslo'},
                                                    }
                                                    ).execute()
        print(f'Training event {event["description"]} added to calendar.')
        # print("id: ", event_result['id'])
        # print("summary: ", event_result['summary'])
        # print("starts at: ", event_result['start']['dateTime'])
        # print("ends at: ", event_result['end']['dateTime'])

    def update_event(self):
        # update the event to tomorrow 9 AM IST

        d = datetime.now().date()
        tomorrow = datetime(d.year, d.month, d.day, 9) + timedelta(days=1)
        start = tomorrow.isoformat()
        end = (tomorrow + timedelta(hours=2)).isoformat()

        event_result = self.service.events().update(
            calendarId=CALENDAR_ID,
            eventId='<place your event ID here>',
            body={
                "summary": 'Updated Automating calendar',
                "description": 'This is a tutorial example of automating google calendar with python, updated time.',
                "start": {"dateTime": start, "timeZone": 'Asia/Kolkata'},
                "end": {"dateTime": end, "timeZone": 'Asia/Kolkata'},
            },
        ).execute()

        print("updated event")
        print("id: ", event_result['id'])
        print("summary: ", event_result['summary'])
        print("starts at: ", event_result['start']['dateTime'])
        print("ends at: ", event_result['end']['dateTime'])

    def delete_event(self, eventID):
        # Delete the event
        try:
            self.service.events().delete(
                calendarId=CALENDAR_ID,
                eventId=eventID,
            ).execute()
        except googleapiclient.errors.HttpError:
            print("Failed to delete event")

        print("Event deleted")

#
# def main():
#     calendar = Calendar()
#     calendar.list_events()
    # calendar.create_event()

# main()
