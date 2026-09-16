# Reproducing p831

Python 3.12 (3.12.9 here), numpy, scipy, sympy and z3 for everything written in Python.
Sections 5a and 5b of NOTE.md, and the corroborating runs for 5c, also need Docker (Singular
and msolve, see below), and section 6 needs a Reduce build with Redlog. Run everything from
this directory.

Not everything in NOTE.md can be regenerated from here. The last section of this file says
what cannot, and why.

## Fast, exact, no search (seconds)

    python lemmas.py        # Lemmas 1, 2, 3, 4 and 4a in exact rational arithmetic
    python lemma6.py        # Lemma 6's two congruences, symbolically; it does not check Lemma 5
    python verify.py        # re-checks the claims listed in its own output (about 5 s)
    python cp_verify.py     # NOTE.md section 5c (about 100 s, 61 checks; exact except floating-point parts of the last two)

`verify.py` reads the witnesses back out of `results/` and re-derives them from the
definitions in sympy, sharing no code with the searches, prints the bound table, and checks
sections 5a and 5b against their artifacts. It does not check every claim in NOTE.md, and it
does not check the mathematics of section 5c, which is what `cp_verify.py` is for. Both exit
non-zero on any failure. In `cp_verify.py` every PASS line is the result of a computation;
statements that only read earlier checks are printed as NOTE lines and are not counted.

## Pattern enumeration (seconds)

    python penum.py 5 1     # 0 patterns  -> h(5) >= 2 with no external input
    python penum.py 5 2     # 1 pattern, class size 5 > f(5)=4 -> h(5) >= 3
    python penum.py 5 3     # 15 patterns, 12 of them also within f(5)=4

## Upper bounds by search (minutes)

    python lath.py 4 6 6 4          # positive control: must return h = 1
    python lath.py 5 11 11 5        # returns 4
    python lath.py 6 11 11 7        # returns 6, exhaustive over that grid
    python lath.py 5 17 17 4        # none with 3 or fewer radii (8.5M nodes, about 29 minutes)
    python beam.py 8 13 13 30000    # beam over a 13x13 grid, n up to 8: h(7) <= 12, h(8) <= 16

`lath.py` is an exhaustive DFS over subsets of the integer grid with an admissibility
test and a monotone prune on the running radius count; `beam.py` is a heuristic. Both
use exact integer arithmetic, so any configuration they report is genuinely admissible
and its radius count is exact. Neither proves anything about h(n): a lattice is a
restriction, and a beam is not a search.

## The n = 5 case analysis, numerical (minutes to hours)

These are the original numerical instruments, kept because NOTE.md section 5 tells their
history. Several are superseded or withdrawn; read "Corrections after the audit of
2026-09-07" below before reading anything into their output. None of them is evidence for
the exact results of sections 5a and 5c.

    python ctrlA.py         # SUPERSEDED control (4 equations in 4 unknowns solvable, 5 not)
    python caseA.py 150 2   # SUPERSEDED search; prints a best residual of about 7e-8
    python orthobranch.py   # VACUOUS: searches for what Lemma 6 makes impossible
    python typeIII.py 10 10 # sweep of the common-point family; the recorded run is PARTIAL
    python pscreen.py 5 3 500 99      # all 15 patterns; its headline is superseded
    python pdecide.py 5 3 1800000     # z3 nlsat, 30 minutes per pattern; decided nothing
    python caseA2.py 300              # the Case A search that replaced caseA.py
    python r2check.py                 # every solution FOUND is four-concyclic (a sample)
    python gridsweep433.py 140        # global grid sweep of the common-point branch
    python fgp.py                     # largest classes in the witnesses: f_gp(n) = f(n), n <= 6
    python p11diag.py 11 1500         # third-shape pattern 11, numerically; also: 5 1500

`obstruction433.py`, which produced the s^2/2 floors, **cannot run**: its third line execs
`target433.py`, which is not in this directory, and the two functions it needs (`points` and
`r2_of`) are defined nowhere else. `results/obstruction433.json` is the frozen record of that
run and carries every figure NOTE.md quotes; `cp_verify.py` section 13 checks those floors
against their exact closed form, and `audit_round2/probe_obstr.py` is an independent
reimplementation that prints its comparison and writes no artifact. `p11diag.py`'s artifacts
do not record the random seed; the script's default is 831.

