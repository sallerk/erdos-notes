"""Purely combinatorial soundness filters on distance patterns.

All are sound for any planar point set with the general-position hypotheses, need no
solver, and cost microseconds.  None can remove a realisable pattern; each is verified
against every known-realisable pattern before use.

L1 DEGREE.  No four points are cocircular, so at most three lie at any one distance from
   a given point.  Each class has max degree 3.

L2 K(2,3).  Two distinct circles of equal radius meet in at most two points, so no three
   points are all at distance d from both p and q.  Each class graph is K(2,3)-free.
   (No general-position hypothesis needed at all.)

L3 BISECTOR  -- NEW.  If p is equidistant from q and r then p lies on the perpendicular
   bisector of qr, a LINE, which carries at most two points of the set since no three are
   collinear.  In pattern terms:

       for every pair {q,r},  #{p : cls(p,q) = cls(p,r)}  <=  2.

   This is the per-pair form of the counting bound in section 2, which was previously
   only used in aggregate.

L4 CIRCUMCENTRE -- NEW.  If p is equidistant from all of q, r, s then p is the
   circumcentre of triangle qrs, and a triangle has exactly one circumcentre.  So:

       for every triple {q,r,s},  #{p : cls(p,q) = cls(p,r) = cls(p,s)}  <=  1.

   Strictly stronger than L3 on triples.

L5 EQUILATERAL-CENTRE.  If a class X holds a triangle (all three mutual distances in X)
   and a point v joins all three vertices in class Y, then v is the circumcentre of an
   equilateral triangle, so D_Y = D_X/3.  If one class holds two such triangles whose
   centres use DIFFERENT classes Y and Z, then D_Y = D_Z and two distinct classes would
   be the same distance: contradiction.

Usage:  python lemmas.py            (soundness checks and measured cut rates)
"""
import sys, os, json, itertools, collections

sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def _pairs(n):
    return list(itertools.combinations(range(n), 2))


def _cls_fn(pat, n):
    P = _pairs(n)
    idx = {p: i for i, p in enumerate(P)}

    def cls(a, b):
        return pat[idx[(a, b) if a < b else (b, a)]]
    return cls


def l1_degree(pat, n):
    cls = _cls_fn(pat, n)
    for v in range(n):
        cnt = collections.Counter(cls(v, w) for w in range(n) if w != v)
        if any(c > 3 for c in cnt.values()):
            return False
    return True


def l2_k23(pat, n):
    cls = _cls_fn(pat, n)
    byc = collections.defaultdict(lambda: collections.defaultdict(set))
    for a, b in _pairs(n):
        c = cls(a, b)
        byc[c][a].add(b)
        byc[c][b].add(a)
    for c, adj in byc.items():
        for p, q in itertools.combinations(range(n), 2):
            if len(adj[p] & adj[q]) >= 3:
                return False
    return True


def l3_bisector(pat, n):
    """at most 2 points equidistant from any given pair"""
    cls = _cls_fn(pat, n)
    for q, r in itertools.combinations(range(n), 2):
        apex = sum(1 for p in range(n)
                   if p != q and p != r and cls(p, q) == cls(p, r))
        if apex > 2:
            return False
    return True


def l4_circumcentre(pat, n):
    """at most 1 point equidistant from any given triple"""
    cls = _cls_fn(pat, n)
    for q, r, s in itertools.combinations(range(n), 3):
        c = sum(1 for p in range(n)
                if p not in (q, r, s) and cls(p, q) == cls(p, r) == cls(p, s))
        if c > 1:
            return False
    return True


def l5_equilateral(pat, n):
    """one class holding two triangles with different centre-classes is contradictory"""
    cls = _cls_fn(pat, n)
    byc = collections.defaultdict(list)
    for a, b in _pairs(n):
        byc[cls(a, b)].append((a, b))
    forced = collections.defaultdict(set)
    for X, edges in byc.items():
        adj = collections.defaultdict(set)
        for a, b in edges:
            adj[a].add(b)
            adj[b].add(a)
        for a, b, c in itertools.combinations(sorted(adj), 3):
            if b in adj[a] and c in adj[a] and c in adj[b]:
                for v in range(n):
                    if v in (a, b, c):
                        continue
                    ys = {cls(v, a), cls(v, b), cls(v, c)}
                    if len(ys) == 1:
                        forced[X].add(ys.pop())
    for X, ys in forced.items():
        if len(ys) > 1:
            return False
    return True


