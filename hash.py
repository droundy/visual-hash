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

todo = ['old', # 'fractal',
        'optimized']

timereport = ''

if 'old' in todo:
    print '\nworking on old fractal'
    print '======================'
    before = time.clock()
    img = VisualHash.OldFractal(VisualHash.StrongRandom(data), 128)
    after = time.clock()
    timereport += '\nold fractal algorithm took %g seconds' % (after - before)
    img.save('oldimage.png')

if 'fractal' in todo:
    print '\nworking on new fractal'
    print '======================'
    before = time.clock()
    img = VisualHash.Fractal(VisualHash.StrongRandom(data), 128)
    after = time.clock()
    timereport += '\nnew fractal algorithm took %g seconds' % (after - before)
    img.save('image.png')

if 'optimized' in todo:
    print '\nworking on optimized fractal'
    print '============================'
    before = time.clock()
    img = VisualHash.OptimizedFractal(VisualHash.StrongRandom(data), 128)
    after = time.clock()
    timereport += '\noptimized fractal algorithm took %g seconds' % (after - before)
    img.save('optimizedimage.png')
#img.show()

print timereport

# for i in range(10):
#     print "\n==========", i
#     tweaked = myhash(VisualHash.TweakedRandom(data, 0.1, i, i), 128)
#     #tweaked.show()
#     tweaked.save('tweaked.png')
#     #time.sleep(3)

