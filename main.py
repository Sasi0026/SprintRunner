from src.task import Task
from src.schedule import Schedule
from src.timer import Timer

import time 


def main():
    print('Sprint Runner Started')

    name = input('Enter the Task Name : ')
    total_duration_minutes = int(input('Enter Total Time (minutes) : '))
    work_block_minutes = int(input('Enter work block Time (minutes) : '))
    break_block_seconds = int(input('Enter break Time (Seconds) : '))

    task = Task(name,total_duration_minutes,work_block_minutes,break_block_seconds)

    if task.validate():
        print(f"\n Task Created Successfully!")
        print(task)
    else:
        print("Invalid task settings!")


    # Create schedule and timer
    schedule = Schedule(task)
    print(f'\nTotal blocks Created : {len(schedule.blocks)}')

    print(f"Blocks in schedule: {len(schedule.blocks)}")
    
    # Create timer 
    timer = Timer(schedule)
    timer.start()

    # Run Timer
    while timer.is_running:
        time.tick()
        time.sleep(1)



if __name__ == "__main__":
    main()