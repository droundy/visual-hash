#cy  thon: nonecheck=True
#        ^^^ Turns o  n nonecheck globally
# cython: profile=True

from libc.math cimport log, sqrt, cos, sin, atan2, M_PI
from cpython.mem cimport PyMem_Malloc, PyMem_Free

from PIL import Image as IMG

import Color

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
    a.theta = 2*M_PI*random.random()
    a.compressme = random.gauss(0.8, 0.2)
    a.Mxx =  cos(a.theta)*a.compressme
    a.Mxy =  sin(a.theta)*a.compressme
    a.Myx = -sin(a.theta)*a.compressme
    a.Myy =  cos(a.theta)*a.compressme
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

cdef struct Symmetry:
    Affine a
    int Nsym

cdef Symmetry MakeSymmetry(random):
    cdef Symmetry s
    cdef double theta = 2*M_PI*random.random()
    cdef double translation_scale = 0.1
    s.a.Ox = random.gauss(0, translation_scale)
    s.a.Oy = random.gauss(0, translation_scale)
    cdef double nnn = random.expovariate(1.0/3)
    s.Nsym = 1 + <int>nnn
    if s.Nsym == 1 and random.randint(0,1) == 0:
        # print 'Mirror plane'
        s.Nsym = 2
        theta = 2*M_PI*random.random()
        vx = sin(theta)
        vy = cos(theta)
        s.a.Mxx = vx
        s.a.Myy = -vx
        s.a.Mxy = vy
        s.a.Myx = vy
    else:
        # print 'Rotation:', s.Nsym, 'from', nnn
        s.a.Mxx = cos(2*M_PI/s.Nsym)
        s.a.Myy = s.a.Mxx
        s.a.Mxy = sin(2*M_PI/s.Nsym)
        s.a.Myx = -s.a.Mxy
    # print 'origin', s.a.Ox, s.a.Oy
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

cdef place_point(double *h, Point p, double roundedness, double scaleup, int size):
    cdef double x = p.x*scaleup
    cdef double y = p.y*scaleup
    cdef int ix = <int>((x/sqrt(x*x + roundedness*y*y + 1)+1)/2*size)
    cdef int iy = <int>((y/sqrt(y*y + roundedness*x*x + 1)+1)/2*size)
    ix = ix % size
    iy = iy % size
    h[0*(size*size) + ix*size + iy] += p.A
    h[1*(size*size) + ix*size + iy] += p.R
    h[2*(size*size) + ix*size + iy] += p.G
    h[3*(size*size) + ix*size + iy] += p.B

cdef Simulate(double *h, CMultiple t, Point p, int size):
    if t.Ntot == 0:
        print 'weird business'
    cdef QuickRandom r
    cdef double scale_up_by = 1.0
    r.m_w = 1
    r.m_z = 2
    for i in xrange(4*size*size):
        place_point(h, p, t.roundedness, scale_up_by, size)
        p = multipleTransform(t, p, &r)
    cdef double meandist = 0
    cdef double norm = 0
    cdef double xx, yy
    for i in range(size):
        xx = (i - size/2.0)/(size/2.0)
        for j in range(size):
            yy = (j - size/2.0)/(size/2.0)
            norm += h[0*(size*size) + i*size + j]
            meandist += h[0*(size*size) + i*size + j]*sqrt(xx**2 + yy**2)
            for k in range(4):
                h[k*(size*size) + i*size + j] = 0
    meandist /= norm
    # print 'meandist is', meandist
    scale_up_by = 1.0/meandist
    for i in xrange(100*size*size):
        place_point(h, p, t.roundedness, scale_up_by, size)
        p = multipleTransform(t, p, &r)

cdef get_colors(double *img, double *h, int size):
    cdef double maxa = 0
    cdef double mean_nonzero_a = 0
    cdef int num_nonzero = 0
    cdef double mina = 1e300
    cdef double a
    for i in xrange(size):
        for j in xrange(size):
            a = h[0*(size*size) + i*size + j]
            if a > maxa:
                maxa = a
            if a > 0 and a < mina:
                mina = a
            if a > 0:
                mean_nonzero_a += a
                num_nonzero += 1
    mean_nonzero_a /= num_nonzero
    cdef double factor = maxa/(mean_nonzero_a*mean_nonzero_a)
    if factor*maxa == 1:
        factor /= 2
    print 'maxa', maxa, 'factor', factor
    print 'log(factor*maxa)', log(factor*maxa)
    cdef double norm = 1.0/log(factor*maxa)
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
                        djmax = int(sqrt((blackrad+.5)*(blackrad+.5) - di*di))
                        for dj in xrange(-djmax,djmax+1,1):
                            jj = j + dj
                            d = sqrt(di*di + dj*dj)
                            if jj >= 0 and jj < size and h[3*(size*size) + ii*size + jj] > 0:
                                v = (1.0 + blackrad - d)/blackrad
                                img[3*(size*size) + i*size + j] = max(img[3*(size*size) + i*size + j], v)

cpdef Image(random, int size = 128):
    cdef CMultiple transform = MakeCMultiple(random)
    cdef Point p = MakePoint(0.1, 0.232332)
    cdef double *h = <double *>PyMem_Malloc(size*size*4*sizeof(double))
    cdef double *colors = <double *>PyMem_Malloc(size*size*4*sizeof(double))
    Simulate(h, transform, p, size)
    img = IMG.new( 'RGBA', (size,size), "black") # create a new black image
    pixels = img.load() # create the pixel map
    get_colors(colors, h, size)
    PyMem_Free(h)

    for i in range(img.size[0]):    # for every pixel:
        for j in range(img.size[1]):
            pixels[i,j] = (int(256*colors[0*(size*size) + i*size + j]),
                           int(256*colors[1*(size*size) + i*size + j]),
                           int(256*colors[2*(size*size) + i*size + j]),
                           int(256*colors[3*(size*size) + i*size + j])) # set the colour accordingly
    PyMem_Free(colors)
    return img
