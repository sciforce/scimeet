import datetime

from ui.views.common import AutoRefreshWidget


class StatusScreen(AutoRefreshWidget):

    NAME = "status_screen"

    def __init__(self, **kwargs):
        super(StatusScreen, self).__init__(name=self.NAME)

    def refresh(self, *args):
        current_meeting = self.app.root.current_meeting
        if current_meeting is not None:
            self.ids.current_date_time_label.text = datetime.datetime.now().strftime("%A, %B %d - %H:%M")
            self.ids.start_time_label.time = current_meeting.start_time
            self.ids.end_time_label.time = current_meeting.end_time
            self.ids.meeting_title_label.text = current_meeting.title

            time_diff = (current_meeting.end_time - current_meeting.start_time).total_seconds()
            passes = (datetime.datetime.now() - current_meeting.start_time).total_seconds()
            self.ids.meeting_progress_bar.value = int(passes / time_diff * 100)
        else:
            self.app.root.go_to_main_screen()
