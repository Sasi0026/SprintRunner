from datetime import date, datetime, timedelta
from src.timer_repository import JsonStore


class SessionLog:
    """Records finished sessions and calculates the numbers on the Stats screen."""

    MAX_ENTRIES = 2000

    def __init__(self, file_path="sessions.json"):
        self.store = JsonStore(file_path, [])

    def record(self, task_name, focused_seconds, sprints_done, sprints_planned, when=None):
        """Save one session. Sessions with no focused time are ignored."""
        if focused_seconds <= 0:
            return
        when = when or datetime.now()
        sessions = self.store.read()
        sessions.append({
            'task': task_name,
            'date': when.date().isoformat(),
            'time': when.strftime('%H:%M'),
            'focused_seconds': int(focused_seconds),
            'sprints_done': sprints_done,
            'sprints_planned': sprints_planned,
        })
        self.store.write(sessions[-self.MAX_ENTRIES:])

    def sessions(self, period='all', today=None):
        """Sessions in a period: 'today', 'week' (last 7 days) or 'all'."""
        today = today or date.today()
        sessions = self.store.read()
        if period == 'today':
            start = today
        elif period == 'week':
            start = today - timedelta(days=6)
        else:
            return sessions
        return [s for s in sessions if start <= date.fromisoformat(s['date']) <= today]

    def summary(self, period='all', today=None):
        today = today or date.today()
        sessions = self.sessions(period, today)
        return {
            'sessions': len(sessions),
            'focused_seconds': sum(s['focused_seconds'] for s in sessions),
            'sprints': sum(s['sprints_done'] for s in sessions),
            'completed': sum(1 for s in sessions if s['sprints_done'] >= s['sprints_planned']),
            'current_streak': self.current_streak(today),
            'best_streak': self.best_streak(),
        }

    def _active_days(self):
        return sorted({date.fromisoformat(s['date']) for s in self.store.read()})

    def current_streak(self, today=None):
        """Days in a row with at least one session, ending today (or yesterday)."""
        today = today or date.today()
        days = set(self._active_days())
        day = today if today in days else today - timedelta(days=1)
        streak = 0
        while day in days:
            streak += 1
            day -= timedelta(days=1)
        return streak

    def best_streak(self):
        best = run = 0
        previous = None
        for day in self._active_days():
            run = run + 1 if previous and day - previous == timedelta(days=1) else 1
            best = max(best, run)
            previous = day
        return best


def format_duration(seconds):
    """3725 -> '1h 2m', 125 -> '2m', 40 -> '40s'"""
    seconds = int(seconds)
    hours, rest = divmod(seconds, 3600)
    minutes, secs = divmod(rest, 60)
    if hours:
        return f"{hours}h {minutes}m" if minutes else f"{hours}h"
    if minutes:
        return f"{minutes}m"
    return f"{secs}s"
