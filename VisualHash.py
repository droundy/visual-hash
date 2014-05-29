#!/usr/bin/python2

from PIL import Image

import pyximport; pyximport.install()
import FractalTransform
from internal import identicon

import random, struct
from Crypto.Hash import SHA512 as _hash

class StrongRandom(random.Random):
    def __init__(self, string):
        self.string = string
        self.hash = _hash.new(string).digest()
        self.bits = _hash.new(string).digest()
        self.gauss_next = None
    def random32(self):
        fmt = '<L'
        N = struct.calcsize(fmt)
        if len(self.bits) < N:
            self.bits += _hash.new(self.hash).digest()
            self.hash = _hash.new(self.hash).digest()
        val = struct.unpack('<L', self.bits[:N])[0]
        self.bits = self.bits[N:]
        return val
    def random(self):
        return self.random32()/(2.0**32)

def Hash(string, size = 128):
    """
    Given a string (and optionally a size in pixels) return a PIL
    Image that is a strong cryptographic hash of the string.
    """
    transform = FractalTransform.Multiple().Randomize(StrongRandom(string))
    h = FractalTransform.Simulate(transform, FractalTransform.MakePoint(.1,.232332), size, size)
    img = Image.new( 'RGBA', (size,size), "black") # create a new black image
    pixels = img.load() # create the pixel map
    colors = FractalTransform.get_colors(h)

    for i in range(img.size[0]):    # for every pixel:
        for j in range(img.size[1]):
            pixels[i,j] = (int(256*colors[0,i,j]),
                           int(256*colors[1,i,j]),
                           int(256*colors[2,i,j]),
                           int(256*colors[3,i,j])) # set the colour accordingly
    return img


def Flag(string, size = 128):
    """
    The "flag" visual hash.
    """
    img = Image.new( 'RGBA', (size,size), "black") # create a new black image
    return img

def Identicon(string, size = 128):
    random = StrongRandom(string)
    code = random.random32()
    img = identicon.render_identicon(code, int(size/3))
    return img
