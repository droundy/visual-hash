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

from statistics.PBA import Estimator

from random import SystemRandom

import VisualHash

class Home(TabbedPanel):
    def on_current_tab(self, *args):
        try:
            args[1].content.on_select
        except:
            return
        args[1].content.on_select()
    def on_current(self, *args):
        print 'current changed!', args

animtime = 1.0

class Matching(BoxLayout):
    bits = Estimator(0, 128, 0.1)
    differs = False
    next_differs = False
    def begin_next_img(self):
        # pick the next image to test against, and start working on
        # the hashing.
        hasher = get_hasher()
        nbits = self.bits.median()
        frac = 1 - 0.5**(1.0/nbits)
        print 'nbits', nbits, 'frac', frac
        rnd = VisualHash.BitTweakedRandom(self.img.text,frac, self.img.num,self.img.num)
        self.next_differs = True
        self.img.num += 1
        if VisualHash.StrongRandom(self.img.text+'hi'+str(self.img.num)).random() < 0.25:
            self.next_differs = False
            rnd = VisualHash.StrongRandom(self.img.text)
        NextImage(self.img, 512, rnd, hasher)
    def on_select(self, *args):
        self.bits = Estimator(0, 128, 0.1)
        self.left_button.disabled = True
        self.right_button.text = 'I remember this'
        self.img.x = self.width
        hasher = get_hasher()
        self.img.text += '!'
        rnd = VisualHash.StrongRandom(self.img.text)
        NextImage(self.img, 512, rnd, hasher)
        self.begin_next_img()
        self.Reset()
    def Reset(self):
        self.entropy_label.text = 'Entropy:  %.1f' % self.bits.median()
        if self.img.have_next:
            self.differs = self.next_differs
            im = self.img.next[0]
            self.img.current_im = im.tostring()
            texture = Texture.create(size=im.size)
            texture.blit_buffer(im.tostring(), colorfmt='rgba', bufferfmt='ubyte')
            self.img.texture = texture
        else:
            Clock.schedule_once(lambda dt: self.Reset(), 0.25)
            return
        self.left_button.disabled = True
        self.right_button.text = 'I remember this'
        anim = Animation(x=self.width, duration=animtime)
        anim.start(self.img)
        anim = Animation(x=0, t='in_back', duration=animtime)
        anim.start(self.img)
    def Start(self):
        if self.img.have_next:
            im = self.img.next[0]
            self.img.current_im = im.tostring()
            texture = Texture.create(size=im.size)
            texture.blit_buffer(im.tostring(), colorfmt='rgba', bufferfmt='ubyte')
            self.img.texture = texture
            self.begin_next_img()
        else:
            Clock.schedule_once(lambda dt: self.Start(), 0.25)
            return
        self.left_button.disabled = False
        self.right_button.text = 'Same'
        anim = Animation(x=0, t='in_back', duration=animtime)
        anim.start(self.img)
        anim = Animation(x=-self.width, duration=animtime)
        anim.start(self.img)
    def ItMatches(self):
        print 'same:', self.differs, self.img.current_im != self.img.current_im
        if self.differs:
            self.bits.measured(self.bits.median(), False)
            print 'new bits:', self.bits.median()
        else:
            print 'Nice!'
        self.Reset()
    def ItDiffers(self):
        print 'differs:', self.differs, self.img.current_im != self.img.current_im
        if self.differs:
            self.bits.measured(self.bits.median(), True)
            print 'new bits:', self.bits.median()
        else:
            print 'Oops!'
        self.Reset()

def get_hasher():
    # pick the next image to test against, and start working on
    # the hashing.
    kind = app.config.getdefault('game', 'hashtype', 'oops')
    hasher = VisualHash.Flag
    if kind == 'tflag':
        hasher = VisualHash.TFlag
    if kind == 'fractal':
        hasher = VisualHash.OptimizedFractal
    if kind == 'identicon':
        hasher = VisualHash.Identicon
    if kind == 'randomart':
        hasher = VisualHash.RandomArt
    return hasher

class Memory(BoxLayout):
    bits = Estimator(0, 128, 0.1)
    differs = False
    next_differs = False
    def begin_next_img(self):
        # pick the next image to test against, and start working on
        # the hashing.
        hasher = get_hasher()
        nbits = self.bits.median()
        frac = 1 - 0.5**(1.0/nbits)
        print 'nbits', nbits, 'frac', frac
        rnd = VisualHash.BitTweakedRandom(self.original.text,frac, self.img.num,self.img.num)
        self.next_differs = True
        self.img.num += 1
        if VisualHash.StrongRandom(self.original.text+'hi'+str(self.img.num)).random() < 0.25:
            self.next_differs = False
            rnd = VisualHash.StrongRandom(self.original.text)
        NextImage(self.img, 512, rnd, hasher)
    def on_select(self, *args):
        self.bits = Estimator(0, 128, 0.1)
        self.left_button.disabled = True
        self.right_button.text = 'I remember this'
        self.original.x = 0
        self.img.x = self.width
        hasher = get_hasher()
        self.original.text = '%08d' % SystemRandom().randrange(0, 10**8)
        rnd = VisualHash.StrongRandom(self.original.text)
        self.img.x = self.width
        NextImage(self.original, 512, rnd, hasher)
        self.img.x = self.width
        self.begin_next_img()
        self.img.x = self.width
        self.Reset()
    def Reset(self):
        self.entropy_label.text = 'Entropy:  %.1f' % self.bits.median()
        if self.original.have_next:
            self.differs = self.next_differs
            im = self.original.next[0]
            self.original.current_im = im.tostring()
            texture = Texture.create(size=im.size)
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
    def Start(self):
        if self.img.have_next:
            im = self.img.next[0]
            self.img.current_im = im.tostring()
            texture = Texture.create(size=im.size)
            texture.blit_buffer(im.tostring(), colorfmt='rgba', bufferfmt='ubyte')
            self.img.texture = texture
            self.begin_next_img()
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
        print 'same:', self.differs, self.img.current_im != self.original.current_im
        if self.differs:
            self.bits.measured(self.bits.median(), False)
            print 'new bits:', self.bits.median()
        else:
            print 'Nice!'
        self.Reset()
    def ItDiffers(self):
        print 'differs:', self.differs, self.img.current_im != self.original.current_im
        if self.differs:
            self.bits.measured(self.bits.median(), True)
            print 'new bits:', self.bits.median()
        else:
            print 'Oops!'
        self.Reset()

class TextHash(BoxLayout):
    def on_select(self, *args):
        self.on_text() # for the very first time
    def update_image(self):
        if self.thehash.have_next:
            im = self.thehash.next[0]
            texture = Texture.create(size=im.size)
            texture.blit_buffer(im.tostring(), colorfmt='rgba', bufferfmt='ubyte')
            self.thehash.texture = texture
        else:
            Clock.schedule_once(lambda dt: self.update_image(), 0.5)
            return
    def on_text(self, *args):
        rnd = VisualHash.StrongRandom(self.text)
        hasher = get_hasher()
        NextImage(self.thehash, 256, rnd, hasher)
        Clock.schedule_once(lambda dt: self.update_image(), 0.5)

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
        texture = Texture.create(size=im.size)
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
