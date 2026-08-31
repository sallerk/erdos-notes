"""Count the n=8 pattern space WITHOUT materialising it.

enumerate_patterns() accumulates every colouring in a list; at n=8 that took
23 GB of RAM and had to be killed. This is the same recursion with the storage
removed, so it measures the size of the problem before any compute is committed
to it. Prints progress so a partial run is still informative.

Usage: python count8.py N [SECONDS]
"""
import sys, time
from itertools import combinations

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.setrecursionlimit(10000)

n = int(sys.argv[1]) if len(sys.argv) > 1 else 8
budget = float(sys.argv[2]) if len(sys.argv) > 2 else 600.0

k = n // 2 - 1
edges = list(combinations(range(n), 2))
edges.sort(key=lambda e: (e[1], e[0]))
m = len(edges)
last_edge_of = [max(i for i, e in enumerate(edges) if v in e) for v in range(n)]

col = [-1] * m
vcolors = [0] * n
vcount = [0] * n
vsize = [dict() for _ in range(n)]

stat = {'raw': 0, 'raw_noaltman': 0, 'nodes': 0, 'stop': False}
t0 = time.time()
last = [t0]


def vertex_ok_complete(v):
    sizes = sorted(vsize[v].values(), reverse=True)
    if len(sizes) > k:
        return False
    excess = sum(max(0, s - 2) for s in sizes)
    return excess >= (n - 1) - 2 * k


def rec(i, ncol):
    if stat['stop']:
        return
    stat['nodes'] += 1
    if (stat['nodes'] & 0xFFFFF) == 0:
        now = time.time()
        if now - last[0] >= 30:
            last[0] = now
            print('  %6.0fs nodes=%.4g raw(with Altman)=%.6g raw(all)=%.6g'
                  % (now - t0, stat['nodes'], stat['raw'], stat['raw_noaltman']),
                  flush=True)
        if now - t0 > budget:
            stat['stop'] = True
            return
    if i == m:
        stat['raw_noaltman'] += 1
        if ncol >= n // 2:                 # Altman 1963 filter
            stat['raw'] += 1
        return
    a, b = edges[i]
    for c in range(ncol + 1):
        newa = not (vcolors[a] >> c) & 1
        newb = not (vcolors[b] >> c) & 1
        if newa and vcount[a] + 1 > k:
            continue
        if newb and vcount[b] + 1 > k:
            continue
        col[i] = c
        if newa:
            vcolors[a] |= 1 << c; vcount[a] += 1
        if newb:
            vcolors[b] |= 1 << c; vcount[b] += 1
        vsize[a][c] = vsize[a].get(c, 0) + 1
        vsize[b][c] = vsize[b].get(c, 0) + 1
        good = True
        for v in (a, b):
            if last_edge_of[v] == i and not vertex_ok_complete(v):
                good = False
                break
        if good:
            rec(i + 1, ncol + (1 if c == ncol else 0))
        vsize[a][c] -= 1
        if vsize[a][c] == 0:
            del vsize[a][c]
        vsize[b][c] -= 1
        if vsize[b][c] == 0:
            del vsize[b][c]
        if newa:
            vcolors[a] &= ~(1 << c); vcount[a] -= 1
        if newb:
            vcolors[b] &= ~(1 << c); vcount[b] -= 1
        col[i] = -1


print('n=%d  k=floor(n/2)-1=%d  edges=%d  budget=%.0fs' % (n, k, m, budget), flush=True)
rec(0, 0)
el = time.time() - t0
print()
print('COMPLETED' if not stat['stop'] else 'STOPPED AT BUDGET (counts are LOWER BOUNDS)')
print('  search nodes        : %d' % stat['nodes'])
print('  raw colourings      : %d   (no Altman filter)' % stat['raw_noaltman'])
print('  raw with Altman     : %d' % stat['raw'])
print('  wall                : %.1fs' % el)
if not stat['stop']:
    print('  classes are at least raw/(2n) = %.4g, since only the dihedral group '
          'of order %d remains (colour renaming is already factored out by the '
          'first-appearance rule in the recursion)' % (stat['raw'] / (2.0 * n), 2 * n))
