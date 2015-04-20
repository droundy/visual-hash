#!/usr/bin/python2
from __future__ import division

import numpy
import numpy.random as random
import csv

class model:
    def __init__(self, H, A):
        self.H = H
        self.A = A
    def __call__(self, f):
        return ((1-f*0.5)**self.H)*(1-self.A)
    def __str__(self):
        return '<%g entropy with error rate %g>' % (self.H, self.A)

def readcsv(csvname, hashkind):
    with open(csvname, 'rb') as csvf:
        reader = csv.reader(csvf)
        fs = []
        results = []
        for row in reader:
            f = float(row[3])
            result= float(row[4])
            kind = row[2].lstrip() # strip off leading spaces
            if kind == hashkind:
                fs.append(f)
                results.append(result)
        return(numpy.array(fs), numpy.array(results))

def findBayesProbability(P, fs, results):
    """ Find the Bayesian estimate of the probability that P is the
    correct hypothesis, given results from experiments at f values fs.
    """
    prob = 1.0
    for i in range(len(fs)):
        if results[i] == 1:
            prob *= P(1.0*fs[i]) # *= is the same as prob*P(fs[i])
        else:
            prob *= 1 - P(1.0*fs[i])
    return prob

def findBestHA(fs, results):
    As_1d = numpy.arange(0, 1.0, 0.001)
    Hs_1d = numpy.arange(1, 400, 0.5)
    Hs, As = numpy.meshgrid(Hs_1d, As_1d)
    bestH = 0.0
    bestA = 0.0

    Pprior = 1 # 1.0/(1 + Hs/50 + 2*As)
    PP = model(Hs, As)
    prob = Pprior*findBayesProbability(PP, fs, results)

    maxprob = prob.max()
    i,j = numpy.unravel_index(prob.argmax(), prob.shape)
    bestH = Hs[i,j]
    bestA = As[i,j]
    return model(bestH, bestA)


if __name__ == '__main__':
    import matplotlib.pyplot as plt

    fs, results = readcsv("../pairs.csv", 'fractal')

    print 'number that look the same', len(fs[results<0.5])
    print 'number that look different', len(fs[results>0.5])
    print 'number of comparisons made', len(fs)

    Pbest = findBestHA(fs, results)
    print 'Pbest is', Pbest

    As_1d = numpy.arange(0, 1.0, 0.001)
    Hs_1d = numpy.arange(1, 400, 0.5)
    Hs, As = numpy.meshgrid(Hs_1d, As_1d)
    bestH = 0.0
    bestA = 0.0

    Pprior = 1 # 1.0/(1 + Hs/50 + 2*As)
    PP = model(Hs, As)
    prob = Pprior*findBayesProbability(PP, fs, results)
    prob /= sum(sum(prob)) # normalize the probability

    plt.figure()
    levels = numpy.linspace(0, prob.max(), 10)
    plt.contourf(As, Hs, prob, levels=levels)
    plt.xlabel('$A$')
    plt.ylabel('$H$')
    cbar = plt.colorbar()
    labels = ['foo']*len(levels)
    for i in range(len(levels)):
        labels[i] = '%.0f%% credible' % (100*sum(prob[prob>levels[i]]))
    cbar.ax.set_yticklabels(labels)
    plt.plot([Pbest.A], [Pbest.H], 'o', markersize=30., markeredgewidth=3, markerfacecolor='none', markeredgecolor='w')

    prob_H = numpy.zeros_like(Hs_1d)
    for i in range(len(prob_H)):
        prob_H[i] = numpy.sum(prob[:,i])
    print 'max H', max(Hs_1d), 'min H', min(Hs_1d)
    prob_H /= numpy.sum(prob_H)*(max(Hs_1d)-min(Hs_1d))/len(prob_H)
    plt.figure()
    plt.plot(Hs_1d, prob_H)
    plt.xlabel('H')
    plt.ylabel('probability per bit')

    plt.show()
