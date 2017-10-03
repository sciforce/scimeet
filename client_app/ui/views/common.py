import datetime

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics.context_instructions import Color
from kivy.graphics.instructions import InstructionGroup
from kivy.graphics.vertex_instructions import Rectangle
from kivy.properties import ObjectProperty
from kivy.logger import Logger
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager

from core.schedule.meeting import Meeting
from core.settings import WORKDAY_END
from ui.views.styles import GlobalStyle, image

# helpers ###############################################################


def error_screen_wrapper(fn):
    def inner(*args):
        app = App.get_running_app()
        debug_mode = int(app.config.get('main', 'debugmode'))

        if debug_mode:
            return fn(*args)
        else:
            try:
                res = fn(*args)
            except Exception as e:
                if isinstance(app.root, ScreenManager):
                    message = '{} - {}:\n{}'.format(fn.__name__, type(e).__name__, e.message)
                    app.root.error_message = message
                    Logger.error(message)
            else:
                return res
    return inner


def round_to_minute(date_time):
    if not date_time.minute % 5:
        return date_time
    if date_time.minute < 55:
        return date_time.replace(minute=date_time.minute + 5 - date_time.minute % 5)
    else:
        return date_time.replace(minute=0, second=0) + datetime.timedelta(hours=1)

# base widgets ##########################################################


class BaseWidget(object):
    def __init__(self):
        self.app = App.get_running_app()
        self.context_key = None

    @property
    def context_key(self):
        return self.context_key

    @context_key.setter
    def context_key(self, value):
        self.app.context[value] = self


class CustomTimeLabel(Label):

    def __init__(self, **kwargs):
        super(CustomTimeLabel, self).__init__(**kwargs)

    @property
    def time(self):
        return self.text

    @time.setter
    def time(self, value):
        if type(value) == tuple:
            self.text = "{} - {}".format(value[0].time().strftime("%H:%M"),
                                         value[1].time().strftime("%H:%M"))
        else:
            self.text = value.time().strftime("%H:%M")


class TimeResizableHeightWidget(BaseWidget):
    PIXELS_BY_MINUTE = 2.2

    def __init__(self):
        super(TimeResizableHeightWidget, self).__init__()
        self.start = None
        self.end = None

    @property
    def start_time(self):
        return self.start

    @start_time.setter
    def start_time(self, value):
        self.start = value
        self._resize()

    @property
    def end_time(self):
        return self.end

    @end_time.setter
    def end_time(self, value):
        self.end = value
        self._resize()

    def _resize(self):
        if self.start and self.end:
            new_height = ((self.end - self.start).seconds / 60) * self.PIXELS_BY_MINUTE
            self.size = [self.width, new_height if new_height > self.font_size * 1.5 else self.font_size * 1.5]

# screens ###############################################################


class AutoSwitchToMainScreenWidget(Screen, BaseWidget):
    def __init__(self, *args, **kwargs):
        super(AutoSwitchToMainScreenWidget, self).__init__(*args, **kwargs)
        self.autoswitch_delay = 8
        self.autoswitch_event = None
        self.last_touch_up_time = datetime.datetime.now()

    def on_pre_enter(self, *args):
        self.last_touch_up_time = datetime.datetime.now()
        self.autoswitch_event = Clock.schedule_interval(self.autoswitch_callback, 1)
        self.refresh(*args)
        super(AutoSwitchToMainScreenWidget, self).on_pre_enter(*args)

    def on_leave(self, *args):
        self.autoswitch_event.cancel()
        super(AutoSwitchToMainScreenWidget, self).on_leave(*args)

    def on_touch_up(self, *args):
        self.last_touch_up_time = datetime.datetime.now()
        super(AutoSwitchToMainScreenWidget, self).on_touch_up(*args)

    def autoswitch_callback(self, *args):
        now = datetime.datetime.now()
        if (now - self.last_touch_up_time).total_seconds() >= self.autoswitch_delay:
            self.manager.go_to_main_screen()

    def refresh(self, *args):
        pass


class AutoRefreshWidget(Screen, BaseWidget):
    def __init__(self, *args, **kwargs):
        super(AutoRefreshWidget, self).__init__(*args, **kwargs)
        self.autorefresh_event = None
        self.autorefresh_time = 2

    def on_enter(self, *args):
        self.refresh(*args)

    def on_pre_enter(self, *args):
        self.autorefresh_event = Clock.schedule_interval(self.refresh, self.autorefresh_time)

    def on_pre_leave(self, *args):
        self.autorefresh_event.cancel()
        super(AutoRefreshWidget, self).on_leave(*args)


