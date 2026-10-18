from kivy.event import EventDispatcher
from kivy.properties import BooleanProperty, ColorProperty
from kivy.utils import get_color_from_hex


def hex_color(value, alpha=1.0):
    color = get_color_from_hex(value)
    color[3] = alpha
    return color


def mix(color_a, color_b, amount):
    """Blend color_a into color_b. amount=0 -> color_b, amount=1 -> color_a."""
    return [a * amount + b * (1 - amount) for a, b in zip(color_a[:3], color_b[:3])] + [1]


# Base palettes. Accent colours are applied on top of these.
PALETTES = {
    'light': {
        'bg': '#F4F6FA',
        'surface': '#FFFFFF',
        'surface_alt': '#EBEEF4',
        'text': '#1D2433',
        'text_muted': '#8A93A6',
        'divider': '#E6E9F0',
        'pending': '#DCE2EC',
        'success': '#22B45A',
        'warning': '#F29A2E',
        'danger': '#E5484D',
        'shadow': ('#1D2433', 0.07),
    },
    'dark': {
        'bg': '#0F1218',
        'surface': '#1A1F29',
        'surface_alt': '#252C3A',
        'text': '#EEF1F6',
        'text_muted': '#8C95A8',
        'divider': '#2A3140',
        'pending': '#2E3646',
        'success': '#34C46E',
        'warning': '#F5A84A',
        'danger': '#F06468',
        'shadow': ('#000000', 0.35),
    },
}

# (light mode, dark mode) shade of every accent
ACCENTS = {
    'blue': ('#1F5EDC', '#5B8DEF'),
    'purple': ('#7B3FE4', '#A27BF2'),
    'green': ('#14935A', '#3CC489'),
    'orange': ('#E0761A', '#F59E4C'),
    'pink': ('#D63A7A', '#EE6FA2'),
}


class Theme(EventDispatcher):
    """
    Colours used by every widget in sprintrunner.kv.

    The kv rules read e.g. ``app.theme.surface``, so calling apply() recolours
    the whole app instantly, without rebuilding any screen.
    """

    is_dark = BooleanProperty(False)
    bg = ColorProperty()
    surface = ColorProperty()
    surface_alt = ColorProperty()
    text = ColorProperty()
    text_muted = ColorProperty()
    divider = ColorProperty()
    pending = ColorProperty()
    success = ColorProperty()
    warning = ColorProperty()
    danger = ColorProperty()
    danger_soft = ColorProperty()
    shadow = ColorProperty()
    primary = ColorProperty()
    primary_soft = ColorProperty()
    primary_text = ColorProperty([1, 1, 1, 1])
    nav_bg = ColorProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.apply('light', 'blue')

    def apply(self, mode, accent):
        """mode is 'light' or 'dark' (resolve 'system' before calling)."""
        palette = PALETTES[mode]
        dark = mode == 'dark'
        for key, value in palette.items():
            if isinstance(value, tuple):
                setattr(self, key, hex_color(*value))
            else:
                setattr(self, key, hex_color(value))
        self.primary = hex_color(ACCENTS[accent][1 if dark else 0])
        self.primary_soft = mix(self.primary, self.surface, 0.22 if dark else 0.12)
        self.danger_soft = mix(self.danger, self.surface, 0.22 if dark else 0.12)
        self.nav_bg = self.surface
        self.is_dark = dark

    @staticmethod
    def accent_preview(accent, dark=False):
        return hex_color(ACCENTS[accent][1 if dark else 0])
