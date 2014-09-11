from __future__ import division
import numpy as np
import random
#import matplotlib.pyplot as plt

import random_data

P = 0 #probability of two hashes being the same
b=100  #number of times two hashes are compared
#f = np.zeros(b+1) # f is the fraction of the original
 #hash to the new hash in terms of variables changed

N = 1#the constants are given float values here 
q = 1
A = 0

p = np.zeros_like(random_data.f) # the probability of staying the same for each f value
for i in range(len(random_data.f)):
    p[i] = random_data.Prob(random_data.f[i])

print(p)