class OkCancelModalScreen(AutoSwitchToMainScreenWidget):

    NAME = "modal_dialog"
    data = ObjectProperty()

    def __init__(self):
        super(OkCancelModalScreen, self).__init__(name=self.NAME)

    def on_data(self, *args):
        self.clear_widgets()
        instance, data = args

        # TODO: move to draw_static
        menu_background = InstructionGroup()
        menu_background.add(Color(*GlobalStyle.menu_background_color))
        menu_background.add(Rectangle(pos=self.pos, size=self.size))
        self.canvas.add(menu_background)

        v_layout = BoxLayout(orientation="vertical")

        label = Label(text=data['text'],
                      halign='center',
                      font_name=GlobalStyle.standard_caption_font,
                      font_size=GlobalStyle.big_caption_font_size,
                      size_hint_y=80)

        v_layout.add_widget(label)

        h_layout = BoxLayout(orientation="horizontal",
                             size_hint_y=20,
                             padding=[0, 0, 0, 20],
                             spacing=40)

        dummy = Label(size_hint_x=1)
        h_layout.add_widget(dummy)

        ok_button = Button(size_hint=(None, None),
                           size=GlobalStyle.standard_button_size,
                           border=(0, 0, 0, 0),
                           background_normal=image('ok'),
                           background_down=image('ok_pressed'))
        ok_button.bind(on_release=data['ok_callback'])
        h_layout.add_widget(ok_button)

        cancel_button = Button(size_hint=(None, None),
                               size=GlobalStyle.standard_button_size,
                               border=(0, 0, 0, 0),
                               background_normal=image('x'),
                               background_down=image('x_pressed'))
        cancel_button.bind(on_release=data['cancel_callback'])
        h_layout.add_widget(cancel_button)

        dummy = Label(size_hint_x=1)
        h_layout.add_widget(dummy)

        v_layout.add_widget(h_layout)
        self.add_widget(v_layout)


class StartAppModalScreen(AutoRefreshWidget):

    NAME = "start_app_dialog"
    data = ObjectProperty()

    def __init__(self):
        super(StartAppModalScreen, self).__init__(name=self.NAME)
        self.start_app_callback = None
        self.autorefresh_time = 120

    def refresh(self, *args):
        if callable(self.start_app_callback):
            self.start_app_callback()

    def on_data(self, *args):
        instance, data = args
        self.start_app_callback = data['start_app_callback']

    def start_app(self, *args):
        if callable(self.start_app_callback):
            self.start_app_callback()

    def on_enter(self, *args):
        menu_background = InstructionGroup()
        menu_background.add(Color(*GlobalStyle.menu_background_color))
        menu_background.add(Rectangle(size=[Window.width, Window.height]))
        self.canvas.add(menu_background)

        v_layout = BoxLayout(orientation="vertical")

        label = Label(text="SciMeet",
                      halign='center',
                      font_name=GlobalStyle.extrabold_caption_font,
                      font_size=GlobalStyle.extra_huge_caption_font_size,
                      size_hint_y=80)

        v_layout.add_widget(label)

        h_layout = BoxLayout(orientation="horizontal",
                             size_hint_y=20,
                             padding=[0, 0, 0, 20],
                             spacing=40)

        dummy = Label(size_hint_x=1)
        h_layout.add_widget(dummy)

        cancel_button = Button(size_hint=(None, None),
                               size=GlobalStyle.standard_button_size,
                               border=(0, 0, 0, 0),
                               background_normal=image('menu'),
                               background_down=image('menu_pressed'))
        cancel_button.bind(on_release=self.app.open_settings)
        h_layout.add_widget(cancel_button)

        ok_button = Button(size_hint=(None, None),
                           size=GlobalStyle.standard_button_size,
                           border=(0, 0, 0, 0),
                           background_normal=image('forward'),
                           background_down=image('forward_pressed'))
        ok_button.bind(on_release=self.start_app)
        h_layout.add_widget(ok_button)

        dummy = Label(size_hint_x=1)
        h_layout.add_widget(dummy)

        v_layout.add_widget(h_layout)
        self.add_widget(v_layout)


