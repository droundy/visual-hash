# see dissertation http://people.orie.cornell.edu/shane/theses/ThesisRolfWaeber.pdf

default_Ntries = 20

class Estimator(object):
    def __init__(self, lo, hi, dx):
        Nx = int((hi-lo)/dx)
        self.xs = [lo + i*dx for i in range(Nx)]
        self.f = {}
        self.f[0.5] = [1]*Nx
        self.lo = lo
        self.hi = hi
    def add_frac(self, frac):
        self.f[frac] = [1]*len(self.xs)
    def median(self):
        return self.frac_median(0.5)
    def frac_median(self, frac):
        tot = sum(self.f[frac])
        sofar = 0
        for i in range(len(self.f[frac])):
            sofar += self.f[frac][i]
            if sofar > frac*tot:
                return self.xs[i]
        return self.xs[len(self.f[frac])-1]
    def measured(self, x, val):
        #print self.xs
        #print self.f
        #print self.median()
        pc = 0.55
        qc = 1 - pc
        for frac in self.f.iterkeys():
            if val:
                for i in range(len(self.xs)):
                    if self.xs[i] > x:
                        self.f[frac][i] *= (2*pc)**(2*frac)
                    else:
                        self.f[frac][i] *= (2*qc)**(2*frac)
            else:
                for i in range(len(self.xs)):
                    if self.xs[i] < x:
                        self.f[frac][i] *= (2*pc)**(2*(1-frac))
                    else:
                        self.f[frac][i] *= (2*qc)**(2*(1-frac))

