from src.timer_repository import JsonStore


class Settings:
    """User preferences, saved to a JSON file."""

    THEMES = ('light', 'dark', 'system')
    ACCENTS = ('blue', 'purple', 'green', 'orange', 'pink')

    DEFAULTS = {
        'theme': 'system',
        'accent': 'blue',
        'sound': True,
        'vibrate': True,
    }

    def __init__(self, file_path="settings.json"):
        self.store = JsonStore(file_path, {})
        self.values = dict(self.DEFAULTS)
        saved = self.store.read()
        if isinstance(saved, dict):
            self.values.update({k: v for k, v in saved.items() if k in self.DEFAULTS})
        # Ignore values a newer/older version might have written
        if self.values['theme'] not in self.THEMES:
            self.values['theme'] = self.DEFAULTS['theme']
        if self.values['accent'] not in self.ACCENTS:
            self.values['accent'] = self.DEFAULTS['accent']

    def get(self, key):
        return self.values[key]

    def set(self, key, value):
        self.values[key] = value
        self.store.write(self.values)
