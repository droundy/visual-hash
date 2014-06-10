#!/usr/bin/python2

import VisualHash
import time

data = 'Hello world'

myhash = VisualHash.Flag
myhash = VisualHash.TFlag
myhash = VisualHash.RandomArt
myhash = VisualHash.Identicon
myhash = VisualHash.OldFractal
myhash = VisualHash.Fractal

use = 'old'
use = 'new'
use = 'both'

if use == 'old' or use == 'both':
    print '\nworking on old fractal'
    print '======================'
    img = VisualHash.OldFractal(VisualHash.StrongRandom(data), 128)
    img.save('oldimage.png')

if use == 'new' or use == 'both':
    print '\nworking on new fractal'
    print '======================'
    img = myhash(VisualHash.StrongRandom(data), 128)
    img.save('image.png')
#img.show()


# for i in range(10):
#     print "\n==========", i
#     tweaked = myhash(VisualHash.TweakedRandom(data, 0.1, i, i), 128)
#     #tweaked.show()
#     tweaked.save('tweaked.png')
#     #time.sleep(3)

