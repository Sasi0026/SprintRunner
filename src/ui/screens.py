from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView 
from kivy.uix.gridlayout import GridLayout
from src.task import Task
from src.timer_repository import TimerRepository
from src.schedule import Schedule

class HomeScreen(Screen):  #  inherit from Screen

    def __init__(self, **kwargs):  # **kwargs - to pass internal arguments (like name, size, etc.)
        super().__init__(name='home', **kwargs)  #  pass **kwargs
        
        # Main layout
        layout = BoxLayout(orientation='vertical')
        
        # Top bar (horizontal!)
        top_bar = BoxLayout(orientation='horizontal', size_hint=(1, 0.1), padding=10)  
        
        # App Title
        title = Label(
            text='🏃 SprintRunner',
            font_size='24sp',
            size_hint=(0.8, 1),
            bold=True
        )
        
        # Add Button
        add_btn = Button(
            text='+',
            font_size='32sp',
            size_hint=(0.2, 1),
            background_color=(0.2, 0.8, 0.4, 1)
        )
        add_btn.bind(on_press=self.go_to_create)  # Add this line

        

        top_bar.add_widget(title)
        top_bar.add_widget(add_btn)

        # Scrollable area for tasks
        scroll = ScrollView(size_hint=(1,0.9))
        self.task_container = GridLayout(cols=1, spacing=10, size_hint_y=None, padding=10)
        self.task_container.bind(minimum_height=self.task_container.setter('height'))

        scroll.add_widget(self.task_container)
        

        
        # Add top bar to main layout
        layout.add_widget(top_bar)
        layout.add_widget(scroll)
        
        # Add layout to screen
        self.add_widget(layout)
        self.load_tasks()

    def go_to_create(self, instance):
        """Navigate to Create Task screen"""
        self.manager.current = 'create_task'

    def load_tasks(self):
        """Load saved tasks from repository"""
        from src.timer_repository import TimerRepository

        self.task_container.clear_widgets()

        repo = TimerRepository()
        tasks = repo.list_timers()

        if tasks:
            for task_name in tasks:
                card = self.create_task_card(task_name)
                self.task_container.add_widget(card)

        else:
            placeholder = Label(text="No Saved Tasks.\nTap + to Create one.", font_size='18sp')
            self.task_container(self.add_widget(placeholder))


    def create_task_card(self,task_name):
        """Create a styled task card button"""
        card = Button(
            text = task_name,
            size_hint_y = None,
            height = 80,
            background_color=(0.2, 0.4, 0.8, 1),
            font_size = '20sp',
            bold = True
            )
        card.bind(on_press=lambda x:self.start_task(task_name))
        return card
    
    def start_task(self,task_name):
        """Start the selected task timer"""
        from src.timer_repository import TimerRepository
        from src.schedule import Schedule

        # Load task from repository
        repo = TimerRepository()
        task = repo.load_timer(task_name)

        if task:
            schedule = Schedule(task)

            # Get tiemr screen and set it up
            timer_screen = self.manager.get_screen('timer')
            timer_screen.setup_timer(task,schedule)
            
            self.manager.current = 'timer'

    def on_pre_enter(self, *args):
        """Called when screen is about to be shown"""
        self.load_tasks()




