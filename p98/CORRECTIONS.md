# Corrections found by the full audit

Every item below was found by re-reading a primary source rather than by re-reading my
own notes. Each was WRONG in a file that was otherwise ready to post.

## 1. The "Pach" bound is not uncited. It is Erdős–Hickerson–Pach 1989.

**Was claimed:** "the page attributes `h(n) < n^{log_2 3}` to Pach with no citation; I
could not locate it, including in the page's LaTeX source." That went into the comment as
a finding.

**Truth:** P. Erdős, D. Hickerson, J. Pach, *A problem of Leo Moser about repeated
distances on the sphere*, Amer. Math. Monthly **96** (1989) 569–575, **p.571**:

> "THEOREM 1. For every natural number n, G(n) < (3/2)n^{log3/log2}"

with, on the same page, "let G(n) = min g(P), where the minimum is taken over all
n-element point sets P in the plane in general position", and general position defined
p.570 as "no 3 of them on a straight line and no 4 on a circle". **That G(n) is exactly
our D_gen(n).** Verified directly at https://www.renyi.hu/~p_erdos/1989-02.pdf.

The page's attribution to "Pach" alone is incomplete, not absent. The claim has been
removed from the comment.

## 2. Szemerédi conjectured `G(n) >= (n-1)/2`, and I did not know it existed.

Same page, same paragraph:

> "Szemerédi [Sz] observed that G(n) ⩾ (n−1)/3. (In fact, he conjectures G(n) ⩾ (n−1)/2,
> which would generalize a theorem of Altman [A].)"

This is a far more relevant benchmark than the `(n-1)/3` everything was being compared
against. Our values are consistent with it and not close to tight:

| n | D_gen(n) | (n−1)/3 | (n−1)/2 |
|---|---|---|---|
| 3 | 1 | 2/3 | 1 (equality) |
| 4 | 2 | 1 | 3/2 |
| 5 | 3 | 4/3 | 2 |
| 6 | 4 | 5/3 | 5/2 |
| 7 | 5 | 2 | 3 |

## 3. "Harborth and Ruzsa" is wrong: it is HAMBURGER and Ruzsa, and a different function.

[Er75f] p.101 reads "**HAMBURGER** and RUZSA showed that in this case D_2(x_1,…,x_6) **⩾** 6"
(not Harborth, and ⩾ not >). Critically it sits inside the *isosceles-free* variant, not
the no-3-collinear/no-4-cocircular function. So it is **not** a published small value of
h(n) and does not collide with the novelty claim — but the attribution in REFERENCES.md
was wrong on two counts.

## 4. [Er87b]: the crescent-configuration implication is on p.168, not p.167.

"f(n) ≥ n for n > n₀ would of course show that my conjecture is true" is on **p.168**.
Only the other quote ("I have no example to show that f(n)/n² → 0 …") is on p.167.

## 5. NPPZ: the isosceles-triangle question is their Problem 1, not Problem 2.

arXiv:1207.1266, p.3. Their Problem 2 (p.9) is an unrelated bichromatic question. Also
their Problem 1 asks for "convex (or in general) position", not only no-3-collinear.

## 6. A form discrepancy in Szemerédi's bound, worth recording.

Sheffer and the Handbook both state `⌈(n−1)/3⌉`. The primary [Er75f] p.101 prints
`max_i d_2(x_i) ⩾ [n/3]`, i.e. `⌊n/3⌋`. These differ at n ≡ 2 mod 3 (at n=5: 2 versus 1).
Our "best known lower bound" window compares against the **stronger** `⌈(n−1)/3⌉`, so the
window claim is conservative either way.

## 7. Two scripts in the repo were unmarked traps.

`gram.py` is unsound for negative verdicts (17 false unsats) and carried no warning;
`six_pattern.py` reaches the right verdict by unsound reasoning (casus irreducibilis).
Both now have prominent headers.
