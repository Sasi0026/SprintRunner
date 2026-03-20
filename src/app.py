from kivy.app import App
from kivy.uix.boxlayout import BoxLayout # [boxlayout - module] and [BoxLayout - class]
from kivy.uix.label import Label
from kivy.uix.button import Button

from kivy.uix.screenmanager import ScreenManager
from src.ui.screens import HomeScreen
from src.ui.screens import HomeScreen, CreateTaskScreen, TimerScreen # Add CreateTaskScreen
from src.ui.screens import TimerScreen

class SprintRunnerApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(HomeScreen())
        sm.add_widget(CreateTaskScreen())
        sm.add_widget(TimerScreen())

        return sm
    
    def on_pause(self):
        """Allow app to run in background"""
        return True
    
    def on_resume(self):
        """App resumed from background"""
        pass
    
    


if __name__ == '__main__':
    SprintRunnerApp().run()