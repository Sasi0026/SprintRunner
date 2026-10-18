class Task:
    """Represents a timer task configuration"""

    MAX_TOTAL_MINUTES = 24 * 60

    def __init__(self, name, total_duration_minutes, work_block_minutes, break_block_seconds=10):
        self.name = name
        self.total_duration_minutes = total_duration_minutes
        self.work_block_minutes = work_block_minutes
        self.break_block_seconds = break_block_seconds

    def validation_error(self):
        """Return a user-facing message describing what is wrong, or None if valid."""
        if not self.name or not self.name.strip():
            return "Give your sprint a name."
        if self.total_duration_minutes <= 0:
            return "Total time must be at least 1 minute."
        if self.total_duration_minutes > self.MAX_TOTAL_MINUTES:
            return "Total time can be at most 24 hours."
        if self.work_block_minutes <= 0:
            return "Sprint length must be at least 1 minute."
        if self.break_block_seconds < 0:
            return "Break time can't be negative."
        if self.work_block_minutes > self.total_duration_minutes:
            return "Sprint length can't be longer than the total time."
        return None

    def validate(self):
        return self.validation_error() is None

    def to_dict(self):
        """Convert the Task object into a dictionary representation."""
        return {
            'name':self.name,
            'total_duration_minutes':self.total_duration_minutes,
            'work_block_minutes':self.work_block_minutes,
            'break_block_seconds':self.break_block_seconds
            }

    @classmethod
    def from_dict(cls,task_dict):
        """Create a Task object from dictionary"""
        return cls(
            name=task_dict['name'],
            total_duration_minutes=task_dict['total_duration_minutes'],
            work_block_minutes=task_dict['work_block_minutes'],
            break_block_seconds=task_dict.get('break_block_seconds', 10)
        )


    def summary(self):
        return(
            f"\nTask: {self.name}\n"
            f"Total Time : {self.total_duration_minutes}\n"
            f"Sprint : {self.work_block_minutes}\n"
            f"Break Time: {self.break_block_seconds}\n"
        )

    def __str__(self):
        return f"Task: {self.name} ({self.total_duration_minutes} min)"
