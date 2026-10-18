from datetime import datetime

from kivy.app import App
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.properties import (BooleanProperty, ColorProperty, NumericProperty, OptionProperty,
                             StringProperty)
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import FadeTransition, Screen
from kivy.uix.widget import Widget

from src.schedule import Schedule
from src.stats import format_duration
from src.task import Task
from src.templates import TEMPLATES
from src.timer import Timer
from src.ui.icons import ICONS, icon_markup
from src.ui.widgets import Card, Chip, Dialog, Icon, PressableCard, Text


def describe_task(task):
    """'11 × 5 min · 10s breaks'"""
    sprints = Schedule(task).work_block_count
    rest = f"{format_duration(task.break_block_seconds)} breaks" if task.break_block_seconds else "no breaks"
    return f"{sprints} × {task.work_block_minutes} min · {rest}"


def short_describe_task(task):
    return f"{task.total_duration_minutes} min · {task.work_block_minutes} min sprints"


def glyph(name):
    return ICONS.get(name, '')


def pill_widget(rgba, radius):
    """Small rounded bar used in the sprint progress rows."""
    pill = Widget()
    with pill.canvas:
        pill.color = Color(rgba=rgba)
        pill.rect = RoundedRectangle(radius=[radius])
    pill.bind(pos=lambda w, v: setattr(w.rect, 'pos', v),
              size=lambda w, v: setattr(w.rect, 'size', v))
    return pill


# ---------------------------------------------------------------- list items

class TemplateCard(Card):
    title = StringProperty('')
    category = StringProperty('')
    subtitle = StringProperty('')
    icon = StringProperty('')
    color = ColorProperty([0, 0, 0, 1])

    __events__ = ('on_start',)

    def on_start(self):
        pass


class ExploreCard(Card):
    # Not a TemplateCard subclass: kv would apply both layouts to it
    title = StringProperty('')
    category = StringProperty('')
    subtitle = StringProperty('')
    description = StringProperty('')
    icon = StringProperty('')
    color = ColorProperty([0, 0, 0, 1])
    saved = BooleanProperty(False)

    __events__ = ('on_start', 'on_save')

    def on_start(self):
        pass

    def on_save(self):
        pass


class SprintCard(PressableCard):
    title = StringProperty('')
    subtitle = StringProperty('')

    __events__ = ('on_delete',)

    def glyph(self, name):
        return glyph(name)

    def on_delete(self):
        pass


class SprintTile(Label):
    """One numbered tile in the timer screen's Sprints card."""
    number = NumericProperty(1)
    state = OptionProperty('pending', options=['pending', 'current', 'done', 'skipped'])
    fill = NumericProperty(0)  # how much of the current sprint is done, 0..1

    @staticmethod
    def label_markup(state, number):
        if state == 'done':
            return icon_markup('check', '24sp')
        if state == 'skipped':
            return icon_markup('skip-next', '24sp')
        return str(int(number))


class StatCard(Card):
    icon = StringProperty('')
    icon_color = ColorProperty(None, allownone=True)
    value = StringProperty('')
    label = StringProperty('')


class HistoryRow(BoxLayout):
    title = StringProperty('')
    subtitle = StringProperty('')
    value = StringProperty('')
    finished = BooleanProperty(True)

    def glyph(self, name):
        return glyph(name)


class SettingRow(BoxLayout):
    icon = StringProperty('')
    title = StringProperty('')

    def glyph(self, name):
        return glyph(name)


class AccentDot(ButtonBehavior, Widget):
    color = ColorProperty([0, 0, 0, 1])
    selected = BooleanProperty(False)
    accent = StringProperty('')


# ---------------------------------------------------------------- root

