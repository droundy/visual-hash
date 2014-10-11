#!/usr/bin/python2

# from kivy.config import Config
# Config.set('graphics', 'width', '1000')
# Config.write()

__version__ = '0.0.0'

# import cProfile

import os, sys, inspect
from threading import Thread
from Queue import Queue

from kivy.clock import Clock
from kivy.metrics import sp
from kivy.app import App
from kivy.graphics.texture import Texture
from kivy.animation import Animation
from kivy.uix.settings import Settings
from kivy.uix.boxlayout import BoxLayout
import kivy.uix.settings as kivysettings
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelHeader
from kivy import platform
from kivy.properties import StringProperty, NumericProperty #, ConfigParserProperty
import settings as mysettings

try:
    import pyximport; pyximport.install()
except:
    print '****** There does not seem to be cython available!!! *******'

try:
    import VisualHashPrivate.bayes as bayes
except:
    print 'no bayes!'

import math

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

class BinaryEntropyEstimator(object):#dont keep design(probably)
    def __init__(self):
        self.bits = Estimator(0, 128, 0.1)
        self.choices = []
    def choose_bits_frac(self, maxentropy=128):
        if SystemRandom().random() < 0.25:
            frac = 0
            self.choices.append(0)
        else:
            nbits = self.estimate_entropy()
            self.choices.append(nbits)
            frac = 1 - 0.5**(1.0/nbits)
            print 'nbits', nbits, 'frac', frac
        return frac
    def estimate_entropy(self):
         return self.bits.median()
    def reset_entropy_estimate(self):
        self.__init__()
    def measured(self, differs):
        print 'found', differs, 'at', self.choices[0]
        self.bits.measured(self.choices[0], differs)
        self.choices = self.choices[1:]

class BayesEntropyEstimator(object):#dont keep design(probably)
    def __init__(self):
        self.P = bayes.model(30, 30, 0.1)
        self.fs = [0.0, 1.0]
        self.results = [1.0, 0.0]
        self.nextf = 0.5
        self.Puptodate = False
    def _update_P(self):
        if not self.Puptodate:
            self.P = bayes.findBestHNA(self.fs, self.results)
            self.Puptodate = True
    def choose_bits_frac(self, maxentropy=128):
        print 'fs', self.fs
        print 'results', self.results
        self._update_P()
        self.nextf = bayes.pickNextF(self.P)
        return self.nextf
    def estimate_entropy(self):
        self._update_P()
        print self.P
        return self.P.H
    def reset_entropy_estimate(self):
        self.__init__()
    def measured(self, differs):
        self.fs.append(self.nextf)
        if differs:
            self.results.append(0.0)
        else:
            self.results.append(1.0)
        self.Puptodate = False
        print 'found', differs, 'at', self.nextf

image_size = 512

