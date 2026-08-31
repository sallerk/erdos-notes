#!/usr/bin/env python
"""
verify_p97.py -- INDEPENDENT verifier for Erdos problem #97 artifacts.

Standalone.  Shares NO code with any search/construction script in this project.
Re-derives everything from the definitions:

  * "convex polygon on the point set" :  the n points, in some cyclic order,
        form a simple polygon in which every turn is a strict left turn and the
        total turning is exactly 2*pi.  (=> all n points are extreme points of
        their hull, no 3 collinear.)   Checked with exact sign tests.

  * "vertex v has k other vertices equidistant from it" :  there is a value r
        and k distinct other vertices u with |v-u| = r exactly.  Checked by
        exact comparison of SQUARED distances.

JSON schema accepted (one artifact per file):

{
  "name": str,
  "k_version": 3 | 4,          # which version of #97 the object claims to satisfy
  "n": int,
  "coords_exact": [[xstr, ystr], ...],     # sympy-parseable exact expressions
  "coords_float": [[x, y], ...],           # optional, decimal, only used for ordering
  "claimed_min_multiplicity": int,         # optional
  "common_distance": bool                  # optional; if true all r_v claimed equal
}

Usage:   python verify_p97.py FILE.json [FILE2.json ...]
Exit code 0 iff every artifact verified.
"""
import sys, json, itertools
import sympy as sp

X = sp.Symbol('_X')
PREC = 200            # digits used only to *locate* a value once it is proven non-zero


# ----------------------------------------------------------------- exact tests
def _minpoly(e):
    try:
        return sp.minimal_polynomial(e, X, polys=True)
    except Exception:
        return None