A search that cannot find a known solution cannot report an absence, so no negative from these
scripts should be believed without a control that can succeed. The controls that survived the
audits are the ladder inside `caseA2.py`, monotone by construction, and `ctrlB.py`, with the
caveat below. `ctrlA.py` and the control line printed by `pscreen.py` do not qualify: the first
was built wrongly and the second is exactly determined, so it is too easy.

## What was actually run for the numbers in NOTE.md

| claim | produced by | artifact |
|---|---|---|
| h(4) = 1 | lath.py 4 6 6 4, re-verified in sympy by verify.py | results/lath_n4_6x6_t4.json |
| h(5) <= 4 | lath.py 5 11 11 5 | results/lath_n5_11x11_t5.json |
| h(6) <= 6 | lath.py 6 11 11 7, exhaustive over that grid | results/lath_n6_11x11_t7.json |
| no admissible 5-set with 3 or fewer radii on the 17x17 grid | lath.py 5 17 17 4 | results/lath_n5_17x17_t4.json |
| h(7) <= 12, h(8) <= 16 | beam.py 8 13 13 30000 | results/beam_13x13_w30000.json |
| bound table | verify.py, from A003829 | printed |
| f_gp(n) = f(n) for n <= 6 | fgp.py | results/fgp.json |
| 15 patterns | penum.py 5 3 | results/penum_n5_k3.json |
| Case A, numerical history | caseA2.py 300 (caseA.py and ctrlA.py superseded) | results/caseA2.json |
| Case A, exact (NOTE 5a) | caseA_exact.py, in the container | results/caseA_exact_*.json, results/caseA_exact.log |
| third shape, modulo primes only (NOTE 5b) | third_exact.py, and the snippet in the third-shape section for its Singular files | results/third_exact_*.json, results/third_exact.log |
| common-point branch, exact (NOTE 5c) | cp_verify.py | printed; mod-p corroboration in results/cp_exact.log |
| every solution found is four-concyclic (577, numerical) | r2check.py | results/r2_unguarded_roots.json |
| s^2/2 floors | obstruction433.py, which can no longer run | results/obstruction433.json (frozen) |
| parallelogram branch empty | orthobranch.py; VACUOUS, do not cite | results/orthobranch.json |
| engine versions | queried from the container | results/engine_versions.json |

## The harder control (added during the audit)

    python ctrlB.py

Builds an admissible configuration whose pattern has four classes and checks that
`pscreen`'s optimiser recovers it. An earlier version of this file said its six constraint
equations have Jacobian rank five and called it "the control that matters". Both are
withdrawn. The rank is four: `ctrlB.py`'s one-sided differences at eps = 1e-6, compared
against an absolute tolerance, misread it, and exact derivatives show two dependencies. A
larger deficiency makes the control easier, not harder, and the measured per-restart hit
rates, 47/500 against 51/500 for the control it was meant to replace, agree.
`results/ctrlB.json` records both corrections in its `rank` and `rank_note` fields.

**Do not re-run `ctrlB.py` over that file.** The script still computes the rank the old way
and writes the file from scratch, so a re-run puts back `"rank": 5` and deletes the note that
records the withdrawal. Copy `results/ctrlB.json` somewhere first.

## Corrections after the audit of 2026-09-07

Read `AUDIT_SUMMARY.md` first. The following supersede entries above.

* **`ctrlA.py` and `caseA.py` are superseded by `caseA2.py`.** The old control
  normalised by the mean of all six radii while constraining only some, and dropped
  equations in an order that violates Lemma 1; the old search had no degeneracy guards
  at all. Run `python caseA2.py 300` instead. Its artifact is `results/caseA2.json`.
* **`pscreen.py`'s headline is superseded, and so is `tausweep.py`'s.** The screen's
  margin is a parameter now, but sweeping one margin while holding the others fixed just
  relocates the problem: the class-separation guard turned out to be active at almost
  every optimum of the sweep. Do not read TRACKS-TAU or FLAT-IN-TAU as an obstruction.
  **The decisive test is `python r2check.py`**, which drops every guard, solves the
  equalities alone by least squares from 120 random starts per pattern, and finds that every
  one of the 577 solutions it converges to, across all fifteen patterns, puts four points on
  a circle. That is a numerical sample, not a statement about every solution; an earlier
  version of this file and of NOTE.md said "all of them", which would have settled h(5) = 4.
  The sweeps are a record of how floors move.
* **`orthobranch.py` is vacuous** and is retained only as a record. Do not cite it.
* **`gridsweep433.py`** supplies the global grid sweep that NOTE.md previously asserted
  without an artifact. Run `python gridsweep433.py 140`.
