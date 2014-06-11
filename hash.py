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

timereport = ''

if use == 'old' or use == 'both':
    print '\nworking on old fractal'
    print '======================'
    before = time.clock()
    img = VisualHash.OldFractal(VisualHash.StrongRandom(data), 128)
    after = time.clock()
    timereport += '\nold fractal algorithm took %g seconds' % (after - before)
    img.save('oldimage.png')

if use == 'new' or use == 'both':
    print '\nworking on new fractal'
    print '======================'
    before = time.clock()
    img = myhash(VisualHash.StrongRandom(data), 128)
    after = time.clock()
    timereport += '\nnew fractal algorithm took %g seconds' % (after - before)
    img.save('image.png')
#img.show()

print timereport

# for i in range(10):
#     print "\n==========", i
#     tweaked = myhash(VisualHash.TweakedRandom(data, 0.1, i, i), 128)
#     #tweaked.show()
#     tweaked.save('tweaked.png')
#     #time.sleep(3)

