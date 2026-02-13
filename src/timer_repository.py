import json 

class TimerRepository:
    def __init__(self, file_path ="saved_timers.json"):
        self.file_path = file_path

        # Create empty file if doesn't exist
        try:
            with open(self.file_path, 'r') as f:
                pass
        except FileNotFoundError:
            with open(self.file_path, 'w') as f:
                json.dump({}, f)

    def save_timer(self,task):

        with open(self.file_path, 'r') as f:
            timers = json.load(f)

        # Add new task (use task name as key)
        timers[task.name] = task.to_dict()

        with open(self.file_path, 'w') as f:
            json.dump(timers, f, indent=2)
        
        print(f"Timer '{task.name}' saved!")

    def load_timer(self, task_name):
        """Load a saved timer by name"""
        try:
            with open(self.file_path, 'r') as f:
                timers = json.load(f)

            if task_name in timers:
                task_data = timers[task_name]
                return Task.from_dict(task_data)
            else:
                return None

        except FileNotFoundError:
            return None
        
    def list_timers(self):
        """ Loads all timers saved """

        try:
            with open(self.file_path, 'r') as f:
                timers = json.load(f) # if it dict all task names stored as key we can directly return timers right?
            
            if timers:
                print("\n Saved Timers: ")

                for name in timers.keys():
                    print(f'  -{name}')
            else:
                print('No Saved Timers found.')
            
            return list(timers.keys()) # Return list of names
        except FileNotFoundError:
            print('No Saved Timers found.')
            return []   # Return empty list, not None
        
    def delete_timer(self, task_name):
        """Delete a saved timer by name"""

        try:
            with open(self.file_path, 'r') as f:
                timers = json.load(f)

            if task_name in timers:
                del timers[task_name]
                # write back to file! 
                with open(self.file_path, 'w') as f:
                    json.dump(timers, f, indent=2)

                print(f"\nTimer '{task_name}' deleted successfully!")
            else:
                print(f"\nTimer '{task_name}' not found.")
        except FileNotFoundError:
            print("No saved timers found.")
            
            
            

