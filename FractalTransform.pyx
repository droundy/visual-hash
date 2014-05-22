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

cdef class Transform:
    cpdef Point transform(self, Point p):
        return Point(0, 0)
    def __call__(self, p):
        return self.transform(p)

cdef class Affine(Transform):
    cdef public double Mxx, Mxy, Myx, Myy, Ox, Oy
    cdef public Point O
    def __init__(self):
        self.O = Point(random.uniform(-1,1), random.uniform(-1,1))
        self.Mxx = random.uniform(-1,1)
        self.Mxy = random.uniform(-1,1)
        self.Myx = random.uniform(-1,1)
        self.Myy = random.uniform(-1,1)
    cpdef Point transform(self, Point p):
        p.x -= self.O.x
        p.y -= self.O.y
        return Point(p.x*self.Mxx + p.y*self.Mxy,
                     p.x*self.Myx + p.y*self.Myy)
    def __str__(self):
        return 'M='+str(((self.Mxx, self.Mxy), (self.Myx, self.Myy))) + ' O='+str(self.O)

