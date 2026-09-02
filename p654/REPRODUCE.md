# Reproducing the #654 results

Every command below was run **from a fresh `git clone` of this repository**, in this
directory, and the output quoted is what it actually printed. Where something fails or is
inconclusive, that is quoted too.

Requirements: Python 3, `sympy`, `mpmath`. `numM.py` additionally needs `numpy` and
`scipy`; `pz3.py` needs `z3-solver`. Nothing here imports from outside this directory:
the functions shared with the #98 work are vendored in `common.py`.

Sections 1-6 together take about two minutes. Section 7 is the long one.

---

## 1. The enumerator, validated against brute force

```
python penum.py crosscheck
```

Enumerating patterns by DFS with three symmetry reductions is the step most likely to be
silently wrong, so it is checked against an unreduced brute-force enumeration on five
cases. The canonical counts must agree exactly.

```
CROSSCHECK -- the DFS must agree with brute force
==========================================================================
  [PASS] n=4 m=1 cap=3: brute 1 raw -> 1 canonical; dfs 1 raw -> 1 canonical
  [PASS] n=4 m=2 cap=3: brute 47 raw -> 8 canonical; dfs 34 raw -> 8 canonical
  [PASS] n=5 m=2 cap=3: brute 436 raw -> 14 canonical; dfs 188 raw -> 14 canonical
  [PASS] n=5 m=3 cap=3: brute 31507 raw -> 378 canonical; dfs 15042 raw -> 378 canonical
  [PASS] n=4 m=2 cap=2: brute 24 raw -> 4 canonical; dfs 16 raw -> 4 canonical

CROSSCHECK PASSED
```

## 2. The decider, validated against #98

```
python pdecide.py selftest
```

Four verdicts established independently in the #98 work: the pentagon pattern (unsat), the
`D_gen(5)` witness (sat), the heptagon-minus-a-vertex pattern (unsat), and the same witness
under the weaker no-four-concyclic hypothesis (sat).

```
SELFTEST -- must reproduce verdicts established in the #98 work
==========================================================================
  [PASS] n=5 g   expected unsat got unsat         pentagon (p98/pentagon.py)
  [PASS] n=5 g   expected sat   got sat           the n=5 D_gen witness
  [PASS] n=6 g   expected unsat got unsat         heptagon minus a vertex (p98/six_pattern4.py)
  [PASS] n=5 n4  expected sat   got sat           the same witness must survive the weaker hypothesis too

SELFTEST PASSED
```

## 3. The four lower-bound rungs

```
python penum.py 4 1
python pdecide.py 4 1 g
python pdecide.py 4 1 n4
python penum.py 5 2
python pdecide.py 5 2 g
python pdecide.py 5 2 n4
python penum.py 6 2
python pdecide.py 6 2 g
python pdecide.py 6 2 n4
python penum.py 7 2
python pdecide.py 7 2 g
python pdecide.py 7 2 n4
```

Expected: `f(4) > 1`, `f(6) > 2` and `f(7) > 2` come out clean in both modes. **`n=5, m=2`
leaves one pattern inconclusive** (the Gröbner basis is not triangular for it) and is
settled in section 4.

The block below is **condensed** from the twelve commands: it keeps each rung's canonical
pattern count and each run's verdict tally and conclusion line, and drops the per-pattern
progress lines. It is not a verbatim single transcript; every number in it is copied from
the runs.

```
n=4 m=1: 1 canonical pattern
   g   sat 0  unsat 1  inconclusive 0   => NO configuration with M <= 1: f_g(4) > 1
   n4  sat 0  unsat 1  inconclusive 0   => NO configuration with M <= 1: f_n4(4) > 1
n=5 m=2: 14 canonical patterns
   g   sat 0  unsat 13  inconclusive 1  => inconclusive: 1 pattern(s) undecided
   n4  sat 0  unsat 13  inconclusive 1  => inconclusive: 1 pattern(s) undecided
n=6 m=2: 11 canonical patterns
   g   sat 0  unsat 11  inconclusive 0  => NO configuration with M <= 2: f_g(6) > 2
   n4  sat 0  unsat 11  inconclusive 0  => NO configuration with M <= 2: f_n4(6) > 2
n=7 m=2: 1 canonical pattern
   g   sat 0  unsat 1  inconclusive 0   => NO configuration with M <= 2: f_g(7) > 2
   n4  sat 0  unsat 1  inconclusive 0   => NO configuration with M <= 2: f_n4(7) > 2
```

## 4. The one inconclusive pattern, settled by z3

```
python pz3.py 5 g results/audit_n5_incon.json out_g.json 120 1
python pz3.py 5 n4 results/audit_n5_incon.json out_n4.json 120 1
```

z3's `nlsat` is a decision procedure for real closed fields, so its `unsat` is a proof.
No ordering is imposed on the class values (see the header of `pz3.py` for why that
matters). Both modes must return `unsat`, giving `f(5) > 2`.

