"""
Scrble - Main Application Entry Point
Run this file to launch the game: python main.py
"""
import os
os.environ.setdefault('KIVY_NO_ENV_CONFIG', '1')

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.core.window import Window
from kivy.config import Config

# Mobile-friendly window settings
Config.set('graphics', 'resizable', '1')
Config.set('kivy', 'keyboard_mode', 'systemanddock')

# Set a mobile-like window size for desktop testing
Window.size = (390, 844)  # iPhone 14-ish proportions

from screens.home_screen import HomeScreen
from screens.game_screen import GameScreen


class ScrbleApp(App):
    title = 'Scrble'

    def build(self):
        sm = ScreenManager(transition=FadeTransition(duration=0.25))
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(GameScreen(name='game'))
        return sm


if __name__ == '__main__':
    ScrbleApp().run()
