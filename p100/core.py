"""Exact primitives for Erdos #100.

The hypothesis is scale-dependent and the conclusion is not, so the right object is
scale free.  For a finite planar set X with distinct distances d_1 < ... < d_k, the
smallest rescaling that makes every distance at least 1 and every gap at least 1 is
s = 1 / g with

        g = min( d_1, min_i (d_{i+1} - d_i) ),

so the least diameter achievable from the SHAPE of X is

        delta(X) = d_k / g.

`delta(n)` is the minimum of that over all n-point sets, and is exactly the quantity
Erdos asks to determine.  Two consequences used throughout:

  * d_k >= d_1 + (k-1) g >= k g, hence  delta(X) >= k,  the number of distinct distances;
  * equality holds if and only if d_i = i * g for every i, i.e. the distance set is an
    arithmetic progression whose common difference equals its first term.

Everything here works on exact algebraic numbers, never floats, because the whole
question is about whether gaps are exactly equal (L73: a float residual proves nothing
about an equality, and here the equalities are the content).
"""
import sys
from itertools import combinations

import sympy as sp

sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def d2(P, Q):
    """exact squared distance"""
    return sp.expand((P[0] - Q[0]) ** 2 + (P[1] - Q[1]) ** 2)


def distances(pts):
    """the exact sorted list of DISTINCT distances (not squared)"""
    vals = set()
    for P, Q in combinations(pts, 2):
        vals.add(sp.nsimplify(sp.sqrt(sp.simplify(d2(P, Q)))))
    # sympy will not sort symbolic radicals reliably; sort on high-precision floats and
    # then verify the order is strict, so an accidental tie cannot pass unnoticed
    lst = sorted(vals, key=lambda v: float(sp.N(v, 50)))
    for a, b in zip(lst, lst[1:]):
        if sp.simplify(b - a) == 0:
            raise ValueError('two distance values collapsed: %s' % [a, b])
    return lst


def gaps(ds):
    return [sp.simplify(b - a) for a, b in zip(ds, ds[1:])]


def delta(pts):
    """exact delta(X) = d_k / min(d_1, min gap), and the pieces that make it up"""
    ds = distances(pts)
    gs = gaps(ds)
    cand = [ds[0]] + gs
    g = min(cand, key=lambda v: float(sp.N(v, 50)))
    return sp.simplify(ds[-1] / g), dict(k=len(ds), d=ds, gaps=gs, g=g)


def binding(pts):
    """which constraint sets the scale: the minimum distance, or which gap"""
    ds = distances(pts)
    gs = gaps(ds)
    cand = [('d_1', ds[0])] + [('gap_%d' % (i + 1), v) for i, v in enumerate(gs)]
    return min(cand, key=lambda kv: float(sp.N(kv[1], 50)))


def is_admissible_after_scaling(pts):
    """there is always a scaling that works, provided the points are distinct and not
    all equal; this checks the degenerate cases that would make delta meaningless"""
    if len(set(map(tuple, pts))) != len(pts):
        return False, 'repeated point'
    try:
        distances(pts)
    except ValueError as e:
        return False, str(e)
    return True, 'ok'


# maximum size of a planar k-distance set: g(k) for k = 1..6.
# Erdos-Fishburn for k <= 4, Shinohara for k = 5, Wei for k = 6.  Quoted, not proved here.
GMAX = {1: 3, 2: 5, 3: 7, 4: 9, 5: 12, 6: 13}


def k_min(n):
    """least number of distinct distances an n-point planar set can have, from GMAX.
    Returns None once n exceeds the range where g(k) is known."""
    for k in sorted(GMAX):
        if GMAX[k] >= n:
            return k
    return None


def lower_bound(n):
    """delta(n) >= k_min(n).  This is Kanold's eq. (8) with eps = 1 and d_1 >= 1;
    it is NOT new here (Abh. Braunschw. Wiss. Ges. 32 (1981) 55-65)."""
    return k_min(n)
