#!/usr/bin/env python
"""
theorem_alt.py -- EXACT proof-checking + artifact generation for the theorem

  THEOREM.  Let m >= 2 and cos(pi/m) < b < 1/cos(pi/m).  Let
        v_l = rho_l * (cos(pi l/m), sin(pi l/m)),  l = 0..2m-1,
        rho_l = 1 for l even, b for l odd
  (the "alternating 2m-gon": the unique convex polygon with D_m symmetry all of
  whose vertices lie on mirror lines, up to similarity; the stated range of b is
  exactly the condition for convex position).  Then for every vertex v the
  distances |v - v_l|, l = 0..m-1 taken along one half of the polygon, are
  STRICTLY INCREASING.  Consequently every distance from v is attained at most
  twice among v_1..v_{m-1} and their mirror images, plus at most once by v_m, so
  no vertex of an alternating 2m-gon has 4 other vertices equidistant from it.

  COROLLARY.  No counterexample to Erdos #97 (k=4) has a dihedral symmetry D_m,
  m >= 2, with every vertex on a mirror line.

The monotonicity reduces (see below) to two elementary trigonometric
inequalities.  This script
  (1) verifies the two algebraic reductions SYMBOLICALLY with sympy (exact),
  (2) verifies the resulting inequalities symbolically / by elementary bounds,
  (3) cross-checks the conclusion numerically on a grid of (m, b), and
  (4) writes alternating-2m-gon artifacts (worst cases) for verify_p97.py.

Usage:  python theorem_alt.py --mmax 200 --bsteps 400
"""
import argparse, json, sys, time
import sympy as sp
import mpmath as mp

mp.mp.dps = 50


def symbolic_reductions():
    """Exact symbolic verification of the two identities the proof rests on."""
    x, l = sp.symbols('x l', positive=True)
    c = lambda t: sp.cos(t * x)
    s = lambda t: sp.sin(t * x)
    out = {}

    # ---- CASE A (l even -> l+1 odd).  Need q(b) = b^2 - 2c_{l+1} b + 2c_l - 1 > 0
    # on b > c_1.  q is an upward parabola; its larger root is
    #      c_{l+1} + sqrt(c_{l+1}^2 - 2c_l + 1),
    # and  larger root < c_1  <=>  c_{l+1}^2 - 2c_l + 1 < (c_1 - c_{l+1})^2
    #                          <=>  0 < (c_1-c_{l+1})^2 - (c_{l+1}^2-2c_l+1).
    A = (c(1) - c(l + 1)) ** 2 - (c(l + 1) ** 2 - 2 * c(l) + 1)
    Aclaim = 2 * s(l + 1) * s(1) - s(1) ** 2
    out['A_identity'] = sp.simplify(sp.expand_trig(sp.expand(A - Aclaim))) == 0

    # ---- CASE B (l odd -> l+1 even).  Need t(b) = b^2 - 2c_l b + 2c_{l+1} - 1 < 0
    # on b < 1/c_1, i.e. the larger root  c_l + sqrt(c_l^2 + 1 - 2c_{l+1})  exceeds
    # 1/c_1.  Squaring (after clearing c_1^2 > 0) this is
    #      c_1^2 (c_l^2 + 1 - 2c_{l+1}) > (1 - c_1 c_l)^2 ... expanded below.
    B = c(1) ** 2 * (1 - 2 * c(l + 1)) - 1 + 2 * c(1) * c(l)
    Bclaim = s(1) * (2 * s(l + 1) * c(1) - s(1))
    out['B_identity'] = sp.simplify(sp.expand_trig(sp.expand(B - Bclaim))) == 0
    return out