class ErrorScreen(Screen, BaseWidget):
    NAME = "error_screen"

    def __init__(self, *args):
        super(ErrorScreen, self).__init__(name=self.NAME)

    def on_enter(self, *args):
        if not hasattr(self.app.root, "error_message"):
            return None

        self.clear_widgets()
        menu_background = InstructionGroup()
        menu_background.add(Color(*GlobalStyle.error_screen_background_color))
        menu_background.add(Rectangle(pos=self.pos, size=self.size))
        self.canvas.add(menu_background)

        v_layout = BoxLayout(orientation="vertical")

        label = Label(text="Error",
                      font_name=GlobalStyle.extrabold_caption_font,
                      font_size=GlobalStyle.huge_caption_font_size,
                      text_size=self.size,
                      halign="center",
                      valign="middle",
                      size_hint_y=40)
        v_layout.add_widget(label)

        label = Label(text=self.app.root.error_message,
                      font_name=GlobalStyle.semibold_caption_font,
                      font_size=GlobalStyle.big_caption_font_size,
                      text_size=self.size,
                      halign="center",
                      valign="middle",
                      size_hint_y=40)
        v_layout.add_widget(label)

        h_layout = BoxLayout(orientation="horizontal",
                             size_hint_y=20,
                             padding=[0, 0, 0, 20],
                             spacing=40)

        dummy = Label(size_hint_x=1)
        h_layout.add_widget(dummy)

        menu_button = Button(size_hint=(None, None),
                             size=GlobalStyle.standard_button_size,
                             border=(0, 0, 0, 0),
                             background_normal=image('menu'),
                             background_down=image('menu_pressed'))
        menu_button.bind(on_release=self.menu_button_callback)
        h_layout.add_widget(menu_button)

        dummy = Label(size_hint_x=1)
        h_layout.add_widget(dummy)

        v_layout.add_widget(h_layout)
        self.add_widget(v_layout)

    def menu_button_callback(self, *args):
        self.app.root.error_message = ''
        self.app.root.go_to_main_screen()

# buttons ###############################################################


class AddMeetingButton(Button, BaseWidget):
    def __init__(self, **kwargs):
        super(AddMeetingButton, self).__init__(**kwargs)

    def on_release(self):
        scr = self.app.root.screens[self.app.root.screen_names.index('edit_meeting_screen')]
        scr.meeting = Meeting(start_time=datetime.datetime.now(),
                              end_time=datetime.datetime.combine(datetime.datetime.now(), WORKDAY_END))
        self.app.root.current = "edit_meeting_screen"


class CalendarButton(Button, BaseWidget):
    def __init__(self, **kwargs):
        super(CalendarButton, self).__init__(**kwargs)

    def on_release(self):
        self.app.root.current = "calendar_screen"


class StartStopButton(Button, BaseWidget):
    def __init__(self, **kwargs):
        super(StartStopButton, self).__init__(**kwargs)

    def on_release(self):
        self.app.root.show_modal(text='Are you sure you want to\nstop current meeting?',
                                 ok_callback=self.stop_meeting)

    @error_screen_wrapper
    def stop_meeting(self, *args):
        button, = args
        self.app.google_calendar.stop_event(self.app.root.current_meeting)
        self.app.root.current_meeting = None
        self.app.root.go_to_main_screen()


class ForwardButton(Button, BaseWidget):
    def __init__(self, **kwargs):
        super(ForwardButton, self).__init__(**kwargs)


class BackwardButton(Button, BaseWidget):
    def __init__(self, **kwargs):
        super(BackwardButton, self).__init__(**kwargs)


class MenuButton(Button, BaseWidget):
    def __init__(self, **kwargs):
        super(MenuButton, self).__init__(**kwargs)

    def on_release(self):
        self.app.root.go_to_main_screen()


class EditItemButton(Button, BaseWidget):
    def __init__(self, **kwargs):
        super(EditItemButton, self).__init__(**kwargs)


class DeleteItemButton(Button, BaseWidget):
    def __init__(self, **kwargs):
        super(DeleteItemButton, self).__init__(**kwargs)


class BackButton(Button, BaseWidget):
    def __init__(self, **kwargs):
        super(BackButton, self).__init__(**kwargs)

    def on_release(self, *args):
        self.app.root.back_to_previous_screen()


class SaveButton(Button, BaseWidget):
    def __init__(self, **kwargs):
        super(SaveButton, self).__init__(**kwargs)

    def on_release(self, *args):
        self.app.root.back_to_previous_screen()