class RootLayout(BoxLayout):
    """Screen manager plus the bottom navigation bar."""

    TABS = ('home', 'explore', 'stats', 'settings')
    nav_visible = BooleanProperty(True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        sm = self.ids.sm
        sm.transition = FadeTransition(duration=0.15)
        # Screens have no pos_hint, so they don't follow the manager when the
        # bottom bar hides/shows and the manager moves.
        sm.bind(pos=lambda manager, pos: [setattr(screen, 'pos', pos) for screen in manager.screens])
        for screen in (HomeScreen(), ExploreScreen(), StatsScreen(), SettingsScreen(),
                       CreateTaskScreen(), TimerScreen()):
            sm.add_widget(screen)

    @property
    def current(self):
        return self.ids.sm.current

    def go(self, name):
        self.ids.sm.current = name
        self.nav_visible = name in self.TABS
        if name in self.TABS:
            self.ids.nav.current = name

    def start_task(self, task):
        self.ids.sm.get_screen('timer').setup_timer(task)
        self.go('timer')

    def handle_back(self):
        """Android back button. Returns True if handled (app stays open)."""
        current = self.current
        if current == 'timer':
            self.ids.sm.get_screen('timer').ask_stop()
            return True
        if current != 'home':
            self.go('home')
            return True
        return False


# ---------------------------------------------------------------- screens

class HomeScreen(Screen):
    streak_text = StringProperty('0 days')
    focus_text = StringProperty('0s today')
    count_text = StringProperty('')
    greeting = StringProperty('')

    def __init__(self, **kwargs):
        super().__init__(name='home', **kwargs)
        Clock.schedule_once(lambda dt: self.build_templates())

    def build_templates(self):
        app = App.get_running_app()
        for template in TEMPLATES:
            card = TemplateCard(title=template.name, category=template.category,
                                subtitle=short_describe_task(template.task),
                                icon=template.icon, color=template.color)
            card.bind(on_start=lambda c, t=template: app.root.start_task(t.task))
            self.ids.template_row.add_widget(card)

    def on_pre_enter(self, *args):
        self.load_tasks()

    def load_tasks(self):
        """Load saved tasks from repository"""
        app = App.get_running_app()
        hour = datetime.now().hour
        self.greeting = ("Good morning" if hour < 12 else
                         "Good afternoon" if hour < 17 else "Good evening")

        summary = app.sessions.summary('today')
        streak = summary['current_streak']
        self.streak_text = f"{streak} day{'' if streak == 1 else 's'}"
        self.focus_text = f"{format_duration(summary['focused_seconds'])} today"

        container = self.ids.sprint_list
        container.clear_widgets()
        tasks = app.repo.list_tasks()
        self.count_text = f"{len(tasks)} saved" if tasks else ''

        if not tasks:
            container.add_widget(self.empty_state())
            return

        for task in reversed(tasks):  # newest first
            card = SprintCard(title=task.name, subtitle=describe_task(task))
            card.bind(on_release=lambda c, t=task: app.root.start_task(t),
                      on_delete=lambda c, t=task: self.confirm_delete(t))
            container.add_widget(card)

    def empty_state(self):
        card = Card(orientation='vertical', size_hint_y=None, height=dp(150),
                    padding=(dp(20), dp(18)), spacing=dp(6))
        icon = Icon(icon='rocket-launch', font_size='40sp', size_hint_y=None, height=dp(48))
        icon.color = App.get_running_app().theme.primary
        card.add_widget(icon)
        card.add_widget(Text(text='No sprints yet', bold=True, halign='center', font_size='17sp'))
        card.add_widget(Text(text='Start a template above or tap New Sprint to build your own.',
                             tone='muted', halign='center', font_size='14sp'))
        return card

    def confirm_delete(self, task):
        app = App.get_running_app()

        def delete():
            app.repo.delete_timer(task.name)
            self.load_tasks()

        Dialog(icon='delete-outline', icon_color=app.theme.danger,
               title=f'Delete "{task.name}"?', message="This can't be undone.",
               confirm_text='Delete', confirm_style='danger',
               confirm_action=delete).open()


class CreateTaskScreen(Screen):
    preview_title = StringProperty('')
    preview_detail = StringProperty('')
    error = StringProperty('')

    def __init__(self, **kwargs):
        super().__init__(name='create', **kwargs)

    def on_pre_enter(self, *args):
        """Start every visit with a clean form"""
        self.ids.name_input.text = ''
        self.ids.total.value = 60
        self.ids.work.value = 5
        self.ids.rest.value = 10
        self.error = ''
        self.refresh_preview()

    def build_task(self):
        return Task(self.ids.name_input.text.strip(), int(self.ids.total.value),
                    int(self.ids.work.value), int(self.ids.rest.value))

    def refresh_preview(self):
        """Live summary of what the inputs will produce"""
        if 'preview_pills' not in self.ids:
            return  # kv rules not applied yet
        task = self.build_task()
        self.error = ''
        pills = self.ids.preview_pills
        pills.clear_widgets()

        # Check only the timing here; the name is checked on save
        timing_problem = Task('preview', task.total_duration_minutes, task.work_block_minutes,
                              task.break_block_seconds).validation_error()
        if timing_problem:
            self.preview_title = 'Check the timing'
            self.preview_detail = timing_problem
            return

        schedule = Schedule(task)
        sprints = schedule.work_block_count
        self.preview_title = f"{sprints} sprint{'' if sprints == 1 else 's'} of {task.work_block_minutes} min"
        breaks = schedule.total_break_seconds
        unused = task.total_duration_minutes * 60 - sprints * task.work_block_minutes * 60 - breaks
        detail = f"{format_duration(breaks)} of breaks in total" if breaks else "No breaks"
        if unused > 0:
            detail += f" · {format_duration(unused)} left unused"
        self.preview_detail = detail

        theme = App.get_running_app().theme
        for _ in range(min(sprints, 48)):
            pills.add_widget(pill_widget(theme.primary, dp(4)))

    def save(self):
        """Create task from inputs and save it"""
        app = App.get_running_app()
        task = self.build_task()
        problem = task.validation_error()
        if problem:
            self.error = problem
            return
        if app.repo.has_timer(task.name):
            self.error = f'You already have a sprint called "{task.name}".'
            return
        app.repo.save_timer(task)
        app.root.go('home')


class TimerScreen(Screen):
    task_name = StringProperty('')
    time_text = StringProperty('00:00')
    sub_text = StringProperty('')
    phase_text = StringProperty('READY')
    phase_color = ColorProperty([0, 0, 0, 1])
    progress = NumericProperty(1.0)
    progress_text = StringProperty('')
    running = BooleanProperty(False)
    started = BooleanProperty(False)
    # Notification banner shown when a block ends
    banner_title = StringProperty('')
    banner_text = StringProperty('')
    banner_icon = StringProperty('check-circle')
    banner_color = ColorProperty([0, 0, 0, 1])
    banner_shown = NumericProperty(0)  # 0 hidden .. 1 visible, animated

    def __init__(self, **kwargs):
        super().__init__(name='timer', **kwargs)
        self.timer = None
        self.task = None
        self.schedule = None
        self.clock_event = None
        self.tiles = []
        self.sprint_states = []  # 'done' / 'skipped' per finished sprint
        self.scrolled_to = None
        self.total_sprints = 0
        self.work_index = 0
        self.pending_alarm = None
        self._banner_hide = None
        self.wake_lock = self._create_wake_lock()

    # -- setup

    def setup_timer(self, task):
        """Initialize timer with task and schedule"""
        self._cancel_clock()
        self._release_wake_lock()
        self.task = task
        self.schedule = Schedule(task)
        self.timer = Timer(self.schedule)
        self.timer.on_block_complete_callback = self.on_timer_block_complete
        self.task_name = task.name
        self.running = False
        self.started = False
        self.work_index = 0
        self.pending_alarm = None
        Animation.cancel_all(self, 'banner_shown')
        self.banner_shown = 0
        self.total_sprints = self.schedule.work_block_count

        self.phase_color = App.get_running_app().theme.primary
        self.phase_text = 'READY'
        self.progress = 1.0
        self.time_text = self._fmt(task.work_block_minutes * 60)
        self.sub_text = 'Tap play to start'
        self._build_tiles()
        self._refresh_progress_text()

    def _build_tiles(self):
        row = self.ids.tiles
        row.clear_widgets()
        self.tiles = [SprintTile(number=i + 1) for i in range(self.total_sprints)]
        for tile in self.tiles:
            row.add_widget(tile)
        self.sprint_states = []
        self.scrolled_to = None
        self.ids.tile_scroll.scroll_x = 0

    def _paint_tiles(self):
        current = self.work_index if self.started and self._in_work() else None
        for i, tile in enumerate(self.tiles):
            if i < len(self.sprint_states):
                tile.state = self.sprint_states[i]
            elif i == current:
                tile.state = 'current'
                tile.fill = 1 - self.progress
            else:
                tile.state = 'pending'
        # Keep the active (or next) sprint in view
        focus = min(self.work_index, len(self.tiles) - 1)
        if self.tiles and focus != self.scrolled_to:
            self.scrolled_to = focus
            self.ids.tile_scroll.scroll_to(self.tiles[focus], padding=dp(70), animate=True)

    # -- controls

    def toggle(self):
        """Start, pause or resume"""
        if not self.timer:
            return
        if not self.started:
            if not self.timer.start():
                return
            self.started = True
            self.running = True
            self.clock_event = Clock.schedule_interval(self.update_timer, 0.25)
            self._acquire_wake_lock()
            App.get_running_app().alerts.request_permission()
        elif self.timer.is_paused:
            self.timer.resume()
            self.running = True
        else:
            self.timer.pause()
            self.running = False
        self.update_timer(0)

    def skip(self):
        if not self.started or not self.timer.is_running:
            return
        was_work = self._in_work()
        self.timer.skip()
        if was_work:
            self.sprint_states.append('skipped')
            self.work_index += 1
        self.update_timer(0)

    def ask_stop(self):
        if not self.started:
            self.finish(save=False)
            return
        was_running = self.running
        if was_running:
            self.toggle()  # pause while the dialog is open

        def keep_going(*args):
            if was_running and self.started and not self.running:
                self.toggle()

        dialog = Dialog(title='End this session?',
                        message='Your progress so far will still be saved to Stats.',
                        confirm_text='End session', cancel_text='Keep going',
                        confirm_action=lambda: self.finish(save=True))
        dialog.bind(on_dismiss=keep_going)
        dialog.open()

    def finish(self, save=True):
        """Stop the timer, record the session and go home"""
        self._cancel_clock()
        self._release_wake_lock()
        app = App.get_running_app()
        if save and self.timer and self.started:
            app.sessions.record(self.task.name, self.timer.focus_so_far(),
                                self.timer.completed_work_blocks, self.total_sprints)
        if self.timer:
            self.timer.stop()
        self.running = False
        self.started = False
        app.root.go('home')

    # -- ticking

    def update_timer(self, dt):
        """Called 4 times a second to refresh the display"""
        if not self.timer or not self.started:
            return False
        self.timer.tick()
        self._play_pending_alarm()

        if self.timer.is_finished:
            self._session_complete()
            return False

        block = self.timer.current_block
        theme = App.get_running_app().theme
        remaining = self.timer.remaining_seconds
        self.time_text = self._fmt(remaining)
        self.progress = remaining / block.duration_seconds if block.duration_seconds else 0

        paused = self.timer.is_paused
        if self._in_work():
            self.phase_color = theme.primary
            self.phase_text = f"SPRINT {self.work_index + 1} OF {self.total_sprints}"
            self.sub_text = 'Paused' if paused else 'Focus'
        else:
            self.phase_color = theme.warning
            self.phase_text = 'BREAK'
            self.sub_text = 'Paused' if paused else 'Breathe'
        self._refresh_progress_text()
        self._paint_tiles()

    def on_timer_block_complete(self, block):
        """Called by timer when block completes"""
        if block.block_type == 'work':
            self.sprint_states.append('done')
            self.work_index += 1
        # Several blocks can end in one tick after the app was in the
        # background; only the last one is announced.
        self.pending_alarm = block

    def _session_complete(self):
        self._cancel_clock()
        self._release_wake_lock()
        self.running = False
        self.started = False
        app = App.get_running_app()
        app.sessions.record(self.task.name, self.timer.focused_seconds,
                            self.timer.completed_work_blocks, self.total_sprints)
        self.progress = 0
        self.time_text = '00:00'
        self.phase_text = 'DONE'
        self.phase_color = app.theme.success
        self._refresh_progress_text()
        self._paint_tiles()
        Dialog(icon='party-popper', icon_color=app.theme.warning,
               title='Session complete!',
               message=(f"{self.timer.completed_work_blocks} sprints · "
                        f"{format_duration(self.timer.focused_seconds)} of focus"),
               confirm_text='Done', cancel_text='',
               confirm_action=lambda: app.root.go('home'),
               auto_dismiss=False).open()

    def _refresh_progress_text(self):
        done = self.timer.completed_work_blocks if self.timer else 0
        self.progress_text = f"{done} / {self.total_sprints} done"

    def _in_work(self):
        block = self.timer.current_block if self.timer else None
        return block is not None and block.block_type == 'work'

    @staticmethod
    def _fmt(seconds):
        hours, rest = divmod(int(seconds), 3600)
        mins, secs = divmod(rest, 60)
        return f"{hours}:{mins:02d}:{secs:02d}" if hours else f"{mins:02d}:{secs:02d}"

    def _cancel_clock(self):
        if self.clock_event:
            self.clock_event.cancel()
            self.clock_event = None

    # -- sound, vibration and wake lock

    def _play_pending_alarm(self):
        """Chime, vibrate and notify for the block that just ended"""
        if not self.pending_alarm:
            return
        finished, self.pending_alarm = self.pending_alarm, None
        app = App.get_running_app()
        theme = app.theme
        nxt = self.timer.current_block

        if self.timer.is_finished:
            sound = 'session_done'
            title = 'Session complete!'
            text = (f"{self.timer.completed_work_blocks} sprints · "
                    f"{format_duration(self.timer.focused_seconds)} of focus")
            icon, color = 'party-popper', theme.warning
        elif finished.block_type == 'work':
            sound = finished.alarm_tone
            title = f"Sprint {self.work_index} of {self.total_sprints} done"
            if nxt.block_type == 'break':
                text = f"Take a {format_duration(nxt.duration_seconds)} break"
                icon = 'coffee'
            else:
                text = f"Sprint {self.work_index + 1} starts now"
                icon = 'lightning-bolt'
            color = theme.success
        else:
            sound = finished.alarm_tone
            title = 'Break over'
            text = f"Sprint {self.work_index + 1} of {self.total_sprints} · let's go"
            icon, color = 'lightning-bolt', theme.primary

        if app.prefs.get('sound'):
            app.alerts.play(sound)
        if app.prefs.get('vibrate'):
            app.vibrate(0.4)
        app.alerts.notify(f"{title} · {self.task.name}", text)
        if not self.timer.is_finished:  # the completion dialog covers that case
            self.show_banner(title, text, icon, color)

    def show_banner(self, title, text, icon, color):
        """Slide a notification card down from the top for a few seconds"""
        self.banner_title, self.banner_text = title, text
        self.banner_icon, self.banner_color = icon, color
        Animation.cancel_all(self, 'banner_shown')
        Animation(banner_shown=1, d=0.3, t='out_back').start(self)
        if self._banner_hide:
            self._banner_hide.cancel()
        self._banner_hide = Clock.schedule_once(
            lambda dt: Animation(banner_shown=0, d=0.25, t='in_quad').start(self), 3.5)

    @staticmethod
    def _create_wake_lock():
        # Keeps the CPU awake so the timer runs while the screen is off
        try:
            from android import mActivity
            from jnius import autoclass
            PowerManager = autoclass('android.os.PowerManager')
            power_manager = mActivity.getSystemService('power')
            return power_manager.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK,
                                             'SprintRunner::TimerWakeLock')
        except Exception:
            return None

    def _acquire_wake_lock(self):
        if self.wake_lock:
            try:
                if not self.wake_lock.isHeld():
                    self.wake_lock.acquire()
            except Exception:
                pass

    def _release_wake_lock(self):
        if self.wake_lock:
            try:
                if self.wake_lock.isHeld():
                    self.wake_lock.release()
            except Exception:
                pass


