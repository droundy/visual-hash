#!/usr/bin/python2

from PIL import Image
import random
#random.seed(0)

import pyximport; pyximport.install()
import FractalTransform

a = FractalTransform.Multiple()
parts = a.TakeApart()

size = 128

for filename, transform in parts:
    h = FractalTransform.Simulate(transform, FractalTransform.MakePoint(.1,.232332), size, size)
    img = Image.new( 'RGB', (size,size), "black") # create a new black image
    pixels = img.load() # create the pixel map
    colors = FractalTransform.get_colors(h)

    for i in range(img.size[0]):    # for every pixel:
        for j in range(img.size[1]):
            pixels[i,j] = (int(256*colors[0,i,j]), int(256*colors[1,i,j]), int(256*colors[2,i,j])) # set the colour accordingly

    img.save(filename)
#img.show()

