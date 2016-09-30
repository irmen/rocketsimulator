"""
Efficient 2d vector class using complex number type to store x,y coordinates.

Copyright by Irmen de Jong (irmen@razorvine.net).
Open source software license: MIT.
"""
from __future__ import division
import cmath


class Vector2D(object):
    def __init__(self, value):
        if type(value) is complex:
            self.vec = value
        else:
            self.vec = complex(*value)

    @property
    def x(self):
        return self.vec.real

    @property
    def y(self):
        return self.vec.imag

    @property
    def xy(self):
        return self.vec.real, self.vec.imag

    @property
    def length(self):
        return abs(self.vec)

    @property
    def heading(self):
        if self.vec:
            return cmath.phase(self.vec)
        else:
            raise ValueError("vector (0,0) has no defined heading")

    def rotate(self, angle):
        self.vec *= cmath.exp(angle*1j)
        return self

    def rotate_around(self, xy, angle):
        point = complex(xy[0], xy[1])
        self.vec = cmath.exp(angle*1j) * (self.vec-point) + point
        return self

    def __mul__(self, value):
        if type(value) is Vector2D:
            value = value.vec
        if type(value) is complex:
            return self.vec.real*value.imag - self.vec.imag*value.real
        return Vector2D(self.vec * value)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __add__(self, other):
        return Vector2D(self.vec + other.vec)

    def __iadd__(self, other):
        self.vec += other.vec
        return self

    def __sub__(self, other):
        return Vector2D(self.vec - other.vec)

    def __isub__(self, other):
        self.vec -= other.vec
        return self

    def __abs__(self):
        return abs(self.vec)

    def __eq__(self, other):
        return self.vec == other.vec

    def __complex__(self):
        return self.vec

    def __neg__(self):
        return Vector2D(-self.vec)

    def __hash__(self):
        return hash(self.vec)

    def __repr__(self):
        return "<Vector2D at 0x{0:x}; ({1}, {2})>".format(id(self), self.vec.real, self.vec.imag)