class ExploreScreen(Screen):
    CATEGORIES = ['All'] + sorted({t.category for t in TEMPLATES})

    def __init__(self, **kwargs):
        super().__init__(name='explore', **kwargs)
        self.category = 'All'
        Clock.schedule_once(lambda dt: self._build_filters())

    def _build_filters(self):
        for name in self.CATEGORIES:
            chip = Chip(label=name, value=name, selected=name == self.category)
            chip.bind(on_release=lambda c: self.set_category(c.value))
            self.ids.filters.add_widget(chip)

    def set_category(self, category):
        self.category = category
        for chip in self.ids.filters.children:
            chip.selected = chip.value == category
        self.load_cards()

    def on_pre_enter(self, *args):
        self.load_cards()

    def load_cards(self):
        app = App.get_running_app()
        cards = self.ids.cards
        cards.clear_widgets()
        for template in TEMPLATES:
            if self.category not in ('All', template.category):
                continue
            card = ExploreCard(title=template.name, category=template.category,
                               description=template.description,
                               subtitle=describe_task(template.task), icon=template.icon,
                               color=template.color, saved=app.repo.has_timer(template.name))
            card.bind(on_start=lambda c, t=template: app.root.start_task(t.task),
                      on_save=lambda c, t=template: self.save_template(c, t))
            cards.add_widget(card)

    def save_template(self, card, template):
        App.get_running_app().repo.save_timer(template.task)
        card.saved = True


