"""
VERIFY THE VERIFIER.  Run this before believing any search result.

Three independent layers of validation:
  L1  hand-known cycle spectra (K4, K5, K33, Petersen, Heawood, C_n, Moebius-Kantor)
  L2  cross-check has_cycle_len / has_pow2_cycle against networkx.simple_cycles
      (a completely independent implementation) on hundreds of random graphs
  L3  cross-check has_hamiltonian_cycle against the brute-force spectrum
"""

import random
import sys

import networkx as nx

from cycles import (
    adj_from_edges,
    cycle_spectrum_bruteforce,
    has_cycle_len,
    has_hamiltonian_cycle,
    has_pow2_cycle,
    is_counterexample,
    pow2_lengths_upto,
)

FAIL = []


def check(cond, msg):
    if cond:
        print(f"  ok   {msg}")
    else:
        print(f"  FAIL {msg}")
        FAIL.append(msg)


def nx_to_adj(G):
    G = nx.convert_node_labels_to_integers(G)
    return adj_from_edges(G.number_of_nodes(), list(G.edges()))


def nx_spectrum(G):
    """Independent ground truth via networkx.simple_cycles (undirected)."""
    return {len(c) for c in nx.simple_cycles(G)}


# ---------------------------------------------------------------- L1
print("L1: known cycle spectra")

K4 = nx_to_adj(nx.complete_graph(4))
check(cycle_spectrum_bruteforce(K4) == {3, 4}, "K4 spectrum == {3,4}")
check(has_cycle_len(K4, 4), "K4 has a 4-cycle")
check(has_pow2_cycle(K4), "K4 has a power-of-2 cycle")

K5 = nx_to_adj(nx.complete_graph(5))
check(cycle_spectrum_bruteforce(K5) == {3, 4, 5}, "K5 spectrum == {3,4,5}")

K33 = nx_to_adj(nx.complete_bipartite_graph(3, 3))
check(cycle_spectrum_bruteforce(K33) == {4, 6}, "K3,3 spectrum == {4,6}")

# Petersen.  Independently known: girth 5, no 7-cycles, non-Hamiltonian (no 10-cycle),
# so the spectrum is {5,6,8,9}.  We assert the whole set, and also re-derive it from
# networkx so the "known" value is not taken on faith.
P = nx.petersen_graph()
Padj = nx_to_adj(P)
spec_mine = cycle_spectrum_bruteforce(Padj)
spec_nx = nx_spectrum(P)
check(spec_mine == {5, 6, 8, 9}, f"Petersen spectrum == {{5,6,8,9}} (got {sorted(spec_mine)})")
check(spec_mine == spec_nx, "Petersen: my spectrum == networkx spectrum")
check(not has_cycle_len(Padj, 4), "Petersen has NO 4-cycle (girth 5)")
check(has_cycle_len(Padj, 8), "Petersen HAS an 8-cycle")
check(not has_hamiltonian_cycle(Padj), "Petersen is NOT Hamiltonian")
check(has_pow2_cycle(Padj), "Petersen satisfies the conjecture (via C8)")
check(not is_counterexample(Padj), "Petersen is not a counterexample")

# Heawood graph: cubic, bipartite, girth 6, 14 vertices.  Spectrum {6,8,10,12,14}.
H = nx.heawood_graph()
Hadj = nx_to_adj(H)
check(
    cycle_spectrum_bruteforce(Hadj) == {6, 8, 10, 12, 14},
    "Heawood spectrum == {6,8,10,12,14}",
)
check(has_cycle_len(Hadj, 8), "Heawood has an 8-cycle")
check(has_hamiltonian_cycle(Hadj), "Heawood is Hamiltonian")

# Moebius-Kantor: cubic bipartite, 16 vertices, girth 6.
MK = nx.moebius_kantor_graph()
MKadj = nx_to_adj(MK)
check(cycle_spectrum_bruteforce(MKadj) == nx_spectrum(MK), "Moebius-Kantor: mine == networkx")
check(has_cycle_len(MKadj, 16) == has_hamiltonian_cycle(MKadj), "MK: C16 test == Hamiltonicity")