* **`enc_test.py`** now writes `results/enc_test.json`.
* **Artifact names carry the search target**: `lath_n5_17x17_t4.json`, not
  `lath_n5_17x17.json`. Two runs at different targets are different experiments and the
  old naming let one silently overwrite the other.
* **The 17x17 run** is `python lath.py 5 17 17 4` (now in the table above), and it is the
  command behind the headline exhaustive statement in NOTE section 4.
* `results/typeIII_n5.json` is a PARTIAL run (3 of 10 splits). That branch is now closed
  exactly by NOTE.md section 5c and checked by `cp_verify.py`; `gridsweep433.py` and the
  frozen `results/obstruction433.json` are corroborating numerics only.

## The clean run (2026-09-16, after the third audit)

    python lemmas.py        # ALL CHECKS PASSED   (Lemmas 1, 2, 3, 4, 4a, exact)
    python lemma6.py        # ALL CHECKS PASSED   (Lemma 6's congruences, symbolic)
    python AUDIT_SELF.py    # 0 defects
    python verify.py        # ALL CHECKS PASSED
    python cp_verify.py     # ALL 61 CHECKS PASSED

`verify.py` now re-derives every recorded witness from the definitions rather than
reading a flag, excludes checkpoint files, and enforces that the write-up discloses the
weaknesses the audit found rather than that those weaknesses are absent. Where a
limitation cannot be removed, the check asserts that NOTE.md states it.

## The quantifier elimination that did not finish (2026-09-07 to 2026-09-08)

`mkqe.py` writes the surviving common-point pattern as a real quantifier-elimination
problem in three variables, `qe_typeIII.red` with all eighteen side conditions and
`qe_typeIII_lean.red` with five. To run them you need Reduce with Redlog; the build used
here was Free PSL revision 7327 of 2026-03-08, unpacked into a scratch directory:

    cd reduce
    ./psl/bpsl.exe -td 3000000000 -f ./red/reduce.img < ../qe_typeIII.red > ../qe_out.log

Two traps. The input must have Unix line endings; a carriage return makes Redlog answer
"Declare ? operator?" and stop. And the output is buffered, so the log file's size stays
at whatever the projection phase wrote and tells you nothing about progress; track
processor time instead, which is what `qewatch.py` does. Its docstring records why: the first
version watched the log's size and could not tell a busy run from a dead one. `qewatch.py`
reads the Redlog log from an absolute path inside one session's scratchpad directory, so set
`LOG` at its top before using it anywhere else.

Neither run finished. Both reached the extension phase within a minute and then produced
no further output for 20.4 and 19.5 hours of processor time, at about 2 GB each,
and were stopped on 2026-09-08. NOTE.md section 6 says what that does and does not mean.
Do not repeat the runs as they stand; change the projection first.

## Case A decided exactly (2026-09-14 to 2026-09-15)

Needs Docker. The computer algebra runs in an Ubuntu 24.04 container with Singular 4.3.2
and msolve 0.6.5, both from Ubuntu's own archive (about 16 MB of packages). The exact builds,
queried from the container that ran every job, are recorded in `results/engine_versions.json`:
Debian packages `singular 1:4.3.2-p10+ds-1.1build1` and `msolve 0.6.5-1build2`. The Dockerfile
does not pin versions, so a later rebuild may install newer ones; compare against that file.

    docker build -t erdos831-cas docker
    docker run -d --name cas831 --cpus 7 -v "<path to p831>:/work" erdos831-cas sleep infinity

The container runs with a limit of 7 CPUs now. The limit in force for each individual run is
not recorded, but the job thread counts the logs do record never exceed 7. Several jobs often
ran at once, so every timing below is wall-clock time under load.

`caseA_exact.py` writes the polynomial systems and drives the container. Every run appends
to `logs/caseA_exact.log` (the repository does not carry `logs/`; the log as of 2026-09-16 is
archived as `results/caseA_exact.log`), streams progress to `exact/<job>.<engine>.live`, and records its
verdict in `results/caseA_exact_<engine>.json`.

    python caseA_exact.py gen                           # 9 splits x 2 gauges, and controls
    python caseA_exact.py xcheck                        # against caseA2.py's near-solutions
    python caseA_exact.py run msolve F1 control 6       # 32 real roots, planted one among them
    python caseA_exact.py run msolve F2 control 6
    python caseA_exact.py run msolve F2 0,1,2,3,4,5,6,7,8 6   # each: no complex solution
    python caseA_exact.py run msolve F1 0,1,2,3,4,5,6,7,8 6
    python caseA_exact.py genplant                      # also writes the pinned controls
    python caseA_exact.py run msolve F1 pin4 1          # the planted configuration returns
    python caseA_exact.py run msolve F2 pin4 1

