# Erdos problem notes

Supporting material for comments on erdosproblems.com. Each directory holds one note
(`NOTE.md`), its bibliography with provenance (`REFERENCES.md`), and the code and
artifacts behind it.

| dir | problem | claim |
|---|---|---|
| p64 | #64 Erdos-Gyarfas powers-of-two cycles | no cubic bipartite counterexample on at most 62 vertices |
| p97 | #97 four equidistant vertices | a dihedral-symmetry exclusion theorem; exact Danzer coordinates; k=3 impossible for n <= 6 |
| p506 | #506 minimum circles from n points | Wang arXiv:2608.19844 Thm 1.2 already settles the thread's values; two 17-circle witnesses verified, isomorphic but not similar |
| p982 | #982 distinct distances from a vertex | **SHELVED** - correct and reproducible but not new; n <= 7 already follows from Moser 1952 and Erdos-Fishburn 1994, and n = 8 is out of reach |
| p1082 | #1082 no three collinear | the first question for n <= 15 |
| p548 | #548 Erdos-Sos | a k-convention mismatch between the statement and the cited literature; re-locates the first open instance to n = 15, 61 edges, trees on 10 vertices |
| p583 | #583 Gallai path decomposition | verified for every connected graph on n <= 11; the cited theorems already cover n <= 6, but not a majority of graphs by n = 10 |
| p217 | #217 crescent configurations | no 9-point configuration on the triangular lattice with squared diameter <= 400; extends the published 91-point search 16-fold |
| p98 | #98 distinct distances in general position | exact values D_gen(3..7) = 1, 2, 3, 4, 5, the best known lower bound for 4 <= n <= 13; D_gen(8) in [5,7] |
| p654 | #654 pinned distinct distances | exact values f(3..6) = 1, 2, 3, 3 under both hypotheses; f(7), f(8) in [3,4]; a solver-free proof that f(7) > 2; two discrepancies to check on the problem page |

Where a directory has a `REPRODUCE.md`, every command in it was run from a fresh copy
of that directory and the output quoted is what it actually printed, including where a
control fails. p64, p97, p506, p654, p982 and p1082 all have one; p98 has one too.

Every claim carries a status: VERIFIED (re-checked by an independent code path),
ASSERTED (search output only), CITED (from the literature), or CONDITIONAL. Searches
that found nothing are reported as searches, not as proofs. Each `REFERENCES.md`
marks whether I read a source myself or have it only secondhand.

Disclosure: the computations and the drafting of these notes were done with AI
assistance.
