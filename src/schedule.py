from src.time_block import WorkBlock, BreakBlock

class Schedule:
    def __init__(self, task):

        self.task = task 
        self.blocks = []
        self.generate_block() # Generates blocks when schedule is created
    
    def generate_block(self):
        total_seconds  = self.task.total_duration_minutes * 60 
        work_seconds = self.task.work_block_minutes * 60
        break_seconds = self.task.break_block_seconds

        cycle_duration = work_seconds + break_seconds
        num_cycles = int(total_seconds / cycle_duration)

        for i in range(num_cycles):
            self.blocks.append(WorkBlock(work_seconds))

            if i < num_cycles - 1:
                self.blocks.append(BreakBlock(break_seconds))




    def get_next_block(self):
        if self.blocks:
            return self.blocks.pop(0)
        
        return None
    

    def is_complete(self):
        return len(self.blocks) == 0