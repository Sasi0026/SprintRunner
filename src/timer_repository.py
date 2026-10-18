import json
import os
from src.task import Task


class JsonStore:
    """Small helper that keeps one JSON document in a file."""

    def __init__(self, file_path, default):
        self.file_path = file_path
        self.default = default

    def read(self):
        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Missing or corrupted file: start fresh instead of crashing the app
            return json.loads(json.dumps(self.default))

    def write(self, data):
        folder = os.path.dirname(self.file_path)
        if folder:
            os.makedirs(folder, exist_ok=True)
        # Write to a temp file first so a crash mid-write can't corrupt the data
        tmp_path = self.file_path + '.tmp'
        with open(tmp_path, 'w') as f:
            json.dump(data, f, indent=2)
        os.replace(tmp_path, self.file_path)


class TimerRepository:
    def __init__(self, file_path ="saved_timers.json"):
        self.store = JsonStore(file_path, {})

    def save_timer(self,task):
        timers = self.store.read()

        # Add new task (use task name as key)
        timers[task.name] = task.to_dict()
        self.store.write(timers)

    def has_timer(self, task_name):
        return task_name in self.store.read()

    def load_timer(self, task_name):
        """Load a saved timer by name"""
        task_data = self.store.read().get(task_name)
        return Task.from_dict(task_data) if task_data else None

    def list_timers(self):
        """ Returns the names of all saved timers, in the order they were saved """
        return list(self.store.read().keys())

    def list_tasks(self):
        """ Returns all saved timers as Task objects """
        return [Task.from_dict(data) for data in self.store.read().values()]

    def delete_timer(self, task_name):
        """Delete a saved timer by name. Returns True if it existed."""
        timers = self.store.read()
        if task_name not in timers:
            return False
        del timers[task_name]
        self.store.write(timers)
        return True
