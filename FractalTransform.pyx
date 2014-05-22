#cython: nonecheck=True
#        ^^^ Turns on nonecheck globally

import random

cdef class Point:
    cdef public double x
    cdef public double y
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __str__(self):
        return str((self.x, self.y))
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
    def __call__(self, p):
        return self.transform(p)

cdef class Affine(Transform):
    cdef public double Mxx, Mxy, Myx, Myy, Ox, Oy
    cdef public Point O
    def __init__(self):
        # currently we always initialize pseudorandomly, but
        # eventually we'll want to generate this deterministically.
        self.O = Point(random.uniform(-1,1), random.uniform(-1,1))
        self.Mxx = random.uniform(-1,1)
        self.Mxy = random.uniform(-1,1)
        self.Myx = random.uniform(-1,1)
        self.Myy = random.uniform(-1,1)
    cpdef Point transform(self, Point p):
        p.isub(self.O) # or p -= self.O would that be slower?
        return Point(p.x*self.Mxx + p.y*self.Mxy,
                     p.x*self.Myx + p.y*self.Myy)
    def __str__(self):
        return 'M='+str(((self.Mxx, self.Mxy), (self.Myx, self.Myy))) + ' O='+str(self.O)

