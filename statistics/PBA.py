# see dissertation http://people.orie.cornell.edu/shane/theses/ThesisRolfWaeber.pdf

default_Ntries = 20

class Estimator(object):
    def __init__(self, lo, hi, dx):
        Nx = int((hi-lo)/dx)
        self.xs = [lo + i*dx for i in range(Nx)]
        self.f = [1]*Nx
        self.lo = lo
        self.hi = hi
    def median(self):
        tot = sum(self.f)
        sofar = 0
        for i in range(len(self.f)):
            sofar += self.f[i]
            if sofar > tot/2:
                return self.xs[i]
        return self.xs[len(self.f)-1]
    def measured(self, x, val):
        #print self.xs
        #print self.f
        #print self.median()
        p = 2.0
        if val:
            for i in range(len(self.xs)):
                if self.xs[i] > x:
                    self.f[i] *= p
                else:
                    self.f[i] /= p
        else:
            for i in range(len(self.xs)):
                if self.xs[i] < x:
                    self.f[i] *= p
                else:
                    self.f[i] /= p

