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

x0 = 10
width = 2
f = mytanh(x0, width)
rnd = mytanh_random(x0, width)

default_Ntries = 15

for attempt in range(5):
    out = [0]*default_Ntries
    e = PBA.Estimator(0, 100, 0.01)
    for i in range(default_Ntries):
        out[i] = e.median()
        e.measured(out[i], rnd(out[i]))
    plt.plot(out, '.')
    print out[-1]

plt.plot(np.arange(len(out)), np.zeros_like(out)+x0, 'b-')

plt.show()
