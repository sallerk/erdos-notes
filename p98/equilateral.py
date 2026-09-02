"""The equilateral-centre lemma, and its application to stubborn patterns.

LEMMA.  Suppose three points a, b, c have all three of their mutual distances in class X,
so abc is EQUILATERAL with squared side D_X.  Suppose a fourth point v has all three of
va, vb, vc in class Y.  Then v is equidistant from a, b, c, i.e. v is the CIRCUMCENTRE of
an equilateral triangle, so

        D_Y  =  D_X / 3

because an equilateral triangle of squared side s^2 has circumradius^2 = s^2 / 3.

COROLLARY (the one that bites).  If a single class X contains TWO disjoint equilateral
triangles, and some vertex v is the centre of one via class Y and of the other via class
Z, then D_Y = D_X/3 = D_Z, so Y and Z are the same distance.  But distinct classes are
distinct distances.  CONTRADICTION, and the pattern is unsatisfiable -- with no solver.

This is elementary and needs no general-position hypothesis beyond distinctness of the
classes.  It is what kills two of the three n=7 candidates z3 could not decide.

Usage:  python equilateral.py <candfile>
"""
import sys, itertools, json, collections

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from hdecide import pairs


def classes_of(pat, n):
    P = pairs(n)
    g = collections.defaultdict(set)
    for i, pr in enumerate(P):
        g[pat[i]].add(pr)
    return g


def triangles(edges):
    """all triples whose three mutual pairs are all present"""
    adj = collections.defaultdict(set)
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    out = []
    for a, b, c in itertools.combinations(sorted(adj), 3):
        if b in adj[a] and c in adj[a] and c in adj[b]:
            out.append((a, b, c))
    return out


def analyse(pat, n, verbose=True):
    """returns (verdict, reason); verdict in {'unsat', 'no conclusion'}"""
    g = classes_of(pat, n)
    P = pairs(n)
    idx = {p: i for i, p in enumerate(P)}

    def cls(u, v):
        return pat[idx[(u, v) if u < v else (v, u)]]

    # relation D_Y = D_X / 3, recorded as centre_relations[Y] = set of X
    forced = collections.defaultdict(set)
    notes = []
    for X, edges in g.items():
        for tri in triangles(edges):
            a, b, c = tri
            for v in range(n):
                if v in tri:
                    continue
                ys = {cls(v, a), cls(v, b), cls(v, c)}
                if len(ys) == 1:
                    Y = ys.pop()
                    forced[X].add((Y, tri, v))
                    notes.append('class %d triangle %s has centre %d via class %d'
                                 '  =>  D_%d = D_%d / 3' % (X, tri, v, Y, Y, X))
    if verbose:
        for nt in notes:
            print('     ' + nt)
    # contradiction: one class X forcing two DIFFERENT classes to equal D_X/3
    for X, rel in forced.items():
        ys = {r[0] for r in rel}
        if len(ys) > 1:
            y1, y2 = sorted(ys)[:2]
            return 'unsat', ('class %d forces both D_%d and D_%d to equal D_%d/3, '
                             'so classes %d and %d would be the same distance'
                             % (X, y1, y2, X, y1, y2))
    # contradiction: D_Y = D_X/3 and D_X = D_Y/3 simultaneously
    for X, rel in forced.items():
        for (Y, _, _) in rel:
            for (Z, _, _) in forced.get(Y, ()):
                if Z == X:
                    return 'unsat', ('D_%d = D_%d/3 and D_%d = D_%d/3 force D_%d = D_%d/9'
                                     % (Y, X, X, Y, X, X, X))
    return 'no conclusion', 'no forced-centre contradiction found'


if __name__ == '__main__':
    cands = [tuple(p) for p in json.load(open(sys.argv[1]))['candidates']]
    n = 7 if len(cands[0]) == 21 else 6
    print('=' * 74)
    print('EQUILATERAL-CENTRE LEMMA applied to %d candidates (n=%d)' % (len(cands), n))
    print('=' * 74)
    killed, left = [], []
    for i, pat in enumerate(cands):
        print()
        print('CANDIDATE %d: %s' % (i, list(pat)))
        v, why = analyse(pat, n)
        print('   VERDICT: %s -- %s' % (v.upper(), why))
        (killed if v == 'unsat' else left).append(list(pat))
    print()
    print('=' * 74)
    print('killed by the lemma : %d' % len(killed))
    print('still open          : %d' % len(left))
    json.dump({'candidates': left}, open('cand_after_equilateral.json', 'w'), indent=1)
    print('written: cand_after_equilateral.json')