class StatsScreen(Screen):
    PERIODS = [('today', 'Today'), ('week', 'This week'), ('all', 'All time')]

    focus_value = StringProperty('0s')
    focus_detail = StringProperty('')

    def __init__(self, **kwargs):
        super().__init__(name='stats', **kwargs)
        self.period = 'week'
        Clock.schedule_once(lambda dt: self._build_periods())

    def _build_periods(self):
        for value, label in self.PERIODS:
            chip = Chip(label=label, value=value, selected=value == self.period)
            chip.bind(on_release=lambda c: self.set_period(c.value))
            self.ids.periods.add_widget(chip)

    def set_period(self, period):
        self.period = period
        for chip in self.ids.periods.children:
            chip.selected = chip.value == period
        self.refresh()

    def on_pre_enter(self, *args):
        self.refresh()

    def refresh(self):
        app = App.get_running_app()
        theme = app.theme
        summary = app.sessions.summary(self.period)
        self.focus_value = format_duration(summary['focused_seconds'])
        sessions = summary['sessions']
        self.focus_detail = f"across {sessions} session{'' if sessions == 1 else 's'}"

        grid = self.ids.stat_grid
        grid.clear_widgets()
        for icon, color, value, label in [
            ('flag-checkered', theme.primary, str(summary['sprints']), 'Sprints done'),
            ('check-circle', theme.success, str(summary['completed']), 'Sessions finished'),
            ('fire', theme.warning, f"{summary['current_streak']} d", 'Current streak'),
            ('trophy', theme.warning, f"{summary['best_streak']} d", 'Best streak'),
        ]:
            grid.add_widget(StatCard(icon=icon, icon_color=color, value=value, label=label))

        history = self.ids.history
        history.clear_widgets()
        recent = list(reversed(app.sessions.sessions('all')))[:6]
        if not recent:
            history.add_widget(HistoryRow(title='No sessions yet',
                                          subtitle='Finish a sprint to see it here',
                                          finished=False))
        for s in recent:
            when = datetime.fromisoformat(s['date']).strftime('%b %d')
            history.add_widget(HistoryRow(
                title=s['task'],
                subtitle=f"{when} · {s['time']} · {s['sprints_done']}/{s['sprints_planned']} sprints",
                value=format_duration(s['focused_seconds']),
                finished=s['sprints_done'] >= s['sprints_planned']))


