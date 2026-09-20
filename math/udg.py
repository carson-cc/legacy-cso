"""
udg.py -- exact arithmetic for unit-distance-graph constructions.

Numbers are elements of the multiquadratic field Q(sqrt(d1), sqrt(d2), ...):
an element is a finite sum  c_1*sqrt(d_1) + c_2*sqrt(d_2) + ...  with rational c_i
and squarefree positive integers d_i.  Since {sqrt(d) : d squarefree} are linearly
independent over Q, two elements are equal iff their coefficient dicts are equal,
so `==` on F is a genuine exact equality test (no epsilons anywhere).

Points P are pairs (x, y) of F.  Rotations are represented as points on the unit
circle and applied with complex multiplication (`P.cmul`).
"""
from fractions import Fraction as Fr
from math import isqrt, sqrt


def _squarefree(n):
    """Split n = s*s*d with d squarefree; return (s, d).  n must be a positive int."""
    s, d, p = 1, 1, 2
    while p * p <= n:
        while n % (p * p) == 0:
            n //= p * p
            s *= p
        if n % p == 0:
            n //= p
            d *= p
        p += 1
    return s, d * n


class F:
    """Element of Q(sqrt(d) : d squarefree), stored as {d: Fraction}."""
    __slots__ = ("c",)

    def __init__(self, c=None):
        self.c = {d: v for d, v in (c or {}).items() if v != 0}

    # ---- constructors ----
    @classmethod
    def const(cls, q):
        return cls({1: Fr(q)})

    @classmethod
    def root(cls, d, coeff=Fr(1)):
        """coeff * sqrt(d) for a positive integer d (reduced to squarefree form)."""
        s, d = _squarefree(int(d))
        return cls({d: Fr(coeff) * s})

    # ---- arithmetic ----
    def __add__(self, o):
        o = _lift(o)
        c = dict(self.c)
        for d, v in o.c.items():
            c[d] = c.get(d, 0) + v
        return F(c)

    __radd__ = __add__

    def __neg__(self):
        return F({d: -v for d, v in self.c.items()})

    def __sub__(self, o):
        return self + (-_lift(o))

    def __rsub__(self, o):
        return _lift(o) - self

    def __mul__(self, o):
        o = _lift(o)
        c = {}
        for d1, v1 in self.c.items():
            for d2, v2 in o.c.items():
                s, d = _squarefree(d1 * d2)
                c[d] = c.get(d, 0) + v1 * v2 * s
        return F(c)

    __rmul__ = __mul__

    # ---- comparison / hashing ----
    def key(self):
        return tuple(sorted(self.c.items()))

    def __eq__(self, o):
        return isinstance(o, F) and self.c == o.c

    def __ne__(self, o):
        return not self == o

    def __hash__(self):
        return hash(self.key())

    def is_zero(self):
        return not self.c

    # ---- numerics ----
    def to_float(self):
        return sum(float(v) * sqrt(d) for d, v in self.c.items())

    def __repr__(self):
        if not self.c:
            return "0"
        terms = []
        for d, v in sorted(self.c.items()):
            terms.append(str(v) if d == 1 else "%s*sqrt(%d)" % (v, d))
        return " + ".join(terms)


def _lift(x):
    if isinstance(x, F):
        return x
    return F.const(Fr(x))


class P:
    """Exact point in the plane, also used as an exact complex number."""
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x = _lift(x)
        self.y = _lift(y)

    def __add__(self, o):
        return P(self.x + o.x, self.y + o.y)

    def __sub__(self, o):
        return P(self.x - o.x, self.y - o.y)

    def __neg__(self):
        return P(-self.x, -self.y)

    def cmul(self, r):
        """Complex multiplication (self as x+iy) by r (as a+ib): rotation/scaling."""
        return P(self.x * r.x - self.y * r.y, self.x * r.y + self.y * r.x)

    def norm2(self):
        return self.x * self.x + self.y * self.y

    def key(self):
        return (self.x.key(), self.y.key())

    def __eq__(self, o):
        return isinstance(o, P) and self.x == o.x and self.y == o.y

    def __hash__(self):
        return hash(self.key())

    def to_float(self):
        return (self.x.to_float(), self.y.to_float())

    def __repr__(self):
        return "P(%r, %r)" % (self.x, self.y)


def conj(r):
    return P(r.x, -r.y)


def unit_from_cos(p, q):
    """Unit complex number with cos = p/q (0 < p < q); sin = sqrt(q^2 - p^2)/q, exact."""
    p, q = int(p), int(q)
    assert 0 <= p < q
    return P(F.const(Fr(p, q)), F.root(q * q - p * p, Fr(1, q)))


def rotate_set(pts, r):
    return [p.cmul(r) for p in pts]


def minkowski(A, B):
    """Minkowski sum {a + b}, deduplicated by exact key."""
    out = {}
    for a in A:
        for b in B:
            s = a + b
            out[s.key()] = s
    return list(out.values())


# ---- standard constants ----
ZERO = P(0, 0)
ONE_PT = P(1, 0)
# rotation by 60 degrees: (1/2, sqrt(3)/2)
OMEGA = P(F.const(Fr(1, 2)), F.root(3, Fr(1, 2)))
# origin + regular unit hexagon
HEX7 = [ZERO]
_v = ONE_PT
for _ in range(6):
    HEX7.append(_v)
    _v = _v.cmul(OMEGA)
del _v


if __name__ == "__main__":
    # self-checks
    assert OMEGA.norm2() == F.const(1)
    w6 = ONE_PT
    for _ in range(6):
        w6 = w6.cmul(OMEGA)
    assert w6 == ONE_PT
    rho = unit_from_cos(5, 6)
    assert rho.norm2() == F.const(1)
    assert (rho.cmul(conj(rho))) == ONE_PT
    assert F.root(12) == F.root(3, 2)
    assert F.root(3) * F.root(3) == F.const(3)
    assert isqrt(4) == 2
    print("udg self-checks passed; HEX7 =", len(HEX7), "points")
