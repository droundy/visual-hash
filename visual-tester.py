from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition



# Create both screens. Please note the root.manager.current: this is how
# you can control the ScreenManager from kv. Each screen has by default a
# property manager that gives you the instance of the ScreenManager used.
Builder.load_string("""
<MenuScreen>:
    BoxLayout:
        orientation: 'vertical'
        Button:
            size_hint_x: 0.5
            pos_hint: {'center_x': 0.5}
            text: 'Go to Memory Games'
            on_press: root.manager.current = 'memory'
        Button:
            size_hint_x: 0.5
            pos_hint: {'center_x': 0.5}
            text: 'Quit'
        Button:
            size_hint_x: 0.5
            pos_hint: {'center_x': 0.5}
            text: 'Go to Options'
            on_press: root.manager.current = 'options'

<MemoryScreen>:
    BoxLayout:
        orientation: 'vertical'
        Button:
            text: 'Game 1'
            size_hint_x: 0.25
            pos_hint: {'center_x': 0.5}
        Button:
            text: 'Game 2'
            size_hint_x: 0.25
            pos_hint: {'center_x': 0.5}
        Button:
            orientation: 'vertical'
            size_hint_x: 0.25
            pos_hint: {'center_x': 0.5}
            text: 'Back to menu'
            on_press: root.manager.current = 'menu'
<OptionsScreen>:
    BoxLayout:
        orientation: 'vertical'
        Button:
            orientation: 'vertical'
            size_hint_x: 0.25
            pos_hint: {'center_x': 0.5}
            text: 'Option #1'
        Button:
            text: 'Back to menu'
            on_press: root.manager.current = 'menu'
""")

# Declare both screens
class MenuScreen(Screen):
    pass

class MemoryScreen(Screen):
    pass
class OptionsScreen(Screen):
    pass
# Create the screen manager
sm = ScreenManager(transition=NoTransition())
sm.add_widget(MenuScreen(name='menu'))
sm.add_widget(MemoryScreen(name='memory'))
sm.add_widget(OptionsScreen(name='options'))

class TestApp(App):

    def build(self):
        return sm

if __name__ == '__main__':
    TestApp().run()
