from datetime import datetime

from kivy.properties import ListProperty

from core.schedule.meeting import Meeting
from ui.views.common import AutoRefreshWidget, error_screen_wrapper
from ui.views.styles import GlobalStyle


class FreeRoomScreen(AutoRefreshWidget):

    NAME = "free_room"
    background_color = ListProperty()

    def __init__(self):
        super(FreeRoomScreen, self).__init__(name=self.NAME)
        self.background_color = GlobalStyle.free_room_background_color

    def refresh(self, *args):
        self.ids.next_event_link.text = ""
        self.ids.current_date_time_label.text = datetime.now().strftime("%A, %B %d - %H:%M")

        try:
            next_event = next(_ for _ in self.app.root.today_meetings if isinstance(_, Meeting)
                              if _.start_time > datetime.now())
        except StopIteration:
            pass
        else:
            self.ids.next_event_link.text = "[color=449e3d][ref={}]next event:\n{} at {}[/ref][/color]".format(
                next_event.title, next_event.title, next_event.start_time.strftime("%H:%M"))
            self.ids.next_event_link.bind(on_ref_press=self.start_next_meeting_modal)

        self.app.root.go_to_main_screen()

    def start_next_meeting_modal(self, *args):
        self.app.root.show_modal(text='Are you sure you want to\nstart next meeting immediately?',
                                 ok_callback=self.start_next_event_in_service)

    @error_screen_wrapper
    def start_next_event_in_service(self, *args):
        next_event = self.app.google_calendar.start_next_event()
        self.app.root.current_meeting = next_event
        self.app.root.go_to_main_screen()
