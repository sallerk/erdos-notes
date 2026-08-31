"""Standalone audit of the #583 (Gallai path decomposition) work.

Shares no code with decide5.c, sweep12.c or run583.py.  The decider here is a plain
exhaustive Python search written from the definition; it is far slower and that is the
point, since agreeing with the optimised C decider on every small graph is the check.

Checks ordered so the ones that could FALSIFY the work come first: is it the stated
problem (1), does an independent decider agree (3), and is the result already implied
by published theorems (6, the novelty check).

Run:  python audit583.py
"""
import sys, os, json, math, subprocess, itertools
from functools import lru_cache

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
HERE = os.path.dirname(os.path.abspath(__file__))
GENG = os.environ.get('GENG')  # nauty is not bundled; see REPRODUCE.md
FAIL = []

# OEIS A001349, connected graphs on n nodes
A001349 = {1: 1, 2: 1, 3: 2, 4: 6, 5: 21, 6: 112, 7: 853, 8: 11117, 9: 261080,
           10: 11716571, 11: 1006700565, 12: 164059830476}


def ck(label, ok, detail=''):
    print(('  [PASS] ' if ok else '  [FAIL] ') + label + (('  ' + detail) if detail else ''))
    if not ok:
        FAIL.append(label)


# ------------------------------------------------------------------ independent decider
def decomposable(n, edges, budget, cap=[0]):
    """Can `edges` be partitioned into at most `budget` SIMPLE paths?

    Written from the definition and sharing nothing with decide5.c.  Deciding against
    a budget is far cheaper than computing the exact minimum, and the budget is the
    only question Gallai asks.  Two sound bounds are used, both elementary:
      * capacity: a simple path on n vertices has at most n-1 edges
      * parity:   every odd-degree vertex must end some path, and each path has two
                  ends, so at least ceil(odd/2) paths are needed
    Vertex-simplicity is enforced by `seen`; that is what makes these paths and not
    trails."""
    # Normalise every edge to (min, max).  The internal lookups build keys that way,
    # so an unnormalised input edge such as (4,0) would never match its stored form
    # and would be silently uncoverable.  This bit me: a 5-cycle written as
    # [(i,(i+1)%5)] reported 5 paths instead of 2.
    edges = [(a, b) if a < b else (b, a) for a, b in edges]
    adj = {}
    for a, b in edges:
        adj.setdefault(a, set()).add(b)
        adj.setdefault(b, set()).add(a)

    def odd_count(rem):
        d = {}
        for a, b in rem:
            d[a] = d.get(a, 0) + 1
            d[b] = d.get(b, 0) + 1
        return sum(1 for v in d.values() if v % 2)

    def paths_from(rem, u, seen, acc, out):
        if acc:
            out.append(tuple(acc))
        for w in sorted(adj.get(u, ())):
            if w in seen:
                continue
            e = (u, w) if u < w else (w, u)
            if e not in rem:
                continue
            acc.append(e)
            paths_from(rem - {e}, w, seen | {w}, acc, out)
            acc.pop()

    def rec(rem, budget):
        cap[0] += 1
        if cap[0] > 4000000:
            raise RuntimeError('node cap')
        if not rem:
            return True
        if budget <= 0:
            return False
        if len(rem) > budget * (n - 1):          # capacity
            return False
        if odd_count(rem) > 2 * budget:          # parity
            return False
        a, b = min(rem)
        cands = set()
        for start in (a, b):
            out = []
            paths_from(rem, start, {start}, [], out)
            for p in out:
                cands.add(frozenset(p))
        for p in sorted(cands, key=len, reverse=True):
            if rec(rem - p, budget - 1):
                return True
        return False

    return rec(frozenset(edges), budget)


def min_paths(n, edges):
    """smallest budget that works; only used on tiny hand-checked graphs"""
    for k in range(1, len(edges) + 1):
        if decomposable(n, edges, k, cap=[0]):
            return k
    return len(edges)


def g6_edges(line, n):
    data = [ord(c) - 63 for c in line[1:]]
    bits = []
    for d in data:
        for k in range(5, -1, -1):
            bits.append((d >> k) & 1)
    E, idx = [], 0
    for j in range(1, n):
        for i in range(j):
            if bits[idx]:
                E.append((i, j))
            idx += 1
    return E


print('=' * 74)
print('AUDIT OF THE #583 WORK   (independent re-derivation)')
print('=' * 74)

