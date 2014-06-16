"""
Strong and repeatable random number generation
"""

from math import sqrt, log, exp, sin, cos, pi

import random, struct
from Crypto.Hash import SHA512 as _hash

class StrongRandom(object):
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
            x2pi = random() * 2*pi
            g2rad = sqrt(-2.0 * log(1.0 - random()))
            z = cos(x2pi) * g2rad
            self.gauss_next = sin(x2pi) * g2rad

        return mu + z*sigma

class TweakedRandom(StrongRandom):
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