def exact_is_zero(e):
    """Return True/False, plus a string describing how it was decided."""
    e = sp.expand(e)
    if e == 0:
        return True, "syntactic"
    z = sp.simplify(e)
    if z == 0:
        return True, "simplify"
    if z.is_number:
        if z.is_zero is True:
            return True, "is_zero"
        if z.is_zero is False:
            return False, "is_zero"
    p = _minpoly(z)
    if p is not None:
        # z is algebraic; z==0 iff its minimal polynomial is X
        return (p.as_expr() == X), "minimal_polynomial"
    # last resort: high precision.  flagged by the caller.
    v = sp.N(z, PREC)
    return (abs(v) < sp.Float(10) ** (-PREC // 2)), "HIGHPREC(%s)" % sp.nstr(v, 6)


def exact_sign(e):
    """(sign in {-1,0,1}, method, margin).  Rigorous when method != 'HIGHPREC'.

    For a non-zero algebraic number a with minimal polynomial
    sum_{i} c_i X^i  (integer c_i, c_0 != 0), 1/a is a root of the reversed
    polynomial, so |1/a| <= 1 + max|c_i|/|c_0|, i.e. |a| >= |c_0|/(|c_0|+max|c_i|).
    Evaluating to PREC digits therefore determines the sign with certainty
    whenever the evaluation exceeds that bound.
    """
    isz, how = exact_is_zero(e)
    if isz:
        return 0, how, sp.Integer(0)
    z = sp.simplify(e)
    p = _minpoly(z)
    v = sp.N(z, PREC)
    if p is None:
        return (1 if v > 0 else -1), "HIGHPREC", abs(v)
    co = [sp.Integer(c) for c in sp.Poly(p, X).all_coeffs()]
    den = sp.lcm([sp.denom(c) for c in co]) if any(sp.denom(c) != 1 for c in co) else 1
    co = [sp.Integer(c * den) for c in co]
    c0 = co[-1]
    if c0 == 0:
        return (1 if v > 0 else -1), "HIGHPREC", abs(v)
    bound = sp.Rational(abs(c0), abs(c0) + max(abs(c) for c in co))
    if abs(v) > sp.N(bound, 30) and abs(v) > sp.Float(10) ** (-PREC // 3):
        return (1 if v > 0 else -1), "minpoly+bound", abs(v)
    return (1 if v > 0 else -1), "HIGHPREC", abs(v)


# ------------------------------------------------------------------- geometry
def cross(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def d2(a, b):
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


def upper(d, sgn):
    """half-plane class of a direction vector d (as a pair of exact exprs)."""
    sy = sgn(d[1])
    if sy > 0:
        return 1
    if sy < 0:
        return 0
    sx = sgn(d[0])
    return 1 if sx > 0 else 0


def verify_float(art, tol, verbose=True):
    """FLOAT path, used only for near-misses that have no exact coordinates.
    Everything it reports is float64 with the stated tolerance -- NOT a proof."""
    import math
    P = [(float(a), float(b)) for a, b in art["coords_float"]]
    n = len(P)
    cx = sum(p[0] for p in P) / n
    cy = sum(p[1] for p in P) / n
    o = sorted(range(n), key=lambda i: math.atan2(P[i][1] - cy, P[i][0] - cx))
    Q = [P[i] for i in o]
    crs = [ (Q[(i+1)%n][0]-Q[i][0])*(Q[(i+2)%n][1]-Q[(i+1)%n][1])
          - (Q[(i+1)%n][1]-Q[i][1])*(Q[(i+2)%n][0]-Q[(i+1)%n][0]) for i in range(n)]
    convex = min(crs) > 0
    per = []
    for i in range(n):
        d = sorted(math.hypot(P[i][0]-P[j][0], P[i][1]-P[j][1]) for j in range(n) if j != i)
        best = 1
        for a in range(n - 1):
            c = sum(1 for b in range(n - 1) if abs(d[b] - d[a]) <= tol)
            best = max(best, c)
        per.append(best)
    rep = {"name": art.get("name", "?"), "n": n, "arithmetic": "float64",
           "tolerance": tol, "exact": False,
           "convex_position": bool(convex), "min_convexity_cross": min(crs),
           "per_vertex_max_equidistant_count": per, "min_multiplicity": min(per),
           "deficient_vertices_k4": [i for i, c in enumerate(per) if c < 4],
           "deficient_vertices_k3": [i for i, c in enumerate(per) if c < 3]}
    rep["VERDICT"] = "FLOAT-CHECKED (not a proof)"
    if verbose:
        print("  [float, tol=%g] n=%d convex=%s min mult=%d counts=%s"
              % (tol, n, convex, min(per), per))
    return True, rep


def verify(art, verbose=True, tol=1e-9):
    if "coords_exact" not in art:
        return verify_float(art, tol, verbose)
    name = art.get("name", "?")
    kv = art.get("k_version")
    pts = [(sp.sympify(a), sp.sympify(b)) for a, b in art["coords_exact"]]
    n = len(pts)
    report = {"name": name, "n": n, "k_version": kv}
    ok = True
    methods = set()

    def sgn(e):
        s, m, _ = exact_sign(e)
        methods.add(m)
        return s

    # ---- 1. all points distinct (exact)
    for i, j in itertools.combinations(range(n), 2):
        isz, m = exact_is_zero(d2(pts[i], pts[j]))
        methods.add(m)
        if isz:
            print("  FAIL: points %d and %d coincide" % (i, j))
            ok = False
    # ---- 2. cyclic order.  Use the supplied float coords (or numeric evaluation)
    #         only to *propose* an order; every subsequent test is exact.
    fl = art.get("coords_float")
    if fl is None:
        fl = [(float(sp.N(p[0], 50)), float(sp.N(p[1], 50))) for p in pts]
    cx = sum(p[0] for p in fl) / n
    cy = sum(p[1] for p in fl) / n
    import math
    order = sorted(range(n), key=lambda i: math.atan2(fl[i][1] - cy, fl[i][0] - cx))
    P = [pts[i] for i in order]

    # ---- 3. strict convexity: every turn a strict left turn (exact signs)
    turns = []
    for i in range(n):
        s = sgn(cross(P[i], P[(i + 1) % n], P[(i + 2) % n]))
        turns.append(s)
    if not all(t == 1 for t in turns):
        bad = [order[i] for i, t in enumerate(turns) if t != 1]
        print("  FAIL: non-left turn at vertices %s (signs %s)" % (bad, turns))
        ok = False

    # ---- 4. total turning is exactly 2*pi:  in ccw order the edge directions
    #         are angularly sorted, so the angle wraps past the +x axis once.
    dirs = [(P[(i + 1) % n][0] - P[i][0], P[(i + 1) % n][1] - P[i][1]) for i in range(n)]
    wraps = 0
    for i in range(n):
        a, b = dirs[i], dirs[(i + 1) % n]
        ua, ub = upper(a, sgn), upper(b, sgn)
        if ua > ub:
            wraps += 1                       # crossed the +x axis going ccw
        elif ua == ub and sgn(a[0] * b[1] - a[1] * b[0]) < 0:
            wraps += 1
    if wraps != 1:
        print("  FAIL: total turning is %d*2pi, not 2pi (self-intersecting)" % wraps)
        ok = False
    report["convex_position"] = ok

    # ---- 5. equidistance multiplicities, exact.
    per_vertex = []
    minmult = 10 ** 9
    for i in range(n):
        ds = [d2(pts[i], pts[j]) for j in range(n) if j != i]
        idx = [j for j in range(n) if j != i]
        classes = []          # list of (representative_expr, [vertex ids])
        for t, j in zip(ds, idx):
            placed = False
            for cl in classes:
                isz, m = exact_is_zero(t - cl[0])
                methods.add(m)
                if isz:
                    cl[1].append(j)
                    placed = True
                    break
            if not placed:
                classes.append((t, [j]))
        best = max(classes, key=lambda c: len(c[1]))
        mult = len(best[1])
        minmult = min(minmult, mult)
        per_vertex.append({"vertex": i,
                           "max_equidistant_count": mult,
                           "equidistant_set": sorted(best[1]),
                           "radius_sq": sp.srepr(sp.simplify(best[0]))[:400],
                           "radius_sq_num": str(sp.N(sp.sqrt(sp.simplify(best[0])), 30)),
                           "all_class_sizes": sorted((len(c[1]) for c in classes), reverse=True)})
    report["per_vertex"] = per_vertex
    report["min_multiplicity"] = minmult
    report["deficient_vertices_k3"] = [d["vertex"] for d in per_vertex if d["max_equidistant_count"] < 3]
    report["deficient_vertices_k4"] = [d["vertex"] for d in per_vertex if d["max_equidistant_count"] < 4]
    report["arithmetic_methods"] = sorted(methods)
    report["exact"] = not any(m.startswith("HIGHPREC") for m in methods)

    if kv is not None:
        need = kv
        if minmult < need:
            print("  FAIL: claimed k=%d but min multiplicity is %d (deficient: %s)"
                  % (need, minmult, report["deficient_vertices_k4" if need == 4 else "deficient_vertices_k3"]))
            ok = False
    cd = art.get("common_distance")
    if cd:
        r0 = sp.simplify(sp.sympify(per_vertex[0]["radius_sq"]))
        # recompute rather than trust the srepr round-trip
        rs = []
        for i in range(n):
            ds = [d2(pts[i], pts[j]) for j in range(n) if j != i]
            best = None
            for t in ds:
                c = sum(1 for u in ds if exact_is_zero(t - u)[0])
                if best is None or c > best[1]:
                    best = (t, c)
            rs.append(best[0])
        same = all(exact_is_zero(rs[0] - r)[0] for r in rs)
        report["common_distance_verified"] = bool(same)
        if not same:
            print("  FAIL: claimed common distance, but the radii differ")
            ok = False

    report["VERDICT"] = "VERIFIED" if ok else "FAILED"
    if verbose:
        print("  n=%d  convex=%s  min multiplicity=%d  exact=%s  methods=%s"
              % (n, report["convex_position"], minmult, report["exact"], sorted(methods)))
        print("  per-vertex max equidistant counts: %s"
              % [d["max_equidistant_count"] for d in per_vertex])
        print("  => satisfies k=3 version: %s ;  k=4 version: %s"
              % (minmult >= 3, minmult >= 4))
    return ok, report


def main():
    files = sys.argv[1:]
    if not files:
        print(__doc__)
        return 1
    allok = True
    for f in files:
        print("=== %s" % f)
        art = json.load(open(f))
        arts = art if isinstance(art, list) else [art]
        for a in arts:
            print(" -- %s" % a.get("name", "?"))
            ok, rep = verify(a)
            allok &= ok
            print("  VERDICT: %s" % rep["VERDICT"])
            out = f.replace(".json", "") + ".verify.json"
            json.dump(rep, open(out, "w"), indent=1, default=str)
            print("  report -> %s" % out)
    return 0 if allok else 2


if __name__ == "__main__":
    sys.exit(main())
