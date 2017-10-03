import datetime

from kivy.properties import ObjectProperty, ListProperty
from kivy.uix.button import Button
from kivy.uix.carousel import Carousel

from ui.views.calendar.daily.view import DailyScreen
from ui.views.calendar.weekly.view import WeeklyScreen
from ui.views.common import AutoSwitchToMainScreenWidget, BaseWidget
from ui.views.styles import GlobalStyle


class CarouselBackButton(Button, BaseWidget):
    def __init__(self, **kwargs):
        super(CarouselBackButton, self).__init__(**kwargs)

    def on_release(self, *args):
        carousel = self.app.context["calendar_carousel"]
        if carousel.index == 1:
            carousel.load_previous()
        else:
            self.app.root.back_to_previous_screen()


class CalendarCarousel(Carousel, BaseWidget):
    direction = 'right'

    def __init__(self, **kwargs):
        super(CalendarCarousel, self).__init__(**kwargs)
        self.context_key = 'calendar_carousel'
        self.add_widget(WeeklyScreen())
        self.add_widget(DailyScreen())

    def slide(self, name):
        try:
            next_slide = next(_ for _ in self.slides if _.NAME == name)
        except StopIteration:
            pass
        else:
            return next_slide


class CalendarScreen(AutoSwitchToMainScreenWidget):
    NAME = "calendar_screen"
    show_day = ObjectProperty()
    show_week = ObjectProperty()

    def __init__(self, *args, **kwargs):
        super(CalendarScreen, self).__init__(name=self.NAME)
        self.context_key = self.NAME
        self.draw_static()

    @property
    def carousel(self):
        return self.ids.calendar_carousel

    def draw_static(self):
        self.ids.previous_day_button.bind(on_release=self.minus_date)
        self.ids.next_day_button.bind(on_release=self.plus_date)

    def refresh(self, *args):
        if self.carousel.current_slide.NAME == DailyScreen.NAME:
            self.ids.current_day_button.text = self.show_day.strftime("%A \n%B %d, %Y")
            self.carousel.slide(DailyScreen.NAME).start_day = self.show_day
            # TODO: we need to trigger this manually because if property is not changed
            if self.show_day == datetime.datetime.today().date():
                self.carousel.slide(DailyScreen.NAME).on_start_day()

        elif self.carousel.current_slide.NAME == WeeklyScreen.NAME:
            self.show_week = self.show_week - datetime.timedelta(days=self.show_week.weekday())
            end_of_week = self.show_week + datetime.timedelta(days=5)
            self.ids.current_day_button.text = "{}\n{}".format(self.show_week.strftime("%B %d"),
                                                               end_of_week.strftime("%B %d"))
            # TODO: we need to trigger this manually because if property is not changed
            self.carousel.slide(WeeklyScreen.NAME).start_day = self.show_week
            if self.show_day == datetime.datetime.today().date():
                self.carousel.slide(WeeklyScreen.NAME).on_start_day()

    def minus_date(self, *args):
        if self.carousel.current_slide.NAME == DailyScreen.NAME:
            self.show_day -= datetime.timedelta(days=1)
            self.show_week = self.show_day - datetime.timedelta(days=self.show_day.weekday())
        elif self.carousel.current_slide.NAME == WeeklyScreen.NAME:
            self.show_week -= datetime.timedelta(weeks=1)
            self.show_day = self.show_week - datetime.timedelta(days=self.show_week.weekday())
        self.refresh()

    def plus_date(self, *args):
        if self.carousel.current_slide.NAME == DailyScreen.NAME:
            self.show_day += datetime.timedelta(days=1)
            self.show_week = self.show_day - datetime.timedelta(days=self.show_day.weekday())
        elif self.carousel.current_slide.NAME == WeeklyScreen.NAME:
            self.show_week += datetime.timedelta(weeks=1)
            self.show_day = self.show_week - datetime.timedelta(days=self.show_week.weekday())
        self.refresh()

    def on_pre_enter(self, *args):
        self.carousel.index = 0
        self.show_day = datetime.date.today()
        self.show_week = datetime.date.today()
        super(CalendarScreen, self).on_pre_enter(*args)

    def on_enter(self, *args):
        self.refresh()
