#!/usr/bin/python2
from __future__ import division

import numpy
import numpy.random as random

class model:
    def __init__(self, H, N, A):
        self.N = N
        self.H = H
        self.q = 2.0**(-H/N)
        self.A = A
    def __call__(self, f):
        return ((1-f+f*self.q)**self.N)*(1-self.A)
    def __str__(self):
        return '<%g entropy, with %g "things" with %g states with error rate %g>' % (self.H, self.N, 1./self.q, self.A)

def playGame(P, fs):
    """ Given the true probability distribution P, perform random
    experiments at f values fs. """
    results = numpy.zeros_like(fs)
    for i in range(len(fs)):
        if random.uniform() < P(fs[i]):#where is the P(f) function in the code?
            results[i] = 1
    return results

def findBayesProbability(P, fs, results):
    """ Find the Bayesian estimate of the probability that P is the
    correct hypothesis, given results from experiments at f values fs.
    """
    prob = 1
    for i in range(len(fs)):
        if results[i] == 1:
            prob *= P(fs[i]) # *= is the same as prob*P(fs[i])
        else:
            prob *= 1 - P(fs[i])
    return prob # it's actually log probability

def pickNextF(fs, results):
	import random
	import math
	""" Choose the next f value to try an experiment on. """
	sort_fs = sorted(fs) #sort the fs list into ascending order of values

	largest_gap = 0 #reset gap and track values to zero
	track = 0
	mu = 0
	window = 0
	i = 0
	gap = numpy.zeros(len(fs)+1) #create an array to hold gap values
	""" Choosing the next fs value by finding the largest current gap 
	in the fs values and using that gap location to center
	a gaussian distribution curve on it. This curve peaks at the center of the 
	gap and through probability of random numbers being under the dist. curve, 
	a higher percentage of next fs will fall in the area where there are currently fewer fs
	located. This gaussian dist. curve does not have to belocated where the largest gap is,
	as it can be centered on any area of the P(f) curve where more information is wanted."""

	for i in range(len(gap)): #there will be 1 more gap than fs
	
		if i == 0:
			print"first"
			gap[i] = sort_fs[i] 
			'''
			if sort_fs[i] <= .5001 :
				largest_gap = 1-gap[i]			
			else:
				largest_gap = gap[i]
			'''
		elif i == len(sort_fs):
			gap[i] = 1-sort_fs[i-1]
			
			if gap[i] >= largest_gap:
				largest_gap = gap[i]
				track = i #tracks the i'th value of where the largest gap occurs in sort_fs
		else:
			gap[i] = sort_fs[i] - sort_fs[i-1]
			
			if gap[i] >= largest_gap:
				largest_gap = gap[i]
				track = i
	#print largest_gap,"lg"
	#print sort_fs[track], sort_fs[track-1]

		
	window = sort_fs[track] - sort_fs[track-1] #defines the gap window
	mu = sort_fs[track-1] + window/2 #sets variable mu to be centered on the gap
	print mu, "mu"
	sigma = window/2.0
	scale = .3

        rand_f = -1
        while rand_f > 1 or rand_f < 0:
            rand_f = random.gauss(mu, sigma)
        return rand_f

if __name__ == '__main__':
    import matplotlib.pyplot as plt

    P = model(26, 4, 0.05) # H, N, A

    useDeterministic = True
    if useDeterministic:
        random.seed(0)
        fs = numpy.arange(0, 1, 0.001)
        results = playGame(P, fs)
        print 'total results', sum(results)
    else:
        fs = numpy.array([0, 0.5, 1]) #starting f?
        results = playGame(P, fs) #seed results
        for i in range(100): #loop to generate further hash comparisons
            nextf = pickNextF(fs, results)
            print 'our next f is', nextf, 'and fs is', fs[-3:], 'length fs is', len(fs)
            res = playGame(P, [nextf])
            fs = numpy.append(fs, nextf) #adds newest f to fs array
            results = numpy.append(results, res[0]) #updates results with newest result

    plt.figure()
    plt.hist((fs, fs[results>0.5], fs[results<0.5]))
    plt.xlabel('$f$')

    #plt.show()

    Ns_1d = numpy.arange(1, 30, 0.5)
    Hs_1d = numpy.arange(1, 100, 0.5)
    Ns, Hs = numpy.meshgrid(Ns_1d, Hs_1d)
    prob = numpy.zeros_like(Ns)
    dA = 0.1
    for A in numpy.arange(dA/2.0, 1, dA): # sum over all possible A values
        PP = model(Hs, Ns, A)
        Pprior = 1.0/(1 + Hs/100)
        thisprob = Pprior*findBayesProbability(PP, fs, results)*dA
        print 'prob of A =', A, 'is', sum(sum(thisprob))
        prob += thisprob
    prob /= sum(sum(prob)) # normalize the probability

    plt.figure()
    levels = numpy.linspace(0, prob.max(), 10)
    plt.contourf(Ns, Hs, prob, levels=levels)
    plt.xlabel('$N$')
    plt.ylabel('$H$')
    cbar = plt.colorbar()
    labels = ['foo']*len(levels)
    for i in range(len(levels)):
        labels[i] = '%.0f%% credible' % (100*sum(prob[prob>levels[i]]))
    cbar.ax.set_yticklabels(labels)
    plt.plot([P.N], [P.H], 'wx', markersize=30., markeredgewidth=3)

    prob_H = numpy.zeros_like(Hs_1d)
    for i in range(len(prob_H)):
        prob_H[i] = numpy.sum(prob[i,:])
    print 'max H', max(Hs_1d), 'min H', min(Hs_1d)
    prob_H /= numpy.sum(prob_H)*(max(Hs_1d)-min(Hs_1d))/len(prob_H)
    plt.figure()
    plt.plot(Hs_1d, prob_H)
    plt.xlabel('H')
    plt.ylabel('probability per bit')

    plt.show()
