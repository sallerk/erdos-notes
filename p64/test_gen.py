"""
VALIDATE THE GENERATOR against published enumeration counts.

If the generator is complete, then after reducing its output up to isomorphism the
counts must match the known sequences exactly:

  A002851  connected cubic graphs:                  n=4:1, 6:2, 8:5, 10:19, 12:85,
                                                    14:509, 16:4060
  A006924  connected cubic graphs of girth >= 5:    n=10:1 (Petersen), 12:2, 14:9,
                                                    16:49, 18:455
  connected cubic graphs of girth >= 6:             n=14:1 (Heawood), 16:1, 18:5, 20:32
"""

import sys
import time

import networkx as nx

from gen import generate_cubic

FAIL = []


def check(cond, msg):
    print(("  ok   " if cond else "  FAIL ") + msg)
    if not cond:
        FAIL.append(msg)


def iso_classes(n, forbidden):
    """Generate, then bucket by WL hash and reduce with exact isomorphism testing."""
    buckets = {}

    def on_complete(adj):
        G = nx.Graph()
        G.add_nodes_from(range(n))
        for u in range(n):
            for v in adj[u]:
                if u < v:
                    G.add_edge(u, v)
        h = nx.weisfeiler_lehman_graph_hash(G, iterations=4)
        b = buckets.setdefault(h, [])
        for H in b:
            if nx.is_isomorphic(G, H):
                return
        b.append(G)

    generate_cubic(n, forbidden=forbidden, on_complete=on_complete,
                   forbid_check_limit=max(forbidden) if forbidden else 0)
    return sum(len(v) for v in buckets.values())


print("A002851 -- connected cubic graphs (no cycle constraints)")
A002851 = {4: 1, 6: 2, 8: 5, 10: 19, 12: 85, 14: 509}
for n, want in A002851.items():
    t = time.time()
    got = iso_classes(n, ())
    check(got == want, f"n={n}: got {got}, expected {want}   ({time.time()-t:.1f}s)")
    sys.stdout.flush()

print("\nA006924 -- connected cubic graphs of girth >= 5 (forbid C3, C4)")
A006924 = {10: 1, 12: 2, 14: 9, 16: 49, 18: 455}
for n, want in A006924.items():
    t = time.time()
    got = iso_classes(n, (3, 4))
    check(got == want, f"n={n}: got {got}, expected {want}   ({time.time()-t:.1f}s)")
    sys.stdout.flush()

print("\nconnected cubic graphs of girth >= 6 (forbid C3, C4, C5)")
G6 = {14: 1, 16: 1, 18: 5, 20: 32}
for n, want in G6.items():
    t = time.time()
    got = iso_classes(n, (3, 4, 5))
    check(got == want, f"n={n}: got {got}, expected {want}   ({time.time()-t:.1f}s)")
    sys.stdout.flush()

print()
if FAIL:
    print(f"*** {len(FAIL)} FAILURES -- generator is NOT complete, do not use ***")
    sys.exit(1)
print("GENERATOR VALIDATED (complete on every tested class)")
