#!/usr/bin/python2

from PIL import Image

import pyximport; pyximport.install()
import FractalTransform
from FractalTransform import Point

a = FractalTransform.Affine()
print a.transform(Point(0, 0))
print a

img = Image.new( 'RGB', (255,255), "black") # create a new black image
pixels = img.load() # create the pixel map

for i in range(img.size[0]):    # for every pixel:
    for j in range(img.size[1]):
        pixels[i,j] = (i, j, 200) # set the colour accordingly

img.save('image.png')
img.show()
