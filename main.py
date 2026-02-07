from src.task import Task

def main():
    print('Sprint Runner Started')

    name = input('Enter the Task Name : ')
    total_duration_minutes = int(input('Enter Total Time (minutes) : '))
    work_block_minutes = int(input('Enter work block Time (minutes) : '))
    break_block_seconds = int(input('Enter break Time (minutes) : '))

    task = Task(name,total_duration_minutes,work_block_minutes,break_block_seconds)

    if task.validate():
        print(f"\n Task Created Successfully!")
        print(task)
    else:
        print("Invalid task settings!")

    # Test loading from dict
    task_dict = task.to_dict()
    print(f"\nTask as dictionary: {task_dict}")

    loaded_task = Task.from_dict(task_dict)
    print(f"\nLoaded task: {loaded_task}")
    #print(task.summary())
    #print(task.validate())
    #print(task.__str__())

if __name__ == "__main__":
    main()