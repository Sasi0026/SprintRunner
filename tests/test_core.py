from datetime import date, datetime

from src.schedule import Schedule
from src.settings import Settings
from src.stats import SessionLog, format_duration
from src.task import Task
from src.timer import Timer
from src.timer_repository import TimerRepository


class FakeClock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


def make_timer(total=10, work=5, rest=30):
    clock = FakeClock()
    timer = Timer(Schedule(Task("t", total, work, rest)), clock=clock)
    return timer, clock


# --- Task -------------------------------------------------------------------

def test_task_validation_messages():
    assert Task("ok", 60, 5, 10).validate()
    assert Task("", 60, 5).validation_error() == "Give your sprint a name."
    assert Task("x", 0, 5).validation_error()
    assert Task("x", 60, 0).validation_error()
    assert Task("x", 60, 5, -1).validation_error()
    assert Task("x", 5, 10).validation_error()


def test_task_round_trip_and_missing_break_default():
    task = Task("Code", 60, 5, 10)
    assert Task.from_dict(task.to_dict()).to_dict() == task.to_dict()
    assert Task.from_dict({'name': 'a', 'total_duration_minutes': 1,
                           'work_block_minutes': 1}).break_block_seconds == 10


# --- Schedule ---------------------------------------------------------------

def test_schedule_fits_sprints_without_trailing_break():
    # 60 min, 5 min sprints, 10 s breaks -> 11 sprints and 10 breaks (3700s > 3600s for 12)
    schedule = Schedule(Task("t", 60, 5, 10))
    assert schedule.work_block_count == 11
    assert schedule.total_break_seconds == 100
    assert schedule.all_blocks[-1].block_type == 'work'


def test_schedule_exact_fit_and_zero_break():
    assert Schedule(Task("t", 10, 5, 0)).work_block_count == 2
    assert all(b.block_type == 'work' for b in Schedule(Task("t", 10, 5, 0)).all_blocks)
    assert Schedule(Task("t", 5, 5, 300)).work_block_count == 1


# --- Timer ------------------------------------------------------------------

def test_timer_counts_down_by_wall_clock():
    timer, clock = make_timer()
    assert timer.start()
    clock.advance(61)
    timer.tick()
    assert timer.remaining_seconds == 300 - 61
    assert timer.current_block.block_type == 'work'


def test_timer_catches_up_after_missed_ticks():
    timer, clock = make_timer(total=11, work=5, rest=30)  # work, break, work
    finished = []
    timer.on_block_complete_callback = finished.append
    timer.start()
    clock.advance(300 + 30 + 10)  # app was in background for both blocks
    timer.tick()
    assert [b.block_type for b in finished] == ['work', 'break']
    assert timer.current_block.block_type == 'work'
    assert timer.remaining_seconds == 290


def test_timer_finishes_and_counts_focus():
    timer, clock = make_timer(total=11, work=5, rest=30)
    timer.start()
    clock.advance(10_000)
    timer.tick()
    assert timer.is_finished
    assert timer.completed_work_blocks == 2
    assert timer.focused_seconds == 600


def test_pause_freezes_time():
    timer, clock = make_timer()
    timer.start()
    clock.advance(100)
    timer.pause()
    clock.advance(1000)
    timer.tick()
    assert timer.remaining_seconds == 200
    timer.resume()
    clock.advance(50)
    timer.tick()
    assert timer.remaining_seconds == 150


def test_skip_moves_to_next_block_and_counts_partial_focus():
    timer, clock = make_timer(total=11, work=5, rest=30)
    timer.start()
    clock.advance(120)
    timer.skip()
    assert timer.current_block.block_type == 'break'
    assert timer.focused_seconds == 120
    assert timer.completed_work_blocks == 0


def test_focus_so_far_includes_current_sprint():
    timer, clock = make_timer(total=11, work=5, rest=30)
    timer.start()
    clock.advance(330 + 45)  # sprint 1 + break + 45s of sprint 2
    timer.tick()
    assert timer.focused_seconds == 300
    assert timer.focus_so_far() == 345


def test_start_with_empty_schedule_returns_false():
    timer = Timer(Schedule(Task("t", 1, 0)))
    assert timer.start() is False


# --- Repository / settings / stats -------------------------------------------

def test_repository_crud_and_corrupt_file(tmp_path):
    path = tmp_path / "timers.json"
    repo = TimerRepository(str(path))
    assert repo.list_timers() == []
    repo.save_timer(Task("A", 60, 5, 10))
    repo.save_timer(Task("B", 30, 5, 0))
    assert repo.list_timers() == ["A", "B"]
    assert repo.load_timer("B").total_duration_minutes == 30
    assert repo.delete_timer("A") is True
    assert repo.delete_timer("A") is False
    path.write_text("{not json")
    assert repo.list_timers() == []


def test_settings_persist_and_reject_unknown_values(tmp_path):
    path = str(tmp_path / "settings.json")
    settings = Settings(path)
    assert settings.get('theme') == 'system'
    settings.set('theme', 'dark')
    assert Settings(path).get('theme') == 'dark'
    settings.set('accent', 'neon')
    assert Settings(path).get('accent') == 'blue'


def test_session_log_summary_and_streaks(tmp_path):
    log = SessionLog(str(tmp_path / "sessions.json"))
    for day in (3, 4, 5, 15, 16):
        log.record("Code", 600, 2, 2, when=datetime(2026, 10, day, 9, 0))
    log.record("Code", 0, 0, 2, when=datetime(2026, 10, 16, 10, 0))  # ignored
    today = date(2026, 10, 16)
    summary = log.summary('all', today)
    assert summary['sessions'] == 5
    assert summary['focused_seconds'] == 3000
    assert summary['current_streak'] == 2
    assert summary['best_streak'] == 3
    assert log.summary('today', today)['sessions'] == 1
    assert log.summary("week", today)["sessions"] == 2


def test_format_duration():
    assert format_duration(3725) == "1h 2m"
    assert format_duration(3600) == "1h"
    assert format_duration(125) == "2m"
    assert format_duration(40) == "40s"
