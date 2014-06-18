#!/usr/bin/python

from __future__ import division
import math
import numpy as np
from numpy import random
from matplotlib import pyplot as plt

def mytanh(mean, width):
    def prob(x):
        return math.atan((x - mean)/width)/math.pi + 0.5
    return prob

def mytanh_random(mean, width):
    f = mytanh(mean, width)
    def prob(x):
        return random.random() > f(x)
    return prob

N = 500
out = np.zeros(N)
x0 = 30
width = 10
f = mytanh(x0, width)
rnd = mytanh_random(x0, width)

# see dissertation http://people.orie.cornell.edu/shane/theses/ThesisRolfWaeber.pdf

def ProperMedian(vals):
    tot = np.sum(vals)
    sofar = 0
    for i in range(len(vals)):
        sofar += vals[i]
        if sofar > tot/2:
            return i
    return len(vals)-1

def PBA(f, lo, hi, Ntries = 20, dx = 0.01):
    xs = np.arange(lo, hi, dx)
    df = 0.1
    fguess = np.zeros_like(xs) + df/100
    guesses = np.zeros(Ntries)
    for i in range(Ntries):
        med = xs[ProperMedian(fguess)]
        #print 'median', med
        xtry = med
        guesses[i] = xtry
        good = f(xtry)
        if good:
            fguess[xs > xtry] += df
        else:
            fguess[xs < xtry] += df
    return guesses, xs, fguess

out, xs, fguess = PBA(rnd, 0, 100)

print 'answer:', xs[ProperMedian(fguess)]

#plt.plot(out, 'r.')

plt.figure()
plt.plot(xs, fguess)

plt.show()
