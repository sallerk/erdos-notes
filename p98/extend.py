"""Decide D_gen(6) by augmenting realisable 5-point patterns.

Why augmentation.  The single-formula encoding (direct.py) finds witnesses fast but
cannot prove UNSAT: it returned unknown on n=5,k=2 after 872 s, a case we know is
unsatisfiable.  Brute-force pattern enumeration at n=6 is 3^15 = 14.3M colourings before
symmetry reduction, too many to canonicalise in Python.  Augmentation avoids both.

Soundness.  Deleting a point from a general-position set leaves a general-position set
and cannot increase the number of distinct distances.  So every realisable 6-point
pattern restricts, on each of its six 5-subsets, to a realisable 5-point pattern with at
most 3 classes.  Generating 6-patterns by extending realisable 5-patterns is therefore
COMPLETE, and filtering on "all six 5-subsets realisable" is a sound prune.

An UNKNOWN 5-pattern is treated as possibly-realisable, so nothing is lost.

Also note monotonicity gives D_gen(6) >= D_gen(5) = 3, so the only question is whether
D_gen(6) is 3 or 4 (a 4-distance witness is already verified).

Usage:  python extend.py [stage]      stage in {five, six, all}
"""
import sys, itertools, json, os, time
from multiprocessing import Pool

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import z3
from hdecide import pairs, enumerate_patterns, det4
from witness import vertex_ok

WORKERS = 5
TMO5 = 90000
TMO6 = 60000


def canon(pat, n):
    P = pairs(n)
    index = {p: i for i, p in enumerate(P)}
    best = None
    for sigma in itertools.permutations(range(n)):
        moved = []
        for (i, j) in P:
            a, b = sigma[i], sigma[j]
            moved.append(pat[index[(a, b) if a < b else (b, a)]])
        seen, ren = {}, []
        for c in moved:
            if c not in seen:
                seen[c] = len(seen)
            ren.append(seen[c])
        t = tuple(ren)
        if best is None or t < best:
            best = t
    return best


def solve(args):
    pat, n, tmo = args
    P = pairs(n)
    m = max(pat) + 1
    X = [z3.Real('x%d' % i) for i in range(n)]
    Y = [z3.Real('y%d' % i) for i in range(n)]
    D = [z3.Real('d%d' % c) for c in range(m)]
    s = z3.Solver()
    s.set('timeout', tmo)
    s.add(X[0] == 0, Y[0] == 0, Y[1] == 0, X[1] > 0, Y[2] >= 0, D[0] > 0)
    for c in range(m - 1):
        s.add(D[c] < D[c + 1])
    for idx, (i, j) in enumerate(P):
        s.add((X[i] - X[j]) ** 2 + (Y[i] - Y[j]) ** 2 == D[pat[idx]])
    for (i, j, l) in itertools.combinations(range(n), 3):
        s.add((X[j] - X[i]) * (Y[l] - Y[i]) - (X[l] - X[i]) * (Y[j] - Y[i]) != 0)
    for quad in itertools.combinations(range(n), 4):
        rows = [[X[t] ** 2 + Y[t] ** 2, X[t], Y[t], 1] for t in quad]
        s.add(det4(rows) != 0)
    r = s.check()
    if r == z3.sat:
        return pat, 'sat', str(s.model())
    return pat, ('unsat' if r == z3.unsat else 'unknown'), None


_C5 = {}


def canon5(pat):
    """memoised canonical form of a 5-point pattern (120 permutations each)"""
    v = _C5.get(pat)
    if v is None:
        v = canon(pat, 5)
        _C5[pat] = v
    return v


def restrict(pat6, drop):
    """the 5-point pattern obtained by deleting point `drop` from a 6-point pattern"""
    P6 = pairs(6)
    idx = {p: i for i, p in enumerate(P6)}
    keep = [v for v in range(6) if v != drop]
    out = []
    for (i, j) in itertools.combinations(range(5), 2):
        a, b = keep[i], keep[j]
        out.append(pat6[idx[(a, b) if a < b else (b, a)]])
    seen, ren = {}, []
    for c in out:
        if c not in seen:
            seen[c] = len(seen)
        ren.append(seen[c])
    return tuple(ren)


def stage_five():
    print('=' * 74)
    print('STAGE 1 -- decide every 5-point pattern with at most 3 classes')
    print('=' * 74)
    pats = [p for p in enumerate_patterns(5, 3) if vertex_ok(p, 5)]
    print('  %d canonical patterns after the at-most-3-per-vertex prune' % len(pats))
    t0 = time.time()
    with Pool(WORKERS) as pool:
        res = pool.map(solve, [(p, 5, TMO5) for p in pats])
    out = {'sat': [], 'unsat': [], 'unknown': []}
    for pat, r, mdl in res:
        out[r].append(list(pat))
    print('  sat %d / unsat %d / unknown %d   (%.1fs)'
          % (len(out['sat']), len(out['unsat']), len(out['unknown']), time.time() - t0))
    json.dump(out, open('five_patterns.json', 'w'), indent=1)
    print('  written: five_patterns.json')
    return out