# "Create Task" Screen
class CreateTaskScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(name='create_task', **kwargs)

        # Vertical layout with padding
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        # Title
        title = Label(
            text='Create New Task',  # Fix: add comma
            font_size='24sp',
            size_hint=(1, 0.1),
            bold=True
        )

        # Input fields (use TextInput, not Label!)
        self.task_name = TextInput(
            hint_text='Task Name',
            multiline=False,
            size_hint=(1, 0.1)
        )

        self.task_total_time = TextInput(
            hint_text='Total Time (minutes)',
            multiline=False,
            input_filter='int',  # Only numbers
            size_hint=(1, 0.1)
        )
        
        self.task_work_block = TextInput(
            hint_text='Work Block (minutes)',
            multiline=False,
            input_filter='int',
            size_hint=(1, 0.1)
        )

        self.task_break_block = TextInput(
            hint_text='Break Time (seconds)',
            multiline=False,
            input_filter='int',
            size_hint=(1, 0.1)
        )

        # Buttons
        create_btn = Button(
            text='Create Task',
            font_size='20sp',
            size_hint=(1, 0.1),
            background_color=(0.2, 0.8, 0.4, 1)
        )
        create_btn.bind(on_press=self.create_task)

        cancel_btn = Button(
            text='Cancel',
            font_size='20sp',
            size_hint=(1, 0.1),
            background_color=(0.8, 0.2, 0.2, 1)
        )
        
        cancel_btn.bind(on_press=self.go_back) # Make Cancel button go back to HomeScreen.

        # Add all widgets
        layout.add_widget(title)
        layout.add_widget(self.task_name)
        layout.add_widget(self.task_total_time)
        layout.add_widget(self.task_work_block)
        layout.add_widget(self.task_break_block)
        layout.add_widget(create_btn)
        layout.add_widget(cancel_btn)
        
        self.add_widget(layout) 

    def go_back(self, instance):
        """Go back to home screen"""
        self.manager.current = 'home'

    def create_task(self, instance):
        """Create task from inputs and save it"""
        from src.task import Task
        from src.timer_repository import TimerRepository

        # Get values from inputs
        name = self.task_name.text
        total_time = int(self.task_total_time.text)
        work_block = int(self.task_work_block.text)
        break_time = int(self.task_break_block.text)

        # Create Task 
        task = Task(name, total_time, work_block, break_time)

        # Save Task
        repo = TimerRepository()
        repo.save_timer(task)

        # Go back to Home 
        self.manager.current = 'home'

class TimerScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(name='timer', **kwargs)

        self.task_name = None
        self.current_block_index = 0  # Track which block is active

        # Main Layout
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        # Top bar 
        top_bar = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))

        self.task_label = Label(
            text='Task Name',
            bold=True,
            font_size='20sp',
            size_hint=(0.5, 1)
        )

        self.timer_display = Label(
            text='00:00',
            font_size='32sp',
            bold=True,
            size_hint=(0.5, 1),
            color=(1, 1, 1, 1)
        )

        top_bar.add_widget(self.task_label)
        top_bar.add_widget(self.timer_display)
        layout.add_widget(top_bar)

        # Progress blocks area
        self.blocks_container = GridLayout(
            cols=10,
            spacing=5,
            size_hint=(1, 0.5),
            padding=10
        )
        layout.add_widget(self.blocks_container)

        # Control buttons
        btn_container = BoxLayout(orientation='horizontal', size_hint=(1, 0.2), spacing=10)

        self.start_btn = Button(
            text='Start',
            background_color=(0.06, 0.38, 0.99, 1),  # IBM blue
            font_size='20sp'
        )

        self.pause_btn = Button(
            text='Pause',
            background_color=(0.3, 0.3, 0.3, 1),  # Gray
            font_size='20sp',
            disabled=True  # Disabled until timer starts
        )

        self.stop_btn = Button(
            text='Stop',
            background_color=(0.9, 0.2, 0.2, 1),  # Red
            font_size='20sp'
        )

        self.start_btn.bind(on_press=self.on_start)
        self.pause_btn.bind(on_press=self.on_pause)
        self.stop_btn.bind(on_press=self.on_stop)

        btn_container.add_widget(self.start_btn)
        btn_container.add_widget(self.pause_btn)
        btn_container.add_widget(self.stop_btn)

        layout.add_widget(btn_container)

        self.add_widget(layout)

    def on_start(self, instance):
        """Start or resume the timer countdown"""
        from src.timer import Timer
        from kivy.clock import Clock

        if not hasattr(self, 'timer'):
            # First time starting - create timer
            self.timer = Timer(self.schedule)
            self.timer.on_block_complete_callback = self.on_timer_block_complete  # ADD THIS LINE
            self.timer.start()
            self.current_block_index = 0
            
            # Mark first block as active (green)
            if len(self.blocks) > 0:
                self.mark_block_active(0)  # ADD THIS
            
            # Cancel any existing clock
            if hasattr(self, 'clock_event'):
                self.clock_event.cancel()
            
            # Start clock
            self.clock_event = Clock.schedule_interval(self.update_timer, 1)
            
            # Update button states
            self.start_btn.disabled = True
            self.pause_btn.disabled = False
        else:
            # Resume from pause
            self.timer.resume()
            self.pause_btn.text = 'Pause'

    def on_pause(self, instance):
        """Pause/Resume the timer"""
        if hasattr(self, 'timer'):
            if self.timer.is_paused:
                self.timer.resume()
                self.pause_btn.text = 'Pause'
            else:
                self.timer.pause()
                self.pause_btn.text = 'Resume'

    def on_stop(self, instance):
        """Stop timer and return home"""
        if hasattr(self, 'clock_event'):
            self.clock_event.cancel()
        if hasattr(self, 'timer'):
            self.timer.stop()
        
        # Reset button states
        self.start_btn.disabled = False
        self.pause_btn.disabled = True
        self.pause_btn.text = 'Pause'
        
        self.manager.current = 'home'

    def update_timer(self, dt):
        if not hasattr(self, 'timer') or not self.timer.is_running or self.timer.is_paused:
            return True
        
        self.timer.tick()
        
        if self.timer.current_block:
            mins = self.timer.remaining_seconds // 60
            secs = self.timer.remaining_seconds % 60
            self.timer_display.text = f"{mins:02d}:{secs:02d}"
        
        return self.timer.is_running
    def create_progress_blocks(self, num_blocks):
        """Create visual blocks for work/break progress"""
        from kivy.graphics import Color, Rectangle

        self.blocks_container.clear_widgets()
        self.blocks = []

        for i in range(num_blocks):
            # Create a widget to hold the colored background
            block = Label(
                text='',
                size_hint=(None, None),
                size=(50, 50)
            )
            
            # Add black background initially (pending)
            with block.canvas.before:
                Color(0.1, 0.1, 0.1, 1)  # Black - pending
                block.rect = Rectangle(pos=block.pos, size=block.size)
            
            # Update rectangle when block moves
            block.bind(pos=self.update_rect, size=self.update_rect)
            
            self.blocks.append(block)
            self.blocks_container.add_widget(block)

    def update_rect(self, instance, value):
        """Update rectangle position/size when block moves"""
        instance.rect.pos = instance.pos
        instance.rect.size = instance.size

    def mark_block_active(self, index):
        """Mark a block as currently active (green)"""
        from kivy.graphics import Color, Rectangle
        
        if index < len(self.blocks):
            block = self.blocks[index]
            block.canvas.before.clear()
            
            with block.canvas.before:
                Color(0.1, 0.9, 0.1, 1)  # Green - active (NVIDIA color)
                block.rect = Rectangle(pos=block.pos, size=block.size)

    def mark_block_complete(self, index):
        """Mark a block as completed (orange)"""
        from kivy.graphics import Color, Rectangle
        
        if index < len(self.blocks):
            block = self.blocks[index]
            block.canvas.before.clear()
            
            with block.canvas.before:
                Color(1, 0.5, 0, 1)  # Orange - completed (Amazon color)
                block.rect = Rectangle(pos=block.pos, size=block.size)

    def play_alarm(self, alarm_file):
        """Play alarm sound when block ends"""
        print(f">>> PLAY_ALARM CALLED with: {alarm_file}")  # ADD THIS
        try:
            import pygame
            
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            
            pygame.mixer.music.stop()
            pygame.mixer.music.load(alarm_file)
            pygame.mixer.music.play()
            
            print(f">>> Sound should be playing now")  # ADD THIS
        except Exception as e:
            print(f">>> ERROR: {e}")  # ADD THIS

    def setup_timer(self, task, schedule):
        """Initialize timer with task and schedule"""
        self.task = task
        self.schedule = schedule
        self.current_block_index = 0

        # Reset timer if exists
        if hasattr(self, 'timer'):
            delattr(self, 'timer')
        if hasattr(self, 'clock_event'):
            self.clock_event.cancel()

        # Update UI
        self.task_label.text = task.name
        self.timer_display.text = f"{task.work_block_minutes}:00"

        # Reset button states
        self.start_btn.disabled = False
        self.pause_btn.disabled = True
        self.pause_btn.text = 'Pause'

        # Create progress blocks
        num_blocks = len(schedule.blocks)
        self.create_progress_blocks(num_blocks)

    def on_timer_block_complete(self, alarm_tone):
        """Called by timer when block completes"""
        self.play_alarm(alarm_tone)
        self.mark_block_complete(self.current_block_index)
        self.current_block_index += 1
        if self.current_block_index < len(self.blocks):
            self.mark_block_active(self.current_block_index)

    def on_timer_block_complete(self, alarm_tone):
        """Called by timer when block completes"""
        self.play_alarm(alarm_tone)
        self.mark_block_complete(self.current_block_index)
        self.current_block_index += 1
        if self.current_block_index < len(self.blocks):
            self.mark_block_active(self.current_block_index)




    



