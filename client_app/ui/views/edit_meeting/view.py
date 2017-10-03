import datetime

from kivy.adapters.listadapter import ListAdapter
from kivy.properties import ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.carousel import Carousel
from kivy.uix.label import Label
from kivy.uix.listview import ListView, ListItemButton
from kivy.uix.widget import Widget

from core.schedule.meeting import UnoccupiedTime, Meeting
from ui.views.common import BaseWidget, AutoSwitchToMainScreenWidget, round_to_minute, BackButton
from ui.views.styles import GlobalStyle

from ui.views.common import error_screen_wrapper
from core.settings import EVENT_MINIMUM_DURATION


def meeting_times_to_ui_meeting_times(meeting_times):
    available_times = []
    for t in meeting_times:
        if t.available:
            rounded_start_time = round_to_minute(t.start_time)
            available_times.append(rounded_start_time)
            if (t.end_time - rounded_start_time).total_seconds() > EVENT_MINIMUM_DURATION:
                next_start_time = rounded_start_time + datetime.timedelta(minutes=15)
                while next_start_time < t.end_time:
                    available_times.append(next_start_time)
                    next_start_time += datetime.timedelta(minutes=15)

    ui_meeting_times = [MeetingStartTimeItem(start_time=t) for t in available_times]
    return ui_meeting_times


def meeting_durations_to_ui_meeting_durations(today_meetings, meeting_start_time):
    max_time = meeting_start_time
    filtered_available_times = [_ for _ in today_meetings if isinstance(_, UnoccupiedTime)]
    for available_time in filtered_available_times:
        if available_time.end_time > meeting_start_time:
            max_time = available_time.end_time
            break
    durations = []
    end_time = round_to_minute(meeting_start_time)
    while end_time < max_time:
        end_time += datetime.timedelta(seconds=EVENT_MINIMUM_DURATION)
        durations.append(MeetingDurationItem(start_time=meeting_start_time, end_time=end_time))
    return durations


# screen

class EditMeetingScreen(AutoSwitchToMainScreenWidget):

    NAME = "edit_meeting_screen"

    def __init__(self):
        super(EditMeetingScreen, self).__init__(name=self.NAME)
        self.context_key = self.NAME
        self.meeting = None

    def on_enter(self, *args):
        self.ids.buttons_container.clear_widgets()
        self.ids.buttons_container.add_widget(Label(size_hint_x=1))
        self.ids.buttons_container.add_widget(BackButton())
        self.ids.buttons_container.add_widget(Label(size_hint_x=1))

        self.ids.edit_meeting_carousel.meeting = self.meeting
        self.ids.edit_meeting_carousel.clear()
        super(EditMeetingScreen, self).on_enter(*args)

    def on_leave(self, *args):
        self.ids.edit_meeting_carousel.clear()
        super(EditMeetingScreen, self).on_leave(*args)


class EditMeetingCarousel(Carousel, BaseWidget):
    direction = 'right'

    meeting_types = ListProperty()
    available_periods = ListProperty()
    meeting_durations = ListProperty()

    def __init__(self, **kwargs):
        super(EditMeetingCarousel, self).__init__(**kwargs)
        self.context_key = 'edit_meeting_carousel'
        self.meeting = None

    def on_meeting_types(self, *args):
        if self.meeting and self.meeting.google_id:
            # Fill meeting start times
            meeting = self.meeting
            if meeting.start_time.date() == datetime.datetime.now().date():
                meetings = self.app.root.today_meetings
            else:
                meetings = self.app.google_calendar.get_meetings_for_day(meeting.start_time.date())

            filtered_available_times = []
            for i, m in enumerate(meetings):
                if isinstance(m, Meeting) and m.google_id == meeting.google_id:
                    if i > 0 and isinstance(meetings[i-1], UnoccupiedTime):
                        filtered_available_times.append(meetings[i-1])

                    filtered_available_times.append(m)

                    if i < len(meetings) - 1 and isinstance(meetings[i+1], UnoccupiedTime):
                        filtered_available_times.append(meetings[i+1])

            self.available_periods = meeting_times_to_ui_meeting_times(filtered_available_times)
            self.load_next()
        else:
            adapter = MeetingTypesListAdapter(data=self.meeting_types, args_converter=MeetingTypeItem.args_converter)
            meeting_types_list = EditMeetingListView(adapter=adapter, size=self.size, text='Select meeting type')
            self.add_widget(meeting_types_list)

    def on_available_periods(self, *args):
        # TODO: refactor this hack
        if len(self.slides) == 3:
            self.slides.pop()
        if len(self.slides) == 2:
            self.slides.pop()
        adapter = MeetingStartTimesListAdapter(data=self.available_periods, args_converter=MeetingStartTimeItem.args_converter)
        meeting_time_list_view = EditMeetingListView(adapter=adapter, size=self.size, text='Select meeting start time')
        self.add_widget(meeting_time_list_view)

    def on_meeting_durations(self, *args):
        # TODO: refactor this hack
        if len(self.slides) == 3:
            self.slides.pop()
        adapter = MeetingDurationsListAdapter(data=self.meeting_durations, args_converter=MeetingDurationItem.args_converter)
        meeting_duration_list = EditMeetingListView(adapter=adapter, size=self.size, text='Select meeting duration')
        self.add_widget(meeting_duration_list)

    @error_screen_wrapper
    def clear(self):
        self.meeting_types = []
        self.available_periods = []
        self.meeting_durations = []
        self.clear_widgets()
        # Meeting types
        self.meeting_types = [MeetingTypeItem(text=t['name'], color=t['color'])
                              for t in self.app.google_calendar.get_meeting_types()]

    @error_screen_wrapper
    def save_meeting(self):
        if self.meeting.google_id:
            self.app.google_calendar.edit_event(self.meeting.google_id, self.meeting)
        else:
            self.app.google_calendar.create_event(self.meeting)