def stage_six(five):
    print()
    print('=' * 74)
    print('STAGE 2 -- extend to 6 points and decide')
    print('=' * 74)
    # possibly-realisable 5-patterns: sat plus unknown (nothing is discarded unproven)
    ok5 = set(tuple(p) for p in five['sat']) | set(tuple(p) for p in five['unknown'])
    print('  %d possibly-realisable 5-patterns used as seeds '
          '(%d sat + %d unknown)' % (len(ok5), len(five['sat']), len(five['unknown'])))

    P6 = pairs(6)
    idx6 = {p: i for i, p in enumerate(P6)}
    cands = set()
    for seed in ok5:
        base = {}
        for n_, (i, j) in enumerate(pairs(5)):
            base[(i, j)] = seed[n_]
        for newc in itertools.product(range(3), repeat=5):
            full = [0] * 15
            for (i, j), c in base.items():
                full[idx6[(i, j)]] = c
            for v in range(5):
                full[idx6[(v, 5)]] = newc[v]
            t = tuple(full)
            if max(t) > 2:
                continue
            if not vertex_ok(t, 6):
                continue
            # Every 5-subset must itself be possibly-realisable.  `restrict` renumbers
            # CLASSES but not POINTS, while ok5 holds forms canonical in both, so the
            # restriction has to be canonicalised before the lookup.  Comparing the raw
            # restriction would silently reject valid candidates and break completeness.
            if any(canon5(restrict(t, d)) not in ok5 for d in range(6)):
                continue
            cands.add(canon(t, 6))
    print('  %d canonical 6-point candidates survive augmentation + subset filter'
          % len(cands))
    if not cands:
        print()
        print('  => no 6-point pattern with 3 classes can be realised, so D_gen(6) > 3')
        print('  => combined with the verified 4-distance witness, D_gen(6) = 4')
        json.dump({'candidates': 0, 'conclusion': 'D_gen(6) = 4'},
                  open('six_result.json', 'w'), indent=1)
        return
    t0 = time.time()
    with Pool(WORKERS) as pool:
        res = pool.map(solve, [(p, 6, TMO6) for p in sorted(cands)])
    sat = [(p, m) for p, r, m in res if r == 'sat']
    unk = [p for p, r, m in res if r == 'unknown']
    print('  sat %d / unsat %d / unknown %d   (%.1fs)'
          % (len(sat), len(res) - len(sat) - len(unk), len(unk), time.time() - t0))
    json.dump({'candidates': len(cands), 'sat': [list(p) for p, _ in sat],
               'unknown': [list(p) for p in unk],
               'model': (sat[0][1] if sat else None)},
              open('six_result.json', 'w'), indent=1)
    print('  written: six_result.json')
    if sat:
        print()
        print('  SAT -- D_gen(6) = 3.  model:')
        print('   ', sat[0][1])
    elif not unk:
        print()
        print('  all UNSAT => D_gen(6) > 3, and with the 4-distance witness, D_gen(6) = 4')
    else:
        print()
        print('  INCONCLUSIVE: %d patterns undecided, they need the pentagon.py treatment'
              % len(unk))


def stage_control():
    """The pipeline must accept a configuration we have already verified by hand.

    The 6-point triangular-lattice witness has 4 distinct distances.  Its pattern must
    (a) pass the at-most-3-per-vertex prune, (b) have all six of its 5-subsets come out
    realisable, and (c) be SAT.  If any of that fails, restrict/canon5/solve is broken
    and no UNSAT verdict from this script means anything.
    """
    print('=' * 74)
    print('CONTROL -- the pipeline on a witness already verified independently')
    print('=' * 74)
    pts = [(0, 0), (-1, 0), (-1, 2), (-3, 1), (-3, 2), (-2, 3)]     # latmin_n6_a2

    def nrm(p, q):
        da, db = p[0] - q[0], p[1] - q[1]
        return da * da + da * db + db * db
    vals = sorted({nrm(pts[i], pts[j]) for i, j in itertools.combinations(range(6), 2)})
    pat = tuple(vals.index(nrm(pts[i], pts[j])) for i, j in pairs(6))
    print('  witness squared distances %s -> %d classes' % (vals, len(vals)))
    print('  pattern %s' % (pat,))
    ok = True
    a = vertex_ok(pat, 6)
    print('  [%s] passes the at-most-3-per-vertex prune' % ('PASS' if a else 'FAIL'))
    ok &= a
    subs = [canon5(restrict(pat, d)) for d in range(6)]
    sub_ok = []
    for d, sc in enumerate(subs):
        _, r, _ = solve((sc, 5, TMO5))
        sub_ok.append(r)
    b = all(r in ('sat', 'unknown') for r in sub_ok)
    print('  [%s] all six 5-subsets realisable: %s' % ('PASS' if b else 'FAIL', sub_ok))
    ok &= b
    _, r6, m6 = solve((pat, 6, 120000))
    c = (r6 == 'sat')
    print('  [%s] the 6-point pattern itself is SAT (got %s)'
          % ('PASS' if c else 'FAIL', r6))
    ok &= c
    print()
    print('CONTROL PASSED' if ok else 'CONTROL FAILED -- do not trust any verdict below')
    return ok


if __name__ == '__main__':
    stage = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if stage == 'control':
        sys.exit(0 if stage_control() else 1)
    five = None
    if stage in ('five', 'all'):
        five = stage_five()
    if stage in ('six', 'all'):
        if five is None:
            five = json.load(open('five_patterns.json'))
        stage_six(five)
