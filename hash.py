#!/usr/bin/python2

import VisualHash
import time

data = 'Hello world'

myhash = VisualHash.Flag
myhash = VisualHash.Fractal
myhash = VisualHash.TFlag
myhash = VisualHash.Identicon
myhash = VisualHash.RandomArt


img = myhash(VisualHash.StrongRandom(data), 128)
img.save('image.png')
#img.show()


for i in range(5):
    for j in range(2):
        print "\n==========", i, j
        tweaked = myhash(VisualHash.TweakedRandom(data, 0.01, i, j), 128)
        #tweaked.show()
        tweaked.save('tweaked.png')
        time.sleep(3)

