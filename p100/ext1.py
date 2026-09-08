"""One-point extensions of a rigid few-distance set, exactly enumerated.

Given a k-distance set X and its distance values d_1 < ... < d_k, every point P whose
distances to X all lie in {d_1..d_k} together with AT MOST ONE new value is found by a
finite computation: fix any two points A, B of X and two radii r_A, r_B from the values,
intersect the circles, and read off the remaining distances.  If P's distances to A and
B are both old values, P is one of the <= 2 intersection points.  If P has a new value t
to some point, P still has old distances to at least |X| - (number of t's); with a new
value to at most |X| - 2 points, P is again pinned by two old-value circles.  So the
search over pairs and radius pairs is complete for extensions in which at least two
distances to X are old values.  The remaining case (a point with new-value distances to
all but at most one point of X) is a (k+1)-distance set with one distance almost
constant, and is handled separately below by intersecting one old-value circle with the
equidistance conditions (P equidistant from two points of X puts P on a bisector line).

This gives delta(|X|+1) upper bounds from a known optimum, and a control: an extension
with NO new value would be a (|X|+1)-point k-distance set.

Usage: python ext1.py piepmeyer
"""
import sys
import json
from itertools import combinations, product

import mpmath as mp
import sympy as sp

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
mp.mp.dps = 60
TOL = mp.mpf('1e-45')


def load_piepmeyer():
    from piepmeyer import route_B
    pts = route_B()
    return [(mp.mpf(str(sp.N(x, 70))), mp.mpf(str(sp.N(y, 70)))) for x, y in pts], pts


def dist(P, Q):
    return mp.sqrt((P[0] - Q[0]) ** 2 + (P[1] - Q[1]) ** 2)


def values_of(pts):
    vals = []
    for P, Q in combinations(pts, 2):
        d = dist(P, Q)
        if not any(abs(d - v) < TOL for v in vals):
            vals.append(d)
    return sorted(vals)


def circle_meet(A, rA, B, rB):
    """intersection points of two circles, 60-digit"""
    dx, dy = B[0] - A[0], B[1] - A[1]
    d = mp.sqrt(dx * dx + dy * dy)
    if d < TOL or d > rA + rB + TOL or d < abs(rA - rB) - TOL:
        return []
    a = (rA * rA - rB * rB + d * d) / (2 * d)
    h2 = rA * rA - a * a
    if h2 < -TOL:
        return []
    h = mp.sqrt(max(h2, mp.mpf(0)))
    mx, my = A[0] + a * dx / d, A[1] + a * dy / d
    out = [(mx + h * dy / d, my - h * dx / d)]
    if h > TOL:
        out.append((mx - h * dy / d, my + h * dx / d))
    return out


def classify(P, pts, vals):
    """distances from P to pts: which are old values, and the set of new ones"""
    new = []
    old = 0
    for Q in pts:
        d = dist(P, Q)
        if d < TOL:
            return None
        if any(abs(d - v) < TOL for v in vals):
            old += 1
        else:
            if not any(abs(d - w) < TOL for w in new):
                new.append(d)
    return old, new


def delta_of(vals):
    gaps = [b - a for a, b in zip(vals, vals[1:])]
    g = min([vals[0]] + gaps)
    return vals[-1] / g


def run(pts, name):
    n = len(pts)
    vals = values_of(pts)
    print('%s: %d points, %d distances, delta = %s' % (name, n, len(vals), mp.nstr(delta_of(vals), 12)))
    found = {}
    tried = 0
    # case 1: two old-value distances pin P
    for (i, j) in combinations(range(n), 2):
        for rA, rB in product(vals, repeat=2):
            for P in circle_meet(pts[i], rA, pts[j], rB):
                tried += 1
                c = classify(P, pts, vals)
                if c is None:
                    continue
                old, new = c
                if len(new) <= 1:
                    allv = sorted(vals + new)
                    key = tuple(mp.nstr(v, 30) for v in allv) + (mp.nstr(P[0], 30), mp.nstr(P[1], 30))
                    found[key] = dict(point=[mp.nstr(P[0], 40), mp.nstr(P[1], 40)], old=old,
                                      new=[mp.nstr(v, 40) for v in new],
                                      delta=mp.nstr(delta_of(allv), 20), k=len(allv),
                                      values=[mp.nstr(v, 20) for v in allv])
    # case 2: at most one old-value distance; P equidistant (new value t) from >= n-1 points.
    # n-1 >= 8 points equidistant from P lie on a circle about P: impossible for a set with
    # no 8 concyclic points; checked directly by circumcentres of triples.
    for (i, j, l) in combinations(range(n), 3):
        A, B, C = pts[i], pts[j], pts[l]
        d = 2 * (A[0] * (B[1] - C[1]) + B[0] * (C[1] - A[1]) + C[0] * (A[1] - B[1]))
        if abs(d) < TOL:
            continue
        a2 = A[0] ** 2 + A[1] ** 2; b2 = B[0] ** 2 + B[1] ** 2; c2 = C[0] ** 2 + C[1] ** 2
        P = ((a2 * (B[1] - C[1]) + b2 * (C[1] - A[1]) + c2 * (A[1] - B[1])) / d,
             (a2 * (C[0] - B[0]) + b2 * (A[0] - C[0]) + c2 * (B[0] - A[0])) / d)
        c = classify(P, pts, vals)
        if c is None:
            continue
        old, new = c
        if len(new) <= 1 and old <= 1:
            allv = sorted(vals + new)
            key = tuple(mp.nstr(v, 30) for v in allv) + (mp.nstr(P[0], 30), mp.nstr(P[1], 30))
            found[key] = dict(point=[mp.nstr(P[0], 40), mp.nstr(P[1], 40)], old=old,
                              new=[mp.nstr(v, 40) for v in new],
                              delta=mp.nstr(delta_of(allv), 20), k=len(allv),
                              values=[mp.nstr(v, 20) for v in allv], case=2)
    rows = sorted(found.values(), key=lambda r: mp.mpf(r['delta']))
    print('  %d candidate points examined; %d extensions with <= 1 new distance' % (tried, len(rows)))
    nonew = [r for r in rows if not r['new']]
    print('  extensions with NO new distance (would be a %d-point %d-distance set): %d'
          % (n + 1, len(vals), len(nonew)))
    for r in rows[:12]:
        print('  delta(%d) <= %s  k=%d  old=%d  new=%s' % (n + 1, r['delta'][:14], r['k'], r['old'],
                                                           [x[:12] for x in r['new']]))
    json.dump(dict(base=name, n=n, values=[mp.nstr(v, 40) for v in vals], tried=tried,
                   extensions=rows, no_new_value=len(nonew), completed=True),
              open('results/ext1_%s.json' % name, 'w'), indent=1)
    return rows


if __name__ == '__main__':
    which = sys.argv[1] if len(sys.argv) > 1 else 'piepmeyer'
    if which == 'piepmeyer':
        pts, _ = load_piepmeyer()
        run(pts, 'piepmeyer')
    elif which == 'nonagon':
        pts = [(mp.cos(2 * mp.pi * i / 9), mp.sin(2 * mp.pi * i / 9)) for i in range(9)]
        run(pts, 'nonagon')
