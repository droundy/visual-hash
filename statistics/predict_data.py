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

# TO DO!  :)

to_do = [""" Write a function to simulate measurements, which is to say, given a set of
             f values and q, A and N, return a set of 0s and 1s indicating whether it
             remained the same.  Using random number generator.""",
         """ Write a function that given a bunch of measurement results and a q, A, N,
             will return the "probability" of finding this set of measurements. """,
         """ (later) Think about eliminating q or N in favor of entropy. """,
         """ (later) Visualize the probability above, how it depends on q, A, and N,
             to show what combinations are likely. """,
         """ (later) Choose next f based on previous observations. """]

p = np.zeros_like(random_data.f) # the probability of staying the same for each f value
for i in range(len(random_data.f)):
    p[i] = random_data.Prob(random_data.f[i])

print(p)


