"""INDEPENDENT VERIFIER for Erdos #982 artifacts.

Shares NO code with core.py, patterns.py, decide.py, tworing.py or any search
script -- everything below is re-implemented from the definitions.

Definitions used here (deliberately different algorithms from the search side):

  * squared distance          d2(p,q) = (px-qx)^2 + (py-qy)^2                [definition]
  * distinct distances at v   |{ d2(v,u) : u != v }|                         [definition]
  * strictly convex position  (Caratheodory, O(n^4), no hull algorithm):
        - all points distinct, AND
        - no three points collinear, AND
        - no point lies in the closed triangle spanned by three others.
    The search side uses an Andrew monotone-chain hull; this side never does.
  * counterexample to #982    strictly convex position AND
                              max_v (distinct distances at v) <= floor(n/2) - 1

Usage:
    python verify_artifacts.py                # verify every artifacts/*.json
    python verify_artifacts.py FILE [FILE...]
"""

import sys, os, glob, json
from fractions import Fraction
from itertools import combinations

EPS_KIND_EXACT = ('int', 'sympy')


# ------------------------------------------------------------------ coordinates

def load_coords(rec):
    kind = rec['coords_kind']
    if kind == 'int':
        pts = [(int(x), int(y)) for x, y in rec['coords']]
        return pts, 'exact-integer'
    if kind == 'rational':
        pts = [(Fraction(x), Fraction(y)) for x, y in rec['coords']]
        return pts, 'exact-rational'
    if kind == 'sympy':
        import sympy as sp
        pts = [(sp.nsimplify(sp.sympify(x)), sp.nsimplify(sp.sympify(y)))
               for x, y in rec['coords']]
        return pts, 'exact-symbolic'
    if kind == 'mp':
        from mpmath import mp, mpf
        mp.dps = int(rec.get('precision_dps', 60)) + 20
        pts = [(mpf(str(x)), mpf(str(y))) for x, y in rec['coords']]
        return pts, 'high-precision-float'
    raise ValueError('unknown coords_kind ' + kind)


