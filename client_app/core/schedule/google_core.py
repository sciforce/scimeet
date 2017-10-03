import argparse
from collections import defaultdict
from datetime import datetime, timedelta
from cachetools import TTLCache, cached
from core.schedule.abstract import AbstractSchedule
from core.schedule.meeting import Meeting

import httplib2

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from core.settings import EVENT_MINIMUM_DURATION

ttl_cache = TTLCache(maxsize=20, ttl=10)


# TODO: refactor fn calls
def rgb_to_kivy(rgb):
    return [
        float(rgb[0]) / 255,  # red
        float(rgb[1]) / 255,  # green
        float(rgb[2]) / 255,  # blue
        float(rgb[3])         # alpha
    ]


class GoogleCalendar(AbstractSchedule):

    COLOR_MAPPING = defaultdict(lambda x: [225, 225, 225, 1],
                                **{'1': [164, 189, 252, 0.8],  # blue
                                   '2': [122, 231, 191, 0.8],  # green
                                   '3': [219, 173, 255, 0.8],  # purple
                                   '4': [255, 136, 124, 0.8],  # red
                                   '5': [251, 215, 91, 0.8],   # yellow
                                   '6': [255, 184, 120, 0.8],  # orange
                                   '7': [70, 214, 219, 0.8],   # turquoise
                                   '8': [225, 225, 225, 0.8],  # grey
                                   '9': [84, 132, 236, 0.8],   # bold blue
                                   '10': [81, 183, 73, 0.8],   # bold green
                                   '11': [220, 33, 39, 0.8]})  # bold red

    def __init__(self, config=None):
        super(GoogleCalendar, self).__init__(config)
        credentials = self.__get_credentials(config)
        http = credentials.authorize(httplib2.Http())
        self.core = discovery.build('calendar', 'v3', http=http)

    @staticmethod
    def __get_credentials(config):
        client_secret_file = config["CLIENT_SECRET_FILE"]
        app_name = config["APPLICATION_NAME"]
        scopes = config["SCOPES"]
        credential_path = config["CREDENTIAL_PATH"]

        store = Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(client_secret_file, scopes)
            flow.user_agent = app_name
            flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
            credentials = tools.run_flow(flow, store, flags)
        return credentials

    def get_meeting_types(self):
        return [dict(name="AL Local", type="internal", color="9"),
                dict(name="AL External", type="external", color="9"),
                dict(name="English", type="internal", color="9"),
                dict(name="Interview", type="internal", color="9"),
                dict(name="SA External", type="external", color="9"),
                dict(name="TLO Local", type="internal", color="9"),
                dict(name="TLO External", type="external", color="9")]

    def external_to_internal_event_dto(self, google_event):
        start_time = datetime.strptime(google_event['start'].get('dateTime')[:-6], "%Y-%m-%dT%H:%M:%S")
        end_time = datetime.strptime(google_event['end'].get('dateTime')[:-6], "%Y-%m-%dT%H:%M:%S")
        return Meeting(available=end_time > datetime.now(),
                       google_id=google_event['id'],
                       start_time=start_time,
                       end_time=end_time,
                       title=google_event['summary'],
                       participants=[],
                       color=rgb_to_kivy(self.COLOR_MAPPING[google_event.get('colorId', '1')]))

    @cached(ttl_cache)
    def get_meetings(self, start_time, end_time):
        # TODO: TZ hack. Seems that request start_time, end_time should be in UTC
        current_time_zone_offset = 3 * 60 * 60
        start_time = start_time - timedelta(seconds=current_time_zone_offset)
        end_time = end_time - timedelta(seconds=current_time_zone_offset)

        start_time = start_time.isoformat() + 'Z'
        end_time = end_time.isoformat() + 'Z'
        events_result = self.core.events().list(
            calendarId='primary',
            timeMin=start_time,
            timeMax=end_time,
            singleEvents=True,
            orderBy='startTime').execute()

        events = events_result.get('items', [])
        return events

    def get_current_meeting(self):
        pass

    def create_event(self, meeting):
        ttl_cache.clear()
        end_time = meeting.end_time - timedelta(seconds=1)
        event = {
            'summary': meeting.title,
            'description': meeting.title,
            'start': {
                'dateTime': meeting.start_time.isoformat(),
                'timeZone': 'Europe/Kiev',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'Europe/Kiev',
            },
            'colorId': meeting.color,
            # 'attendees': [
            #     {'email': 'lpage@example.com'},
            #     {'email': 'sbrin@example.com'},
            # ],
        }
        response_event = self.core.events().insert(calendarId='primary', body=event).execute()
        return self.external_to_internal_event_dto(response_event)

    def delete_event(self, google_id):
        ttl_cache.clear()
        self.core.events().delete(calendarId='primary', eventId=google_id).execute()

    def edit_event(self, event_id, meeting):
        ttl_cache.clear()

        m = {
            'start': {
                'dateTime': meeting.start_time.isoformat(),
                'timeZone': 'Europe/Kiev',
            },
            'end': {
                'dateTime': meeting.end_time.isoformat(),
                'timeZone': 'Europe/Kiev',
            }
        }
        self.core.events().patch(calendarId='primary', eventId=event_id, body=m).execute()

    def stop_event(self, event):
        ttl_cache.clear()
        delete_this_event = (datetime.now() - event.start_time).total_seconds() < EVENT_MINIMUM_DURATION
        if delete_this_event:
            self.delete_event(event.google_id)
        else:
            event.end_time = datetime.now()
            self.edit_event(event.google_id, event)

    def start_next_event(self, *args):
        meetings = self.get_meetings_for_day()
        try:
            next_event = next(m for m in meetings if m.start_time > datetime.now())
        except StopIteration:
            pass
        else:
            next_event.start_time = datetime.now()
            self.edit_event(next_event.google_id, next_event)
            return next_event

    def get_meeting(self, meeting_id):
        event_result = self.core.events().get(calendarId='primary', eventId=meeting_id).execute()
        return self.external_to_internal_event_dto(event_result)