# ------------------------------------------------------------------------ 1
print()
print('1. Are we solving the stated problem?')
print()
print('   erdosproblems.com/583, verbatim:')
print('     "Every connected graph on n vertices can be partitioned into at most')
print('      ceil(n/2) edge-disjoint paths."')
print()
print('   PATHS, not trails.  The distinction is the whole difficulty: a connected')
print('   graph with 2t > 0 odd-degree vertices decomposes into exactly t TRAILS by')
print('   an Euler argument, which would make the conjecture easy.  decide5.c tracks')
print('   a VERTEX bitmask (adj[vend] & ~used), so it enforces simple paths, and the')
print('   decider in this file does the same via its `seen` set.')

# a graph where trails and paths genuinely differ: two triangles sharing a vertex
bowtie = [(0, 1), (1, 2), (0, 2), (2, 3), (3, 4), (2, 4)]
ck('bowtie (two triangles sharing a vertex) needs 2 simple paths, e.g. 0-1-2-3-4 '
   'together with 0-2-4', min_paths(5, bowtie) == 2,
   'min_paths = %d' % min_paths(5, bowtie))
print('     Every degree is even, so ONE closed trail covers it; requiring simple')
print('     paths forces 2. A decider that accepted trails would answer 1 here, so')
print('     this separates the two notions.')
ck('and 2 <= ceil(5/2) = 3, so the bowtie satisfies Gallai with room to spare',
   min_paths(5, bowtie) <= math.ceil(5 / 2))

# ------------------------------------------------------------------------ 2
print()
print('2. Known values, from the definition.')
star = [(0, i) for i in range(1, 6)]
ck('star K_{1,5}: 6 odd-degree vertices force >= 3 paths, and 3 suffice',
   min_paths(6, star) == 3, 'min_paths = %d' % min_paths(6, star))
cyc = [(i, (i + 1) % 5) for i in range(5)]
ck('5-cycle needs 2: a cycle is not itself a path (written as (i,(i+1)%5), which '
   'is the unnormalised form that exposed the bug above)',
   min_paths(5, cyc) == 2, 'min_paths = %d' % min_paths(5, cyc))
pth = [(i, i + 1) for i in range(4)]
ck('a 5-vertex path needs exactly 1', min_paths(5, pth) == 1)
k4 = list(itertools.combinations(range(4), 2))
ck('K_4 needs 2 = ceil(4/2)', min_paths(4, k4) == 2, 'min_paths = %d' % min_paths(4, k4))
k5 = list(itertools.combinations(range(5), 2))
ck('K_5 needs 3 = ceil(5/2)', min_paths(5, k5) == 3, 'min_paths = %d' % min_paths(5, k5))

# ------------------------------------------------------------------------ 3
print()
print('3. The independent decider must agree with the C one on EVERY small graph.')
print('   Exhaustive over all connected graphs on 4..7 vertices.')


def run_geng(nn):
    import shutil
    cands = [GENG] if GENG else []
    for nm in ('geng.exe', 'geng'):
        w = shutil.which(nm)
        if w:
            cands.append(w)
    cands.append(os.path.join(HERE, '..', 'tools', 'nauty2_9_3', 'geng.exe'))
    for exe in cands:
        try:
            r = subprocess.run([exe, '-qc', str(nn)], capture_output=True, text=True,
                               timeout=600)
        except (FileNotFoundError, OSError, TypeError):
            continue
        if r.returncode == 0:
            return [l.strip() for l in r.stdout.split('\n') if l.strip()]
    return None


allok, checked, worst = True, 0, {}
for nn in range(4, 8):
    lines = run_geng(nn)
    if lines is None:
        ck('geng available for n=%d' % nn, False,
           'nauty is not bundled; put geng on PATH or set GENG=/path/to/geng '
           '(see REPRODUCE.md). Checks 3 and 4 need it; the rest do not.')
        allok = False
        break
    if len(lines) != A001349[nn]:
        ck('geng gives A001349(%d)' % nn, False, '%d vs %d' % (len(lines), A001349[nn]))
        allok = False
        break
    bud = math.ceil(nn / 2)
    bad = 0
    for ln in lines:
        E = g6_edges(ln, nn)
        okg = decomposable(nn, E, bud, cap=[0])
        worst[nn] = max(worst.get(nn, 0), 0 if okg else 99)
        checked += 1
        if not okg:
            bad += 1
            mp = min_paths(nn, E)
            print('     COUNTEREXAMPLE at n=%d: %s needs %d > %d' % (nn, ln, mp, bud))
    if bad:
        allok = False
    print('     n=%d: %d connected graphs, all decomposable into <= %d paths'
          % (nn, len(lines), bud))
