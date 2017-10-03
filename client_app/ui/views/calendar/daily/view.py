from kivy.properties import ObjectProperty
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen

from core.schedule.meeting import UnoccupiedTime, Meeting
from core.settings import EVENT_MINIMUM_DURATION
from ui.views.common import CustomTimeLabel, BaseWidget
from ui.views.styles import GlobalStyle

from ui.views.common import error_screen_wrapper


class MeetingTimeLabel(CustomTimeLabel):
    def __init__(self, start_time=None, end_time=None):
        super(MeetingTimeLabel, self).__init__()
        self.font_size = GlobalStyle.big_caption_font_size
        self.height = GlobalStyle.standard_menu_item_size
        self.outline_color = GlobalStyle.list_item_selected_color
        self.size_hint = (20, None)
        self.font_name = GlobalStyle.standard_caption_font
        self.start_time = start_time
        self.end_time = end_time
        self.time = (start_time, end_time)


class MeetingButton(Button, BaseWidget):
    def __init__(self, start_time=None, end_time=None, available=True, meeting_id=None, **kwargs):
        super(MeetingButton, self).__init__(**kwargs)
        self.size_hint = (70, None)
        self.meeting_id = meeting_id
        self.font_size = GlobalStyle.big_caption_font_size
        self.height = GlobalStyle.standard_menu_item_size
        self.font_name = GlobalStyle.standard_caption_font
        self.start_time = start_time
        self.end_time = end_time
        self.available = available
        if self.available:
            self.background_color = GlobalStyle.daily_available_meeting_color
        else:
            self.background_color = GlobalStyle.daily_unavailable_meeting_color

    def on_press(self):
        meeting_details_screen = self.app.context['meeting_details_screen']
        meeting_details_screen.meeting = self.app.google_calendar.get_meeting(self.meeting_id)
        self.app.root.current = meeting_details_screen.NAME


class UnoccupiedTimeLabel(CustomTimeLabel):
    def __init__(self, start_time=None, end_time=None):
        super(UnoccupiedTimeLabel, self).__init__()
        self.font_size = GlobalStyle.big_caption_font_size
        self.height = GlobalStyle.standard_menu_item_size
        self.outline_color = GlobalStyle.list_item_selected_color
        self.size_hint = (20, None)
        self.font_name = GlobalStyle.standard_caption_font
        if start_time and end_time:
            self.time = (start_time, end_time)


class UnoccupiedTimeButton(MeetingButton):
    def __init__(self, start_time=None, end_time=None, available=False):
        super(UnoccupiedTimeButton, self).__init__(start_time=start_time, end_time=end_time)
        self.start_time = start_time
        self.end_time = end_time
        self.available = available
        self.height = GlobalStyle.standard_menu_item_size
        if self.available:
            self.text = "available"
            self.background_color = GlobalStyle.list_item_deselected_color
        else:
            # self.text = "no events on {}".format(self.start_time.strftime("%A"))
            self.text = "no events"
            self.background_color = GlobalStyle.daily_unavailable_meeting_color
            self.background_down = self.background_normal

    def on_press(self):
        if self.available:
            edit_meeting_screen = self.app.context['edit_meeting_screen']
            edit_meeting_screen.meeting = Meeting(start_time=self.start_time, end_time=self.end_time)
            self.app.root.current = edit_meeting_screen.NAME


class DailyScreen(Screen, BaseWidget):

    NAME = "daily_screen"
    start_day = ObjectProperty()
    meetings = ObjectProperty()

    def __init__(self, **kwargs):
        super(DailyScreen, self).__init__(name=self.NAME)
        self.context_key = self.NAME
        self.draw_static()

    def draw_static(self):
        layout = self.ids.daily_grid
        layout.bind(minimum_height=layout.setter('height'))

    def refresh(self, *args):
        layout = self.ids.daily_grid
        layout.clear_widgets()

        if len(self.meetings) == 1:
            event = self.meetings[0]
            if isinstance(event, UnoccupiedTime):
                layout.add_widget(UnoccupiedTimeButton(start_time=event.start_time,
                                                       end_time=event.end_time,
                                                       available=event.available))
        else:
            for event in self.meetings:
                if isinstance(event, UnoccupiedTime):
                    if event.available and (event.end_time - event.start_time).total_seconds() > EVENT_MINIMUM_DURATION:
                        layout.add_widget(UnoccupiedTimeLabel(start_time=event.start_time,
                                                              end_time=event.end_time))
                        layout.add_widget(UnoccupiedTimeButton(start_time=event.start_time,
                                                               end_time=event.end_time,
                                                               available=event.available))

                elif isinstance(event, Meeting):
                    layout.add_widget(UnoccupiedTimeLabel(start_time=event.start_time,
                                                          end_time=event.end_time))
                    layout.add_widget(MeetingButton(start_time=event.start_time,
                                                    end_time=event.end_time,
                                                    text=event.title,
                                                    available=event.available,
                                                    meeting_id=event.google_id))

    @error_screen_wrapper
    def on_start_day(self, *args):
        self.meetings = self.app.google_calendar.get_meetings_for_day(self.start_day)

    def on_meetings(self, *args):
        self.refresh(*args)

    def load_day_and_slide(self, day):
        self.start_day = day
        self.app.context['calendar_carousel'].load_next()
