#!/usr/bin/python2

from PIL import Image

import pyximport; pyximport.install()
import FractalTransform

import random, struct
from Crypto.Hash import SHA512 as _hash

class StrongRandom(random.Random):
    def __init__(self, string):
        self.string = string
        self.hash = _hash.new(string).digest()
        self.bits = _hash.new(string).digest()
        self.gauss_next = None
    def random(self):
        fmt = '<L'
        N = struct.calcsize(fmt)
        if len(self.bits) < N:
            self.bits += _hash.new(self.hash).digest()
            self.hash = _hash.new(self.hash).digest()
        val = struct.unpack('<L', self.bits[:N])[0]
        self.bits = self.bits[N:]
        return val/(2.0**32)


a = FractalTransform.Multiple().Randomize(StrongRandom('Hello world'))
parts = a.TakeApart()

size = 128

for filename, transform in parts[:1]:
    h = FractalTransform.Simulate(transform, FractalTransform.MakePoint(.1,.232332), size, size)
    img = Image.new( 'RGB', (size,size), "black") # create a new black image
    pixels = img.load() # create the pixel map
    colors = FractalTransform.get_colors(h)

    for i in range(img.size[0]):    # for every pixel:
        for j in range(img.size[1]):
            pixels[i,j] = (int(256*colors[0,i,j]), int(256*colors[1,i,j]), int(256*colors[2,i,j])) # set the colour accordingly

    img.save(filename)
#img.show()

