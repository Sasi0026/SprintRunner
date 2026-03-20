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
from kivy.core.audio import SoundLoader
from kivy.graphics import Color, RoundedRectangle


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(name='home', **kwargs)
        
        # Main layout
        layout = BoxLayout(orientation='vertical')
        
        # Top bar
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
        add_btn.bind(on_press=self.go_to_create)

        top_bar.add_widget(title)
        top_bar.add_widget(add_btn)

        # Scrollable area for tasks
        scroll = ScrollView(size_hint=(1, 0.9))
        self.task_container = GridLayout(cols=1, spacing=10, size_hint_y=None, padding=10)
        self.task_container.bind(minimum_height=self.task_container.setter('height'))

        scroll.add_widget(self.task_container)
        
        # Add to main layout
        layout.add_widget(top_bar)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
        self.load_tasks()

    def go_to_create(self, instance):
        """Navigate to Create Task screen"""
        self.manager.current = 'create_task'

    def load_tasks(self):
        """Load saved tasks from repository"""
        self.task_container.clear_widgets()

        repo = TimerRepository()
        tasks = repo.list_timers()

        if tasks:
            for task_name in tasks:
                card = self.create_task_card(task_name)
                self.task_container.add_widget(card)
        else:
            placeholder = Label(text="No Saved Tasks.\nTap + to Create one.", font_size='18sp')
            self.task_container.add_widget(placeholder)

    def create_task_card(self, task_name):
        """Create a styled task card button with Long-Press delete"""
        card = TaskCard(
            task_name=task_name,
            delete_callback=self.delete_task, # Pass the delete function down
            text=task_name,
            size_hint_y=None,
            height=80,
            background_color=(0.2, 0.4, 0.8, 1),
            font_size='20sp',
            bold=True
        )
        card.bind(on_press=lambda x: self.start_task(task_name))
        return card
    
    def delete_task(self,task_name):
        """Called when a user long-presses a task card"""
        repo = TimerRepository()
        repo.delete_timer(task_name)
        self.load_tasks()
    
    def start_task(self, task_name):
        """Start the selected task timer"""
        repo = TimerRepository()
        task = repo.load_timer(task_name)

        if task:
            schedule = Schedule(task)
            timer_screen = self.manager.get_screen('timer')
            timer_screen.setup_timer(task, schedule)
            self.manager.current = 'timer'

    def on_pre_enter(self, *args):
        """Called when screen is about to be shown"""
        self.load_tasks()


class CreateTaskScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(name='create_task', **kwargs)

        # Vertical layout with padding
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        # Title
        title = Label(
            text='Create New Task',
            font_size='24sp',
            size_hint=(1, 0.1),
            bold=True
        )

        # Input fields
        self.task_name = TextInput(
            hint_text='Task Name',
            multiline=False,
            size_hint=(1, 0.1)
        )

        self.task_total_time = TextInput(
            hint_text='Total Time (minutes)',
            multiline=False,
            input_filter='int',
            size_hint=(1, 0.1)
        )
        
        self.task_work_block = TextInput(
            hint_text='Work Block (minutes)',
            multiline=False,
            input_filter='int',
            size_hint=(1, 0.1)
        )

        self.task_break_block = TextInput(
            hint_text='Break Time (seconds, default: 10)',
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
        cancel_btn.bind(on_press=self.go_back)

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
        # Get values from inputs
        name = self.task_name.text
        total_time = int(self.task_total_time.text)
        work_block = int(self.task_work_block.text)
        
        # Use default 10 seconds if break time is empty
        break_time = int(self.task_break_block.text) if self.task_break_block.text else 10

        # Create and save task
        task = Task(name, total_time, work_block, break_time)
        repo = TimerRepository()
        repo.save_timer(task)

        # Go back to home
        self.manager.current = 'home'


class TimerScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(name='timer', **kwargs)

        self.task_name = None
        self.current_block_index = 0

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

        # Progress blocks area - MODERN UI
        self.blocks_container = GridLayout(
            cols=10,
            spacing=8,
            size_hint=(1, 0.5),
            padding=15
        )
        # container background behind the blocks
        with self.blocks_container.canvas.before:
            Color(0.12, 0.12, 0.15, 1)
            self.container_bg =RoundedRectangle(
                pos=self.blocks_container.pos,
                size=self.blocks_container.size,
                radius=[15]
            )
        self.blocks_container.bind(pos=self.update_container_bg, size=self.update_container_bg)
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
            background_color=(0.3, 0.3, 0.3, 1),
            font_size='20sp',
            disabled=True
        )

        self.stop_btn = Button(
            text='Stop',
            background_color=(0.9, 0.2, 0.2, 1),
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

        # Initialize wake lock to prevent Android from killing timer in background

        try:
            from android import mActivity
            from jnius import autoclass
            PowerManager = autoclass('android.os.PowerManager')
            power_manager = mActivity.getSystemService('power')
            self.wake_lock = power_manager.newWakeLock(
                PowerManager.PARTIAL_WAKE_LOCK,
                'SprintRunner::TimerWakeLock'
            )
        except:
            self.wake_lock = None


    def on_start(self, instance):
        """Start or resume the timer countdown"""
        from src.timer import Timer
        from kivy.clock import Clock

        if not hasattr(self, 'timer'):
            # First time starting
            self.timer = Timer(self.schedule)
            self.timer.on_block_complete_callback = self.on_timer_block_complete
            self.timer.start()
            self.current_block_index = 0
            
            # Mark first block as active
            if len(self.blocks) > 0:
                self.mark_block_active(0)
            
            # Cancel existing clock
            if hasattr(self, 'clock_event'):
                self.clock_event.cancel()
            
            # Start clock
            self.clock_event = Clock.schedule_interval(self.update_timer, 1)
            
            # Update buttons
            self.start_btn.disabled = True
            self.pause_btn.disabled = False

            #  Acquire wake lock to keep timer running in background
            if self.wake_lock:
                self.wake_lock.acquire()
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
        
        # Reset buttons
        self.start_btn.disabled = False
        self.pause_btn.disabled = True
        self.pause_btn.text = 'Pause'

        # Release wake lock when timer stops
        if hasattr(self, 'wake_lock') and self.wake_lock:
            try:
                if self.wake_lock.isHeld():
                    self.wake_lock.release()
            except:
                pass
        
        self.manager.current = 'home'

    def update_timer(self, dt):
        """Called every second to update display"""
        if not hasattr(self, 'timer') or not self.timer.is_running or self.timer.is_paused:
            return True
        
        self.timer.tick()
        
        if self.timer.current_block:
            mins = self.timer.remaining_seconds // 60
            secs = self.timer.remaining_seconds % 60
            self.timer_display.text = f"{mins:02d}:{secs:02d}"
        else:
            # Session complete
            print("Session Complete! Returning to Home...")
            self.on_stop(None)
            return False
        
        return self.timer.is_running
    
    def update_container_bg(self, instance, value):
        """Keeps the container background sized correctly"""
        self.container_bg.pos = instance.pos
        self.container_bg.size = instance.size


    def create_progress_blocks(self, num_blocks):
        """Create modern pill-shaped progress blocks"""
        from kivy.graphics import Color, RoundedRectangle

        self.blocks_container.clear_widgets()
        self.blocks = []

        for i in range(num_blocks):
            # Modern thin, stretchable blocks
            block = Label(
                text='',
                size_hint=(1, None),  # Stretch full width
                height=25  # Thin, modern height
            )
            
            with block.canvas.before:
                # Dark Slate Gray for pending blocks
                Color(0.2, 0.2, 0.25, 1)
                # Rounded pill shape
                block.rect = RoundedRectangle(pos=block.pos, size=block.size, radius=[5])            
            # Update when block moves
            block.bind(pos=self.update_rect, size=self.update_rect)
            
            self.blocks.append(block)
            self.blocks_container.add_widget(block)

    def update_rect(self, instance, value):
        """Update rectangle position/size when block moves"""
        instance.rect.pos = instance.pos
        instance.rect.size = instance.size

    def mark_block_active(self, index):
        """Mark block as currently active - Vibrant Mint Green"""
        from kivy.graphics import Color, RoundedRectangle
        
        if index < len(self.blocks):
            block = self.blocks[index]
            block.canvas.before.clear()
            
            with block.canvas.before:
                Color(0.0, 0.85, 0.45, 1)  # Vibrant Mint Green
                block.rect = RoundedRectangle(pos=block.pos, size=block.size, radius=[7])

    def mark_block_complete(self, index):
        """Mark block as completed - Warm Amber/Orange"""
        from kivy.graphics import Color, RoundedRectangle
        
        if index < len(self.blocks):
            block = self.blocks[index]
            block.canvas.before.clear()
            
            with block.canvas.before:
                Color(0.95, 0.6, 0.2, 1)  # Warm Amber/Orange
                block.rect = RoundedRectangle(pos=block.pos, size=block.size, radius=[7])

    def play_alarm(self, alarm_file):
        """Play alarm sound when block ends"""
        try:
            # Android-safe audio playing
            sound = SoundLoader.load(alarm_file)
            if sound:
                sound.play()
                print(f"✓ Playing alarm: {alarm_file}")
            else:
                print(f"✗ Could not load alarm: {alarm_file}")
        except Exception as e:
            print(f"✗ Audio error: {e}")

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

        # Reset buttons
        self.start_btn.disabled = False
        self.pause_btn.disabled = True
        self.pause_btn.text = 'Pause'

        # Create modern progress blocks
        num_blocks = len(schedule.blocks)
        self.create_progress_blocks(num_blocks)

    def on_timer_block_complete(self, alarm_tone):
        """Called by timer when block completes"""
        self.play_alarm(alarm_tone)
        self.mark_block_complete(self.current_block_index)
        self.current_block_index += 1
        if self.current_block_index < len(self.blocks):
            self.mark_block_active(self.current_block_index)



# Delete the Task 
from kivy.clock import Clock

class TaskCard(Button):
    def __init__(self, task_name, delete_callback, **kwargs):
        super().__init__(**kwargs)
        self.task_name = task_name
        self.delete_callback = delete_callback
        self.long_press_event = None

    def on_touch_down(self, touch):
        # If the user touches inside this specific button
        if self.collide_point(*touch.pos):
            # Schedule the delete action to trigger after 1.5 seconds
            self.long_press_event = Clock.schedule_once(self.trigger_delete, 1.5)
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        # If the user lets go before 1.5 seconds, cancel the deletion
        if self.collide_point(*touch.pos):
            if self.long_press_event:
                self.long_press_event.cancel()
        return super().on_touch_up(touch)

    def trigger_delete(self, dt):
        """This runs if they successfully hold for 1.5 seconds"""
        print(f">>> Long press detected! Deleting {self.task_name}...")
        self.delete_callback(self.task_name)