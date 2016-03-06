import math

class Color:
    def __init__(self, (r, g, b)):
        self.r = r
        self.g = g
        self.b = b
        self.h = (self.r, self.g, self.b)
    def __str__(self):
        return `self.h`
    def __repr__(self):
        return 'Color({0})'.format(self.h)
    def __add__(self,rhs):
        r = min(self.r + rhs.r, 255)
        g = min(self.g + rhs.g, 255)
        b = min(self.b + rhs.b, 255)
        return Color((r, g, b))
    def __sub__(self, rhs):
        r = max(self.r - rhs.r, 0)
        g = max(self.g - rhs.g, 0)
        b = max(self.b - rhs.b, 0)
        return Color((r, g, b))
    def __eq__(self, rhs):
        return self.h == rhs.h
    def __ne__(self, rhs):
        return not self.__eq__(rhs)
    def __gt__(self, other):
        self._illegal('>')
    def __ge__(self, other):
        self._illegal('>=')
    def __lt__(self, other):
        self._illegal('<')
    def __le__(self, other):
        self._illegal('<=')
    def __nonzero__(self):
        return bool(self.h == (0, 0, 0))
    def _illegal(self, op):
        print 'Illegal operation "%s" for cyclic integers' % op
