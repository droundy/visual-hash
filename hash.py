#!/usr/bin/python2

import VisualHash
import time

doprofile = True
if doprofile:
    import pstats, cProfile

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

todo = ['old', 'fractal', 'optimized']

timereport = ''

if 'fractal' in todo:
    if doprofile:
        print '\nworking on pure python fractal'
        print '==============================='

        before = time.clock()
        cProfile.runctx("VisualHash.Fractal(VisualHash.StrongRandom(data), 128)",
                        globals(), locals(), "pure.prof")
        after = time.clock()
        timereport += '\nprofiling old fractal algorithm took %g seconds' % (after - before)
        s = pstats.Stats("pure.prof")
        s.strip_dirs().sort_stats("time").print_stats(10)

    # print '\nworking on pure python fractal'
    # print '=============================='
    before = time.clock()
    img = VisualHash.Fractal(VisualHash.StrongRandom(data), 128)
    after = time.clock()
    timereport += '\npure python fractal algorithm took %g seconds' % (after - before)
    img.save('image.png')

if 'old' in todo:
    if doprofile:
        print '\nworking on old fractal'
        print '======================'

        before = time.clock()
        cProfile.runctx("VisualHash.OldFractal(VisualHash.StrongRandom(data), 128)",
                        globals(), locals(), "old.prof")
        after = time.clock()
        timereport += '\nprofiling old fractal algorithm took %g seconds' % (after - before)
        s = pstats.Stats("old.prof")
        s.strip_dirs().sort_stats("time").print_stats(10)

    before = time.clock()
    img = VisualHash.OldFractal(VisualHash.StrongRandom(data), 128)
    after = time.clock()
    timereport += '\nold fractal algorithm took %g seconds' % (after - before)
    img.save('oldimage.png')

if 'optimized' in todo:
    if doprofile:
        print '\nworking on optimized fractal'
        print '============================'

        before = time.clock()
        cProfile.runctx("VisualHash.OptimizedFractal(VisualHash.StrongRandom(data), 128)",
                        globals(), locals(), "opt.prof")
        after = time.clock()
        timereport += '\nprofiling optimized fractal algorithm took %g seconds' % (after - before)
        s = pstats.Stats("opt.prof")
        s.strip_dirs().sort_stats("time").print_stats(10)

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

