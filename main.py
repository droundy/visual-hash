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
from kivy.animation import Animation
from kivy.uix.settings import Settings
from kivy.uix.boxlayout import BoxLayout
import kivy.uix.settings as kivysettings
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelHeader
from kivy import platform
from kivy.properties import StringProperty, NumericProperty #, ConfigParserProperty
import settings as mysettings

import VisualHash

class Home(TabbedPanel):
    def on_current_tab(self, *args):
        try:
            args[1].content.on_select()
        except:
            pass
    def on_current(self, *args):
        print 'current changed!', args

animtime = 1.0
class Matching(BoxLayout):
    def get_hasher(self):
        # pick the next image to test against, and start working on
        # the hashing.
        kind = app.config.getdefault('game', 'hashtype', 'oops')
        hasher = VisualHash.Flag
        if kind == 'tflag':
            hasher = VisualHash.TFlag
        if kind == 'fractal':
            hasher = VisualHash.OptimizedFractal
        return hasher
    def NextImg(self):
        self.img.frac = 0.1
        self.img.num += 1
    def on_select(self, *args):
        self.left_button.disabled = True
        self.right_button.text = 'I remember this'
        self.original.x = 0
        self.img.x = self.width
        hasher = self.get_hasher()
        self.original.text += '!'
        rnd = VisualHash.StrongRandom(self.original.text)
        NextImage(self.original, 512, rnd, hasher)
        self.Reset()
    def Reset(self):
        if self.original.have_next:
            im = self.original.next[0]
            texture = Texture.create(size=(512, 512))
            texture.blit_buffer(im.tostring(), colorfmt='rgba', bufferfmt='ubyte')
            self.original.texture = texture
        else:
            Clock.schedule_once(lambda dt: self.Reset(), 0.25)
            return
        self.left_button.disabled = True
        self.right_button.text = 'I remember this'
        anim = Animation(x=self.width, duration=animtime)
        anim.start(self.img)
        anim = Animation(x=0, t='in_back', duration=animtime)
        anim.start(self.original)
        #Clock.schedule_once(lambda dt: self.NextImg(), animtime)

        # pick the next image to test against, and start working on
        # the hashing.
        kind = app.config.getdefault('game', 'hashtype', 'oops')
        hasher = self.get_hasher()
        rnd = VisualHash.BitTweakedRandom(self.original.text,0.1, self.img.num,self.img.num)
        self.img.num += 1
        if VisualHash.StrongRandom(self.original.text+'hi'+str(self.img.num)).random() < 0.25:
            rnd = VisualHash.StrongRandom(self.original.text)
        NextImage(self.img, 512, rnd, hasher)
    def Start(self):
        if not self.have_started:
            self.have_started = True
            self.Reset()
        if self.img.have_next:
            im = self.img.next[0]
            texture = Texture.create(size=(512, 512))
            texture.blit_buffer(im.tostring(), colorfmt='rgba', bufferfmt='ubyte')
            self.img.texture = texture
            self.img.have_next = False
        else:
            Clock.schedule_once(lambda dt: self.Start(), 0.25)
            return
        self.left_button.disabled = False
        self.right_button.text = 'Same'
        anim = Animation(x=0, t='in_back', duration=animtime)
        anim.start(self.img)
        anim = Animation(x=-self.width, duration=animtime)
        anim.start(self.original)
    def ItMatches(self):
        self.Reset()
    def ItDiffers(self):
        self.Reset()

class Memory(BoxLayout):
    pass

class NextImage(Thread):
    def __init__(self, whosenext, size, rnd, hasher):
        super(NextImage, self).__init__()
        self.size = size
        self.rnd = rnd
        self.next = whosenext
        self.next.have_next = False
        self.hasher = hasher
        self.start()
    def run(self):
        sz = self.size
        im = self.hasher(self.rnd, sz)
        texture = Texture.create(size=(sz, sz))
        texture.blit_buffer(im.tostring(), colorfmt='rgba', bufferfmt='ubyte')
        self.next.next = [im]
        self.next.have_next = True

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
            rnd = VisualHash.BitTweakedRandom(self.text,self.frac, self.num,self.num)
            if VisualHash.StrongRandom(self.text+'hi'+str(self.num)).random() < 0.25:
                rnd = VisualHash.StrongRandom(self.text)
            im = self.hasher(rnd, sz)
            print (self.text, self.frac, self.num, sz)
            self.q.put((sz, im.tostring()))
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
            sz, im = self.q.get(False)
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
        self.q = Queue()
        kind = app.config.getdefault('game', 'hashtype', 'oops')
        hasher = VisualHash.Flag
        if kind == 'tflag':
            hasher = VisualHash.TFlag
        if kind == 'fractal':
            hasher = VisualHash.OptimizedFractal
        ImageUpdater(self.text, hasher, self.q, self.stop, 64, 512, self.frac, self.num)

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
