# k=3 minimality for a convex polygon — results

**Question (Erdos 1975, explicitly open):** what is the smallest n for which there is a
strictly convex n-gon in which **every vertex has at least 3 other vertices equidistant
from it**?  Danzer's unpublished construction gives n = 9, so the answer is at most 9.
See `LITERATURE.md` — Erdos wrote "It would be of interest to determine or estimate the
smallest possible value of n" and no source found since answers it.

Why this project reached the question: a #982 counterexample on n points has budget
floor(n/2)-1 distinct distances among the other n-1, so pigeonhole forces some distance
from every vertex to have multiplicity at least ceil((n-1)/(floor(n/2)-1)), which is
**exactly 3 for every n from 6 to 15**.  So small-n work on #982 and on the k=3 case of
#97 are the same computation.

## Method

1. **Patterns.** A pattern assigns each vertex i a witness triple T_i of three other
   vertices claimed equidistant from v_i.  A k=3 polygon yields at least one pattern;
   any real realisation of a pattern IS a k=3 polygon.  So deciding every pattern
   decides the question.
2. **Obtuse-middle prune** (`control.py`, `enum_nb.py`).  Writing T_i = {j,k,l} in ccw
   order starting after i, v_i is the circumcentre of triangle jkl.  Seen from v_i the
   other vertices lie in a wedge of angle < pi (the interior angle), so k is on the
   MINOR arc of chord jl and the inscribed angle there is strictly obtuse:
   `D_jl > D_jk + D_kl`.  Union-find on the equalities plus cycle detection on these
   strict order relations refutes most partial patterns in microseconds.
3. **Dihedral reduction** (`enum2.py`).  The triple index encodes the relative offsets
   identically at every vertex, so rotation rotates the sequence (t_0..t_{n-1}) and
   reflection maps t by a fixed involution and reverses it.  Keep only lex-minimal
   representatives.
4. **Decision** (`solve2.py`).  z3 nlsat over the reals, gauge v_0=(0,0), v_1=(1,0),
   FULL convex position (all C(n,3) orientations), plus two implied lemmas that
   shorten refutations: the obtuse inequality and the circumradius identity
   `D_ij (2 D_jk D_kl + 2 D_kl D_jl + 2 D_jl D_jk - D_jk^2 - D_kl^2 - D_jl^2) = D_jk D_kl D_jl`
   (proved symbolically over Q in `cmlemma.py`).

## Results

| n | raw patterns | after prune | classes (mod D_n) | verdict | status |
|---|---|---|---|---|---|
| 4 | 1 | 0 | 0 | **no k=3 convex 4-gon** | `VERIFIED` |
| 5 | 1,024 | 0 | 0 | **no k=3 convex 5-gon** | `VERIFIED` |
| 6 | 1,000,000 | 564 | 66 | **no k=3 convex 6-gon** | `VERIFIED` |
| 7 | 1,280,000,000 | 2,581,924 | 184,424 | running | — |
| 8 | 2,251,875,390,625 | — | enumeration running | — | — |
| 9 | — | — | — | exists (Danzer) | `CITED` |

**Conclusion: the minimum n for the k=3 property is at least 7 and at most 9.**
This is FINAL for this project -- n=7 was stopped by the user on 2026-08-30 as out of
scope (it is Erdos's own 1975 question but not the statement of numbered problem #97,
which asks for k=4).  n=7 therefore stays open and the bound stays at >= 7, not >= 8.

## Controls run (every one passed)

| control | purpose | result |
|---|---|---|
| Danzer's 9-gon vs the obtuse lemma | lemma must hold on a real k=3 polygon | 0 violations over all 9 vertices |
| Danzer's 9-gon pattern vs the prune, depths 0..8 | prune must not reject a realisable pattern | survives every depth |
| Danzer's 9-gon vs the LP prune | same | survives |
| diagonal-crossing on 400 random convex polygons | the only geometric input to the lemma | 0 violations |
| circumradius identity, symbolic | lemma must be implied, not an extra assumption | `lhs - rhs = 0` exactly over Q |
| n=4 brute force, ALL patterns, no prune | conclusion must not depend on the prune | 1/1 unsat |
| n=5 brute force, ALL 1024 patterns, no prune | same | 1024/1024 unsat |
| n=6, 300 prune-REJECTED patterns given to z3 | every rejected pattern must be unsat | 298 unsat, 2 timeout, **0 sat** |
| n=6 independent numerical search (scipy, no z3) | second code path | 0/66 realisable as a strictly convex hexagon |
| n=7 hexagon-plus-centre, no convexity | encoding must find a real k=3 set | SAT, returns the hexagon+centre itself |
| n=7 hexagon-plus-centre, with convexity | convexity must be what bites | UNSAT |

