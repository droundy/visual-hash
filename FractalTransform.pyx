#cython: nonecheck=True
#        ^^^ Turns on nonecheck globally

import random
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

cdef class Point:
    cdef public double x, y, R, G, B, A
    def __cinit__(self, x, y):
        self.x = x
        self.y = y
        self.A = 0
        self.R = 0
        self.G = 0
        self.B = 0
    def __str__(self):
        return str((self.x, self.y)) + ' color ' + str((self.R, self.G, self.B, self.A))
    cpdef Point add(self, Point p):
        return Point(self.x + p.x, self.y + p.y)
    def __add__(self, p):
        return self.add(p)
    cpdef iadd(self, Point p):
        self.x += p.x
        self.y += p.y
    def __iadd__(self, p):
        self.iadd(p)
    cpdef Point sub(self, Point p):
        return Point(self.x - p.x, self.y - p.y)
    def __sub__(self, p):
        return self.sub(p)
    cpdef isub(self, Point p):
        self.x -= p.x
        self.y -= p.y
    def __isub__(self, p):
        self.isub(p)

cdef class Transform:
    cpdef Point transform(self, Point p):
        return Point(0, 0)
    cdef double R, G, B, A
    def __call__(self, p):
        return self.transform(p)
    def __cinit__(self):
        self.A = 1
        self.R = random.uniform(0,1)
        self.G = random.uniform(0,1)
        self.B = random.uniform(0,1)
        cdef double m = self.R
        if self.G > m:
            m = self.G
        if self.B > m:
            m = self.B
        self.R /= m
        self.G /= m
        self.B /= m
    cpdef Point colortransform(self, Point p):
        p.R = (self.A*self.R + p.A*p.R)/(self.A + p.A)
        p.G = (self.A*self.G + p.A*p.G)/(self.A + p.A)
        p.B = (self.A*self.B + p.A*p.B)/(self.A + p.A)
        p.A = (self.A+p.A)/2
        return p

cdef class Affine(Transform):
    cdef public double Mxx, Mxy, Myx, Myy, Ox, Oy
    cdef public Point O
    def __cinit__(self):
        # currently we always initialize pseudorandomly, but
        # eventually we'll want to generate this deterministically.
        self.O = Point(random.uniform(-1,1), random.uniform(-1,1))
        self.Mxx = random.uniform(-1,1)
        self.Mxy = random.uniform(-1,1)
        self.Myx = random.uniform(-1,1)
        self.Myy = random.uniform(-1,1)
    cpdef Point transform(self, Point p):
        p.isub(self.O) # or p -= self.O would that be slower?
        cdef Point out = self.colortransform(p)
        out.x = p.x*self.Mxx + p.y*self.Mxy
        out.y = p.x*self.Myx + p.y*self.Myy
        return out
    def __str__(self):
        return 'M='+str(((self.Mxx, self.Mxy), (self.Myx, self.Myy))) + ' O='+str(self.O) + ' C=%g, %g, %g, %g' % (self.R, self.G, self.B, self.A)

cdef place_point(np.ndarray[DTYPE_t, ndim=3] h, Point p):
    cdef int ix = <int>((p.x+1)/2*h.shape[1])
    cdef int iy = <int>((p.y+1)/2*h.shape[2])
    h[0, ix % h.shape[1], iy % h.shape[2]] += p.A
    h[1, ix % h.shape[1], iy % h.shape[2]] += p.R
    h[2, ix % h.shape[1], iy % h.shape[2]] += p.G
    h[3, ix % h.shape[1], iy % h.shape[2]] += p.B

cpdef np.ndarray[DTYPE_t, ndim=3] Simulate(Transform t, Point p,
                                           int nx, int ny):
    cdef np.ndarray[DTYPE_t, ndim=3] h = np.zeros([4, nx,ny], dtype=DTYPE)
    for i in xrange(1000):
        place_point(h, p)
        p = t.transform(p)
    return h

cpdef np.ndarray[DTYPE_t, ndim=3] get_colors(np.ndarray[DTYPE_t, ndim=3] h):
    cdef np.ndarray[DTYPE_t, ndim=3] img = np.zeros([3, h.shape[1], h.shape[2]], dtype=DTYPE)
    cdef DTYPE_t maxa = 0
    cdef DTYPE_t mina = 1e300
    for i in xrange(h.shape[1]):
        for j in xrange(h.shape[2]):
            if h[0,i,j] > maxa:
                maxa = h[0,i,j]
            if h[0,i,j] > 0 and h[0,i,j] < mina:
                mina = h[0,i,j]
    for i in xrange(h.shape[1]):
        for j in xrange(h.shape[2]):
            img[0,i,j] = h[1,i,j]/maxa
            img[1,i,j] = h[2,i,j]/maxa
            img[2,i,j] = h[3,i,j]/maxa
    return img
