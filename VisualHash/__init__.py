#!/usr/bin/python2

"""
Create a visual hash of a string.

VisualHash is a package that includes several methods to create a
strong visual hash of an arbitrary string.
"""

from PIL import Image

import pyximport; pyximport.install()
from VisualHashPrivate import FractalTransform
from VisualHashPrivate import identicon
from VisualHashPrivate import randomart

import random, struct
from Crypto.Hash import SHA512 as _hash

class StrongRandom(random.Random):
    """
    A strong random number generator.

    StrongRandom enables the generation of a sequence of
    crytographically strong random numbers given a string as a seed
    (or something that can be converted into a string).  StrongRandom
    is a subclass of random.Random, which enables most of the
    random-number generation facilities of the standard random
    package.  It does not, however, work with the re-seeding features
    in that class.
    """
    def __init__(self, string):
        """ Create a random number generator given a string. """
        self.string = str(string)
        self.hash = _hash.new(string).digest()
        self.bits = _hash.new(string).digest()
        self.gauss_next = None
        self.bits_used = 0
    def random32(self):
        """ Generate a random 32-bit integer. """
        fmt = '<L'
        N = struct.calcsize(fmt)
        if len(self.bits) < N:
            self.bits += _hash.new(self.hash).digest()
            self.hash = _hash.new(self.hash).digest()
        val = struct.unpack('<L', self.bits[:N])[0]
        self.bits = self.bits[N:]
        self.bits_used += 32
        return val
    def random(self):
        """ Generate a random floating point number in [0,1)."""
        return self.random32()/(2.0**32)

class TweakedRandom(random.Random):
    """
    A "tweaked" version of the StrongRandom number generator.

    This enables changing just some of the output bits, in a
    pseudorandom manner.  The idea is to be able to make small changes
    to the random number stream in order to investigate these sorts of
    effects.
    """
    def __init__(self, string, fraction, seed):
        """
        Create a tweaked random number generator.

        string - the "untweaked" seed
        fraction - the fraction of bits that should be altered
        seed - a seed that determines which bits to modify
        """
        self._random = StrongRandom(string)
        self.fraction = fraction
        self.tweaker = StrongRandom(seed)
        self.gauss_next = None
    def random32(self):
        """Generate a random 32-bit integer."""
        r = self._random.random32()
        for i in range(32):
            if self.tweaker.random() < self.fraction:
                r ^= (1 << i)
        return r
    def random(self):
        """ Generate a random floating point number in [0,1)."""
        return self.random32()/(2.0**32)

def Fractal(random = StrongRandom(""), size = 128):
    """
    Create a hash as a fractal flame.

    Given a string (and optionally a size in pixels) return a PIL
    Image that is a strong cryptographic hash of the string.
    """
    transform = FractalTransform.Multiple().Randomize(random)
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


def Flag(random = StrongRandom(""), size = 128):
    """
    Create a hash using the "flag" algorithm.

    Given a string (and optionally a size in pixels) return a PIL
    Image that is a strong cryptographic hash of the string.
    """
    img = Image.new( 'RGBA', (size,size), "black") # create a new black image
    return img

def Identicon(random = StrongRandom(""), size = 128):
    """
    Create an identicon hash.

    Given a string (and optionally a size in pixels) return a PIL
    Image that is a hash of the string.  This hash has only 32 bits in
    it, so it is not a strong hash.
    """
    code = random.random32()
    img = identicon.render_identicon(code, int(size/3))
    return img

def RandomArt(random = StrongRandom(""), size = 128):
    """
    Create a hash using the randomart algorithm.

    Given a string (and optionally a size in pixels) return a PIL
    Image that is a strong cryptographic hash of the string.
    """
    img = randomart.Create(random, size)
    return img
