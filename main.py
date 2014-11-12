#!/usr/bin/python2

# from kivy.config import Config
# Config.set('graphics', 'width', '1000')
# Config.write()

__version__ = '0.0.0'

# import cProfile

import os, sys, inspect
from threading import Thread
from Queue import Queue

from kivy.core.window import Window
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

import perceptual

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

class BayesUpdate(Thread):
    def __init__(self, estimator):
        super(BayesUpdate, self).__init__()
        self.e = estimator
        self.start()
    def run(self):
        if self.e.Puptodate:
            #print 'skipping because all is up to date'
            return
        if self.e.Pworking:
            #print 'skipping because already working on findBestHNA'
            return
        self.e.Puptodate = True
        self.e.Pworking = True
        #print 'starting findBestHNA'
        self.e.P = bayes.findBestHNA(self.e.fs, self.e.results)
        self.e.Pworking = False
        #print 'done with findBestHNA'

class BayesEntropyEstimator(object):
    def __init__(self):
        self.P = bayes.model(30, 30, 0.1)
        self.fs = [0.0, 1.0]
        self.results = [1.0, 0.0]
        self.nextf = 0.5
        self.Puptodate = False
        self.Pworking = False
    def _update_P(self):
        BayesUpdate(self)
    def choose_bits_frac(self, maxentropy=128):
        #print 'fs', self.fs
        #print 'results', self.results
        self._update_P()
        self.nextf = bayes.pickNextF(self.P)
        return self.nextf
    def estimate_entropy(self):
        self._update_P()
        print self.P
        return self.P.H
    def reset_entropy_estimate(self):
        self.__init__()
    def measured(self, f, differs):
        self.fs.append(f)
        if differs:
            self.results.append(0.0)
        else:
            self.results.append(1.0)
        self.Puptodate = False
        print 'found', differs, 'at', f

image_size = 400

def pickFrac(H, N, A):
    P = bayes.model(H, N, A)
    return bayes.pickNextF(P)

