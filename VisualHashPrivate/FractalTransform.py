from __future__ import division
#cython: nonecheck=True
#        ^^^ Turns on nonecheck globally

#from libc.math cimport log, sqrt, cos, sin, atan2
from math import log, sqrt, cos, sin, atan2

import random
import numpy as np

# QuickRandom is a low-quality random number generator used for the
# chaos game only.  It should ensure that we always generate an
# identical image for a given resolution.
class QuickRandom:
    m_w = 1
    m_z = 2

def quickrand32(s):
    s.m_z = 36969 * (s.m_z & 65535) + (s.m_z >> 16)
    s.m_w = 18000 * (s.m_w & 65535) + (s.m_w >> 16)
    return (s.m_z << 16) + s.m_w  # 32-bit result

class Point:
    def __init__(self, x,y,R=0,G=0,B=0,A=0):
        self.x = x
        self.y = y
        self.R = R
        self.G = G
        self.B = B
        self.A = A

def DistinctColorFloat(random):
    h = 6*random.random()
    saturation = random.random()**.5
    value = random.random()
    cutoff = 0.4
    power = 0.25
    if value < cutoff:
        value = cutoff*(value/cutoff)**power
    if value > 1.0 - cutoff:
        value = (1.0-cutoff) + cutoff*(value - (1.0 - cutoff))**power
    c = saturation*value
    x = c*(1-(h % 2 - 1))
    if h < 1:
        r, g, b = c, x, 0
    elif h < 2:
        r, g, b = x, c, 0
    elif h < 3:
        r, g, b = 0, c, x
    elif h < 4:
        r, g, b = 0, x, c
    elif h < 5:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    m = value - c
    r = r + m
    g = g + m
    b = b + m
    return r, g, b

def DistinctColor(random):
    r, g, b = DistinctColorFloat(random)
    return int(256*r), int(256*g), int(256*b)

class ColorTransform:
    def __init__(self, random):
        self.R, self.G, self.B = DistinctColorFloat(random)
        # self.R = random.uniform(0,1)
        # self.G = random.uniform(0,1)
        # self.B = random.uniform(0,1)
        m = self.R
        if self.G > m:
            m = self.G
        if self.B > m:
            m = self.B
        self.R /= m
        self.G /= m
        self.B /= m
        self.A = 1
    def Transform(c, p):
        p.R = (c.A*c.R + p.A*p.R)/(c.A + p.A)
        p.G = (c.A*c.G + p.A*p.G)/(c.A + p.A)
        p.B = (c.A*c.B + p.A*p.B)/(c.A + p.A)
        p.A = (c.A+p.A)/2
        return p

class Affine:
    def __init__(self, random):
        self.c = ColorTransform(random)
        # currently we always initialize pseudorandomly, but
        # eventually we'll want to generate this deterministically.
        self.theta = 2*np.pi*random.random()
        rot = np.matrix([[cos(self.theta), sin(self.theta)],
                         [-sin(self.theta),cos(self.theta)]])
        self.compressme = random.gauss(0.8, 0.2)
        compress = np.matrix([[self.compressme, 0],
                              [0, self.compressme]])
        mat = compress*rot
        self.Mxx = mat[0,0]
        self.Mxy = mat[0,1]
        self.Myx = mat[1,0]
        self.Myy = mat[1,1]
        translation_scale = 0.8
        self.Ox = random.gauss(0, translation_scale)
        self.Oy = random.gauss(0, translation_scale)
    def Transform(self, p):
        out = self.c.Transform(p)
        p.x -= self.Ox
        p.y -= self.Oy
        out.x = p.x*self.Mxx + p.y*self.Mxy # + self.Ox
        out.y = p.x*self.Myx + p.y*self.Myy # + self.Oy
        #p.x += self.Ox
        #p.y += self.Oy
        return out

class Fancy:
    #Affine a
    #double spiralness, radius, bounciness
    #int bumps
    def __init__(self, random):
        self.a = Affine(random)
        self.spiralness = random.gauss(0, 3)
        self.radius = random.gauss(.4, .2)
        self.bounciness = random.gauss(2, 2)
        self.bumps = random.randint(1, 4)
    def Transform(self, p):
        out = self.a.Transform(p)
        r = sqrt(out.x*out.x + out.y*out.y)
        theta = atan2(out.y, out.x)
        maxrad = self.radius*(1+self.bounciness*sin(theta*self.bumps))
        out.x = maxrad*sin(r/maxrad)*sin(theta + self.spiralness*r)
        out.y = maxrad*sin(r/maxrad)*cos(theta + self.spiralness*r)
        return out
    def Filename(self):
        return 'image_%.2g_%.2g_%.2g_%d__%.2g_%.2g.png' % (self.radius, self.spiralness, self.bounciness, self.bumps, self.a.compressme, self.a.theta)

class rzero(random.Random):
    def random(self):
        return 0.1

