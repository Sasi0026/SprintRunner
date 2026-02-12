from src.schedule import Schedule

class Timer:

    def __init__(self,schedule):
        self.schedule = schedule
        self.current_block = None
        self.remaining_seconds = None
        self.is_running = False
        self.is_paused = False

    def start(self):
        """
        Start the timer with the first block from schedule.
        
        Gets the next block, sets remaining time, and begins countdown.
        """
            
        self.current_block = self.schedule.get_next_block()
        self.remaining_seconds = self.current_block.duration_seconds
        self.is_running = True
        print(f"Started {self.current_block.block_type.capitalize()} Block - {self.remaining_seconds}s")

    def tick(self):

        """
        Called every second to countdown the timer.
        
        Decreases remaining_seconds by 1 and prints progress.
        """

        if not self.is_running or self.is_paused :
            return
        
        self.remaining_seconds -= 1
        print(f"Time Remaining : {self.remaining_seconds}s")

        if self.remaining_seconds == 0:
            self.on_block_complete()

    def on_block_complete(self):
        """
        Called when current block finishes.
        
        Plays alarm, gets next block, or stops if no blocks left.
        """
        print(f"Block finished! Alarm: {self.current_block.alarm_tone}")

        # Get next block 
        self.current_block = self.schedule.get_next_block()

        if self.current_block is None:
            self.stop()
        else: # start next block
            self.remaining_seconds = self.current_block.duration_seconds
            print(f"\nStarted {self.current_block.block_type.capitalize()} Block - {self.remaining_seconds}s")



    def pause(self):
        """Pause the timer. Can be resumed later."""
        self.is_paused = True
        print("Timer paused")

    def resume(self):
        """Resume the paused timer."""
        self.is_paused = False
        print("Timer resumed")
    
    def stop(self):
        """Stop the timer completely."""
        self.is_running = False  # Fix: False not false (capital F)
        print("Timer stopped. All blocks completed!")


        