from datetime import date, datetime, timedelta

from core.schedule.meeting import UnoccupiedTime
from core.settings import WORKDAY_START
from core.settings import EVENT_MINIMUM_DURATION
from core.settings import WORKDAY_END


class AbstractSchedule(object):

    def __init__(self, config):
        self.config = config

    def external_to_internal_event_dto(self, event_from_service):
        raise NotImplementedError

    def external_to_internal_daily_meetings(self, events_from_service):
        internal_events = []
        for index, event_from_service in enumerate(events_from_service):
            actual_event = self.external_to_internal_event_dto(event_from_service)
            current_time = datetime.now()

            # time before the first event
            if index == 0:
                if (actual_event.start_time - datetime.combine(actual_event.start_time, WORKDAY_START)).total_seconds() >= EVENT_MINIMUM_DURATION:
                    start_time = datetime.combine(actual_event.start_time, WORKDAY_START)
                    end_time = actual_event.start_time - timedelta(seconds=1)
                    if start_time > current_time:
                        internal_events.append(UnoccupiedTime(start_time=start_time,
                                                              end_time=end_time,
                                                              available=True))
                    if start_time < current_time < end_time:
                        internal_events.append(UnoccupiedTime(start_time=start_time,
                                                              end_time=current_time - timedelta(seconds=1),
                                                              available=False))

                        internal_events.append(UnoccupiedTime(start_time=current_time,
                                                              end_time=end_time,
                                                              available=True))
                    if end_time < current_time:
                        internal_events.append(UnoccupiedTime(start_time=start_time,
                                                              end_time=end_time,
                                                              available=False))

            # time after the previous event
            else:
                previous_event = self.external_to_internal_event_dto(events_from_service[index - 1])
                if (actual_event.start_time - previous_event.end_time).seconds >= EVENT_MINIMUM_DURATION:
                    start_time = previous_event.end_time + timedelta(seconds=1)
                    end_time = actual_event.start_time - timedelta(seconds=1)
                    if start_time > current_time:
                        internal_events.append(UnoccupiedTime(start_time=start_time,
                                                              end_time=end_time,
                                                              available=True))
                    if start_time < current_time < end_time:
                        internal_events.append(UnoccupiedTime(start_time=start_time,
                                                              end_time=current_time - timedelta(seconds=1),
                                                              available=False))

                        internal_events.append(UnoccupiedTime(start_time=current_time,
                                                              end_time=end_time,
                                                              available=(end_time - current_time).total_seconds()>=EVENT_MINIMUM_DURATION))
                    if end_time < current_time:
                        internal_events.append(UnoccupiedTime(start_time=start_time,
                                                              end_time=end_time,
                                                              available=False))

            # actual event
            internal_events.append(actual_event)

            # time after the last event
            if index == len(events_from_service) - 1:
                if (datetime.combine(actual_event.start_time, WORKDAY_END) - actual_event.end_time).total_seconds() >= EVENT_MINIMUM_DURATION:
                    start_time = actual_event.end_time + timedelta(seconds=1)
                    end_time = datetime.combine(actual_event.end_time, WORKDAY_END)
                    if start_time > current_time:
                        internal_events.append(UnoccupiedTime(start_time=start_time,
                                                              end_time=end_time,
                                                              available=True))
                    if start_time < current_time < end_time:
                        internal_events.append(UnoccupiedTime(start_time=start_time,
                                                              end_time=current_time - timedelta(seconds=1),
                                                              available=False))

                        internal_events.append(UnoccupiedTime(start_time=current_time,
                                                              end_time=end_time,
                                                              available=True))
                    if end_time < current_time:
                        internal_events.append(UnoccupiedTime(start_time=start_time,
                                                              end_time=end_time,
                                                              available=False))

        return internal_events

    def get_meeting_types(self):
        raise NotImplementedError

    def get_current_meeting(self):
        raise NotImplementedError

    def get_next_meeting(self, now=None):
        raise NotImplementedError

    def get_meetings_for_day(self, day=None):
        if day is None:
            day = date.today()
        events_from_service = self.get_meetings(datetime.combine(day, WORKDAY_START),
                                                datetime.combine(day, WORKDAY_END))

        internal_events = self.external_to_internal_daily_meetings(events_from_service)
        if not events_from_service:
            workday_start_datetime = datetime.combine(day, WORKDAY_START)
            start_time = workday_start_datetime if workday_start_datetime > datetime.now() else datetime.now()
            internal_events.append(UnoccupiedTime(start_time,
                                                  datetime.combine(day, WORKDAY_END),
                                                  available=day >= datetime.now().date()))
        return internal_events

    def get_meetings_for_week(self, week_start=None):
        if week_start is None:
            today = date.today()
            week_start = today - timedelta(days=today.weekday())
        events_from_service = self.get_meetings(datetime.combine(week_start, WORKDAY_START),
                                                datetime.combine(week_start + timedelta(days=6), WORKDAY_END))
        weekly_events_from_service = [list() for _ in range(6)]
        for event_from_service in events_from_service:
            event = self.external_to_internal_event_dto(event_from_service)
            day_index = event.start_time.weekday()
            if day_index != 6:
                weekly_events_from_service[day_index].append(event_from_service)
        internal_meetings_by_day = []

        for day_index, weekly_event_from_service in enumerate(weekly_events_from_service):

            converted = self.external_to_internal_daily_meetings(weekly_event_from_service)
            if converted:
                internal_meetings_by_day.append(converted)
            else:
                internal_meetings_by_day.append([UnoccupiedTime(
                    start_time=datetime.combine(week_start + timedelta(days=day_index), WORKDAY_START),
                    end_time=datetime.combine(week_start + timedelta(days=day_index), WORKDAY_END))]
                )
        return internal_meetings_by_day

    def get_meetings(self, start_time, end_time):
        raise NotImplementedError

    def get_meeting(self, meeting_id):
        raise NotImplementedError
