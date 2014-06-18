from __future__ import division
#cython: nonecheck=True
#        ^^^ Turns on nonecheck globally

#from libc.math cimport log, sqrt, cos, sin, atan2
from math import log, sqrt, cos, sin, atan2, pi

import random
import array

from PIL import Image as IMG
import Color

# QuickRandom is a low-quality random number generator used for the
# chaos game only.  It should ensure that we always generate an
# identical image for a given resolution.
class QuickRandom:
    m_w = 1
    m_z = 2
    def quickrand32(self):
        self.m_z = 36969 * (self.m_z & 65535) + (self.m_z >> 16)
        self.m_w = 18000 * (self.m_w & 65535) + (self.m_w >> 16)
        return ((self.m_z << 16) + self.m_w) & 0xFFFFFFFF  # 32-bit result

class Point:
    def __init__(self, x,y,R=0,G=0,B=0,A=0):
        self.x = x
        self.y = y
        self.R = R
        self.G = G
        self.B = B
        self.A = A
    def __str__(self):
        return str({'A': self.A,
                    'B': self.B,
                    'G': self.G,
                    'R': self.R,
                    'x': self.x,
                    'y': self.y})


class ColorTransform:
    def __init__(self, random):
        self.R, self.G, self.B = Color.DistinctColorFloat(random)
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
        out = Point(p.x, p.y)
        out.R = (c.A*c.R + p.A*p.R)/(c.A + p.A)
        out.G = (c.A*c.G + p.A*p.G)/(c.A + p.A)
        out.B = (c.A*c.B + p.A*p.B)/(c.A + p.A)
        out.A = (c.A+p.A)/2
        return out

class Affine:
    def __init__(self, random):
        self.c = ColorTransform(random)
        # currently we always initialize pseudorandomly, but
        # eventually we'll want to generate this deterministically.
        self.theta = 2*pi*random.random()
        self.compressme = random.signed_expovariate(0.8, 0.2)
        self.Mxx =  cos(self.theta)*self.compressme
        self.Mxy =  sin(self.theta)*self.compressme
        self.Myx = -sin(self.theta)*self.compressme
        self.Myy =  cos(self.theta)*self.compressme
        translation_scale = 0.8
        self.Ox = random.signed_expovariate(0, translation_scale)
        self.Oy = random.signed_expovariate(0, translation_scale)
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
        self.spiralness = random.signed_expovariate(0, 3)
        self.radius = random.signed_expovariate(.4, .2)
        self.bounciness = random.signed_expovariate(2, 2)
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
        theta = 2*pi*random.random()
        translation_scale = 0.1
        self.a = Affine(rzero())
        self.a.Ox = random.signed_expovariate(0, translation_scale)
        self.a.Oy = random.signed_expovariate(0, translation_scale)
        nnn = random.expovariate(1.0/3)
        self.Nsym = 1 + int(nnn)
        if self.Nsym == 1 and random.randint(0,1) == 0:
            # print 'Mirror plane'
            self.Nsym = 2
            theta = 2*pi*random.random()
            vx = sin(theta)
            vy = cos(theta)
            self.a.Mxx = vx
            self.a.Myy = -vx
            self.a.Mxy = vy
            self.a.Myx = vy
        else:
            # print 'Rotation:', self.Nsym, 'from', nnn
            self.a.Mxx = cos(2*pi/self.Nsym)
            self.a.Myy = self.a.Mxx
            self.a.Mxy = sin(2*pi/self.Nsym)
            self.a.Myx = -self.a.Mxy
        # print 'origin', self.a.Ox, self.a.Oy
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
        i = r.quickrand32() % self.Ntot
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
    def place_point(self, h, p, size):
        x = p.x*self.scale_up_by
        y = p.y*self.scale_up_by
        ix = int((x/sqrt(x*x + self.roundedness*y*y + 1)+1)/2*size)
        iy = int((y/sqrt(y*y + self.roundedness*x*x + 1)+1)/2*size)
        h[0*(size*size) + (ix % size)*size + iy % size] += p.A
        h[1*(size*size) + (ix % size)*size + iy % size] += p.R
        h[2*(size*size) + (ix % size)*size + iy % size] += p.G
        h[3*(size*size) + (ix % size)*size + iy % size] += p.B
    def Simulate(self, p, size):
        h = array.array('d', [0]*(size*size*4))
        if self.Ntot == 0:
            print 'weird business'
            return h
        r = QuickRandom()
        self.scale_up_by = 1.0
        for i in xrange(4*size*size):
            self.place_point(h, p, size)
            p = self.Transform(p, r)
        meandist = 0
        norm = 0
        for i in range(size):
            xx = (i - size/2.0)/(size/2.0)
            for j in range(size):
                yy = (j - size/2.0)/(size/2.0)
                norm += h[0*(size*size) + i*size + j]
                meandist += h[0*(size*size) + i*size + j]*sqrt(xx**2 + yy**2)
                h[0*(size*size) + i*size + j] = 0
                h[1*(size*size) + i*size + j] = 0
                h[2*(size*size) + i*size + j] = 0
                h[3*(size*size) + i*size + j] = 0
        meandist /= norm
        # print 'meandist is', meandist
        self.scale_up_by = 1.0/meandist
        for i in xrange(100*size*size):
            self.place_point(h, p, size)
            p = self.Transform(p, r)
        return h

