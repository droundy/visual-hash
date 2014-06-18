import numpy as np

# see dissertation http://people.orie.cornell.edu/shane/theses/ThesisRolfWaeber.pdf

def ProperMedian(vals):
    tot = np.sum(vals)
    sofar = 0
    for i in range(len(vals)):
        sofar += vals[i]
        if sofar > tot/2:
            return i
    return len(vals)-1

default_Ntries = 20

def PBA(f, lo, hi, Ntries = default_Ntries, dx = 0.01):
    xs = np.arange(lo, hi, dx)
    fguess = np.zeros_like(xs) + 1
    guesses = np.zeros(Ntries)
    for i in range(Ntries):
        med = xs[ProperMedian(fguess)]
        #print 'median', med
        xtry = med
        guesses[i] = xtry
        good = f(xtry)
        p = 0.9
        q = 1 - p
        p = 2.0
        q = 1./p
        F = np.cumsum(fguess)
        F /= F[-1]
        gamma = (1-F)*p + F*(1-p)
        if good:
            fguess[xs > xtry] *= p # /gamma[xs > xtry]
            fguess[xs < xtry] *= q # /gamma[xs < xtry]
        else:
            fguess[xs < xtry] *= p # /(1 - gamma[xs < xtry])
            fguess[xs > xtry] *= q # /(1 - gamma[xs > xtry])
    return guesses, xs, fguess, xs[ProperMedian(fguess)]

class Estimator(object):
    def __init__(self, lo, hi, dx, initmedian = 0):
        self.lo = lo
        self.hi = hi
        self.dx = dx
        self.xs = np.arange(lo, hi, dx)
        self.f = np.zeros_like(self.xs) + 1
        if initmedian != 0:
            self.f[np.abs(self.xs-initmedian) < 1.5*dx] += np.sum(self.f)
    def median(self):
        tot = np.sum(self.f)
        sofar = 0
        for i in range(len(self.f)):
            sofar += self.f[i]
            if sofar > tot/2:
                return self.xs[i]
        return self.xs[len(self.f)-1]
    def measured(self, x, val):
        p = 2.0
        if val:
            self.f[self.xs > x] *= p
            self.f[self.xs < x] /= p
        else:
            self.f[self.xs < x] *= p
            self.f[self.xs > x] /= p
