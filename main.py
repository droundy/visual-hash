#!/usr/bin/python2

# from kivy.config import Config
# Config.set('graphics', 'width', '1000')
# Config.write()

__version__ = '0.0.0'

import os, sys, inspect
from threading import Thread
from Queue import Queue

from kivy.clock import Clock
from kivy.metrics import sp
from kivy.app import App
from kivy.graphics.texture import Texture
from kivy.uix.image import Image
from kivy.uix.settings import Settings
from kivy.uix.boxlayout import BoxLayout
import kivy.uix.settings as kivysettings
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelHeader
from kivy import platform
from kivy.properties import StringProperty, NumericProperty #, ConfigParserProperty
import settings as mysettings

import VisualHash

class Home(TabbedPanel):
    pass

class Matching(BoxLayout):
    def Start(self):
        print 'Start'
        self.left_button.disabled = False
        self.right_button.text = 'Same'
        self.img.frac = 0.1
        self.img.num += 1
    def ItMatches(self):
        print 'Matches'
        self.left_button.disabled = False
        self.img.num += 1
    def ItDiffers(self):
        print 'Differs'
        self.left_button.disabled = False
        self.img.num += 1

class Memory(BoxLayout):
    pass

class ImageUpdater(Thread):
    def __init__(self, text, hasher, q, stop, minsize, maxsize, frac=0.0, num=1):
        super(ImageUpdater, self).__init__()
        self.text = text
        self.minsize = minsize
        self.maxsize = maxsize
        self.size = minsize
        self.hasher = hasher
        self.q = q
        self.stop = stop
        self.frac = frac
        self.num = num
        self.start()
    def run(self):
        sz = self.minsize
        while sz <= self.maxsize:
            try:
                self.stop.get(False)
                return
            except:
                pass # we have not been asked to stop, yet!
            print 'running', self.text, 'with sz', sz
            im = self.hasher(VisualHash.TweakedRandom(self.text,self.frac,
                                                      self.num,self.num), sz)
            texture = Texture.create(size=(sz, sz))
            texture.blit_buffer(im.tostring(), colorfmt='rgba', bufferfmt='ubyte')
            print (self.text, sz)
            self.q.put((self.text, self.frac, self.num, sz, im.tostring()))
            sz *= 2

class NiceImage(Image):
    text = StringProperty('hi')
    num = NumericProperty(0)
    frac = NumericProperty(0)
    # kind = ConfigParserProperty('', 'game', 'hashtype', 'example')
    def __init__(self, **kw):
        super(NiceImage, self).__init__(**kw)
        self.q = Queue()
        self.stop = Queue()
        self.on_text()
        Clock.schedule_interval(self.read_q, 0.25)
    def read_q(self, dt):
        try:
            #print 'trying with', self.text, self.frac, self.num
            t, frac, num, sz, im = self.q.get(False)
            while t != self.text and frac != self.frac and num != self.num:
                t, frac, num, sz, im = self.q.get(False)
            print 'read', (t, frac, num, sz)
            texture = Texture.create(size=(sz, sz))
            texture.blit_buffer(im, colorfmt='rgba', bufferfmt='ubyte')
            self.texture = texture
        except:
            pass
    def on_num(self, *args):
        self.on_text()
    def on_frac(self, *args):
        self.on_text()
    def on_text(self, *args):
        self.stop.put('stop!')
        self.stop = Queue()
        kind = app.config.getdefault('game', 'hashtype', 'oops')
        hasher = VisualHash.Flag
        if kind == 'tflag':
            hasher = VisualHash.TFlag
        if kind == 'fractal':
            hasher = VisualHash.OptimizedFractal
        ImageUpdater(self.text, hasher, self.q, self.stop, 32, 1024, self.frac, self.num)
        self.q.get()

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
