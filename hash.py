#!/usr/bin/python2

import VisualHash
import time

data = 'Hello world'

myhash = VisualHash.Flag
myhash = VisualHash.TFlag
myhash = VisualHash.RandomArt
myhash = VisualHash.Identicon
myhash = VisualHash.Fractal


img = myhash(VisualHash.StrongRandom(data), 128)
img.save('image.png')
#img.show()


# for i in range(10):
#     print "\n==========", i
#     tweaked = myhash(VisualHash.TweakedRandom(data, 0.1, i, i), 128)
#     #tweaked.show()
#     tweaked.save('tweaked.png')
#     #time.sleep(3)

