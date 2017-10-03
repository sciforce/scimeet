from datetime import datetime, date, time

from core.schedule.abstract import AbstractSchedule
from core.schedule.meeting import Meeting


class MockSchedule(AbstractSchedule):

    def __init__(self, config=None):
        super(MockSchedule, self).__init__(config)

    def get_current_meeting(self):
        return Meeting(
            start_time=datetime.combine(date.today(), time(12, 30)),
            end_time=datetime.combine(date.today(), time(13, 00)),
            title="AL Local",
            color=[1, 0, 0, 0.8],
            participants=["Natasha Kmet",
                           "Alex Shkop",
                           "Yuri Ageev",
                           "Dima Velychko",
                           "Alex Koiuda",
                           "Sergey Piskunov",
                           "Somebody Else"]
        )

    def get_next_meeting(self, now=None):
        return Meeting(
            start_time=datetime.combine(date.today(), time(14, 30)),
            end_time=datetime.combine(date.today(), time(15, 30)),
            title="Interview"
        )

    def get_meetings(self, start_time, end_time):
        return [
            Meeting(
                start_time=datetime.combine(date.today(), time(11, 00)),
                end_time=datetime.combine(date.today(), time(12, 20)),
                title="TLO Local",
                color=[0.9, 0.3, 0, 0.8],
                participants=["Natasha Kmet",
                              "Gosha",
                              "Yuri Ageev"]),
            Meeting(
                start_time=datetime.combine(date.today(), time(12, 30)),
                end_time=datetime.combine(date.today(), time(13, 00)),
                title="AL Local",
                color=[0.2, 0, 0, 0.8],
                participants=["Natasha Kmet",
                              "Alex Shkop",
                              "Yuri Ageev",
                              "Dima Velychko",
                              "Alex Koiuda",
                              "Sergey Piskunov",
                              "Somebody Else"]),
            Meeting(
                start_time=datetime.combine(date.today(), time(16, 00)),
                end_time=datetime.combine(date.today(), time(16, 40)),
                title="AL Retro",
                color=[0, 1, 0.1, 0.8],
                participants=["Natasha Kmet",
                              "Alex Shkop",
                              "Yuri Ageev",
                              "Dima Velychko",
                              "Alex Koiuda",
                              "Sergey Piskunov",
                              "Somebody Else"]),
            Meeting(
                start_time=datetime.combine(date.today(), time(17, 00)),
                end_time=datetime.combine(date.today(), time(18, 00)),
                title="Interview",
                color=[0.7, 0.2, 0.7, 0.8],
                participants=["Max Ved",
                              "Alex Shkop"]),
            Meeting(
                start_time=datetime.combine(date.today(), time(18, 30)),
                end_time=datetime.combine(date.today(), time(18, 45)),
                title="Local Micro Meeting",
                color=[1, 0, 0, 0.8],
                participants=["Gosha",
                              "Yuri Ageev",
                              "Somebody Else"]),
            Meeting(
                start_time=datetime.combine(date.today(), time(19, 00)),
                end_time=datetime.combine(date.today(), time(21, 00)),
                title="SciForce PizzaParty",
                color=[1, 1, 1, 0.8],
                participants=["All"])
        ]

    def create_event(self, data):
        pass

    def delete_event(self, data):
        pass

    def edit_event(self, event, data):
        pass

    def stop_event(self, data):
        pass