class BaseListItem(BaseWidget):
    def __init__(self, *args):
        super(BaseListItem, self).__init__()

    @staticmethod
    def args_converter(row_index, obj):
        return {'text': obj.text,
                'size_hint_y': None,
                'height': GlobalStyle.standard_menu_item_size,
                'font_size': GlobalStyle.standard_caption_font_size,
                'font_name': GlobalStyle.standard_caption_font,
                'deselected_color': GlobalStyle.list_item_selected_color,
                'selected_color': GlobalStyle.list_item_deselected_color}


class LW(ListView):
    def __init__(self, **kwargs):
        super(LW, self).__init__(**kwargs)


class EditMeetingListView(Widget):
    def __init__(self, **kwargs):
        super(EditMeetingListView, self).__init__()
        self.size = kwargs['size']
        bl = BoxLayout(orientation='vertical', size=self.size, spacing=30)
        bl.add_widget(Label(text=kwargs['text'],
                            size_hint_y=5,
                            font_size=GlobalStyle.big_caption_font_size,
                            font_name=GlobalStyle.standard_caption_font))
        bl.add_widget(LW(size_hint_y=95, **kwargs))
        self.add_widget(bl)


# Meeting types

class MeetingTypeItem(BaseListItem):
    def __init__(self, text='', is_selected=False, color=None):
        super(MeetingTypeItem, self).__init__()
        self.text = text
        self.is_selected = is_selected
        self.color = color


class MeetingTypesListAdapter(ListAdapter, BaseWidget):
    def __init__(self, **kwargs):
        super(MeetingTypesListAdapter, self).__init__(propagate_selection_to_data=True,
                                                      cls=ListItemButton,
                                                      **kwargs)

    def on_selection_change(self, *args):
        if not self.selection:
            return None
        carousel = self.app.context['edit_meeting_carousel']
        carousel.meeting.title = self.data[self.selection[0].index].text

        # Fill meeting start times
        meeting = carousel.meeting
        if meeting.start_time.date() == datetime.datetime.now().date():
            # present
            meetings = self.app.root.today_meetings
            if meeting.google_id:
                # edit
                filtered_available_times = meetings
            else:
                # create WORKS
                filtered_available_times = [_ for _ in meetings if isinstance(_, UnoccupiedTime)]
        else:
            # future events
            meetings = self.app.google_calendar.get_meetings_for_day(meeting.start_time.date())
            if meeting.google_id:
                # edit
                filtered_available_times = meetings
            else:
                # create WORKS
                filtered_available_times = [_ for _ in meetings
                                            if isinstance(_, UnoccupiedTime)
                                            if _.end_time <= meeting.end_time
                                            if _.start_time >= meeting.start_time]

        carousel.available_periods = meeting_times_to_ui_meeting_times(filtered_available_times)
        carousel.load_next()


# Meeting start times

class MeetingStartTimeItem(BaseListItem):
    def __init__(self, is_selected=False, start_time=None, text=""):
        super(MeetingStartTimeItem, self).__init__()
        self.is_selected = is_selected
        self.text = text or start_time.strftime("%H:%M")
        if start_time:
            self.start_time = start_time
        else:
            self.start_time = datetime.datetime.now()


class MeetingStartTimesListAdapter(ListAdapter, BaseWidget):
    def __init__(self, **kwargs):
        super(MeetingStartTimesListAdapter, self).__init__(propagate_selection_to_data=True,
                                                           cls=ListItemButton,
                                                           **kwargs)

    def on_selection_change(self, *args):
        if not self.selection:
            return None
        carousel = self.app.context['edit_meeting_carousel']
        selected_item = self.data[self.selection[0].index]
        carousel.meeting.start_time = selected_item.start_time
        if selected_item.start_time.date() == datetime.datetime.today().date():
            meetings = self.app.root.today_meetings
        else:
            meetings = self.app.google_calendar.get_meetings_for_day(selected_item.start_time.date())
        durations = meeting_durations_to_ui_meeting_durations(meetings,
                                                              selected_item.start_time)
        carousel.meeting_durations = durations
        carousel.load_next()


# Meeting durations

class MeetingDurationItem(BaseListItem):
    def __init__(self, is_selected=False, start_time=None, end_time=None):
        super(MeetingDurationItem, self).__init__()
        self.is_selected = is_selected
        self.start_time = start_time
        self.end_time = end_time
        self.duration = int((self.end_time - self.start_time).total_seconds() / 60)
        self.text = "{}  ({} min)".format(self.end_time.strftime("%H:%M"), self.duration)


class MeetingDurationsListAdapter(ListAdapter, BaseWidget):
    def __init__(self, **kwargs):
        super(MeetingDurationsListAdapter, self).__init__(propagate_selection_to_data=True,
                                                          cls=ListItemButton,
                                                          **kwargs)

    @error_screen_wrapper
    def on_selection_change(self, *args):
        if not self.selection:
            return None
        carousel = self.app.context['edit_meeting_carousel']
        selected_item = self.data[self.selection[0].index]
        carousel.meeting.end_time = selected_item.end_time
        carousel.save_meeting()
        if (carousel.meeting.start_time - datetime.datetime.now()).total_seconds() <= 0:
            self.app.root.current_meeting = carousel.meeting
        self.app.root.go_to_main_screen()
