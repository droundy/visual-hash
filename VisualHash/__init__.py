#!/usr/bin/python2

"""
Create a visual hash of a string.

VisualHash is a package that includes several functions to create a
visual hash of an arbitrary string.  Each function implements a
distinct algorithm that given a random number generator produces a
visual image.  The cryptographic strength of the hash relies on using
a cryptographically strong random number generator that is seeded by
the data to be hashed.

We provide a strong random number generator (called StrongRandom),
which is based on taking the SHA512 hash of the data, followed by the
SHA512 hash of the hash, and so on.  This puts an upper bound of 512
bits of entropy on any of our hashes (which should not be a problem).

We also provide a "tweaked" random number generator TweakedRandom,
which gives a slight variation on a specific strong random number
sequence.  This will enable us to test the effect of small changes in
the generated hashes.

The visual hash styles supported are:

- Fractal
- Flag
- T-Flag
- RandomArt
- Identicon
"""

from PIL import Image

try:
    import pyximport; pyximport.install()
except:
    print '****** There does not seem to be cython available!!! *******'

from VisualHashPrivate import identicon
from VisualHashPrivate import randomart
from VisualHashPrivate.FractalTransform import DistinctColor
from VisualHashPrivate import FractalTransform

# annoying imports to enable "random" duplication without strange
# __init__ error.
import numpy as np
from math import sqrt, log, exp, sin, cos

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
        self.hash = _hash.new(self.string).digest()
        self.bits = _hash.new(self.string).digest()
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

class TweakedRandom(object):
    """
    A "tweaked" version of the StrongRandom number generator.

    This enables changing just some of the output bits, in a
    pseudorandom manner.  The idea is to be able to make small changes
    to the random number stream in order to investigate these sorts of
    effects.
    """
    def __init__(self, string, fraction, seed1, seed2):
        """
        Create a tweaked random number generator.

        string - the "untweaked" seed
        fraction - the fraction of bits that should be altered
        seed - a seed that determines which bits to modify
        """
        self._random = StrongRandom(string)
        self.fraction = fraction
        self.tweaker = StrongRandom(seed1)
        self.tweakness = StrongRandom(seed2)
        self.gauss_next = None
    def random32(self):
        """Generate a random 32-bit integer."""
        v = self._random.random32()
        if self.tweaker.random() < self.fraction:
            return self.tweakness.random32()
        return v
    def random(self):
        """ Generate a random floating point number in [0,1)."""
        return self.random32()/(2.0**32)
    def choice(self, lis):
        return lis[self.randrange(0, len(lis))]
    def randrange(self, imin, imaxnotincluded=0):
        if imaxnotincluded == 0:
            imaxnotincluded = imin
            imin = 0
        n = imaxnotincluded - imin
        return imin + int(n*self.random())
    def uniform(self, a, b):
        return a + (b-a)*self.random()
    def randint(self, imin, imax):
        n = imax + 1 - imin
        return imin + int(n*self.random())
    def expovariate(self, lambd):
        """Exponential distribution.

        lambd is 1.0 divided by the desired mean.  It should be
        nonzero.  (The parameter would be called "lambda", but that is
        a reserved word in Python.)  Returned values range from 0 to
        positive infinity if lambd is positive, and from negative
        infinity to 0 if lambd is negative.

        """
        return -log(1.0 - self.random())/lambd
    def gauss(self, mu, sigma):
        """Gaussian distribution.

        mu is the mean, and sigma is the standard deviation.  This is
        slightly faster than the normalvariate() function.

        Not thread-safe without a lock around calls.

        """
        random = self.random
        z = self.gauss_next
        self.gauss_next = None
        if z is None:
            x2pi = random() * 2*np.pi
            g2rad = sqrt(-2.0 * log(1.0 - random()))
            z = cos(x2pi) * g2rad
            self.gauss_next = sin(x2pi) * g2rad

        return mu + z*sigma

def Fractal(random = StrongRandom(""), size = 128):
    """
    Create a hash as a fractal flame.

    Given a string (and optionally a size in pixels) return a PIL
    Image that is a strong cryptographic hash of the string.
    """
    transform = FractalTransform.Multiple(random)
    h = transform.Simulate(FractalTransform.Point(.1,.232332), size, size)
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
    pixels = img.load() # create the pixel map
    ncolors = 4
    r = [0]*ncolors
    g = [0]*ncolors
    b = [0]*ncolors
    for i in range(ncolors):
        r[i], g[i], b[i] = DistinctColor(random)
    for i in range(img.size[0]):    # for every pixel:
        for j in range(img.size[1]):
            n = (i*ncolors) // img.size[0]
            pixels[i,j] = (r[n], g[n], b[n], 255) # set the colour accordingly
    return img

def TFlag(random = StrongRandom(""), size = 128):
    """
    Create a hash using the "flag" algorithm.

    Given a string (and optionally a size in pixels) return a PIL
    Image that is a strong cryptographic hash of the string.
    """
    img = Image.new( 'RGBA', (size,size), "black") # create a new black image
    pixels = img.load() # create the pixel map
    ncolors = 16
    r = [0]*ncolors
    g = [0]*ncolors
    b = [0]*ncolors
    for i in range(ncolors):
        r[i], g[i], b[i] = DistinctColor(random)
    for i in range(img.size[0]):    # for every pixel:
        for j in range(img.size[1]):
            nx = (2*i) // img.size[0]
            ny = (j*ncolors//4) // img.size[1]
            n = nx+2*ny
            pixels[i,j] = (r[n], g[n], b[n], 255) # set the colour accordingly
    return img

def Identicon(random = StrongRandom(""), size = 128):
    """
    Create an identicon hash.

    Given a string (and optionally a size in pixels) return a PIL
    Image that is a hash of the string.  This hash has only 32 bits in
    it, so it is not a strong hash.
    """
    code = 0
    for i in range(32):
        if random.random() < 0.5:
            code += 1 << i
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
