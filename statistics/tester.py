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
x0 = 50
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

default_Ntries = 20

def PBA(f, lo, hi, Ntries = default_Ntries, dx = 0.01):
    xs = np.arange(lo, hi, dx)
    fguess = np.zeros_like(xs) + 1
    guesses = np.zeros(Ntries)
    for i in range(Ntries):
        med = xs[ProperMedian(fguess)]
        #print 'median', med
        xtry = med
        guesses[i] = xtry
        good = f(xtry)
        p = 0.9
        q = 1 - p
        F = np.cumsum(fguess)
        F /= F[-1]
        gamma = (1-F)*p + F*(1-p)
        if good:
            fguess[xs > xtry] *= p/gamma[xs > xtry]
            fguess[xs < xtry] *= q/gamma[xs < xtry]
        else:
            fguess[xs < xtry] *= p/(1 - gamma[xs < xtry])
            fguess[xs > xtry] *= q/(1 - gamma[xs > xtry])
    return guesses, xs, fguess

class MedianList(object):
    def __init__(self, mn, mx):
        self.left = [(mn,False)]
        self.right = [(mx,True)]
        self.num_left = 1
        self.num_right = 1
    def median(self):
        return 0.5*(self.left[-1][0] + self.right[-1][0])
    def add(self, x, is_right):
        if is_right:
            if self.num_right <= self.num_left or self.num_left == 1:
                self.right.append((x, is_right))
                self.num_right += 1
            else:
                self.right.append((x, is_right))
                self._shift(True)
        else:
            if self.num_left <= self.num_right or self.num_right == 1:
                self.left.append((x, is_right))
                self.num_left += 1
            else:
                self.left.append((x, is_right))
                self._shift(False)
    def _shift(self, to_right):
        if to_right:
            x, is_right = self.left.pop()
            self.right.append((x, is_right))
            if is_right:
                self.num_left += 2
                self.num_right += 1
            else:
                self.num_left -= 1
                self.num_right -= 2
        else:
            x, is_right = self.right.pop()
            self.left.append((x, is_right))
            if not is_right:
                self.num_left += 2
                self.num_right += 1
            else:
                self.num_left -= 1
                self.num_right -= 2
    def __str__(self):
        self.right.reverse()
        s = '%s < %s (%g, %g)' % (self.left, self.right, self.num_left, self.num_right)
        self.right.reverse()
        return s

# ml = MedianList(0, 100)
# print ml.median()
# ml.add(50, False)
# print ml.median()

# for i in range(20):
#     ml.add(ml.median(), True)
#     print ml.median()
#     print ml

# print ml

def PBA_continuum(f, lo, hi, Ntries = default_Ntries):
    ml = MedianList(lo, hi)
    guesses = np.zeros(Ntries)
    for i in range(Ntries):
        x = ml.median()
        guesses[i] = x
        ml.add(x, not f(x))
        #print ml
    return guesses

out, xs, fguess = PBA(rnd, 0, 100)

out_c = PBA_continuum(rnd, 0, 100)

print 'answer:', xs[ProperMedian(fguess)]
print 'answer_c:', out_c[-1]

#plt.plot(out, 'r.')

# plt.figure()
# plt.plot(xs, fguess)

plt.figure()
#plt.plot(out_c, 'b-')
plt.plot(out, 'r.')

out = PBA(rnd, 0, 100)[0]
print out[-1]
plt.plot(out, 'g.')

out = PBA(rnd, 0, 100)[0]
plt.plot(out, 'b.')
print out[-1]

out = PBA(rnd, 0, 100)[0]
plt.plot(out, 'c.')
print out[-1]


plt.plot(np.arange(len(out)), np.zeros_like(out)+x0, 'b-')

plt.show()