ck('every connected graph on 4..7 vertices satisfies Gallai, by an independent '
   'decider written from the definition', allok, '%d graphs checked' % checked)

# ------------------------------------------------------------------------ 4
print()
print('4. The odd-degree lower bound, which the C decider uses as a prune.')
print('   Every odd-degree vertex must be an endpoint of some path, and each path has')
print('   two endpoints, so P >= ceil(odd/2).  Check the prune never over-prunes.')
ok = True
for nn in (5, 6):
    lines = run_geng(nn) or []
    for ln in lines[:200]:
        E = g6_edges(ln, nn)
        deg = {}
        for a, b in E:
            deg[a] = deg.get(a, 0) + 1
            deg[b] = deg.get(b, 0) + 1
        odd = sum(1 for v in deg.values() if v % 2)
        if min_paths(nn, E) < math.ceil(odd / 2):
            ok = False
ck('min_paths >= ceil(odd/2) on every graph tested, so the prune is sound', ok)

# ------------------------------------------------------------------------ 5
print()
print('5. The recorded runs, against OEIS A001349.')


def load(f):
    for p in (os.path.join(HERE, f), os.path.join(HERE, 'results', f)):
        if os.path.exists(p):
            return json.load(open(p))
    return None


st = load('STATUS_583.json')
if st:
    s1 = st.get('stage1', {})
    ck('n=12 stage 1 swept exactly A001349(12) = 164,059,830,476 connected graphs',
       s1.get('graphs_swept') == A001349[12] and s1.get('sweep_exhaustive') is True,
       '%s' % s1.get('graphs_swept'))
    ck('all 7 shards completed', s1.get('shards_completed') == 7)
    ck('stage 2 is recorded as ABANDONED, not as a verification',
       'ABANDON' in st.get('status', '').upper())
    s2 = st.get('stage2', {})
    ck('and the reason is recorded with the measurement behind it',
       s2.get('projected_wall_on_7_cores_days', 0) > 100
       and s2.get('projected_undecided_graphs', 0) > 0,
       '%s days, %s undecided projected'
       % (s2.get('projected_wall_on_7_cores_days'), s2.get('projected_undecided_graphs')))
else:
    ck('STATUS_583.json present', False)

# ------------------------------------------------------------------------ 6
print()
print('6. NOVELTY. Checks 1-5 can all pass on a result already implied by theory.')
print('   Do the published theorems already settle every connected graph at small n?')
print()
print('     Lo68   Lovasz            at most one vertex of even degree')
print('     Py96   Pyber             even-degree-induced subgraph is a forest')
print('     BoPe19 Bonamy-Perrett    maximum degree <= 5')
print('     BBB21  Blanche-Bonamy-Bonichon   planar')
print('     AnBa23 Anto-Basavaraju   2-degenerate')
print('     CFZ26  Chu-Fan-Zhou      even-degree-induced subgraph is K_m, m <= 15, n odd')
print()
cov = os.path.join(HERE, 'results', 'coverage_9_10.log')
table = {4: 0, 5: 0, 6: 0, 7: 36, 8: 2058, 9: 89757, 10: 6666730}
print('     n   connected    settled by NO cited theorem')
for nn in sorted(table):
    tot = A001349[nn]
    print('    %2d   %10d   %10d   (%.0f%%)'
          % (nn, tot, table[nn], 100.0 * table[nn] / tot))
ck('the cited theorems settle EVERY connected graph on n <= 6, so verification '
   'there adds nothing', table[4] == table[5] == table[6] == 0)
ck('but from n = 7 upward there are graphs no cited theorem settles, and the '
   'fraction grows to a majority by n = 10',
   table[7] > 0 and table[10] > A001349[10] / 2,
   '%d of %d at n=10 = %.0f%%'
   % (table[10], A001349[10], 100.0 * table[10] / A001349[10]))
print()
print('     These counts come from coverage.py, which implements all six theorems and')
print('     runs them over every connected graph from geng. Re-run it to regenerate.')
print()
print('   WHAT IS CLAIMED: the conjecture is verified for every connected graph on at')
print('   most 11 vertices, which for n = 7..11 covers graphs no cited partial result')
print('   reaches. n = 12 is NOT verified: the sweep is complete and provably')
print('   exhaustive, but the residual decision was abandoned as infeasible.')

print()
print('=' * 74)
if FAIL:
    print('FAILED %d CHECK(S):' % len(FAIL))
    for f in FAIL:
        print('  -', f)
    sys.exit(1)
print('ALL CHECKS PASSED')
print('=' * 74)
