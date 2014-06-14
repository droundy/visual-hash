#!/usr/bin/python2

# from kivy.config import Config
# Config.set('graphics', 'width', '1000')
# Config.write()

__version__ = '0.0.0'

import os, sys, inspect

from kivy.metrics import sp
from kivy.app import App
from kivy.graphics.texture import Texture
from kivy.uix.image import Image
from kivy.uix.settings import Settings
from kivy.uix.boxlayout import BoxLayout
import kivy.uix.settings as kivysettings
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelHeader
from kivy import platform
from kivy.properties import StringProperty #, ConfigParserProperty
import settings as mysettings

import VisualHash

class Home(TabbedPanel):
    pass

class Matching(BoxLayout):
    pass

class Memory(BoxLayout):
    pass

class NiceImage(Image):
    text = StringProperty('hi')
    # kind = ConfigParserProperty('', 'game', 'hashtype', 'example')
    def __init__(self, **kw):
        super(NiceImage, self).__init__(**kw)
        self.on_text()
    def on_text(self, *args):
        sz = 64
        kind = app.config.getdefault('game', 'hashtype', 'oops')
        hasher = VisualHash.Flag
        if kind == 'tflag':
            hasher = VisualHash.TFlag
        if kind == 'fractal':
            hasher = VisualHash.OldFractal
        im = hasher(VisualHash.StrongRandom(self.text), sz)
        texture = Texture.create(size=(sz, sz))
        texture.blit_buffer(im.tostring(), colorfmt='rgba', bufferfmt='ubyte')
        self.texture = texture

class MainApp(App):
    def build_config(self, config):
        config.setdefaults('game', mysettings.defaults)
    def build_settings(self, settings):
        settings.add_json_panel('Fractal Memory',
            self.config, data=mysettings.json)
    def get_application_config(self):
        if platform == 'android':
            return super(MainApp, self).get_application_config()
        return super(MainApp, self).get_application_config('~/.%(appname)s.ini')
    def build(self):
        self.config.read(self.get_application_config())
        h = Home()
        th = TabbedPanelHeader(text='Settings')
        h.add_widget(th)
        sett = Settings()
        th.content = sett.create_json_panel('Fractal Entropy',
                                            self.config,
                                            data=mysettings.json)
        return h
    def on_stop(self):
        print "I am stopping!!!"
        self.config.write()
    def on_pause(self):
        print "I am pausing!!!"
        self.config.write()
        return True
    def on_resume(self):
        print "I am resuming!!!"
        return True

if __name__ == '__main__':
    os.umask(077)
    app = MainApp()
    app.run()