class Matching(BoxLayout):
    e = BayesEntropyEstimator()
    differs = False
    next_differs = False
    def __init__(self, **kwargs):
        super(Matching, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(
            self._keyboard_closed, self, 'text')
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
    def _keyboard_closed(self):
        print('My keyboard have been closed!')
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None
    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'left':
            self.ItDiffers()
        elif keycode[1] == 'right':
            self.ItMatches()
        elif keycode[1] == 'escape':
            keyboard.release()
            return False # exit the game!
        else:
            print 'keycode', keycode, 'unrecognized'
        # Return True to accept the key. Otherwise, it will be used by
        # the system.
        return True
    def begin_next_img(self):
        # pick the next image to test against, and start working on
        # the hashing.
        hasher, = get_hasher()
        print 'finding frac in matching'
        #frac = self.e.choose_bits_frac()
        frac = pickFrac(100, 100, 0.005)
        self.img.num += 1
        self.rnd.reset()
        #print 'working on image with frac', frac
        if frac != 0:
            # The following could either use TweakedRandom or
            # BitTweaked random.  Either should work, and will give
            # different statistical behavior (which could be handy).
            self.rnd = VisualHash.BitTweakedRandom(self.rnd, frac, self.img.num, self.img.num)
        NextImage(self.img, image_size, lambda: self.rnd, hasher)
    def on_select(self, *args):
        self.img.thisf = 1 # meaningless value so it is defined
        self.img.current_im = ''
        self.rnd = VisualHash.StrongRandom(self.img.text)
        self.e = BayesEntropyEstimator()
        self.left_button.disabled = True
        self.right_button.text = 'I remember this'
        self.img.x = self.width
        hasher, = get_hasher()
        self.img.text = '%08d' % SystemRandom().randrange(0, 10**8)
        self.rnd = VisualHash.StrongRandom(self.img.text)
        self.begin_next_img()
        anim = Animation(x=1.1*self.width, t='in_back', duration=animtime)
        anim.start(self.img)
        Clock.schedule_once(lambda dt: self.Reset(), animtime)
    def Reset(self):
        if self.img.have_next:
            self.entropy_label.text = 'Entropy:  %.1f' % self.e.estimate_entropy()
            #print 'Reset working'
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
            #print 'Reset pending'
            self.left_button.disabled = True
            self.right_button.disabled = True
            Clock.schedule_once(lambda dt: self.Reset(), 0.25)
            return
        anim = Animation(x=0, t='out_back', duration=animtime)
        anim.start(self.img)
    def Begin(self):
        anim = Animation(x=1.1*self.width, duration=animtime)
        anim.start(self.img)
        Clock.schedule_once(lambda dt: self.Start(), animtime)
    def Start(self):
        self.right_button.text = 'Same'
        if self.img.have_next:
            self.differs = self.next_differs
            #print 'Start working'
            im = self.img.next[0]
            self.img.old_im = self.img.current_im
            self.img.current_im = im.tostring()
            assert(not (self.e.nextf == 0 and self.img.current_im != self.img.old_im))
            texture = Texture.create(size=im.size)
            texture.blit_buffer(im.tostring(), colorfmt='rgba', bufferfmt='ubyte')
            texture.flip_vertical()
            self.img.texture = texture
            self.img.thisf = self.e.nextf
            self.begin_next_img()
            self.entropy_label.text = 'Entropy:  %.1f  f %g' % (self.e.estimate_entropy(), self.img.thisf)
        else:
            #print 'Start pending'
            self.left_button.disabled = True
            self.right_button.disabled = True
            Clock.schedule_once(lambda dt: self.Start(), 0.25)
            return
        anim = Animation(x=0, t='out_back', duration=animtime)
        anim.start(self.img)
        self.left_button.disabled = False
        self.right_button.disabled = False
    def ItMatches(self):
        assert(not (self.img.thisf == 0 and self.img.current_im != self.img.old_im))
        if self.img.current_im == self.img.old_im:
            print 'you are correct, it is same', self.img.thisf
        else:
            print 'you are wrong!!! it differs!', self.img.thisf
        self.e.measured(self.img.thisf, False)
        anim = Animation(x=1.1*self.width, duration=animtime)
        anim.start(self.img)
        Clock.schedule_once(lambda dt: self.Start(), animtime)
    def ItDiffers(self):
        assert(not (self.img.thisf == 0 and self.img.current_im != self.img.old_im))
        if self.img.current_im != self.img.old_im:
            print 'you are correct, it differs', self.img.thisf
        else:
            print 'you are wrong!!! it was same', self.img.thisf
        self.e.measured(self.img.thisf, True)
        anim = Animation(x=-1.1*self.width, duration=animtime)
        anim.start(self.img)
        Clock.schedule_once(lambda dt: self.Start(), animtime)


class Pairs(BoxLayout):
    e = BayesEntropyEstimator()
    angle1 = NumericProperty(0)
    angle2 = NumericProperty(0)
    differs = False
    next_differs = False
    def __init__(self, **kwargs):
        super(Pairs, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(
            self._keyboard_closed, self, 'text')
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self.datafile = open('pairs.csv', 'a')
        self.newkind = 'nothing'
    def _keyboard_closed(self):
        print('My keyboard have been closed!')
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None
    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'left':
            self.ItDiffers()
        elif keycode[1] == 'right':
            self.ItMatches()
        elif keycode[1] == 'escape':
            keyboard.release()
            return False # exit the game!
        else:
            print 'keycode', keycode, 'unrecognized'
        # Return True to accept the key. Otherwise, it will be used by
        # the system.
        return True
    def begin_next_img(self):
        # pick the next image to test against, and start working on
        # the hashing.
        self.kind = self.newkind
        hasher, self.newkind = get_hasher()
        self.img.num += 1
        self.rnd.reset()
        self.rnd = VisualHash.StrongRandom(self.img.text + str(self.img.num))
        def get_rnd2():
            frac = self.e.choose_bits_frac()
            #print 'working on image with frac', frac
            if frac != 0:
                # The following could either use TweakedRandom or
                # BitTweaked random.  Either should work, and will give
                # different statistical behavior (which could be handy).
                return VisualHash.BitTweakedRandom(VisualHash.StrongRandom(self.img.text + str(self.img.num)),
                                                        frac,
                                                        self.img.num+1,
                                                        self.img.num+1)
            else:
                return VisualHash.StrongRandom(self.img.text + str(self.img.num))
        NextImage(self.img, 200, lambda: self.rnd, hasher)
        NextImage(self.img2, 200, get_rnd2, hasher)
    def anim_in(self):
        wiggle = int((self.img.width - self.img.height)/2)
        #print 'wiggle', wiggle, 'versus', self.width
        anim = Animation(x=SystemRandom().randrange(-wiggle,wiggle),
                         t='out_back', duration=animtime)
        anim.start(self.img)
        anim = Animation(x=SystemRandom().randrange(-wiggle,wiggle),
                         t='out_back', duration=animtime)
        anim.start(self.img2)
    def anim_out(self):
        anim = Animation(x=1.1*self.width, duration=animtime)
        anim.start(self.img)
        anim = Animation(x=-1.1*self.width, duration=animtime)
        anim.start(self.img2)
        self.left_button.disabled = True
        self.right_button.disabled = True
    def on_select(self, *args):
        self.img.current_im = ''
        self.img2.current_im = ''
        self.rnd = VisualHash.StrongRandom(self.img.text)
        self.e = BayesEntropyEstimator()
        self.img.x = self.width
        self.img2.x = -self.width
        self.img.text = '%08d' % SystemRandom().randrange(0, 10**8)
        self.rnd = VisualHash.StrongRandom(self.img.text)
        self.rnd2 = VisualHash.StrongRandom(self.img.text)
        self.begin_next_img()
        self.anim_out()
        Clock.schedule_once(lambda dt: self.Start(), animtime)
    def Start(self):
        if self.img.have_next and self.img2.have_next:
            self.differs = self.next_differs
            #print 'Start working'
            im = self.img.next[0]
            self.img.current_im = im.tostring()
            texture = Texture.create(size=im.size)
            texture.blit_buffer(im.tostring(), colorfmt='rgba', bufferfmt='ubyte')
            texture.flip_vertical()
            self.img.texture = texture
            self.img.image = im

            im = self.img2.next[0]
            self.img2.current_im = im.tostring()
            texture = Texture.create(size=im.size)
            texture.blit_buffer(im.tostring(), colorfmt='rgba', bufferfmt='ubyte')
            texture.flip_vertical()
            self.img2.texture = texture
            self.img2.image = im

            self.img.thisf = self.e.nextf
            self.begin_next_img()
            self.entropy_label.text = 'Entropy:  %.1f' % (self.e.estimate_entropy())
        else:
            #print 'Start pending'
            Clock.schedule_once(lambda dt: self.Start(), 0.25)
            return
        self.angle1 = SystemRandom().random()*60 - 30
        self.angle2 = SystemRandom().random()*60 - 30
        self.anim_in()
        self.left_button.disabled = False
        self.right_button.disabled = False
    def PrintToFile(self, matches_value):
        self.datafile.write('%s, %f, %d, %d, %g\n'
                            % (self.kind,
                               self.img.thisf,
                               matches_value,
                               self.img.image.tostring() != self.img2.image.tostring(),
                               perceptual.difference(self.img.image, self.img2.image)))
        self.datafile.flush()
    def ItMatches(self):
        self.e.measured(self.img.thisf, False)
        self.PrintToFile(False)
        self.anim_out()
        Clock.schedule_once(lambda dt: self.Start(), animtime)
    def ItDiffers(self):
        self.e.measured(self.img.thisf, True)
        self.PrintToFile(True)
        self.anim_out()
        Clock.schedule_once(lambda dt: self.Start(), animtime)

def get_hasher():
    # pick the next image to test against, and start working on
    # the hashing.
    kind = app.config.getdefault('game', 'hashtype', 'default')
    hasher = VisualHash.Flag

    if kind == 'default':
        variable = SystemRandom().random()
        if variable >.40:
            kind = 'fractal'
        elif .25 < variable <= .40:
            kind = 'hex128'
        elif .15 < variable <= .25:
            kind = 'identicon'
        elif .05 < variable <=.15:
            kind = 'tflag'
        else:
            kind = 'flag'

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
    return hasher, kind

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
        hasher, = get_hasher()
        NextImage(self.thehash, 512, lambda: rnd, hasher)
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
        #print 'working on image'
        sz = self.size
        im = self.hasher(self.rnd(), sz)
        #print 'done with image'
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