class SettingsScreen(Screen):
    THEME_CHOICES = [('light', 'white-balance-sunny', 'Light'),
                     ('dark', 'weather-night', 'Dark'),
                     ('system', 'theme-light-dark', 'System')]

    def __init__(self, **kwargs):
        super().__init__(name='settings', **kwargs)
        Clock.schedule_once(lambda dt: self._build())

    def _build(self):
        app = App.get_running_app()
        for value, icon, label in self.THEME_CHOICES:
            chip = Chip(icon=icon, label=label, value=value)
            chip.bind(on_release=lambda c: self.choose('theme', c.value))
            self.ids.theme_chips.add_widget(chip)
        for accent in app.prefs.ACCENTS:
            dot = AccentDot(accent=accent)
            dot.bind(on_release=lambda d: self.choose('accent', d.accent))
            self.ids.accent_row.add_widget(dot)
        app.theme.bind(is_dark=lambda *a: self.sync())
        self.sync()

    def on_pre_enter(self, *args):
        self.sync()

    def sync(self):
        """Show the saved preferences"""
        app = App.get_running_app()
        for chip in self.ids.theme_chips.children:
            chip.selected = chip.value == app.prefs.get('theme')
        for dot in self.ids.accent_row.children:
            dot.selected = dot.accent == app.prefs.get('accent')
            dot.color = app.theme.accent_preview(dot.accent, app.theme.is_dark)
        self.ids.sound_toggle.active = app.prefs.get('sound')
        self.ids.vibrate_toggle.active = app.prefs.get('vibrate')

    def choose(self, key, value):
        App.get_running_app().set_pref(key, value)
        self.sync()
