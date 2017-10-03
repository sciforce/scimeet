from kivy.app import App
from kivy.core.window import Window
from kivy.uix.settings import SettingsWithSidebar

from core.schedule.google_core import GoogleCalendar

from core.settings import get_default_settings, get_settings_temlate, GC_CONFIG
from ui.views.root import RootWidget

from kivy.logger import Logger

try:
    from jnius import autoclass
    from android.runnable import run_on_ui_thread

    android_api_version = autoclass('android.os.Build$VERSION')
    AndroidView = autoclass('android.view.View')
    AndroidPythonActivity = autoclass('org.renpy.android.PythonActivity')

    Logger.debug('Application runs on Android, API level {0}'.format(android_api_version.SDK_INT))
except ImportError:
    def run_on_ui_thread(func):
        def wrapper(*args):
            Logger.debug('{0} called on non android platform'.format(func.__name__))
        return wrapper


class MainApp(App):

    def __init__(self, **kwargs):
        super(MainApp, self).__init__()
        self.google_calendar = GoogleCalendar(GC_CONFIG)
        self.context = dict()

    def build(self):
        Window.bind(on_keyboard=self.window_on_keyboard)
        self.settings_cls = SettingsWithSidebar
        root_widget = RootWidget()
        return root_widget

    def build_config(self, config):
        config.setdefaults(*get_default_settings())

    def build_settings(self, settings):
        settings.add_json_panel('SciMeet', self.config, data=get_settings_temlate())

    def on_pause(self):
        return True

    def window_on_keyboard(self, window, key, *largs):
        if key == 27:
            return True

    def on_start(self):
        self.android_set_hide_menu()

    def on_resume(self):
        self.android_set_hide_menu()

    @run_on_ui_thread
    def android_set_hide_menu(self):
        if android_api_version.SDK_INT >= 19:
            Logger.debug('API >= 19. Set hide menu')
            view = AndroidPythonActivity.mActivity.getWindow().getDecorView()
            view.setSystemUiVisibility(
                AndroidView.SYSTEM_UI_FLAG_LAYOUT_STABLE |
                AndroidView.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION |
                AndroidView.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN |
                AndroidView.SYSTEM_UI_FLAG_HIDE_NAVIGATION |
                AndroidView.SYSTEM_UI_FLAG_FULLSCREEN |
                AndroidView.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
            )


if __name__ == "__main__":
    #Window.fullscreen = 'auto'
    MainApp().run()
