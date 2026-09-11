from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
import threading
from agent import UltimateAutonomousAgent

class CyberTerminalApp(App):
    def build(self):
        self.title = "Autonomous Network Suite"
        root = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.status_lbl = Label(text="[STATUS]: 100% READY", size_hint=(1, 0.1), color=(0, 1, 0.5, 1))
        root.add_widget(self.status_lbl)
        self.console = TextInput(text="[INIT] Verified Cyber-Terminal Loaded.\n", readonly=True, background_color=(0.04, 0.04, 0.04, 1), foreground_color=(0, 1, 0.3, 1))
        root.add_widget(self.console)
        btn = Button(text="Run Autonomous Suite", size_hint=(1, 0.15), background_color=(0.1, 0.4, 0.8, 1))
        btn.bind(on_press=lambda x: threading.Thread(target=UltimateAutonomousAgent().run_full_suite, daemon=True).start())
        root.add_widget(btn)
        return root

if __name__ == '__main__':
    CyberTerminalApp().run()
