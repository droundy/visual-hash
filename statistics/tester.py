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

x0 = 60
width = 1
f = mytanh(x0, width)
rnd = mytanh_random(x0, width)

default_Ntries = 30

fracs = [1./3, 0.5, 2./3]
fracs = [0.25, 0.5, 0.75]
fracs = [1./3, 2./3]
golden = (math.sqrt(5)-1)/2
fracs = [golden**2, golden]
#fracs = [1./3]
#fracs = [0.5]

for attempt in range(15):
    out = {}
    e = PBA.Estimator(0, 100, 0.01)
    for frac in fracs:
        out[frac] = [0]*default_Ntries
        e.add_frac(frac)
    for i in range(default_Ntries):
        for frac in fracs:
            out[frac][i] = e.frac_median(frac)
            e.measured(out[frac][i], rnd(out[frac][i]))
    syms = { 0.5: '.', 1./3: '+', 2./3: 'x', .25: '>', .75: '<',
             golden: 'o', golden**2: 's' }
    for frac in fracs:
        plt.plot(out[frac], syms[frac])
    mystr = ''
    for frac in fracs:
        mystr += '%8g (%4.2f) ' % (out[frac][-1], f(out[frac][-1]))
    print mystr

for frac in fracs:
    plt.plot(np.arange(len(out[frac])), np.zeros_like(out[frac])+x0, 'b-')

plt.show()