def d2(p, q):
    return (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2


def orient(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


# ------------------------------------------------------ exact / symbolic zero test

def is_zero(v, mode, tol):
    if mode == 'high-precision-float':
        return abs(v) < tol
    if mode == 'exact-symbolic':
        import sympy as sp
        return sp.simplify(v) == 0
    return v == 0


def sgn(v, mode, tol):
    if mode == 'high-precision-float':
        return 0 if abs(v) < tol else (1 if v > 0 else -1)
    if mode == 'exact-symbolic':
        import sympy as sp
        s = sp.simplify(v)
        if s == 0:
            return 0
        return 1 if sp.N(s, 40) > 0 else -1
    return 0 if v == 0 else (1 if v > 0 else -1)


# --------------------------------------------------------------- the three checks

def check_distinct(pts, mode, tol):
    n = len(pts)
    for i, j in combinations(range(n), 2):
        if is_zero(d2(pts[i], pts[j]), mode, tol):
            return False, f"points {i} and {j} coincide"
    return True, ""


def check_no_three_collinear(pts, mode, tol):
    n = len(pts)
    for i, j, k in combinations(range(n), 3):
        if is_zero(orient(pts[i], pts[j], pts[k]), mode, tol):
            return False, f"points {i},{j},{k} are collinear"
    return True, ""


def point_in_closed_triangle(p, a, b, c, mode, tol):
    """True iff p is in the closed triangle abc.  Sign test, no hull code."""
    s1 = sgn(orient(a, b, p), mode, tol)
    s2 = sgn(orient(b, c, p), mode, tol)
    s3 = sgn(orient(c, a, p), mode, tol)
    has_neg = (s1 < 0) or (s2 < 0) or (s3 < 0)
    has_pos = (s1 > 0) or (s2 > 0) or (s3 > 0)
    return not (has_neg and has_pos)


def check_strictly_convex_caratheodory(pts, mode, tol):
    """Caratheodory: in the plane, p in conv(S) iff p in conv(T) for some
    T subset S with |T| <= 3.  So the set is in strictly convex position iff no
    point lies in a closed triangle of three others and no three are collinear.
    O(n^4); used for small n and as the cross-check on the O(n^2) test below."""
    n = len(pts)
    idx = range(n)
    for p in idx:
        for a, b, c in combinations([q for q in idx if q != p], 3):
            if point_in_closed_triangle(pts[p], pts[a], pts[b], pts[c], mode, tol):
                return False, f"point {p} lies in triangle {a},{b},{c}"
    return True, ""


def check_strictly_convex_halfplane(pts, mode, tol):
    """Second, independent characterisation, O(n^2) and still exact:

        p is a VERTEX of conv(S)  iff  every other point of S, seen from p,
        lies in a single OPEN halfplane through p.

    Testing 'all these vectors lie in an open halfplane' is done with cross
    products only -- no angles, no floats: the vectors lie in an open halfplane
    iff some vector d among them has all the others strictly to its left or on
    its ray, i.e. iff there is a d with cross(d, e) >= 0 for every e AND no e
    anti-parallel to d.  We test every candidate d, which is O(n^2) per point.
    """
    n = len(pts)
    for p in range(n):
        vecs = [(pts[q][0] - pts[p][0], pts[q][1] - pts[p][1])
                for q in range(n) if q != p]
        ok_p = False
        for d in vecs:
            good = True
            for e in vecs:
                cr = d[0]*e[1] - d[1]*e[0]
                s = sgn(cr, mode, tol)
                if s < 0:
                    good = False
                    break
                if s == 0:
                    # collinear with d: must point the SAME way, not opposite
                    dot = d[0]*e[0] + d[1]*e[1]
                    if sgn(dot, mode, tol) <= 0:
                        good = False
                        break
            if good:
                ok_p = True
                break
        if not ok_p:
            return False, f"point {p} is not a vertex of the hull (its view of " \
                          f"the other points is not contained in an open halfplane)"
    return True, ""


def check_strictly_convex(pts, mode, tol, cross_check=True):
    ok, msg = check_distinct(pts, mode, tol)
    if not ok:
        return False, msg
    ok, msg = check_no_three_collinear(pts, mode, tol)
    if not ok:
        return False, msg
    n = len(pts)
    ok1, msg1 = check_strictly_convex_halfplane(pts, mode, tol)
    # For small n run the O(n^4) Caratheodory test too and require agreement --
    # two different characterisations, so a bug in one is caught by the other.
    if cross_check and n <= 24:
        ok2, msg2 = check_strictly_convex_caratheodory(pts, mode, tol)
        if ok1 != ok2:
            return False, (f"INTERNAL DISAGREEMENT between the halfplane test "
                           f"({ok1}: {msg1}) and the Caratheodory test "
                           f"({ok2}: {msg2})")
        return ok1, (msg1 or msg2)
    return ok1, msg1


def per_vertex_distinct(pts, mode, tol):
    """Count distinct values of d2(v, .) for each v, from the definition."""
    n = len(pts)
    out = []
    seps = []
    for i in range(n):
        vals = []
        for j in range(n):
            if i == j:
                continue
            d = d2(pts[i], pts[j])
            hit = False
            for k, v in enumerate(vals):
                if is_zero(d - v, mode, tol):
                    hit = True
                    break
            if not hit:
                vals.append(d)
        out.append(len(vals))
        if mode == 'high-precision-float' and len(vals) > 1:
            sv = sorted(vals)
            seps.append(min(sv[t + 1] - sv[t] for t in range(len(sv) - 1)))
    return out, (min(seps) if seps else None)


# ---------------------------------------------------------------------- driver

def verify_record(rec, tol_dps=40):
    label = rec.get('label', '?')
    pts, mode = load_coords(rec)
    n = len(pts)
    tol = None
    if mode == 'high-precision-float':
        from mpmath import mpf
        tol = mpf(10) ** (-tol_dps)
    res = {'label': label, 'n': n, 'mode': mode, 'problems': []}

    conv, msg = check_strictly_convex(pts, mode, tol)
    res['convex'] = conv
    if not conv:
        res['convex_reason'] = msg

    pv, sep = per_vertex_distinct(pts, mode, tol)
    res['per_vertex'] = pv
    res['max_per_vertex'] = max(pv)
    res['target'] = n // 2
    res['is_counterexample'] = bool(conv and max(pv) <= n // 2 - 1)
    if sep is not None:
        res['min_separation_between_distinct_squared_distances'] = str(sep)

    # cross-check the record's own claims
    if rec.get('claimed_per_vertex') is not None:
        if list(rec['claimed_per_vertex']) != list(pv):
            res['problems'].append(
                f"claimed_per_vertex {rec['claimed_per_vertex']} != recomputed {pv}")
    if rec.get('claimed_convex') is not None:
        if bool(rec['claimed_convex']) != bool(conv):
            res['problems'].append(
                f"claimed_convex {rec['claimed_convex']} != recomputed {conv}")
    if rec.get('claim') == 'counterexample' and not res['is_counterexample']:
        res['problems'].append("claimed to be a COUNTEREXAMPLE but is not")
    if rec.get('claim') != 'counterexample' and res['is_counterexample']:
        res['problems'].append("NOT claimed a counterexample but IS one (!)")
    return res


def main(paths):
    if not paths:
        here = os.path.dirname(os.path.abspath(__file__))
        paths = sorted(glob.glob(os.path.join(here, 'artifacts', '*.json')))
    nbad = 0
    ncex = 0
    ntot = 0
    for p in paths:
        data = json.load(open(p))
        recs = data if isinstance(data, list) else [data]
        for rec in recs:
            r = verify_record(rec)
            ntot += 1
            flag = 'CEX!!' if r['is_counterexample'] else ('bad ' if r['problems'] else 'ok  ')
            if r['is_counterexample']:
                ncex += 1
            if r['problems']:
                nbad += 1
            atb = sum(1 for x in r['per_vertex'] if x <= r['target'] - 1)
            print(f"[{flag}] {os.path.basename(p):38s} {r['label'][:28]:28s} "
                  f"n={r['n']:3d} convex={str(r['convex']):5s} "
                  f"pv=[{min(r['per_vertex'])}..{r['max_per_vertex']}] "
                  f"target={r['target']:3d} "
                  f"vertices_at_or_below_budget={atb}/{r['n']} "
                  f"({r['mode']})")
            for pr in r['problems']:
                print("        PROBLEM:", pr)
            if 'convex_reason' in r and not r['convex']:
                print("        not convex:", r['convex_reason'])
            if 'min_separation_between_distinct_squared_distances' in r:
                print("        min gap between distinct squared distances:",
                      r['min_separation_between_distinct_squared_distances'])
    print(f"\n{ntot} records verified, {nbad} with problems, "
          f"{ncex} genuine #982 counterexamples")
    return 1 if nbad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
