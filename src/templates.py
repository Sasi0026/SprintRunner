from src.task import Task


class Template:
    """A ready-made sprint setup shown on the Home and Explore screens."""

    def __init__(self, name, category, description, icon, color, total, work, rest):
        self.name = name
        self.category = category
        self.description = description
        self.icon = icon      # icon name from src/ui/icons.py
        self.color = color    # card colour, hex
        self.task = Task(name, total, work, rest)


TEMPLATES = [
    Template("Coding Sprint", "Developers", "One problem every 5 minutes, a 10 second reset in between.",
             'code-braces', '#2FA8DD', 60, 5, 10),
    Template("Pomodoro", "Focus", "The classic: 25 minutes of focus, 5 minutes off.",
             'timer-sand', '#EF6A5B', 100, 25, 300),
    Template("Exam Practice", "Students", "Timed questions: 3 minutes each with 15 seconds to breathe.",
             'school', '#9B4DCA', 45, 3, 15),
    Template("Deep Work", "Focus", "Two long blocks of focus with a proper break.",
             'brain', '#3D6CE0', 110, 50, 600),
    Template("Reading", "Students", "Read for 15 minutes, look up for one.",
             'book-open-variant', '#F2994A', 45, 15, 60),
    Template("Workout Circuit", "Fitness", "1 minute per exercise, 30 seconds rest.",
             'dumbbell', '#27AE79', 20, 1, 30),
    Template("Language Drill", "Learning", "Short vocabulary rounds that stick.",
             'translate', '#E2558E', 30, 5, 30),
    Template("Meditation", "Wellbeing", "Three calm 5-minute sits.",
             'meditation', '#5B8DEF', 17, 5, 60),
]
