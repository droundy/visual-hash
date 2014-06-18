#!/usr/bin/python

from __future__ import division
import math
import numpy as np
from numpy import random
from matplotlib import pyplot as plt

import PBA

def mytanh(mean, width):
    def prob(x):
        return math.atan((x - mean)/width)/math.pi + 0.5
    return prob

def mytanh_random(mean, width):
    f = mytanh(mean, width)
    def prob(x):
        return random.random() > f(x)
    return prob

x0 = 30
width = 2
f = mytanh(x0, width)
rnd = mytanh_random(x0, width)

default_Ntries = 20

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

out, xs, fguess, med = PBA.PBA(rnd, 0, 100, default_Ntries)
print 'answer:', med

#out_c = PBA.PBA_continuum(rnd, 0, 100)

#print 'answer_c:', out_c[-1]

#plt.plot(out, 'r.')

# plt.figure()
# plt.plot(xs, fguess)

plt.figure()
#plt.plot(out_c, 'b-')
plt.plot(out, 'r.')

out = PBA.PBA(rnd, 0, 100, default_Ntries)[0]
print out[-1]
plt.plot(out, 'g.')

out = PBA.PBA(rnd, 0, 100, default_Ntries)[0]
plt.plot(out, 'b.')
print out[-1]

out = PBA.PBA(rnd, 0, 100, default_Ntries)[0]
plt.plot(out, 'c.')
print out[-1]

e = PBA.Estimator(0, 100, 0.01)
for i in range(default_Ntries):
    out[i] = e.median()
    e.measured(out[i], rnd(out[i]))
plt.plot(out, 'k+')
print out[-1]


plt.plot(np.arange(len(out)), np.zeros_like(out)+x0, 'b-')

plt.show()
