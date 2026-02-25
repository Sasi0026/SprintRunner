class TimeBlock:
    """Base class for work and break blocks"""

    def __init__(self,duration_seconds, block_type):
        self.duration_seconds = duration_seconds
        self.block_type = block_type

    def __str__(self):
        return f"{self.block_type.capitalize()} Block: {self.duration_seconds}s"
    

class WorkBlock(TimeBlock):
    """Represents a work interval"""

    def __init__(self, duration_seconds):

        super().__init__(duration_seconds, 'work')
        self.alarm_tone = 'assets/harry_potter_hedwigs.mp3'

class BreakBlock(TimeBlock):
    """Represents a break interval"""

    def __init__(self, duration_seconds):

        super().__init__(duration_seconds, 'break')
        self.alarm_tone = 'assets/diagon_alley.mp3'
    

