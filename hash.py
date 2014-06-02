#!/usr/bin/python2

import VisualHash

#img = VisualHash.Identicon('Hello world', 128)
img = VisualHash.RandomArt(VisualHash.StrongRandom('Hello world'), 128)
img = VisualHash.TFlag(VisualHash.StrongRandom('Hello world'), 128)
img = VisualHash.Fractal(VisualHash.StrongRandom('Hello world6'), 128)
img.save('image.png')
#img.show()

