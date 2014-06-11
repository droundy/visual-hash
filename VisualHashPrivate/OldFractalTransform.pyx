#cython: nonecheck=True
#        ^^^ Turns on nonecheck globally

from libc.math cimport log, sqrt, cos, sin, atan2

import Color

import numpy as np
cimport numpy as np
# We now need to fix a datatype for our arrays. I've used the variable
# DTYPE for this, which is assigned to the usual NumPy runtime
# type info object.
DTYPE = np.double
# "ctypedef" assigns a corresponding compile-time type to DTYPE_t. For
# every type in the numpy module there's a corresponding compile-time
# type with a _t-suffix.
ctypedef np.double_t DTYPE_t

# QuickRandom is a low-quality random number generator used for the
# chaos game only.  It should ensure that we always generate an
# identical image for a given resolution.
cdef struct QuickRandom:
  unsigned int m_w, m_z
cdef unsigned int quickrand32(QuickRandom *s):
    s.m_z = 36969 * (s.m_z & 65535) + (s.m_z >> 16)
    s.m_w = 18000 * (s.m_w & 65535) + (s.m_w >> 16)
    return (s.m_z << 16) + s.m_w  # 32-bit result

cdef struct Point:
    double x, y, R, G, B, A
def MakePoint(x, y):
    cdef Point p = Point(x, y, 0,0,0,0)
    return p

cdef struct ColorTransform:
    double R, G, B, A

cdef ColorTransform MakeColorTransform(random):
    cdef ColorTransform out
    out.A = 1
    out.R, out.G, out.B = Color.DistinctColorFloat(random)
    # out.R = random.uniform(0,1)
    # out.G = random.uniform(0,1)
    # out.B = random.uniform(0,1)
    cdef double m = out.R
    if out.G > m:
        m = out.G
    if out.B > m:
        m = out.B
    out.R /= m
    out.G /= m
    out.B /= m
    return out

cdef Point colorTransform(ColorTransform c, Point p):
    p.R = (c.A*c.R + p.A*p.R)/(c.A + p.A)
    p.G = (c.A*c.G + p.A*p.G)/(c.A + p.A)
    p.B = (c.A*c.B + p.A*p.B)/(c.A + p.A)
    p.A = (c.A+p.A)/2
    return p

cdef struct Affine:
    ColorTransform c
    double compressme, theta
    double Mxx, Mxy, Myx, Myy, Ox, Oy

cdef Affine MakeAffine(random):
    cdef Affine a
    a.c = MakeColorTransform(random)
    # currently we always initialize pseudorandomly, but
    # eventually we'll want to generate this deterministically.
    a.theta = 2*np.pi*random.random()
    rot = np.matrix([[cos(a.theta), sin(a.theta)],
                     [-sin(a.theta),cos(a.theta)]])
    a.compressme = random.gauss(0.8, 0.2)
    compress = np.matrix([[a.compressme, 0],
                          [0, a.compressme]])
    mat = compress*rot
    a.Mxx = mat[0,0]
    a.Mxy = mat[0,1]
    a.Myx = mat[1,0]
    a.Myy = mat[1,1]
    cdef double translation_scale = 0.8
    a.Ox = random.gauss(0, translation_scale)
    a.Oy = random.gauss(0, translation_scale)
    return a

cdef Point affineTransform(Affine a, Point p):
    cdef Point out = colorTransform(a.c, p)
    p.x -= a.Ox
    p.y -= a.Oy
    out.x = p.x*a.Mxx + p.y*a.Mxy # + a.Ox
    out.y = p.x*a.Myx + p.y*a.Myy # + a.Oy
    #p.x += a.Ox
    #p.y += a.Oy
    return out

cdef struct Fancy:
    Affine a
    double spiralness, radius, bounciness
    int bumps

cdef Fancy MakeFancy(random):
    cdef Fancy f
    f.a = MakeAffine(random)
    f.spiralness = random.gauss(0, 3)
    f.radius = random.gauss(.4, .2)
    f.bounciness = random.gauss(2, 2)
    f.bumps = random.randint(1, 4)
    return f

cdef Point fancyTransform(Fancy f, Point p):
    cdef Point out = affineTransform(f.a, p)
    cdef Point nex = out
    cdef double r = sqrt(out.x*out.x + out.y*out.y)
    cdef double theta = atan2(out.y, out.x)
    cdef double maxrad = f.radius*(1+f.bounciness*sin(theta*f.bumps))
    nex.x = maxrad*sin(r/maxrad)*sin(theta + f.spiralness*r)
    nex.y = maxrad*sin(r/maxrad)*cos(theta + f.spiralness*r)
    return nex

def fancyFilename(Fancy f):
    return 'image_%.2g_%.2g_%.2g_%d__%.2g_%.2g.png' % (f.radius, f.spiralness, f.bounciness, f.bumps, f.a.compressme, f.a.theta)

cdef struct Symmetry:
    Affine a
    int Nsym

