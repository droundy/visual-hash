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
        if random.uniform() < P(fs[i]):
            results[i] = 1
    return results

def findBayesProbability(P, fs, results):
    """ Find the Bayesian estimate of the probability that P is the
    correct hypothesis, given results from experiments at f values fs.
    """
    prob = 1
    for i in range(len(fs)):
        if results[i] == 1:
            prob *= P(fs[i])
        else:
            prob *= 1 - P(fs[i])
    return prob

def pickNextF(fs, results):
    """ Choose the next f value to try an experiment on. """
    return random.uniform()

if __name__ == '__main__':
    import matplotlib.pyplot as plt

    P = model(30, 14, 0.05)

    # fs = numpy.arange(0, 1, 0.0005)
    # results = playGame(P, fs)
    # print numpy.column_stack((fs, P(fs), results))

    fs = numpy.array([0, 0.5, 1])
    results = playGame(P, fs)
    for i in range(100):
        nextf = pickNextF(fs, results)
        res = playGame(P, [nextf])
        fs = numpy.append(fs, nextf)
        results = numpy.append(results, res[0])

    plt.figure()
    nbins = len(fs)/20.
    if nbins < 10:
        nbins = 10
    if nbins > 50:
        nbins = 50
    nbins = int(nbins)
    plt.hist((fs[results>0.5], fs[results<0.5]), len(fs)/50.)
    plt.xlabel('$f$')

    #plt.show()

    Ns_1d = numpy.arange(1, 30, 0.5)
    Hs_1d = numpy.arange(1, 100, 0.5)
    Ns, Hs = numpy.meshgrid(Ns_1d, Hs_1d)
    prob = numpy.zeros_like(Ns)
    dA = 0.1
    for A in numpy.arange(dA/2.0, 1, dA): # sum over all possible A values
        PP = model(Hs, Ns, A)
        thisprob = findBayesProbability(PP, fs, results)*dA
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

    plt.show()
