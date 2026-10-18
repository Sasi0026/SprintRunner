from src.time_block import WorkBlock, BreakBlock

class Schedule:
    def __init__(self, task):

        self.task = task
        self.blocks = []
        self.generate_block() # Generates blocks when schedule is created
        self.all_blocks = list(self.blocks) # Full plan; self.blocks is consumed by the timer

    def generate_block(self):
        total_seconds  = self.task.total_duration_minutes * 60
        work_seconds = self.task.work_block_minutes * 60
        break_seconds = self.task.break_block_seconds

        if work_seconds <= 0:
            return

        # No break after the last sprint, so N sprints need
        # N * work + (N - 1) * break seconds.
        num_cycles = int((total_seconds + break_seconds) / (work_seconds + break_seconds))

        for i in range(num_cycles):
            self.blocks.append(WorkBlock(work_seconds))

            if i < num_cycles - 1 and break_seconds > 0:
                self.blocks.append(BreakBlock(break_seconds))

    @property
    def work_block_count(self):
        return sum(1 for block in self.all_blocks if block.block_type == 'work')

    @property
    def total_break_seconds(self):
        return sum(block.duration_seconds for block in self.all_blocks if block.block_type == 'break')

    def get_next_block(self):
        if self.blocks:
            return self.blocks.pop(0)

        return None


    def is_complete(self):
        return len(self.blocks) == 0