cdef Symmetry MakeSymmetry(random):
    cdef Symmetry s
    cdef double theta = 2*np.pi*random.random()
    cdef double translation_scale = 0.1
    s.a.Ox = random.gauss(0, translation_scale)
    s.a.Oy = random.gauss(0, translation_scale)
    cdef double nnn = random.expovariate(1.0/3)
    s.Nsym = 1 + <int>nnn
    if s.Nsym == 1 and random.randint(0,1) == 0:
        print 'Mirror plane'
        s.Nsym = 2
        theta = 2*np.pi*random.random()
        vx = sin(theta)
        vy = cos(theta)
        s.a.Mxx = vx
        s.a.Myy = -vx
        s.a.Mxy = vy
        s.a.Myx = vy
    else:
        print 'Rotation:', s.Nsym, 'from', nnn
        s.a.Mxx = cos(2*np.pi/s.Nsym)
        s.a.Myy = s.a.Mxx
        s.a.Mxy = sin(2*np.pi/s.Nsym)
        s.a.Myx = -s.a.Mxy
    print np.array([[s.a.Mxx, s.a.Mxy],
                    [s.a.Myx, s.a.Myy]])
    print 'origin', s.a.Ox, s.a.Oy
    return s

cdef Point symmetryTransform(Symmetry s, Point p):
    cdef double px = p.x
    cdef double py = p.y
    px -= s.a.Ox
    py -= s.a.Oy
    p.x = px*s.a.Mxx + py*s.a.Mxy
    p.y = px*s.a.Myx + py*s.a.Myy
    p.x += s.a.Ox
    p.y += s.a.Oy
    return p

DEF Ntransform = 10
cdef struct CMultiple:
    Fancy t[Ntransform]
    Symmetry s
    int N
    int Ntot
    double roundedness

cdef CMultiple MakeCMultiple(random):
    cdef CMultiple m
    m.roundedness = random.random()
    m.s = MakeSymmetry(random)
    m.N = Ntransform # - m.s.Nsym
    if m.N < 5:
        m.N = 5
    cdef int i
    for i in range(m.N):
        m.t[i] = MakeFancy(random)
    # m.t[0].a.c.R = 0
    # m.t[0].a.c.G = 0
    # m.t[0].a.c.B = 0
    m.Ntot = m.N*m.s.Nsym
    return m

cdef Point multipleTransform(CMultiple m, Point p, QuickRandom *r):
    cdef int i = quickrand32(r) % m.Ntot
    if i < m.N:
        return fancyTransform(m.t[i], p)
    return symmetryTransform(m.s, p)

cdef class Multiple:
    cdef CMultiple m
    cpdef Randomize(self, random):
        self.m = MakeCMultiple(random)
        return self
    cdef Point transform(self, Point p, QuickRandom *r):
        return multipleTransform(self.m, p, r)
    def TakeApart(self):
        transforms = [('image.png', self)]
        for i in range(self.m.N):
            foo = Multiple()
            foo.m.N = 1
            foo.m.Ntot = 1
            foo.m.t[0] = self.m.t[i]
            transforms.append((fancyFilename(foo.m.t[0]), foo))
        return transforms

cdef place_point(np.ndarray[DTYPE_t, ndim=3] h, Point p, double roundedness, double scaleup):
    cdef double x = p.x*scaleup
    cdef double y = p.y*scaleup
    cdef int ix = <int>((x/sqrt(x**2 + roundedness*y**2 + 1)+1)/2*h.shape[1])
    cdef int iy = <int>((y/sqrt(y**2 + roundedness*x**2 + 1)+1)/2*h.shape[2])
    h[0, ix % h.shape[1], iy % h.shape[2]] += p.A
    h[1, ix % h.shape[1], iy % h.shape[2]] += p.R
    h[2, ix % h.shape[1], iy % h.shape[2]] += p.G
    h[3, ix % h.shape[1], iy % h.shape[2]] += p.B

cpdef np.ndarray[DTYPE_t, ndim=3] Simulate(Multiple t, Point p,
                                           int nx, int ny):
    cdef np.ndarray[DTYPE_t, ndim=3] h = np.zeros([4, nx,ny], dtype=DTYPE)
    if t.m.Ntot == 0:
        print 'weird business'
        return h
    cdef QuickRandom r
    cdef double scale_up_by = 1.0
    r.m_w = 1
    r.m_z = 2
    for i in xrange(4*nx*ny):
        place_point(h, p, t.m.roundedness, scale_up_by)
        p = multipleTransform(t.m, p, &r)
    cdef double meandist = 0
    cdef double norm = 0
    cdef double xx, yy
    for i in range(h.shape[1]):
        xx = (i - h.shape[1]/2.0)/(h.shape[1]/2.0)
        for j in range(h.shape[2]):
            yy = (j - h.shape[2]/2.0)/(h.shape[2]/2.0)
            norm += h[0, i, j]
            meandist += h[0, i, j]*sqrt(xx**2 + yy**2)
            h[:,i,j] = 0
    meandist /= norm
    print 'meandist is', meandist
    scale_up_by = 1.0/meandist
    for i in xrange(100*nx*ny):
        place_point(h, p, t.m.roundedness, scale_up_by)
        p = multipleTransform(t.m, p, &r)
    return h

cpdef np.ndarray[DTYPE_t, ndim=3] get_colors(np.ndarray[DTYPE_t, ndim=3] h):
    cdef np.ndarray[DTYPE_t, ndim=3] img = np.zeros([4, h.shape[1], h.shape[2]], dtype=DTYPE)
    cdef DTYPE_t maxa = 0
    cdef DTYPE_t mean_nonzero_a = 0
    cdef int num_nonzero = 0
    cdef DTYPE_t mina = 1e300
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
    cdef double factor = maxa/(mean_nonzero_a*mean_nonzero_a)
    cdef double norm = 1.0/log(factor*maxa)
    cdef double a
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
