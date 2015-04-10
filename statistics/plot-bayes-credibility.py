#!/usr/bin/python2
from __future__ import division

import numpy
import numpy.random as random
import csv

class model:
    def __init__(self, H, N, A):
        self.N = N
        self.H = H
        self.q = 2.0**(-H/N)
        self.A = A
    def __call__(self, f):
        return ((1-f+f*self.q)**self.N)*(1-self.A)
    def derivative(self, f):
        return self.N*(1-f+f*self.q)**(self.N-1)*(-1 + self.q)*(1-self.A)
    def C(self, f):
        return (((2*self.N+1)*(1+f*(self.q-1))**(self.N+1)-(self.N+1)*(1+f*(self.q-1))**(2*self.N+1)*(1-self.A)-(2*self.N+1)+(self.N+1)*(1-self.A))
        /((2*self.N+1)*(self.q**(self.N+1))-((self.N+1)*(self.q**(2*self.N+1))*(1-self.A))-(2*self.N+1)+(self.N+1)*(1-self.A)))
    def f_from_C(self, C):
        """ computes the "f" that has value C for the method defined above (i.e. the method named C) """
        fmin = 0
        fmax = 1
        for i in range(20):
            if self.C(0.5*(fmin + fmax)) > C:
                fmax = 0.5*(fmin + fmax)
            else:
                fmin = 0.5*(fmin + fmax)
        return 0.5*(fmin + fmax)

    def __str__(self):
        return '<%g entropy, with %g "things" with %g states with error rate %g>' % (self.H, self.N, 1./self.q, self.A)

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
#print(fs, results)

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

def findBestHNA(fs, results):
    Ns_1d = numpy.arange(1, 200, 0.5)
    Hs_1d = numpy.arange(1, 200, 0.5)
    Ns, Hs = numpy.meshgrid(Ns_1d, Hs_1d)
    prob = numpy.zeros_like(Ns)
    dA = 0.01
    maxprobability = 0
    bestN = 1.0
    bestH = 0.0
    bestA = 0.0
    for A in numpy.arange(dA/2.0, 1, dA): # sum over all possible A values
        PP = model(Hs, Ns, A)
        Pprior = 1.0/(1 + Hs/50 + 2*A)
        Pprior[Ns > Hs] = 0 # we do not believe that we can have less than one "bit" per "thing"
        thisprob = Pprior*findBayesProbability(PP, fs, results)*dA
        maxprob_this_A = thisprob.max()
        if maxprob_this_A > maxprobability:
            i,j = numpy.unravel_index(thisprob.argmax(), thisprob.shape)
            bestN = Ns[i,j]
            bestH = Hs[i,j]
            bestA = A
            maxprobability = maxprob_this_A
        else:
            break # I'm guessing that probably we have surpassed the best A
        #print 'maxprob_this_A for', A, 'is', maxprob_this_A
    #print 'I think that', bestH, bestN, bestA, 'with prob', maxprobability
    print 'maxprobability', maxprobability, 'H', bestH, 'N', bestN, 'A', bestA
    return model(bestH, bestN, bestA)

import matplotlib.pyplot as plt
for hashkind in ['fractal', 'flag']:

    fs, results = readcsv("../pairs.csv", hashkind)

    print 'number that look the same', len(fs[results<0.5])
    print 'number that look different', len(fs[results>0.5])
    print 'number of comparisons made', len(fs)

    Pbest = findBestHNA(fs, results)
    print 'Pbest is', Pbest
    plt.figure()
    fs_to_plot = 2**(numpy.arange(-30, 0, 0.1))
    plt.plot(fs_to_plot, Pbest(fs_to_plot))
    plt.plot(fs_to_plot, 1-4*numpy.abs(Pbest(fs_to_plot) - 0.5)**2) # Try this!
    plt.plot(fs_to_plot, Pbest.derivative(fs_to_plot)/Pbest.derivative(fs_to_plot).min())
    plt.plot(fs_to_plot, (1-4*numpy.abs(Pbest(fs_to_plot) - 0.5)**2 + Pbest(fs_to_plot))/2)
    plt.xlabel('f')
    plt.ylabel('Pbest(f)')

    plt.figure()
    plt.hist((fs, fs[results>0.5], fs[results<0.5]), label=('total', 'looks same', 'looks different'), bins=30)
    plt.legend()
    plt.xlabel('$f$')

    #plt.show()

    Ns_1d = numpy.arange(1, 200, 0.5)
    Hs_1d = numpy.arange(1, 200, 0.5)
    Ns, Hs = numpy.meshgrid(Ns_1d, Hs_1d)
    prob = numpy.zeros_like(Ns)
    dA = 0.01
    for A in numpy.arange(dA/2.0, 1, dA): # sum over all possible A values
        PP = model(Hs, Ns, A)
        Pprior = 1.0/(1 + Hs/50 + 2*A)
        Pprior[Ns > Hs] = 0 # we do not believe that we can have less than one "bit" per "thing"
        thisprob = Pprior*findBayesProbability(PP, fs, results) # *dA
        print 'prob of A =', A, 'is', sum(sum(thisprob)), 'with min value', thisprob.min()
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

    plt.plot([Pbest.N], [Pbest.H], 'o', markersize=30., markeredgewidth=3, markerfacecolor='none', markeredgecolor='w')

    prob_H = numpy.zeros_like(Hs_1d)
    for i in range(len(prob_H)):
        prob_H[i] = numpy.sum(prob[i,:])
    print 'max H', max(Hs_1d), 'min H', min(Hs_1d)
    prob_H /= numpy.sum(prob_H)*(max(Hs_1d)-min(Hs_1d))/len(prob_H)

    plt.title('Nice plot needs better name %s' % hashkind)

    plt.savefig('prob-vs-H-N-%s.pdf' % hashkind)

    plt.figure()
    plt.plot(Hs_1d, prob_H)
    plt.xlabel('H')
    plt.ylabel('probability per bit')

    plt.title('Nice plot needs better name %s' % hashkind)

    plt.savefig('prob-vs-H-%s.pdf' % hashkind)

    #plt.show()
