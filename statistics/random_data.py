from __future__ import division
import numpy as np
import random
#import matplotlib.pyplot as plt
from visual import * # must import visual or vis first
from visual.graph import *	 # import graphing features 
N = 0 #constant
q = 0 #constant
A = 0 #constant
P = 0 #probability of two hashes being the same
b=10  #number of times two hashes are compared
f = np.zeros(b+1) # f is the fraction of the original
 #hash to the new hash in terms of variables changed


a = 0 #a counter variable used only for python purposes
while a <= b: #while loop to assign an f value to each hash comparison
    f[a] = random.random()
    a += 1

f = sorted(f)
print(f)
def Prob(x): #the Probability function to determine
    #the probability that the hashes are the same
    P = (1-(x*q)**N)*(1-A)
    return P
    print(P)

N = 2 #the constants are given float values here 
q = .72
A = .025

a = 0 #counter varibale
p = np.zeros(b+1)#array to convey Probability information



while a <= b:
    p[a] = np.float(Prob(f[a]))
    a += 1

print(p)
f1 = gdots(color=color.cyan)
a = 0
while a<= b:
    f1.plot(pos=(f[a],p[a]))
    a+=1