class Matching(BoxLayout):
    e = BayesEntropyEstimator()
    differs = False
    next_differs = False
    next_frac = 0
    def begin_next_img(self):
        # pick the next image to test against, and start working on
        # the hashing.
        hasher = get_hasher()
        frac = self.e.choose_bits_frac()
        self.img.num += 1
        self.rnd.reset()
        if frac != 0:
            # The following could either use TweakedRandom or
            # BitTweaked random.  Either should work, and will give
            # different statistical behavior (which could be handy).
            self.rnd = VisualHash.BitTweakedRandom(self.rnd, frac, self.img.num, self.img.num)
        NextImage(self.img, image_size, self.rnd, hasher)
    def on_select(self, *args):
        self.img.current_im = ''
        self.rnd = VisualHash.StrongRandom(self.img.text)
        self.e = BayesEntropyEstimator()
        self.left_button.disabled = True
        self.right_button.text = 'I remember this'
        self.img.x = self.width
        hasher = get_hasher()
        self.img.text = '%08d' % SystemRandom().randrange(0, 10**8)
        self.rnd = VisualHash.StrongRandom(self.img.text)
        NextImage(self.img, image_size, self.rnd, hasher)
        self.begin_next_img()
        anim = Animation(x=self.width, t='in_back', duration=animtime)
        anim.start(self.img)
        Clock.schedule_once(lambda dt: self.Reset(), animtime)
    def Reset(self):
        if self.img.have_next:
            self.entropy_label.text = 'Entropy:  %.1f' % self.e.estimate_entropy()
            print 'Reset working'
            self.differs = self.next_differs
            im = self.img.next[0]
            self.img.old_im = self.img.current_im
            self.img.current_im = im.tostring()
            texture = Texture.create(size=im.size)
            texture.blit_buffer(im.tostring(), colorfmt='rgba', bufferfmt='ubyte')
            texture.flip_vertical()
            self.img.texture = texture
            self.right_button.disabled = False
        else:
            print 'Reset pending'
            self.left_button.disabled = True
            self.right_button.disabled = True
            Clock.schedule_once(lambda dt: self.Reset(), 0.25)
            return
        anim = Animation(x=0, t='in_back', duration=animtime)
        anim.start(self.img)
    def Begin(self):
        anim = Animation(x=self.width, duration=animtime)
        anim.start(self.img)
        Clock.schedule_once(lambda dt: self.Start(), animtime)
    def Start(self):
        self.right_button.text = 'Same'
        if self.img.have_next:
            self.entropy_label.text = 'Entropy:  %.1f  f %g' % (self.e.estimate_entropy(), self.e.choose_bits_frac())
            self.differs = self.next_differs
            print 'Start working'
            im = self.img.next[0]
            self.img.old_im = self.img.current_im
            self.img.current_im = im.tostring()
            texture = Texture.create(size=im.size)
            texture.blit_buffer(im.tostring(), colorfmt='rgba', bufferfmt='ubyte')
            texture.flip_vertical()
            self.img.texture = texture
            self.begin_next_img()
        else:
            print 'Start pending'
            self.left_button.disabled = True
            self.right_button.disabled = True
            Clock.schedule_once(lambda dt: self.Start(), 0.25)
            return
        anim = Animation(x=0, duration=animtime)
        anim.start(self.img)
        self.left_button.disabled = False
        self.right_button.disabled = False
    def ItMatches(self):
        print 'same:', self.img.current_im != self.img.old_im
        self.e.measured(False)
        anim = Animation(x=self.width, duration=animtime)
        anim.start(self.img)
        Clock.schedule_once(lambda dt: self.Start(), animtime)
    def ItDiffers(self):
        print 'differs:', self.img.current_im != self.img.old_im
        self.e.measured(True)
        anim = Animation(x=-self.width, duration=animtime)
        anim.start(self.img)
        Clock.schedule_once(lambda dt: self.Start(), animtime)

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
    if kind == 'hex32':
        hasher = VisualHash.MakeHex(32//4)
    if kind == 'hex64':
        hasher = VisualHash.MakeHex(64//4)
    if kind == 'hex128':
        hasher = VisualHash.MakeHex(128//4)
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
        print 'nbits', nbits
        frac = 1 - 0.5**(1.0/nbits)
        print 'nbits', nbits, 'frac', frac
        rnd = VisualHash.BitTweakedRandom(self.original.text,frac, self.img.num,self.img.num)
        self.next_differs = True
        self.img.num += 1
        if VisualHash.StrongRandom(self.original.text+'hi'+str(self.img.num)).random() < 0.25:
            self.next_differs = False
            rnd = VisualHash.StrongRandom(self.original.text)
        NextImage(self.img, image_size, rnd, hasher)
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
        NextImage(self.original, image_size, rnd, hasher)
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
            texture.flip_vertical()
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
            texture.flip_vertical()
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
            texture.flip_vertical()
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
        print 'working on image'
        sz = self.size
        im = self.hasher(self.rnd, sz)
        # I don't know why, but the following three lines cause this to crash on MacOS!
        #texture = Texture.create(size=im.size)
        #print 'texture is', texture
        #texture.blit_buffer(im.tostring(), colorfmt='rgba', bufferfmt='ubyte')
        #texture.flip_vertical()
        print 'done with image'
        self.next.next = [im]
        self.next.have_next = True


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
    # cProfile.run('app.run()', 'visual.profile')
    app.run()
