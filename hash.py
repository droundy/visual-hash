#!/usr/bin/python2

import VisualHash

#img = VisualHash.Identicon('Hello world', 128)
#img = VisualHash.Hash('Hello world', 128)
img = VisualHash.RandomArt(VisualHash.StrongRandom('Hello world'), 128)
img = VisualHash.TFlag(VisualHash.StrongRandom('Hello world'), 128)
img.save('image.png')
#img.show()
