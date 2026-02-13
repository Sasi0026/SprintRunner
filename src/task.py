class Task:
    """Represents a timer task configuration"""

    def __init__(self, name, total_duration_minutes, work_block_minutes, break_block_seconds):
        self.name = name
        self.total_duration_minutes = total_duration_minutes
        self.work_block_minutes = work_block_minutes
        self.break_block_seconds = break_block_seconds

    def validate(self):
        if self.total_duration_minutes <= 0:
            return False
        if self.work_block_minutes <= 0:
            return False
        if self.break_block_seconds < 0:
            return False
        if self.work_block_minutes > self.total_duration_minutes:
            return False
        return True
    
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
            break_block_seconds=task_dict['break_block_seconds']
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