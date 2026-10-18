import time


class Timer:
    """
    Runs a Schedule block by block.

    Time is measured from the wall clock instead of by counting ticks, so the
    countdown stays correct when ticks are late or missing (for example while
    Android has the app paused in the background). The next tick() catches up,
    completing every block that ended in the meantime.
    """

    def __init__(self, schedule, clock=time.time):
        self.schedule = schedule
        self.clock = clock
        self.current_block = None
        self.remaining_seconds = None
        self.is_running = False
        self.is_paused = False
        self.completed_work_blocks = 0
        self.focused_seconds = 0
        self.on_block_complete_callback = None
        self._block_end_time = None

    def start(self):
        """
        Start the timer with the first block from schedule.

        Returns False if the schedule has no blocks.
        """

        self.current_block = self.schedule.get_next_block()
        if self.current_block is None:
            return False

        self.remaining_seconds = self.current_block.duration_seconds
        self._block_end_time = self.clock() + self.remaining_seconds
        self.is_running = True
        return True

    def tick(self):

        """
        Update remaining_seconds from the clock.

        Call this regularly (the UI calls it every half second); calling it
        more or less often does not change how fast time passes.
        """

        if not self.is_running or self.is_paused :
            return

        now = self.clock()
        while self.is_running and now >= self._block_end_time:
            overshoot = now - self._block_end_time
            self.on_block_complete()
            if self.is_running:
                self._block_end_time = now - overshoot + self.current_block.duration_seconds

        if self.is_running:
            self.remaining_seconds = max(0, int(round(self._block_end_time - now)))

    def on_block_complete(self):
        """Called when current block finishes"""
        finished = self.current_block
        if finished.block_type == 'work':
            self.completed_work_blocks += 1
            self.focused_seconds += finished.duration_seconds

        # Notify GUI if callback exists
        if self.on_block_complete_callback:
            self.on_block_complete_callback(finished)

        # Get next block
        self.current_block = self.schedule.get_next_block()

        if self.current_block is None:
            self.remaining_seconds = 0
            self.stop()
        else:
            self.remaining_seconds = self.current_block.duration_seconds

    def skip(self):
        """End the current block now and move on to the next one."""
        if not self.is_running:
            return
        if self.current_block.block_type == 'work':
            # Only count the part of the sprint that was actually done
            done = self.current_block.duration_seconds - self._remaining_exact()
            self.focused_seconds += max(0, int(done))
        self.current_block = self.schedule.get_next_block()
        if self.current_block is None:
            self.remaining_seconds = 0
            self.stop()
            return
        self.remaining_seconds = self.current_block.duration_seconds
        self._block_end_time = self.clock() + self.remaining_seconds

    def pause(self):
        """Pause the timer. Can be resumed later."""
        if not self.is_running or self.is_paused:
            return
        self.remaining_seconds = self._remaining_exact()
        self.is_paused = True

    def resume(self):
        """Resume the paused timer."""
        if not self.is_paused:
            return
        self._block_end_time = self.clock() + self.remaining_seconds
        self.is_paused = False

    def focus_so_far(self):
        """Focused seconds including the part of the current sprint done so far."""
        if self.is_running and self.current_block.block_type == 'work':
            return self.focused_seconds + int(self.current_block.duration_seconds - self._remaining_exact())
        return self.focused_seconds

    @property
    def is_finished(self):
        return not self.is_running and self.current_block is None and self._block_end_time is not None

    def _remaining_exact(self):
        if self.is_paused:
            return self.remaining_seconds
        return max(0, self._block_end_time - self.clock())

    def stop(self):
        """Stop the timer completely."""
        self.is_running = False
