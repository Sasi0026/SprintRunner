"""
Reusable themed widgets. Their look is defined in sprintrunner.kv; this file
holds their properties and behaviour.
"""
from kivy.animation import Animation
from kivy.metrics import dp
from kivy.properties import (BooleanProperty, ColorProperty, ListProperty, NumericProperty,
                             ObjectProperty, OptionProperty, StringProperty)
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.utils import escape_markup

from src.ui.icons import ICONS, icon_markup


def label_with_icon(icon, text):
    text = escape_markup(text)
    if not icon:
        return text
    return f"{icon_markup(icon)}  {text}" if text else icon_markup(icon)


class Text(Label):
    """Left-aligned, wrapping text that sizes its own height."""
    tone = OptionProperty('default', options=['default', 'muted', 'primary', 'inverse', 'danger'])


class Icon(Label):
    icon = StringProperty('')

    def glyph(self, name):
        return ICONS.get(name, '')


class Card(BoxLayout):
    """Rounded surface with a soft shadow."""
    radius = NumericProperty(dp(18))
    bg_color = ColorProperty(None, allownone=True)
    elevation = NumericProperty(1)


class PressableCard(ButtonBehavior, Card):
    pass


class AppButton(ButtonBehavior, Label):
    """Rounded button. style: primary | soft | danger | danger_soft | white | ghost"""
    style = OptionProperty('primary', options=['primary', 'soft', 'danger', 'danger_soft',
                                               'white', 'glass', 'ghost'])
    icon = StringProperty('')
    label = StringProperty('')
    radius = NumericProperty(dp(16))
    # Used by the 'white' style on coloured cards: text takes the card colour
    accent = ColorProperty(None, allownone=True)

    compose = staticmethod(label_with_icon)


class IconButton(ButtonBehavior, Label):
    """Round icon button. style: plain | soft | primary | danger_soft"""
    icon = StringProperty('')
    style = OptionProperty('plain', options=['plain', 'soft', 'primary', 'danger_soft'])

    def glyph(self, name):
        return ICONS.get(name, '')


class Chip(ButtonBehavior, Label):
    """Pill-shaped toggle used for filters and choices."""
    selected = BooleanProperty(False)
    icon = StringProperty('')
    label = StringProperty('')
    value = StringProperty('')

    compose = staticmethod(label_with_icon)


class InfoPill(Label):
    """Non-interactive pill showing an icon and a value (top of Home)."""
    icon = StringProperty('')
    label = StringProperty('')
    icon_color = ColorProperty([1, 1, 1, 1])

    def compose(self, icon, label, icon_color):
        hex_color = ''.join(f"{int(c * 255):02x}" for c in icon_color[:3])
        return f"[color={hex_color}]{icon_markup(icon)}[/color]  {escape_markup(label)}"


class AppTextInput(TextInput):
    pass


class Toggle(ButtonBehavior, Widget):
    """iOS/Material style on/off switch."""
    active = BooleanProperty(False)
    knob_x = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self._place_knob, size=self._place_knob)

    def on_press(self):
        self.active = not self.active

    def on_active(self, *args):
        Animation(knob_x=self._knob_target(), d=0.15, t='out_quad').start(self)

    def _knob_target(self):
        return 1.0 if self.active else 0.0

    def _place_knob(self, *args):
        self.knob_x = self._knob_target()


class Stepper(BoxLayout):
    """A row with a title, minus button, editable number and plus button."""
    title = StringProperty('')
    hint = StringProperty('')
    value = NumericProperty(0)
    step = NumericProperty(1)
    minimum = NumericProperty(0)
    maximum = NumericProperty(9999)

    def change(self, direction):
        self.value = max(self.minimum, min(self.maximum, int(self.value) + direction * self.step))

    def on_text_input(self, text):
        try:
            self.value = max(0, min(self.maximum, int(text)))
        except ValueError:
            self.value = 0


class ProgressRing(Widget):
    progress = NumericProperty(1.0)
    thickness = NumericProperty(dp(12))
    ring_color = ColorProperty([0, 0, 0, 1])
    track_color = ColorProperty([0, 0, 0, 0.1])


class NavItem(ButtonBehavior, BoxLayout):
    icon = StringProperty('')
    label = StringProperty('')
    target = StringProperty('')
    selected = BooleanProperty(False)

    def glyph(self, name):
        return ICONS.get(name, '')


class BottomNav(BoxLayout):
    current = StringProperty('home')
    items = ListProperty([
        ('home', 'home', 'Home'),
        ('explore', 'compass', 'Explore'),
        ('stats', 'chart-box', 'Stats'),
        ('settings', 'cog', 'Settings'),
    ])
    navigate = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for target, icon, label in self.items:
            item = NavItem(icon=icon, label=label, target=target)
            item.bind(on_release=lambda btn: self.navigate and self.navigate(btn.target))
            self.add_widget(item)
        self.on_current()

    def on_current(self, *args):
        for item in self.children:
            item.selected = item.target == self.current


class Dialog(ModalView):
    """
    Centered confirmation card like:
        Are you sure you want to quit?
        [ Exit ]
        [ Cancel ]
    """
    icon = StringProperty('')
    icon_color = ColorProperty(None, allownone=True)
    title = StringProperty('')
    message = StringProperty('')
    confirm_text = StringProperty('OK')
    cancel_text = StringProperty('Cancel')
    confirm_style = StringProperty('primary')
    confirm_action = ObjectProperty(None, allownone=True)

    def confirm(self):
        self.dismiss()
        if self.confirm_action:
            self.confirm_action()