# cycles C_n: spectrum is exactly {n}
for m in range(3, 12):
    Cm = nx_to_adj(nx.cycle_graph(m))
    check(cycle_spectrum_bruteforce(Cm) == {m}, f"C_{m} spectrum == {{{m}}}")

# a graph with NO power-of-2 cycle but min degree 2 (so not a counterexample):
# the triangle has spectrum {3}
T = nx_to_adj(nx.cycle_graph(3))
check(not has_pow2_cycle(T), "triangle has no power-of-2 cycle")
check(not is_counterexample(T), "triangle is not a counterexample (min degree 2)")

# ---------------------------------------------------------------- L2
print("\nL2: cross-check vs networkx.simple_cycles on random graphs")
random.seed(20260828)
bad = 0
trials = 0
for _ in range(400):
    n = random.randint(4, 11)
    p = random.uniform(0.15, 0.75)
    G = nx.gnp_random_graph(n, p, seed=random.randrange(10**9))
    if G.number_of_edges() == 0:
        continue
    adj = nx_to_adj(G)
    truth = nx_spectrum(G)
    mine = cycle_spectrum_bruteforce(adj)
    trials += 1
    if mine != truth:
        bad += 1
        print("   MISMATCH spectrum", n, sorted(mine), sorted(truth))
        continue
    # has_cycle_len must agree with the ground-truth spectrum for every L
    for L in range(3, n + 1):
        if has_cycle_len(adj, L) != (L in truth):
            bad += 1
            print(f"   MISMATCH has_cycle_len n={n} L={L}")
            break
    # has_pow2_cycle must agree
    want = any(L in truth for L in pow2_lengths_upto(n))
    if has_pow2_cycle(adj) != want:
        bad += 1
        print(f"   MISMATCH has_pow2_cycle n={n}")
    # Hamiltonicity must agree
    if has_hamiltonian_cycle(adj) != (n in truth):
        bad += 1
        print(f"   MISMATCH hamiltonian n={n}")
check(bad == 0, f"random cross-check: {trials} graphs, {bad} mismatches")

# ---------------------------------------------------------------- L2b
print("\nL2b: cross-check on random CUBIC graphs (the class we actually search)")
bad = 0
trials = 0
for _ in range(120):
    n = random.choice([6, 8, 10, 12, 14])
    try:
        G = nx.random_regular_graph(3, n, seed=random.randrange(10**9))
    except Exception:
        continue
    adj = nx_to_adj(G)
    truth = nx_spectrum(G)
    trials += 1
    if cycle_spectrum_bruteforce(adj) != truth:
        bad += 1
        print("   MISMATCH cubic spectrum", n)
        continue
    for L in range(3, n + 1):
        if has_cycle_len(adj, L) != (L in truth):
            bad += 1
            print(f"   MISMATCH cubic has_cycle_len n={n} L={L}")
            break
    if has_hamiltonian_cycle(adj) != (n in truth):
        bad += 1
        print(f"   MISMATCH cubic hamiltonian n={n}")
    if has_pow2_cycle(adj) != any(L in truth for L in pow2_lengths_upto(n)):
        bad += 1
        print(f"   MISMATCH cubic pow2 n={n}")
check(bad == 0, f"random cubic cross-check: {trials} graphs, {bad} mismatches")

# ---------------------------------------------------------------- L3
print("\nL3: sanity -- every cubic graph on <= 14 vertices should satisfy the conjecture")
# (this is a weak echo of the published n>=17 bound, using random samples only)
viol = 0
for _ in range(300):
    n = random.choice([4, 6, 8, 10, 12, 14, 16])
    try:
        G = nx.random_regular_graph(3, n, seed=random.randrange(10**9))
    except Exception:
        continue
    if is_counterexample(nx_to_adj(G)):
        viol += 1
        print("   !!! candidate counterexample on", n, "vertices:", sorted(G.edges()))
check(viol == 0, "no counterexample among random small cubic graphs (consistent with n>=32)")

print()
if FAIL:
    print(f"*** {len(FAIL)} FAILURES ***")
    sys.exit(1)
print("ALL CHECKER TESTS PASSED")
