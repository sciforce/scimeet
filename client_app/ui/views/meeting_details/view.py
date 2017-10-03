from kivy.properties import StringProperty, partial
from kivy.uix.label import Label

from core.schedule.meeting import Meeting
from ui.views.common import AutoSwitchToMainScreenWidget, EditItemButton, DeleteItemButton, BackButton


class MeetingDetailsScreen(AutoSwitchToMainScreenWidget):

    NAME = "meeting_details_screen"

    def __init__(self):
        super(MeetingDetailsScreen, self).__init__(name=self.NAME)
        self.context_key = self.NAME
        self.meeting = None

    def draw_static(self, *args):
        self.ids.meeting_name_label.text = self.meeting.title
        self.ids.meeting_date_label.text = self.meeting.start_time.strftime("%A %B %d, %Y")
        self.ids.meeting_time_label.text = '{} - {}'.format(
            self.meeting.start_time.strftime("%H:%M"),
            self.meeting.end_time.strftime("%H:%M")
        )

        self.ids.buttons_container.clear_widgets()

        self.ids.buttons_container.add_widget(Label(size_hint_x=1))
        self.ids.buttons_container.add_widget(BackButton())
        if self.meeting.available:
            self.ids.buttons_container.add_widget(
                EditItemButton(on_press=partial(self.edit_meeting, self.meeting))
            )
            self.ids.buttons_container.add_widget(
                DeleteItemButton(on_press=partial(self.app.root.show_modal,
                                                  'Are you sure you want to\ndelete this meeting?',
                                                  self.delete_meeting))
            )
        self.ids.buttons_container.add_widget(Label(size_hint_x=1))

    def edit_meeting(self, meeting=None, *args):
        edit_meeting_screen = self.app.context['edit_meeting_screen']
        edit_meeting_screen.meeting = self.meeting
        self.app.root.current = edit_meeting_screen.NAME

    def delete_meeting(self, *args):
        self.app.google_calendar.delete_event(google_id=self.meeting.google_id)
        self.app.root.current_meeting = None
        self.app.root.go_to_calendar_screen()

    def on_pre_enter(self, *args):
        self.draw_static()
        super(MeetingDetailsScreen, self).on_pre_enter(self, *args)