ALL = [('L1 degree', l1_degree), ('L2 K(2,3)', l2_k23), ('L3 bisector', l3_bisector),
       ('L4 circumcentre', l4_circumcentre), ('L5 equilateral', l5_equilateral)]


def survives(pat, n):
    return all(f(pat, n) for _, f in ALL)


if __name__ == '__main__':
    import json, time
    from hdecide import enumerate_patterns

    print('=' * 74)
    print('SOUNDNESS FIRST: no lemma may reject a pattern we KNOW is realisable')
    print('=' * 74)
    KNOWN = []
    # every pattern proved realisable in this project
    KNOWN.append(((0, 0, 0, 0, 1, 1), 4, 'n=4 diamond'))
    # These artifacts live in results/ but the scripts write bare filenames, so look in
    # both.  An earlier version wrapped this in `try/except: pass`, which meant that run
    # from the repository root the check silently covered 4 patterns instead of 104 and
    # still reported PASS.  A missing artifact is now a loud failure, not a quiet one.
    _here = os.path.dirname(os.path.abspath(__file__))
    _missing = []
    for f, n in (('sweep_n5_k3.json', 5), ('sweep_n5_k4_robust.json', 5)):
        for cand in (f, os.path.join(_here, f), os.path.join(_here, 'results', f)):
            if os.path.exists(cand):
                d = json.load(open(cand))
                for p in d.get('sat', []):
                    KNOWN.append((tuple(p), n, f))
                break
        else:
            _missing.append(f)
    if _missing:
        print('  ABORT: cannot find %s. This check is meaningless without them; it would '
              'otherwise "pass" over a handful of patterns instead of 104.'
              % ', '.join(_missing))
        sys.exit(1)
    # and the patterns of the verified witnesses
    def pat_of(pts, n):
        def nrm(p, q):
            da, db = p[0] - q[0], p[1] - q[1]
            return da * da + da * db + db * db
        vals = sorted({nrm(pts[i], pts[j]) for i, j in itertools.combinations(range(n), 2)})
        return tuple(vals.index(nrm(pts[i], pts[j])) for i, j in _pairs(n))
    WIT = {6: [(0,0),(-1,0),(-1,2),(-3,1),(-3,2),(-2,3)],
           7: [(0,0),(-1,0),(-1,1),(1,-3),(3,-2),(2,-4),(4,-2)],
           8: [(0,0),(-1,0),(-1,1),(1,-3),(2,-3),(3,-1),(-2,-2),(2,-4)]}
    for n, pts in WIT.items():
        KNOWN.append((pat_of(pts, n), n, 'verified n=%d witness' % n))

    bad = 0
    for name, fn in ALL:
        rejected = [(w, nn) for (w, nn, src) in KNOWN if not fn(w, nn)]
        ok = not rejected
        bad += (not ok)
        print('  [%s] %-16s rejects %d of %d known-realisable patterns'
              % ('PASS' if ok else 'FAIL', name, len(rejected), len(KNOWN)))
    print()
    if bad:
        print('A LEMMA IS UNSOUND -- do not use it')
        sys.exit(1)
    print('all %d lemmas are sound on %d known-realisable patterns' % (len(ALL), len(KNOWN)))

    print()
    print('=' * 74)
    print('MEASURED CUT RATES')
    print('=' * 74)
    print('  n  k   patterns   +L1     +L2     +L3     +L4     +L5   survivors  cut')
    for (n, k) in ((5, 3), (5, 4), (5, 5), (6, 3)):
        t0 = time.time()
        allp = list(enumerate_patterns(n, k))
        cur = allp
        counts = []
        for _, fn in ALL:
            cur = [p for p in cur if fn(p, n)]
            counts.append(len(cur))
        print('  %d  %d   %8d  %6d  %6d  %6d  %6d  %6d   %7d  %.1f%%   (%.0fs)'
              % (n, k, len(allp), counts[0], counts[1], counts[2], counts[3],
                 counts[4], len(cur), 100.0 * (1 - len(cur) / max(1, len(allp))),
                 time.time() - t0))
