import os

# Material Design Icons font (Pictogrammers, see assets/fonts/README.md).
# Kivy's default font has no emoji, so icons come from this font instead.
ICON_FONT = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'fonts',
                         'materialdesignicons-webfont.ttf')
ICON_FONT = os.path.normpath(ICON_FONT)

ICONS = {
    'arrow-left': "\U000F004D",
    'book-open-variant': "\U000F14F7",
    'brain': "\U000F09D1",
    'chart-box': "\U000F154D",
    'check': "\U000F012C",
    'check-circle': "\U000F05E0",
    'chevron-right': "\U000F0142",
    'clock-outline': "\U000F0150",
    'close': "\U000F0156",
    'code-braces': "\U000F0169",
    'cog': "\U000F0493",
    'coffee': "\U000F0176",
    'compass': "\U000F018B",
    'delete-outline': "\U000F09E7",
    'dumbbell': "\U000F01E6",
    'fire': "\U000F0238",
    'flag-checkered': "\U000F023C",
    'home': "\U000F02DC",
    'lightning-bolt': "\U000F140B",
    'meditation': "\U000F117B",
    'minus': "\U000F0374",
    'palette': "\U000F03D8",
    'party-popper': "\U000F1056",
    'pause': "\U000F03E4",
    'play': "\U000F040A",
    'plus': "\U000F0415",
    'rocket-launch': "\U000F14DE",
    'school': "\U000F0474",
    'skip-next': "\U000F04AD",
    'stop': "\U000F04DB",
    'theme-light-dark': "\U000F050E",
    'timer-outline': "\U000F051B",
    'timer-sand': "\U000F051F",
    'translate': "\U000F05CA",
    'trophy': "\U000F0538",
    'vibrate': "\U000F0566",
    'volume-high': "\U000F057E",
    'weather-night': "\U000F0594",
    'white-balance-sunny': "\U000F05A8",
}


def icon_markup(name, size=None):
    """Markup that renders an icon inside a Label with markup=True."""
    glyph = ICONS.get(name, '')
    if not glyph:
        return ''
    size_open = f"[size={size}]" if size else ''
    size_close = "[/size]" if size else ''
    return f"[font={ICON_FONT}]{size_open}{glyph}{size_close}[/font]"
