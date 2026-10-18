import os
import shutil

from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty
from kivy.utils import platform

from src.settings import Settings
from src.stats import SessionLog
from src.timer_repository import TimerRepository
from src.ui.alerts import Alerts
from src.ui.theme import Theme

KV_FILE = os.path.join(os.path.dirname(__file__), 'ui', 'sprintrunner.kv')


class SprintRunnerApp(App):
    title = 'SprintRunner'
    theme = ObjectProperty(None)
    version_name = StringProperty('v0.2')

    def build(self):
        data_dir = self.user_data_dir
        self._migrate_old_data(data_dir)
        self.prefs = Settings(os.path.join(data_dir, 'settings.json'))
        self.repo = TimerRepository(os.path.join(data_dir, 'saved_timers.json'))
        self.sessions = SessionLog(os.path.join(data_dir, 'sessions.json'))
        self.alerts = Alerts()

        self.theme = Theme()
        self.theme.bind(bg=self._paint_system_bars)
        self.apply_theme()

        # Keep text fields visible above the on-screen keyboard
        Window.softinput_mode = 'below_target'
        Window.bind(on_keyboard=self._on_keyboard)

        # Imported here so the kv file can reference app.theme on load
        from src.ui.screens import RootLayout
        Builder.load_file(KV_FILE)
        root = RootLayout()
        root.go('home')
        return root

    # -- preferences and theme

    def set_pref(self, key, value):
        if self.prefs.get(key) == value:
            return
        self.prefs.set(key, value)
        if key in ('theme', 'accent'):
            self.apply_theme()

    def apply_theme(self):
        mode = self.prefs.get('theme')
        if mode == 'system':
            mode = 'dark' if self._system_is_dark() else 'light'
        self.theme.apply(mode, self.prefs.get('accent'))
        Window.clearcolor = self.theme.bg
        self._refresh_screens()

    def _refresh_screens(self):
        # Widgets drawn from Python (progress pills, stat cards) take their
        # colours when created, so rebuild the visible screen.
        if not self.root:
            return
        screen = self.root.ids.sm.current_screen
        if hasattr(screen, 'on_pre_enter') and screen.name != 'timer':
            screen.on_pre_enter()

    @staticmethod
    def _system_is_dark():
        if platform != 'android':
            return False
        try:
            from android import mActivity
            config = mActivity.getResources().getConfiguration()
            UI_MODE_NIGHT_MASK, UI_MODE_NIGHT_YES = 0x30, 0x20
            return (config.uiMode & UI_MODE_NIGHT_MASK) == UI_MODE_NIGHT_YES
        except Exception:
            return False

    def _paint_system_bars(self, *args):
        """Match Android's status and navigation bars to the theme."""
        if platform != 'android':
            return
        try:
            from android.runnable import run_on_ui_thread
            from android import mActivity
            from jnius import autoclass
            Color = autoclass('android.graphics.Color')
            View = autoclass('android.view.View')
            bg = '#%02x%02x%02x' % tuple(int(c * 255) for c in self.theme.bg[:3])
            dark = self.theme.is_dark

            @run_on_ui_thread
            def paint():
                window = mActivity.getWindow()
                window.setStatusBarColor(Color.parseColor(bg))
                window.setNavigationBarColor(Color.parseColor(bg))
                flags = 0 if dark else (View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR
                                        | View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR)
                window.getDecorView().setSystemUiVisibility(flags)

            paint()
        except Exception as e:
            print(f"Could not colour system bars: {e}")

    # -- device helpers

    def vibrate(self, seconds):
        if platform != 'android':
            return
        try:
            from android import mActivity
            from jnius import autoclass
            Context = autoclass('android.content.Context')
            vibrator = mActivity.getSystemService(Context.VIBRATOR_SERVICE)
            vibrator.vibrate(int(seconds * 1000))
        except Exception as e:
            print(f"Vibration failed: {e}")

    def _on_keyboard(self, window, key, *args):
        if key == 27:  # Escape on desktop, Back on Android
            return self.root.handle_back()
        return False

    @staticmethod
    def _migrate_old_data(data_dir):
        """Older versions saved timers next to the code, where updates wipe them."""
        new_path = os.path.join(data_dir, 'saved_timers.json')
        if os.path.exists('saved_timers.json') and not os.path.exists(new_path):
            os.makedirs(data_dir, exist_ok=True)
            shutil.copy('saved_timers.json', new_path)

    # -- lifecycle

    def on_pause(self):
        """Allow app to run in background"""
        return True

    def on_resume(self):
        # The phone may have switched between light and dark while we were away
        if self.prefs.get('theme') == 'system':
            self.apply_theme()


if __name__ == '__main__':
    SprintRunnerApp().run()
