"""Enumerate distance patterns with a bounded PINNED count, for Erdos #654.

A pattern colours the C(n,2) edges of K_n; a colour class is a distance value.  Unlike
#98, the number of colours is NOT an input: what is bounded is the number of colours AT
EACH VERTEX.

    m    at most m distinct colours at every vertex     (this is d_X(x) <= m)
    cap  at most `cap` edges of one colour at a vertex  (cap = 3 under N4, 2 under A2)

Because a vertex has n-1 edges, these force n-1 <= cap*m, which at cap=3 is exactly the
trivial bound f(n) >= ceil((n-1)/3).  They also cap the number of colours: summing "at
most m colours" over the n vertices and noting every colour is present at >= 2 vertices
gives k <= n*m/2.

THREE REDUCTIONS, in increasing cost:

1. RESTRICTED GROWTH.  A colour index may be used only if every smaller index already has
   been.  This quotients out colour renaming exactly, at no cost.

2. VERTEX 0 SORTED.  The first n-1 edges in `pairs(n)` order are exactly the edges at
   vertex 0.  Relabelling vertices 1..n-1 is free, so we may always sort them by colour;
   requiring that sequence to be non-decreasing is therefore sound and very strong.  At
   n=7, m=2 it pins vertex 0's edges to 0,0,0,1,1,1 uniquely.

3. FULL CANONICAL FORM under all n! relabellings, applied only to survivors, reusing
   p98/hdecide.py's `canonical`.  This is the expensive one, so it runs last.

A FEASIBILITY LOOKAHEAD prunes a branch as soon as a vertex cannot possibly finish: with
`u` edges still unassigned at v, `c` colours already used there and `slack` spare capacity
inside them, v needs u <= slack + cap*(m - c).

Usage:  python penum.py <n> <m> [cap]      enumerate and report counts
        python penum.py crosscheck         validate against brute force at n<=5
"""
import sys, itertools, json, time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from common import pairs, canonical             # noqa: E402


def enumerate_pinned(n, m, cap=3, sorted_zero=True, limit=0):
    """Yield raw patterns (tuples of colour indices, in pairs(n) order)."""
    P = pairs(n)
    ne = len(P)
    at = [[] for _ in range(n)]
    for e, (i, j) in enumerate(P):
        at[i].append(e)
        at[j].append(e)
    kmax = (n * m) // 2

    col = [-1] * ne
    cnt = [dict() for _ in range(n)]
    rem = [len(at[v]) for v in range(n)]
    out = []

    def feasible(v):
        c = len(cnt[v])
        if c > m:
            return False
        slack = sum(cap - x for x in cnt[v].values())
        return rem[v] <= slack + cap * (m - c)

    def rec(e, ncol):
        if limit and len(out) >= limit:
            return
        if e == ne:
            out.append(tuple(col))
            return
        i, j = P[e]
        lo = 0
        if sorted_zero and i == 0 and e > 0 and P[e - 1][0] == 0:
            lo = col[e - 1]                       # non-decreasing along vertex 0
        for c in range(lo, min(ncol, kmax - 1) + 1):
            ni = cnt[i].get(c, 0)
            nj = cnt[j].get(c, 0)
            if ni >= cap or nj >= cap:
                continue
            if ni == 0 and len(cnt[i]) >= m:
                continue
            if nj == 0 and len(cnt[j]) >= m:
                continue
            cnt[i][c] = ni + 1
            cnt[j][c] = nj + 1
            rem[i] -= 1
            rem[j] -= 1
            col[e] = c
            if feasible(i) and feasible(j):
                rec(e + 1, max(ncol, c + 1))
            col[e] = -1
            rem[i] += 1
            rem[j] += 1
            if ni:
                cnt[i][c] = ni
            else:
                del cnt[i][c]
            if nj:
                cnt[j][c] = nj
            else:
                del cnt[j][c]

    rec(0, 0)
    return out


def pinned_counts(pat, n):
    """number of distinct colours at each vertex"""
    P = pairs(n)
    s = [set() for _ in range(n)]
    for e, (i, j) in enumerate(P):
        s[i].add(pat[e])
        s[j].add(pat[e])
    return [len(x) for x in s]


def max_class_at_vertex(pat, n):
    P = pairs(n)
    c = [dict() for _ in range(n)]
    for e, (i, j) in enumerate(P):
        c[i][pat[e]] = c[i].get(pat[e], 0) + 1
        c[j][pat[e]] = c[j].get(pat[e], 0) + 1
    return max(max(d.values()) for d in c)


def canon_set(raws, n):
    P = pairs(n)
    index = {p: i for i, p in enumerate(P)}
    seen = {}
    for r in raws:
        c = canonical(r, n, P, index)
        if c not in seen:
            seen[c] = r
    return sorted(seen)


if __name__ == '__main__':
    if sys.argv[1] == 'crosscheck':
        print('=' * 74)
        print('CROSSCHECK -- the DFS must agree with brute force')
        print('=' * 74)
        bad = 0
        for n, m, cap in ((4, 1, 3), (4, 2, 3), (5, 2, 3), (5, 3, 3), (4, 2, 2)):
            kmax = (n * m) // 2
            P = pairs(n)
            brute = []
            for raw in itertools.product(range(kmax), repeat=len(P)):
                s, ok = {}, True                  # restricted growth
                for c in raw:
                    if c not in s:
                        if len(s) != c:
                            ok = False
                            break
                        s[c] = 1
                if not ok:
                    continue
                if max(pinned_counts(raw, n)) > m:
                    continue
                if max_class_at_vertex(raw, n) > cap:
                    continue
                brute.append(raw)
            bc = canon_set(brute, n)
            dfs = enumerate_pinned(n, m, cap)
            dc = canon_set(dfs, n)
            ok = (bc == dc)
            bad += (not ok)
            print('  [%s] n=%d m=%d cap=%d: brute %d raw -> %d canonical; '
                  'dfs %d raw -> %d canonical'
                  % ('PASS' if ok else 'FAIL', n, m, cap,
                     len(brute), len(bc), len(dfs), len(dc)))
            if not ok:
                print('        symmetric difference: %d'
                      % len(set(bc) ^ set(dc)))
        print()
        print('CROSSCHECK FAILED' if bad else 'CROSSCHECK PASSED')
        sys.exit(1 if bad else 0)

    n, m = int(sys.argv[1]), int(sys.argv[2])
    cap = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    print('n=%d  m=%d  cap=%d   (needs n-1=%d <= cap*m=%d)'
          % (n, m, cap, n - 1, cap * m))
    if n - 1 > cap * m:
        print('  INFEASIBLE by the counting bound: no pattern exists.')
        json.dump({'n': n, 'm': m, 'cap': cap, 'raw': 0, 'canonical': 0,
                   'patterns': [], 'infeasible': True}, 
                  open('penum_n%d_m%d.json' % (n, m), 'w'), indent=1)
        sys.exit(0)
    t0 = time.time()
    raws = enumerate_pinned(n, m, cap)
    t1 = time.time()
    print('  raw patterns (restricted growth + vertex-0 sorted): %d   %.1fs'
          % (len(raws), t1 - t0))
    cs = canon_set(raws, n)
    print('  up to relabelling: %d   %.1fs' % (len(cs), time.time() - t1))
    fn = 'penum_n%d_m%d.json' % (n, m)
    json.dump({'n': n, 'm': m, 'cap': cap, 'raw': len(raws), 'canonical': len(cs),
               'patterns': [list(c) for c in cs]}, open(fn, 'w'), indent=1)
    print('  written: %s' % fn)
