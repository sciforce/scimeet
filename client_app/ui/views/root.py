from datetime import datetime

from kivy.properties import ObjectProperty, Clock, ListProperty
from kivy.properties import StringProperty
from kivy.uix.screenmanager import ScreenManager, RiseInTransition

from core.schedule.meeting import Meeting
from ui.views.calendar.view import CalendarScreen
from ui.views.common import BaseWidget, OkCancelModalScreen, ErrorScreen, error_screen_wrapper, StartAppModalScreen
from ui.views.free_room.view import FreeRoomScreen
from ui.views.edit_meeting.view import EditMeetingScreen
from ui.views.meeting_details.view import MeetingDetailsScreen
from ui.views.status.view import StatusScreen


class RootWidget(ScreenManager, BaseWidget):

    current_meeting = ObjectProperty(None, allownone=True)
    today_meetings = ListProperty()
    error_message = StringProperty()

    def __init__(self, **kwargs):
        super(RootWidget, self).__init__(**kwargs)
        self.transition = RiseInTransition()
        self.error_message = ''
        self.previous_screens = []

        self.add_widget(StartAppModalScreen())
        self.current = StartAppModalScreen.NAME
        self.current_screen.data = dict(start_app_callback=self.start_app)

    def start_app(self, *args):
        self.add_widget(ErrorScreen())
        self.add_widget(FreeRoomScreen())
        self.add_widget(OkCancelModalScreen())
        self.add_widget(CalendarScreen())
        self.add_widget(StatusScreen())
        self.add_widget(EditMeetingScreen())
        self.add_widget(MeetingDetailsScreen())

        self.check_meetings()
        self.go_to_main_screen()

        Clock.schedule_interval(self.check_meetings, 5)

    def on_current(self, instance, value):
        if self.current in {StatusScreen.NAME, FreeRoomScreen.NAME}:
            self.previous_screens = []
        self.previous_screens.append(self.current)
        super(RootWidget, self).on_current(instance, value)

    def on_error_message(self, *args):
        if ErrorScreen.NAME in self.screen_names:
            self.current = ErrorScreen.NAME

    @error_screen_wrapper
    def check_meetings(self, *args):
        self.today_meetings = self.app.google_calendar.get_meetings_for_day()
        for meeting in self.today_meetings:
            if isinstance(meeting, Meeting) and meeting.start_time < datetime.now() < meeting.end_time:
                self.current_meeting = meeting
                return None
        self.current_meeting = None

    def go_to_main_screen(self, *args):
        if isinstance(self.current_meeting, Meeting):
            screen_name = StatusScreen.NAME
        else:
            screen_name = FreeRoomScreen.NAME
        self.current = screen_name

    def back_to_previous_screen(self, *args):
        if self.previous_screens:
            index = self.previous_screens.index(self.current)
            self.previous_screens = self.previous_screens[:index+1]
            screen_name = self.previous_screens[:-1].pop()
            if screen_name in {StatusScreen.NAME, FreeRoomScreen.NAME}:
                self.go_to_main_screen()
            else:
                self.current = screen_name

    def go_to_calendar_screen(self, *args):
        self.current = CalendarScreen.NAME

    def show_modal(self, text="", ok_callback=None, *args):
        self.current = OkCancelModalScreen.NAME
        self.current_screen.data = dict(text=text, ok_callback=ok_callback, cancel_callback=self.back_to_previous_screen)

    def on_back_pressed(self, *args):
        return False

    def on_menu_pressed(self, *args):
        return False
