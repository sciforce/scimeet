

class Meeting:
    def __init__(self, start_time, end_time, title='', participants=None, color=None, google_id=None, available=True):
        self.available = available
        self.google_id = google_id
        self.start_time = start_time
        self.end_time = end_time
        self.title = title
        self.participants = participants
        self.color = color or []

    def __repr__(self):
        return 'Meeting "{title}" {start_time} - {end_time}'.format(**self.__dict__)


class UnoccupiedTime:
    def __init__(self, start_time, end_time, available=True):
        self.available = available
        self.start_time = start_time
        self.end_time = end_time
        self.title = ""
        self.participants = []
        self.color = [84, 132, 236, 0.8]

    def __repr__(self):
        return 'UnoccupiedTime {start_time} - {end_time}'.format(**self.__dict__)