```
  mode g :    unsat     1
  mode n4:    unsat     1
```

## 5. The standalone audit

```
python audit654.py
```

Re-derives every claim in `NOTE.md` in exact arithmetic, sharing no code with the scripts
that produced them: the witnesses and their pinned counts, monotonicity, the trivial bound,
the `f(4) > 1` rank argument, and the full structural argument for `f(7) > 2`. Must print
`ALL CHECKS PASSED`.

```
==============================================================================
ALL CHECKS PASSED
```

## 6. The upper bounds

```
python pinned.py
python subsets.py
```

Pinned counts of the #98 witnesses in exact coordinates, then the improvement obtained by
deleting points. This is where `M` and `D` visibly diverge: the `n=8` witness has `D=7` but
`M=4`, better than the `D`-optimal `n=7` witness's `M=5`.

```
  n   D   M = max_i d(x_i)   per-point counts        N3  N4  max on a circle
  --------------------------------------------------------------------------
  3    1    1                 [1, 1, 1]              ok  ok  2
  4    2    2                 [1, 1, 2, 2]           ok  ok  3
  4c   2    2                 [2, 2, 2, 1]           ok  ok  3
  5    3    3                 [2, 2, 3, 2, 2]        ok  ok  3
  6    4    4                 [3, 4, 4, 3, 4, 3]     ok  ok  3
  7    5    5                 [3, 5, 4, 4, 4, 5, 4]  ok  ok  3
  8    7    4                 [3, 4, 4, 3, 4, 4, 4, 4] ok  ok  3

  n   ceil((n-1)/3)   best M found   witness   subset
  --------------------------------------------------------------------
  3   1               1              4         (0, 1, 2)   <-- MATCHES THE BOUND
  4   1               2              4         (0, 1, 2, 3)
  5   2               3              5         (0, 1, 2, 3, 4)
  6   2               4              6         (0, 1, 2, 3, 4, 5)
  7   2               4              8         (0, 1, 2, 3, 4, 5, 6)
  8   3               4              8         (0, 1, 2, 3, 4, 5, 6, 7)
```

## 7. The searches (long; not needed for any claim in the table)

```
python latM.py controls
python latM.py 8 121 a2 g 4 0 3      # one shard of the n=8 lattice sweep
python numM.py 6 3 g 100000 1 200    # the off-lattice control, n=6
```

The lattice controls must reproduce known pinned maxima. The `n=8` sweep takes roughly 45
minutes per shard and finds nothing.

**The `numM.py` control is the important one, and it FAILS to find a configuration that
exists.** At `n=6` an `M=3` configuration is known and verified exactly (`results/
witness_n6_M3.json`), and the search finds nothing: zero leads in the 284 restarts this
200-second budget allowed, and zero in an earlier, longer run of 512. That is why the
off-lattice negatives at `n=7` and `n=8` are reported in `NOTE.md` as carrying no
evidential weight. It is quoted here precisely because it is a negative result about our
own method.

The lattice controls in the same block did not always pass. An earlier version of
`latM.py` expected `M <= 3` at `n=7`, which contradicts our own finding that no `M=3`
configuration exists in `A_2` at that size; the control therefore failed by construction,
and took 357 seconds to do it. The expectations now come from the exact-verified witnesses
and the radii from where those witnesses actually live.

```
CONTROLS -- must reproduce pinned maxima we have already verified exactly
==========================================================================
  [PASS] n=4 g   target M<3: best 2 (expected <= 2)  0.0s
  [PASS] n=6 g   target M<5: best 3 (expected <= 3)  0.3s
  [PASS] n=7 g   target M<5: best 4 (expected <= 4)  1.2s
  [PASS] n=4 n4  target M<3: best 2 (expected <= 2)  0.0s

CONTROLS PASSED

off-lattice search n=6, target M<=3, mode g, seed 1, budget 200.0s
  200 restarts, best objective 2.000e-07, 0 leads, 172s
  done: 284 restarts, best objective 2.000e-07, 0 distinct leads, 200s
  written: numM_n6_m3_g_s1.json   (leads are CANDIDATE PATTERNS, to be decided exactly)
```

## What the results/ directory holds

| file(s) | contents |
|---|---|
| `phase0_pinned.json`, `upper_by_deletion.json` | pinned counts of the #98 witnesses, and of every subset |
| `witness_n6_M3.json` | the `n=6`, `M=3` configuration, exact-verified |
| `penum_n*.json` | the enumerated pattern sets |
| `pdec_n*_m2_*.json` | the per-pattern verdicts for the four rungs, both modes |
| `audit_n5_incon_*.json` | z3's verdicts on the one inconclusive pattern |
| `latM_*.json` | every lattice shard, with its completion status |
| `numM_*.json` | every off-lattice run, with restart counts and leads |
| `leads_n7_m4_*.json`, `lead_n7_n4_pdec.json` | the disagreement between the numerical leads and the exact decider, recorded rather than resolved |