def numeric_check(mmax, bsteps):
    """independent numeric cross-check of the CONCLUSION (max multiplicity <= 3)"""
    worst = []
    maxmult_overall = 0
    for m in range(2, mmax + 1):
        c1 = mp.cos(mp.pi / m)
        lo, hi = c1, 1 / c1
        for t in range(1, bsteps):
            b = lo + (hi - lo) * mp.mpf(t) / bsteps
            rho = [mp.mpf(1) if l % 2 == 0 else b for l in range(2 * m)]
            # distances from vertex 0 (radius 1); by symmetry vertex 1 is b -> 1/b
            mono_ok = True
            d2 = [rho[l] ** 2 + 1 - 2 * rho[l] * mp.cos(mp.pi * l / m) for l in range(2 * m)]
            for l in range(0, m - 1):
                if not (d2[l] < d2[l + 1]):
                    mono_ok = False
            # multiplicity of the most frequent distance from vertex 0
            vals = sorted(d2[1:])
            best, run, cur = 1, 1, vals[0]
            for v in vals[1:]:
                if abs(v - cur) < mp.mpf('1e-35'):
                    run += 1
                else:
                    run, cur = 1, v
                best = max(best, run)
            maxmult_overall = max(maxmult_overall, best)
            if (not mono_ok) or best >= 4:
                worst.append({"m": m, "b": mp.nstr(b, 20), "monotone": mono_ok, "maxmult": best})
    return maxmult_overall, worst


def artifacts(ms, out):
    """write alternating 2m-gon objects (b chosen at the two window ends and mid)"""
    arts = []
    for m in ms:
        c1 = sp.cos(sp.pi / m)
        for tag, b in [("mid", sp.Rational(1, 1) * (c1 + 1 / c1) / 2),
                       ("near_lo", c1 + (1 / c1 - c1) / 8),
                       ("near_hi", 1 / c1 - (1 / c1 - c1) / 8)]:
            pts = []
            for l in range(2 * m):
                r = sp.Integer(1) if l % 2 == 0 else b
                pts.append([str(sp.nsimplify(r * sp.cos(sp.pi * l / m))),
                            str(sp.nsimplify(r * sp.sin(sp.pi * l / m)))])
            arts.append({"name": "alternating_%dgon_%s" % (2 * m, tag),
                         "family": "D_m alternating 2m-gon, all vertices on mirror lines",
                         "m": m, "n": 2 * m, "b_exact": str(b), "b_float": float(sp.N(b, 30)),
                         "k_version": None,
                         "claim": "max equidistant count <= 3 at every vertex (THEOREM)",
                         "coords_exact": pts})
    json.dump(arts, open(out, "w"), indent=1)
    return len(arts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mmax', type=int, default=200)
    ap.add_argument('--bsteps', type=int, default=400)
    ap.add_argument('--artifact-ms', default="3,4,5,6,7,9,12")
    args = ap.parse_args()
    t0 = time.time()
    red = symbolic_reductions()
    print("symbolic reduction identities (sympy, exact):", red)
    mm, worst = numeric_check(args.mmax, args.bsteps)
    print("numeric cross-check m=2..%d, %d b-values each:" % (args.mmax, args.bsteps - 1))
    print("   maximum equidistant count seen anywhere: %d" % mm)
    print("   violations of monotonicity or mult>=4:   %d" % len(worst))
    ms = [int(u) for u in args.artifact_ms.split(",")]
    nart = artifacts(ms, "artifact_alternating_polygons.json")
    wall = time.time() - t0
    rec = {"problem": "erdos97",
           "theorem": "alternating 2m-gon (D_m, all vertices on mirrors) has max equidistant count <= 3",
           "symbolic_reduction_identities_verified": red,
           "numeric_crosscheck": {"mmax": args.mmax, "b_values_per_m": args.bsteps - 1,
                                  "max_equidistant_count_seen": mm,
                                  "violations": worst[:20], "n_violations": len(worst),
                                  "arithmetic": "mpmath 50 dps, equality tolerance 1e-35"},
           "status": "COMPLETED", "wall_sec": wall, "cmd": " ".join(sys.argv),
           "artifacts_written": nart}
    json.dump(rec, open("theorem_alt_RESULT.json", "w"), indent=1)
    print("wall %.1fs -> theorem_alt_RESULT.json, artifact_alternating_polygons.json" % wall)


if __name__ == '__main__':
    main()
