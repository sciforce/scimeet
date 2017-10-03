import datetime

from kivy.properties import ObjectProperty
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen

from core.schedule.meeting import Meeting
from ui.views.calendar.daily.view import DailyScreen
from ui.views.common import BaseWidget
from ui.views.styles import GlobalStyle

from ui.views.common import error_screen_wrapper

# TODO: move to settings
SHOW_MEETINGS = 4


class DayOfWeek(Button, BaseWidget):

    def __init__(self, **kwargs):
        super(DayOfWeek, self).__init__(**kwargs)
        self.day = None
        self.header_text_pattern = "[b]%a, %d[/b]\n"
        self.body_text_pattern = "            {} - {}  {}\n"
        self.footer_text_pattern = "            +{} more..."

    def on_press(self):
        self.app.root.current_day_index = int(self.id)
        self.app.context['calendar_screen'].show_day = self.day
        self.app.context['daily_screen'].load_day_and_slide(self.day)

    def show_contents(self, meetings):
        self.text_size = self.size
        self.text = self.day.strftime(self.header_text_pattern)
        filtered_meetings = [_ for _ in meetings if isinstance(_, Meeting)]
        for index, meeting in enumerate(filtered_meetings):
            if index == SHOW_MEETINGS:
                self.text += self.footer_text_pattern.format(len(filtered_meetings) - SHOW_MEETINGS)
                break
            self.text += self.body_text_pattern.format(meeting.start_time.strftime("%H:%M"),
                                                       meeting.end_time.strftime("%H:%M"),
                                                       meeting.title[:15])


class WeeklyScreen(Screen, BaseWidget):

    NAME = "weekly_screen"
    start_day = ObjectProperty()
    meetings = ObjectProperty()

    def __init__(self, **kwargs):
        super(WeeklyScreen, self).__init__(name=self.NAME)
        self.draw_static()

    def draw_static(self):
        for day_index in range(6):
            button = DayOfWeek()
            button.id = str(day_index)
            button.background_color = GlobalStyle.weekly_item_available_color
            button.font_name = GlobalStyle.standard_caption_font
            self.ids.calendar_layout.add_widget(button)

    def refresh(self, *args):
        instance, meetings = args
        for day_index in range(6):
            button = self.ids.calendar_layout.children[day_index]
            week_start = self.start_day - datetime.timedelta(days=self.start_day.weekday())
            button_day = week_start + datetime.timedelta(days=day_index)
            button.day = button_day
            if datetime.date.today() > button_day:
                button.background_color = GlobalStyle.weekly_item_unavailable_color
            elif datetime.date.today() == button_day:
                button.background_color = GlobalStyle.weekly_item_current_day_color
            else:
                button.background_color = GlobalStyle.weekly_item_available_color
            button.show_contents(meetings[day_index])

    @error_screen_wrapper
    def on_start_day(self, *args):
        week_start = self.start_day - datetime.timedelta(days=self.start_day.weekday())
        self.meetings = self.app.google_calendar.get_meetings_for_week(week_start)

    def on_meetings(self, *args):
        self.refresh(*args)