def get_colors(h, size):
    img = array.array('d', [0]*(size*size*4))
    maxa = 0
    mean_nonzero_a = 0
    num_nonzero = 0
    mina = 1e300
    for i in xrange(size):
        for j in xrange(size):
            if h[0*(size*size) + i*size + j] > maxa:
                maxa = h[0*(size*size) + i*size + j]
            if h[0*(size*size) + i*size + j] > 0 and h[0*(size*size) + i*size + j] < mina:
                mina = h[0*(size*size) + i*size + j]
            if h[0*(size*size) + i*size + j] > 0:
                mean_nonzero_a += h[0*(size*size) + i*size + j]
                num_nonzero += 1
    mean_nonzero_a /= num_nonzero
    factor = maxa/(mean_nonzero_a*mean_nonzero_a)
    norm = 1.0/log(factor*maxa)
    for i in xrange(size):
        for j in xrange(size):
            if h[0*(size*size) + i*size + j] > 0:
                a = norm*log(factor*h[0*(size*size) + i*size + j]);
                img[3*(size*size) + i*size + j] = 1
                img[0*(size*size) + i*size + j] = h[1*(size*size) + i*size + j]/h[0*(size*size) + i*size + j]*a
                img[1*(size*size) + i*size + j] = h[2*(size*size) + i*size + j]/h[0*(size*size) + i*size + j]*a
                img[2*(size*size) + i*size + j] = h[3*(size*size) + i*size + j]/h[0*(size*size) + i*size + j]*a
            else:
                img[3*(size*size) + i*size + j] = 0
    for i in xrange(size):
        for j in xrange(size):
            if img[3*(size*size) + i*size + j] == 0:
                blackrad = 2.0
                for di in xrange(-int(blackrad),int(blackrad)+1,1):
                    ii = i + di
                    if ii >= 0 and ii < size:
                        djmax = int(sqrt((blackrad+.5)**2 - di**2))
                        for dj in xrange(-djmax,djmax+1,1):
                            jj = j + dj
                            d = sqrt(di**2 + dj**2)
                            if jj >= 0 and jj < size and h[3*(size*size) + ii*size + jj] > 0:
                                v = (1.0 + blackrad - d)/blackrad
                                img[3*(size*size) + i*size + j] = max(img[3*(size*size) + i*size + j], v)
    return img

def Image(random, size = 128):
    """
    Create a hash as a fractal flame.

    Given a random generator (and optionally a size in pixels) return a PIL
    Image that is a strong cryptographic hash of the string.
    """
    transform = Multiple(random)
    h = transform.Simulate(Point(.1,.232332), size)
    img = IMG.new( 'RGBA', (size,size), "black") # create a new black image
    pixels = img.load() # create the pixel map
    colors = get_colors(h, size)

    for i in range(img.size[0]):    # for every pixel:
        for j in range(img.size[1]):
            pixels[i,j] = (int(256*colors[0*(size*size) + i*size + j]),
                           int(256*colors[1*(size*size) + i*size + j]),
                           int(256*colors[2*(size*size) + i*size + j]),
                           int(256*colors[3*(size*size) + i*size + j])) # set the colour accordingly
    return img