msolve decides "no solution" from a Groebner basis modulo one prime, so those verdicts are
not proofs. The proofs are the two exact computations over Q:

    python caseA_exact.py genreduced 4 F2 5,11
    python caseA_exact.py run singrab F2 red4 1         # unit ideal, 17 s
    python caseA_exact.py gencand
    python caseA_exact.py run singrab F1 cand1 1        # unit ideal, 8 min

The conditions kept in `F2_red4` (factor 5, P differs from B; factor 11, the first new
radius differs from R) were chosen by `python caseA_exact.py greedy 4 F2 9,2,3,8,6,7,10,1,0,11,4,5,12`,
which works modulo a prime and only chooses; `verify.py` rebuilds both systems from the
geometry and checks that every condition imposed is one admissibility forces.

Traps met on the way (the log records every run, including those stopped by hand):

* Git Bash rewrites `/work/...` in hand-typed `docker exec` arguments; prefix
  `MSYS_NO_PATHCONV=1`. The Python driver is not affected.
* msolve eliminates towards its last variable, and both gauges are symmetric under
  reflection, so a separating linear form `zsep` is appended as the last variable.
* Singular buffers a pipe; the driver runs it under `script` so progress is visible.
* Systems that HAVE solutions (one equation dropped, or a planted split left unpinned) are
  far heavier for F4 than the inconsistent ones and ran the container out of memory; the
  pinned controls replace them.
* Singular on the full 13-condition systems did not finish in hours. The reduced systems
  finish in seconds to minutes; imposing fewer conditions is what made the exact proof
  possible.
* Several runners once shared one results file and overwrote each other's records; the
  driver now re-reads the file before every write, and the lost jobs were re-run.

## The third shape (2026-09-15): evidence modulo primes, not a proof

Same container. `third_exact.py` handles the seven third-shape patterns (5, 7, 8, 9, 10,
11, 13 of `results/penum_n5_k3.json`); it recomputes that list and asserts it. Log:
`logs/third_exact.log`, archived as `results/third_exact.log`; verdicts in
`results/third_exact_<engine>.json`.

    python third_exact.py gen                           # G1_p<i>, G2_p<i> (all twelve conditions), pinned controls
    python third_exact.py run msolve G1_pin5,G1_pin7,G1_pin8,G1_pin9,G1_pin10,G1_pin11,G1_pin13 6
    python third_exact.py run msolve G2_pin5,G2_pin7,G2_pin8,G2_pin9,G2_pin10,G2_pin11,G2_pin13 6
                                                        # each: 1 real root, the planted one

Modulo a prime (evidence, not proof): msolve on the all-conditions system of each pattern
(the first step of `python third_exact.py greedy G1 <pattern>`) returns no solution for every
pattern except 11. On pattern 11 msolve gave no verdict in either gauge: in G1 it crashed after
431 s under a 10 GB memory cap, when enlarging its hash table failed (`exact/G1_p11_modp.live`
ends with that message), and in G2 it was stopped by hand at 5.5 GB, near its 8 GB cap, as
redundant once Singular had decided pattern 11 modulo 32003 (`results/third_exact.log`). Singular's slimgb returns the unit ideal for all
seven modulo 32003 (2 to 138 seconds) and modulo 32749 (3 to 173 seconds).

**No command-line step writes the Singular input files; the code that does is here.**
`third_exact.py gen` writes the msolve systems `G1_p<i>` and `G2_p<i>` and the pinned controls,
and `genreduced` writes reduced systems `G<g>_red<i>` in both formats, but the characteristic-0
files `exact/G1_full<i>.rab.sing` and `exact/G2_full5.rab.sing` (and the common-point files
below) were written from a Python prompt during the session. The functions it used are in the
directory, and this regenerates all ten files byte for byte (checked on 2026-09-16 against the
files in `exact/`; a git checkout that converts line endings, as Git for Windows does by
default, differs from them in line endings only); it writes into `regen/` so nothing existing is
overwritten:

    python - <<'EOF'
    import json, os
    import third_exact as T, caseA_exact as CA
    CA.EXD = 'regen'; os.makedirs('regen', exist_ok=True)
    PZ = json.load(open('results/penum_n5_k3.json'))['patterns']
    for g, i in [('G1', 5), ('G1', 7), ('G1', 8), ('G1', 9), ('G1', 10), ('G1', 13), ('G2', 5)]:
        CA.write_singular_rab('%s_full%d' % (g, i), *T.system(g, PZ[i]['labels']))
    for i in (2, 12, 14):
        CA.write_singular_rab('G1_cp%d' % i, *T.system('G1', PZ[i]['labels']))
    EOF

