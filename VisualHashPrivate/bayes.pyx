#!/usr/bin/python2

#cy  thon: nonecheck=True
#        ^^^ Turns o  n nonecheck globally
# cy thon: profile=True

from __future__ import division

import random as random

cdef class model:
    cdef double N, H, q, A

    property H:
        def __get__(self):
            return self.H
    property A:
        def __get__(self):
            return self.A

    def __cinit__(self, double H, double N, double A):
        self.N = N
        self.H = H
        self.q = 2.0**(-H/N)
        self.A = A

    def __call__(self, double f):
        return ((1-f+f*self.q)**self.N)*(1-self.A)

    def derivative(self, double f):
        return self.N*(1-f+f*self.q)**(self.N-1)*(-1 + self.q)*(1-self.A)

    cdef double C(self, double f):
        return (((2*self.N+1)*(1+f*(self.q-1))**(self.N+1)-(self.N+1)*(1+f*(self.q-1))**(2*self.N+1)*(1-self.A)-(2*self.N+1)+(self.N+1)*(1-self.A))
        /((2*self.N+1)*(self.q**(self.N+1))-((self.N+1)*(self.q**(2*self.N+1))*(1-self.A))-(2*self.N+1)+(self.N+1)*(1-self.A)))

    cpdef double f_from_C(self, double C):
        """ computes the "f" that has value C for the method defined above (i.e. the method named C) """
        cdef double fmin = 0
        cdef double fmax = 1
        cdef int i
        for i in range(20):
            if self.C(0.5*(fmin + fmax)) > C:
                fmax = 0.5*(fmin + fmax)
            else:
                fmin = 0.5*(fmin + fmax)
        return 0.5*(fmin + fmax)

    def __str__(self):
        return '<%g entropy, with %g "things" with %g states with error rate %g>' % (self.H, self.N, 1./self.q, self.A)

def findBayesProbability(model P, fs, results):
    """ Find the Bayesian estimate of the probability that P is the
    correct hypothesis, given results from experiments at f values fs.
    """
    cdef double prob = 1.0
    cdef int i
    for i in range(len(fs)):
        if results[i] == 1:
            prob *= P(1.0*fs[i]) # *= is the same as prob*P(fs[i])
        else:
            prob *= 1 - P(1.0*fs[i])
    return prob # it's actually log probability

def findBestHNA(fs, results):
    cdef double Nmin = 1
    cdef double Nmax = 50
    cdef double dN = 0.5

    cdef double Hmin = 1
    cdef double Hmax = 512
    cdef double dH = 0.5

    cdef double dA = 0.01
    cdef double Amin = 0.005
    cdef double Amax = 1.0

    cdef double maxprobability = 0

    cdef double bestN = 1.0
    cdef double bestH = 0.0
    cdef double bestA = 0.0

    cdef double H, A, N, Pprior, prob
    H = Hmin
    while H <= Hmax:
        N = Nmin
        N = H
        while N <= H: # only allow N <= N one bit minimum entropy per "thing"
            A = Amin
            while A <= Amax:
                Pprior = 1.0/(1 + H/50 + 2*A)
                prob = Pprior*findBayesProbability(model(H,N,A),fs,results)*dA
                if prob > maxprobability:
                    bestH = H
                    bestA = A
                    bestN = N
                    maxprobability = prob
                A += dA
            N += dN
        H += dH
    print 'maxprobability', maxprobability, 'H', bestH, 'N', bestN, 'A', bestA
    return model(bestH, bestN, bestA)

def pickNextF(model P):
    cdef double probsame = P.A
    if P.A < 0.2:
        probsame = 0.2
    if random.random() < probsame:
        return 0.0
    C = random.random()
    return P.f_from_C(C) #  find new f such that P.C(new_f) = R, by solving for f using bisection(numerically)
