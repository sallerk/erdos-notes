# Reproducing the #654 results

Every command below was run **from a fresh `git clone` of this repository**, in this
directory, and the output quoted is what it actually printed. Where something fails or is
inconclusive, that is quoted too.

Requirements: Python 3, `sympy`, `mpmath`. `numM.py` additionally needs `numpy` and
`scipy`; `pz3.py` needs `z3-solver`. Nothing here imports from outside this directory:
the functions shared with the #98 work are vendored in `common.py`.

Total runtime for everything in sections 1–4: about six minutes.

---

## 1. The enumerator, validated against brute force

```
python penum.py crosscheck
```

Enumerating patterns by DFS with three symmetry reductions is the step most likely to be
silently wrong, so it is checked against an unreduced brute-force enumeration on five
cases. The canonical counts must agree exactly.

```
(output)
```

## 2. The decider, validated against #98

```
python pdecide.py selftest
```

Four verdicts established independently in the #98 work: the pentagon pattern (unsat), the
`D_gen(5)` witness (sat), the heptagon-minus-a-vertex pattern (unsat), and the same witness
under the weaker no-four-concyclic hypothesis (sat).

```
(output)
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
leaves one pattern inconclusive** — the Gröbner basis is not triangular for it — and is
settled in section 4.

```
(output)
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
(output)
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
(output)
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
(output)
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
exists.** At `n=6` an `M=3` configuration is known and verified exactly, and the search
returns zero leads in 512 restarts. That is why the off-lattice negatives at `n=7` and
`n=8` are reported in `NOTE.md` as carrying no evidential weight. Quoted here precisely
because it is a negative result about our own method:

```
(output)
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