class Symmetry:
    #Affine a
    #int Nsym
    def __init__(self, random):
        theta = 2*np.pi*random.random()
        translation_scale = 0.1
        self.a = Affine(rzero())
        self.a.Ox = random.gauss(0, translation_scale)
        self.a.Oy = random.gauss(0, translation_scale)
        nnn = random.expovariate(1.0/3)
        self.Nsym = 1 + int(nnn)
        if self.Nsym == 1 and random.randint(0,1) == 0:
            print 'Mirror plane'
            self.Nsym = 2
            theta = 2*np.pi*random.random()
            vx = sin(theta)
            vy = cos(theta)
            self.a.Mxx = vx
            self.a.Myy = -vx
            self.a.Mxy = vy
            self.a.Myx = vy
        else:
            print 'Rotation:', self.Nsym, 'from', nnn
            self.a.Mxx = cos(2*np.pi/self.Nsym)
            self.a.Myy = self.a.Mxx
            self.a.Mxy = sin(2*np.pi/self.Nsym)
            self.a.Myx = -self.a.Mxy
        print np.array([[self.a.Mxx, self.a.Mxy],
                        [self.a.Myx, self.a.Myy]])
        print 'origin', self.a.Ox, self.a.Oy
    def Transform(self, p):
        px = p.x
        py = p.y
        px -= self.a.Ox
        py -= self.a.Oy
        p.x = px*self.a.Mxx + py*self.a.Mxy
        p.y = px*self.a.Myx + py*self.a.Myy
        p.x += self.a.Ox
        p.y += self.a.Oy
        return p

Ntransform = 10
class Multiple:
    #Fancy t[Ntransform]
    #Symmetry s
    #int N
    #int Ntot
    #double roundedness
    def __init__(self, random):
        self.roundedness = random.random()
        self.s = Symmetry(random)
        self.N = Ntransform # - self.s.Nsym
        if self.N < 5:
            self.N = 5
        self.t = [0]*self.N
        for i in range(self.N):
            self.t[i] = Fancy(random)
        # self.t[0].a.c.R = 0
        # self.t[0].a.c.G = 0
        # self.t[0].a.c.B = 0
        self.Ntot = self.N*self.s.Nsym
    def Transform(self, p, r):
        i = quickrand32(r) % self.Ntot
        if i < self.N:
            return self.t[i].Transform(p)
        return self.s.Transform(p)
    def TakeApart(self):
        transforms = [('image.png', self)]
        for i in range(self.N):
            foo = Multiple(rzero())
            foo.N = 1
            foo.Ntot = 1
            foo.t[0] = self.m.t[i]
            transforms.append((fancyFilename(foo.t[0]), foo))
        return transforms
    def place_point(self, h, p):
        x = p.x*self.scale_up_by
        y = p.y*self.scale_up_by
        ix = int((x/sqrt(x**2 + self.roundedness*y**2 + 1)+1)/2*h.shape[1])
        iy = int((y/sqrt(y**2 + self.roundedness*x**2 + 1)+1)/2*h.shape[2])
        h[0, ix % h.shape[1], iy % h.shape[2]] += p.A
        h[1, ix % h.shape[1], iy % h.shape[2]] += p.R
        h[2, ix % h.shape[1], iy % h.shape[2]] += p.G
        h[3, ix % h.shape[1], iy % h.shape[2]] += p.B
    def Simulate(self, p, nx, ny):
        h = np.zeros([4, nx, ny], dtype=np.double)
        if self.Ntot == 0:
            print 'weird business'
            return h
        r = QuickRandom()
        self.scale_up_by = 1.0
        for i in xrange(4*nx*ny):
            self.place_point(h, p)
            p = self.Transform(p, r)
        meandist = 0
        norm = 0
        for i in range(h.shape[1]):
            xx = (i - h.shape[1]/2.0)/(h.shape[1]/2.0)
            for j in range(h.shape[2]):
                yy = (j - h.shape[2]/2.0)/(h.shape[2]/2.0)
                norm += h[0, i, j]
                meandist += h[0, i, j]*sqrt(xx**2 + yy**2)
                h[:,i,j] = 0
        meandist /= norm
        print 'meandist is', meandist
        self.scale_up_by = 1.0/meandist
        for i in xrange(100*nx*ny):
            self.place_point(h, p)
            p = self.Transform(p, r)
        return h

def get_colors(h):
    img = np.zeros([4, h.shape[1], h.shape[2]], dtype=np.double)
    maxa = 0
    mean_nonzero_a = 0
    num_nonzero = 0
    mina = 1e300
    for i in xrange(h.shape[1]):
        for j in xrange(h.shape[2]):
            if h[0,i,j] > maxa:
                maxa = h[0,i,j]
            if h[0,i,j] > 0 and h[0,i,j] < mina:
                mina = h[0,i,j]
            if h[0,i,j] > 0:
                mean_nonzero_a += h[0,i,j]
                num_nonzero += 1
    mean_nonzero_a /= num_nonzero
    factor = maxa/(mean_nonzero_a*mean_nonzero_a)
    norm = 1.0/log(factor*maxa)
    for i in xrange(h.shape[1]):
        for j in xrange(h.shape[2]):
            if h[0,i,j] > 0:
                a = norm*log(factor*h[0,i,j]);
                img[3,i,j] = 1
                img[0,i,j] = h[1,i,j]/h[0,i,j]*a
                img[1,i,j] = h[2,i,j]/h[0,i,j]*a
                img[2,i,j] = h[3,i,j]/h[0,i,j]*a
            else:
                img[3,i,j] = 0
    for i in xrange(h.shape[1]):
        for j in xrange(h.shape[2]):
            if img[3,i,j] == 0:
                blackrad = 2.0
                for di in xrange(-int(blackrad),int(blackrad)+1,1):
                    ii = i + di
                    if ii >= 0 and ii < h.shape[1]:
                        djmax = int(np.sqrt((blackrad+.5)**2 - di**2))
                        for dj in xrange(-djmax,djmax+1,1):
                            jj = j + dj
                            d = np.sqrt(di**2 + dj**2)
                            if jj >= 0 and jj < h.shape[2] and h[3,ii,jj] > 0:
                                v = (1.0 + blackrad - d)/blackrad
                                img[3,i,j] = max(img[3,i,j], v)
    return img