## A trap worth recording

Requiring only CONSECUTIVE-triple orientations to be positive is **not** convex position:
it also admits winding-2 star polygons.  Under that weaker constraint z3 reported 19 SATs
at n=6; all 19 vanish under full convex position, and the independent numerical search
(which checks all C(n,3) orientations) found 0/66.  Any UNSAT under the weak constraint is
still valid, since it is a relaxation — but no SAT under it may be believed.


## n=8 is out of reach, measured not guessed

The pruned DFS was run to depth 5 at n=8 and the surviving-node counts are

    depth 0: 35   depth 1: 549   depth 2: 10,407
    depth 3: 191,204   depth 4: 3,080,726   depth 5: 41,035,399

a growth factor of 13-16 per level, which projects to roughly 1.8e8 classes after
dihedral reduction.  At the measured n=7 throughput (10.9 classes/s on 18 cores)
that is about 190 days.  So n=8 is not attemptable here, and Erdos's question can
at best be narrowed to n in {8, 9} by this route.

## Engineering notes that cost real time

* Per-batch pool recreation was catastrophic: 18 workers each re-importing sympy
  and z3 per batch swamped the ~0.4 s of actual work.  Replaced with independent
  sharded OS processes (`shard.py` + `launch.py`), no multiprocessing at all.
* `multiprocessing.Pool` inside the solver script began failing with
  `PermissionError: [WinError 5]` in `DuplicateHandle` at spawn, while identical
  pools in isolation worked.  Not diagnosed; sidestepped by the sharded design.
* Class indices are in DFS enumeration order, so low indices are systematically
  the HARD ones (they correspond to triples of consecutive neighbours).  Sampling
  randomly gave 0.43 s/class; processing in index order gave >4 s/class.  Shards
  now shuffle their assignment, which also makes early progress representative.


## n=7: STOPPED, not completed -- exactly what was and was not covered

The run was halted by the user at 5.27% coverage.  Recorded state at the stop
(`STATUS_n7_AT_STOP.json`):

    classes decided           9,539  of 184,424
    of which unit ideal       5,489   (refuted exactly over Q, no solver)
    of which nlsat unsat      4,007
    SAT                           0   <-- no realisable pattern found
    z3 unknown                   43
    skipped over budget         171   (Groebner blow-ups, killed by the supervisor)
    coverage                   5.27%
    wall                      2,470 s on 5 workers

Plus 2,700 classes decided by the earlier stalled run (`dead_run/SUMMARY.json`:
1,568 unit ideal + 1,112 unsat + 20 unknown, 0 SAT).  The two runs use different
shuffles so their covered sets overlap and MUST NOT be added together.

**Status of the n=7 claim: `INCOMPLETE`.**  No counterexample was seen in the
~5% examined, which is evidence of nothing -- a search that covers 5% of a space
and finds nothing rules out only what it looked at.  The honest statement remains
the one proved at n <= 6.

## What stands, and what it rests on

`VERIFIED`  no strictly convex 4-gon, 5-gon or 6-gon has every vertex with three
            other vertices equidistant from it.  n=4 and n=5 were brute-forced
            over EVERY pattern with no prune at all; n=6 used the prune plus an
            independent numerical search and a 300-sample soundness check of the
            prune itself.
`CITED`     n=9 is achievable (Danzer, unpublished; figure in Erdos 1987 p.175).
`CITED`     Erdos posed the minimality question in 1975 and it appears unanswered.
=> the minimum lies in {7, 8, 9}.
