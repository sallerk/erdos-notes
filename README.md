# Erdos problem notes

Supporting material for comments on erdosproblems.com. Each directory holds one note
(`NOTE.md`), its bibliography with provenance (`REFERENCES.md`), and the code and
artifacts behind it.

| dir | problem | claim |
|---|---|---|
| p64 | #64 Erdos-Gyarfas powers-of-two cycles | no cubic bipartite counterexample on at most 62 vertices |
| p97 | #97 four equidistant vertices | a dihedral-symmetry exclusion theorem; exact Danzer coordinates; k=3 impossible for n <= 6 |
| p506 | #506 minimum circles from n points | Wang arXiv:2608.19844 Thm 1.2 already settles the thread's values; two 17-circle witnesses verified, isomorphic but not similar |
| p982 | #982 distinct distances from a vertex | the conjecture for n <= 7 (unconditional to n <= 6) |
| p1082 | #1082 no three collinear | the first question for n <= 15 |

Where a directory has a `REPRODUCE.md`, every command in it was run from a fresh copy
of that directory and the output quoted is what it actually printed, including where a
control fails. p64, p97, p506, p982 and p1082 all have one.

Every claim carries a status: VERIFIED (re-checked by an independent code path),
ASSERTED (search output only), CITED (from the literature), or CONDITIONAL. Searches
that found nothing are reported as searches, not as proofs. Each `REFERENCES.md`
marks whether I read a source myself or have it only secondhand.

Disclosure: the computations and the drafting of these notes were done with AI
assistance.
