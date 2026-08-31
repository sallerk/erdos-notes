"""Do the PUBLISHED theorems already settle Gallai's path-decomposition conjecture
for every connected graph on n vertices?

This is the novelty check that should run before any compute is spent.  If the cited
results already cover all small graphs, an exhaustive verification at those n proves
nothing new.

Theorems, as listed on https://www.erdosproblems.com/583:

  Lo68  Lovasz            at most one vertex of even degree
  Py96  Pyber             the subgraph induced by even-degree vertices is a forest
  BoPe19 Bonamy-Perrett   maximum degree <= 5
  BBB21 Blanche-Bonamy-Bonichon   planar
  AnBa23 Anto-Basavaraju  2-degenerate (every subgraph has a vertex of degree <= 2)
  CFZ26 Chu-Fan-Zhou      the even-degree-induced subgraph is K_m for some m <= 15,
                          and n is odd

Usage: python coverage.py N [N2 ...]
"""
import sys, subprocess, os
from itertools import combinations

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
GENG = None  # resolved lazily by _find_geng()

def _find_geng():
    """nauty is a third-party dependency and is deliberately NOT vendored here.
    Look for geng in this order: the $GENG environment variable, then PATH, then a
    sibling tools/ directory (the author's layout).  Fail with instructions rather
    than a traceback."""
    import shutil
    cands = []
    if os.environ.get('GENG'):
        cands.append(os.environ['GENG'])
    for nm in ('geng.exe', 'geng'):
        w = shutil.which(nm)
        if w:
            cands.append(w)
    here = os.path.dirname(os.path.abspath(__file__))
    for rel in (('..', 'tools', 'nauty2_9_3', 'geng.exe'),
                ('..', 'tools', 'nauty2_9_3', 'geng')):
        cands.append(os.path.join(here, *rel))
    for c in cands:
        if c and os.path.exists(c):
            return c
    msg = ["geng (from nauty) was not found.",
           "  nauty is not bundled with this repository. Install it from",
           "  https://pallini.di.uniroma1.it/ and then either put geng on your PATH,",
           "  or set GENG=/path/to/geng before running this script."]
    sys.exit(chr(10).join(msg))


import networkx as nx


def g6_to_adj(line, n):
    """decode graph6 into an adjacency bitmask list"""
    data = [ord(c) - 63 for c in line[1:]] if line[0] != '>' else None
    bits = []
    for d in data:
        for k in range(5, -1, -1):
            bits.append((d >> k) & 1)
    adj = [0] * n
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if bits[idx]:
                adj[i] |= 1 << j
                adj[j] |= 1 << i
            idx += 1
    return adj


def covered(adj, n):
    """return the name of a theorem that settles this graph, or None"""
    deg = [bin(a).count('1') for a in adj]
    ev = [v for v in range(n) if deg[v] % 2 == 0]
    # Lo68
    if len(ev) <= 1:
        return 'Lo68'
    # BoPe19
    if max(deg) <= 5:
        return 'BoPe19'
    # Py96: even-degree-induced subgraph acyclic
    es = set(ev)
    edges_e = [(i, j) for i in ev for j in ev if i < j and (adj[i] >> j) & 1]
    if len(edges_e) <= len(ev) - 1:
        # necessary for a forest; confirm with union-find
        par = {v: v for v in ev}

        def find(x):
            while par[x] != x:
                par[x] = par[par[x]]
                x = par[x]
            return x
        acyclic = True
        for i, j in edges_e:
            a, b = find(i), find(j)
            if a == b:
                acyclic = False
                break
            par[a] = b
        if acyclic:
            return 'Py96'
    # CFZ26: even-degree-induced subgraph is complete, m <= 15, n odd
    m = len(ev)
    if n % 2 == 1 and m <= 15 and len(edges_e) == m * (m - 1) // 2:
        return 'CFZ26'
    # AnBa23: 2-degenerate
    d = list(deg)
    alive = [True] * n
    removed = 0
    changed = True
    while changed:
        changed = False
        for v in range(n):
            if alive[v] and d[v] <= 2:
                alive[v] = False
                removed += 1
                changed = True
                for u in range(n):
                    if alive[u] and (adj[v] >> u) & 1:
                        d[u] -= 1
    if removed == n:
        return 'AnBa23'
    # BBB21: planar  (last, it is the expensive one)
    G = nx.Graph()
    G.add_nodes_from(range(n))
    for i in range(n):
        for j in range(i + 1, n):
            if (adj[i] >> j) & 1:
                G.add_edge(i, j)
    if nx.check_planarity(G, counterexample=False)[0]:
        return 'BBB21'
    return None


for n in [int(x) for x in (sys.argv[1:] or ['4', '5', '6', '7', '8', '9'])]:
    p = subprocess.Popen([_find_geng(), '-qc', str(n)], stdout=subprocess.PIPE,
                         stderr=subprocess.DEVNULL, text=True)
    tot = 0
    by = {}
    uncovered = 0
    first_uncovered = None
    for line in p.stdout:
        line = line.strip()
        if not line:
            continue
        tot += 1
        adj = g6_to_adj(line, n)
        c = covered(adj, n)
        if c is None:
            uncovered += 1
            if first_uncovered is None:
                first_uncovered = line
        else:
            by[c] = by.get(c, 0) + 1
    p.wait()
    print('n=%2d  connected=%d' % (n, tot))
    for k in sorted(by):
        print('        %-8s %d' % (k, by[k]))
    print('        %-8s %d   <-- settled by NO cited theorem' % ('NONE', uncovered))
    if first_uncovered:
        print('        first uncovered graph (graph6): %s' % first_uncovered)
    sys.stdout.flush()
