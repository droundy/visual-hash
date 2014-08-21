from __future__ import division
import numpy as np
import random
#import matplotlib.pyplot as plt

P = 0 #probability of two hashes being the same
b=10000  #number of times two hashes are compared
f = np.zeros(b+1) # f is the fraction of the original
 #hash to the new hash in terms of variables changed


a = 0 #a counter variable used only for python purposes
while a <= b: #while loop to assign an f value to each hash comparison
    f[a] = random.random()
    a += 1

f = sorted(f)
print(f)
def Prob(f): #the Probability function to determine
    #the probability that the hashes are the same
    P = ((1-f + f*q)**N)*(1-A)
    return P
    print(P)

N = 2 # the number of random "things" in our hash
q = .01 # the probability that if we randomize a "thing" it *stays the same*
A = .25 # the "false positive rate" of our human we are testing

p = np.zeros(b+1)#array to convey Probability information

for i in range(b+1):
    p[i] = np.float(Prob(f[i]))

print(p)

if __name__ == '__main__':
    from visual import * # must import visual or vis first
    from visual.graph import *	 # import graphing features 

    f1 = gdots(color=color.cyan)
    a = 0
    while a<= b:
        f1.plot(pos=(np.log10(f[a]),p[a]))
        a+=1


