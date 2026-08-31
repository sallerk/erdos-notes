# Reproducing everything in RESULTS.md

Environment: Windows 10, Python 3.12.9, numpy 2.1.3, scipy 1.15.2, sympy 1.13.1,
mpmath 1.3.0, z3-solver 5.1.0 (`pip install z3-solver`). 20 logical cores; the
machine was **not** idle — another session's jobs ran concurrently, so wall times
below are upper bounds, not benchmarks.

All commands are run from `C:\Users\Tyrant\Desktop\erdos stuff\p982`.

## 0. Verify the verifier (do this first)

    python verify_machinery.py

Exits 0 with `ALL VERIFIER CHECKS PASSED`. Checks: regular n-gon gives exactly
`floor(n/2)` per vertex for n=3..40 (exact, index arithmetic in Z_n) and again at 60 dps
via mpmath; convex-position test accepts convex polygons and rejects interior points,
duplicates and collinear boundary points; Harborth H_8 has per-point count 3 and 4 total
distances and is not convex; concyclic sets never beat `floor(n/2)`; the pigeonhole
excess arithmetic for all n <= 200.

## 1. Controls on the decision procedure

    python control_decide.py

Control A substitutes explicit convex polygons into every constraint of the z3 encoding
(exactly over Q for four lattice polygons; 80 dps for regular 5-, 7-, 9-gons) — this is
what rules out a vacuously-unsatisfiable encoding, and it uses no z3 search.
Control C: "all pairwise distances equal" must be UNSAT for n >= 4.
Control D is informational: z3 returns UNKNOWN on colourings whose only models are
irrational. **This is a real limitation and is stated in RESULTS.md.**

## 2. The certification, n <= 7

    python decide2.py 4 60000          # UNSAT, 0.0 s   -> decide2_n4.json
    python decide2.py 5 60000          # UNSAT, 0.0 s   -> decide2_n5.json
    python decide.py 6 60000 16        # 316 patterns, all UNSAT, 67 s -> decide_n6.json
    python decide.py 7 30000 16        # 5354 patterns, 5348 UNSAT + 6 timeouts, 465 s
    python retry_unknown.py 7 2400000 6    # the 6 timeouts, all UNSAT -> updates decide_n7.json

Independent-of-Altman version (drops the one cited theorem used as a prune, at the cost of
1834 instead of 316 pattern classes for n=6):

    python decide.py 6 60000 16 noaltman     # -> decide_n6_noaltman.json

Encoding-independent re-check (level variables, free scale, reversed vertex labelling):

    python decide_alt.py 6 120000 6          # -> decide_alt_n6.json

Enumeration-free single-formula version (works to n=5, times out at n=6):

    python decide2.py 6 10800000             # -> decide2_n6.json

## 3. Structured family: two staggered concentric regular m-gons

    python tworing_par.py 3 400 14           # -> tworing_m3_400.json
    # single-process extension to m=1200 (mp.Pool spawn failed under load):
    python -c "import json,time; from tworing_par import do_m; \
      out=[do_m(m) for m in range(3,1201)]; \
      json.dump({'per_m':out},open('tworing_m3_1200.json','w'))"

    python tworing_rho.py 3 24               # continuous near-miss measure
                                             # -> tworing_rho_3_24.json
    python nearmiss.py 3 14                  # the near-miss OBJECTS
                                             # -> nearmiss_3_14.json + artifacts/nearmiss_*.json

## 4. Lattice pools (exhaustive over the pool ONLY)

    python run_batch.py lat                  # W=<workers> env var; -> lattice_*.json
    python lattice.py 8 8 Z2 6 3             # single run: n=8, radius 8, square lattice

## 5. Numerical search over real convex n-gons

    python run_batch.py ns                   # -> nsearch_n*.json
    python nsearch.py 12 3000 16             # single n

## 6. Artifacts and the independent verifier

    python export_artifacts.py               # -> artifacts/*.json
    python verify_artifacts.py               # re-checks every artifact from the definitions

`verify_artifacts.py` shares no code with any search script: it derives convex position
from Caratheodory (no point inside a triangle of three others, no three collinear) instead
of from a hull algorithm, and recounts distances from the definition. It reports the mode
used for each object (`exact-integer`, `exact-symbolic`, `high-precision-float`) and, for
high-precision objects, the minimum gap between distinct squared distances so the margin
can be compared with the 1e-40 tolerance.