The prime-field copies (`*_modp.sing` for 32003, `*_mods.sing` for 32749) are those files with
`ring R = 0,` changed to `ring R = 32003,` or `ring R = 32749,` and nothing else changed. Pattern
11 uses `exact/G1_red11.rab.sing`, which `genreduced` writes keeping all twelve conditions
(`python third_exact.py genreduced G1 11 0,1,2,3,4,5,6,7,8,9,10,11`). `verify.py` also rebuilds
the seven characteristic-0 systems from the geometry, with its own code, and checks that they
match. Keep the prime below 2^15: modulo 2147483647 pattern 5 took 1484 seconds against 2, and
65521 was also slow.

**No exact decision over Q was obtained for any third-shape pattern.** These runs were
attempted and none of them returned a verdict:

    python third_exact.py run singrab G1_full5 1        # and G2_full5, G1_full7 ... G1_full13
    python third_exact.py run singrab G1_red11 1        # pattern 11

Pattern 5 (in both gauges) and pattern 9 were stopped for memory after 1 h 38 to 3 h 24, and
patterns 7, 8, 10, 11 and 13 were killed at their six-hour cap, still at degree 7. Pattern 8's
record in `results/third_exact_singrab.json` is flagged as reconstructed from its live output
file, because its log lines were lost when four runners appended in the same second. Exact
runs on REDUCED systems (fewer conditions, the route that decided Case A) also stalled for
hours. Do not repeat these runs as they stand.

## The common-point branch (2026-09-15 to 2026-09-16): proved, checked in pure Python

    python cp_verify.py

This is the whole check of NOTE.md section 5c: Lemmas 7 and 8, both proofs, the Lemma 6 kills
of patterns 2 and 12, the fact that pattern 14 has exactly one canonical splitting, and the
corrections section 5c makes to the s^2/2 paragraph of section 5. It needs only sympy, takes
about 100 seconds, and does not use the container.

The proof uses no decision procedure. Two corroborating runs did use the container and are
recorded in `results/cp_exact.log`: Singular modulo 32003 and modulo 32749 finds the unit ideal
for patterns 2 and 12 and dimension 1 for pattern 14, and Singular over Q on patterns 2 and 12
was killed at its one-hour cap. Their input files, `exact/G1_cp2`, `G1_cp12` and `G1_cp14`
(`.rab.sing`, `_modp.sing`, `_mods.sing`), are regenerated by the snippet in the third-shape
section above, with the same ring-line change for the prime-field copies.

## What cannot be reproduced from this directory

* **The s^2/2 floors.** `obstruction433.py` cannot run (see above), so
  `results/obstruction433.json` is a frozen record. `results/target433.json` and
  `results/slice433.json` have no producing script at all (`target433.py` and `slice433.py`
  are lost), and nothing cites them.
* **No command-line step writes the Singular input files behind NOTE.md sections 5b and 5c.**
  They are reproducible, byte for byte, from the Python snippet in the third-shape section.
* **Figures measured by auditors outside this directory**, which NOTE.md flags where it quotes
  them: the roughly 7,600 roots for the size-5 classes; the 200x200 by 241x241 Case A grid; the
  0.33% and 19% hit rates; the C reimplementation of the lattice node counts and of the
  198,792,594 five-subsets; and the six-significant-figure replication of the s^2/2 law
  (`audit_round2/probe_obstr.py` re-runs it but only prints the comparison).
* **`qewatch.py`** reads its log from an absolute path inside one session's scratchpad
  directory; set `LOG` at its top before using it. The round-2 probes in `audit_round2/` had the
  same problem and have used paths relative to their own location since 2026-09-16, when
  `python audit_round2/probe_guards.py` was re-run and wrote `audit_round2/probe1a.json`, the
  artifact behind NOTE.md's "14 of 15".
* **`caseA.py`'s residual of about 7e-8** is printed by the run and not stored in
  `results/caseA_n5.json`. An auditor re-ran the documented command and reproduced it, but
  re-running overwrites that artifact.
