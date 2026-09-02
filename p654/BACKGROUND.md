# Background study: Erdős #654 and #655

Written before any computation, per the standing rule that the literature comes first
(lesson L53: substitute your own `n` into the published bounds *before* spending compute).
Everything below is read at source or explicitly flagged as unverified.

**Status: no calculations started.** #98 must complete first.

---

## 0. The single most important fact about each

**Both problems are partly DISPROVED. Neither can be "solved" as literally stated.**

* **#655 is false as written.** Zach Hunter's regular `n`-gon satisfies the hypothesis and
  gives exactly `⌊n/2⌋` distances, not `(1+c)n/2`. The disproof is **formalised** in
  google-deepmind/formal-conjectures as `erdos_655`, `research solved, answer(False)`.
* **#654's strongest form is false.** Aletheia constructed `n` points, no four cocircular,
  with at most `3n/4` distances from any point. That set lies on **two lines**, so it does
  not touch the general-position version.

**#655 is additionally flagged AMBIGUOUS.** Terence Tao added that flag to the database;
Thomas Bloom declined to fix an interpretation ("I'd rather not guess"). *Choosing an
interpretation is choosing the problem*, and any writeup must say which variant it means.
There is also an **open discrepancy**: formal-conjectures issue #4298 notes the repo calls
it solved while the website still lists it OPEN (checked 2026-09-02).

## 1. Notation (following Chojecki, and used throughout)

For a finite planar `X` with `|X| = n`:

* `D(X)` = number of distinct pairwise distances (**global**)
* `d_X(x)` = number of distinct distances from `x` (**pinned at x**)
* `M(X) = max_x d_X(x)` (**pinned**), `Σ(X) = Σ_x d_X(x)` (**sum**)
* `A_m` = every circle centred at a point of `X` contains at most `m` other points of `X`
* `N3` = no three collinear, `N4` = no four cocircular, `G = N3 ∩ N4` (general position),
  `C` = convex position

**These must never be blurred.** Global vs pinned vs sum, and `N4` alone vs full `G`, are
four different problems with four different statuses.

## 2. The verified landscape

Chojecki's Table 1 (Ulam, Apr 2026, 11pp), each row checked:

| hypotheses | quantity | status |
|---|---|---|
| `A2` | `D`, `M` | **exact** `= ⌊n/2⌋`, regular `n`-gon extremal |
| `A2` | `Σ` | **exact** `= n⌊n/2⌋` |
| `N3 ∩ A2` | all three | **exact**, same — the `n`-gon still qualifies |
| `C ∩ A2` | all three | **exact**, same |
| `N3` | `D` | **open**, `⌈(n−1)/3⌉ ≤ D_N3(n) ≤ ⌊n/2⌋` |
| `C` | `D` | **exact** `= ⌊n/2⌋` (Altman) |
| `C` | `M` | **open**, `(13/36 + 1/22701)n + O(1) ≤ M_C(n) ≤ ⌊n/2⌋` |
| `G` | `D` | **open** ← **this is #98**, `⌈(n−1)/3⌉ ≤ D_G(n) ≤ n·2^{O(√log n)}` |
| `G` | `M` | **open** ← **this is #654** |
| `N4 ∩ A2` | `M` | **open** — "the most faithful repair of #655" |

**The structural point.** Adding only `N3`, or only `C`, does **not** repair #655: the
regular `n`-gon has no three collinear and is convex. **Only excluding four cocircular
points removes it.** Confirmed independently (Sheffer p.6: "The convex n-gon configuration
is not in general position").

## 3. Sources, verified at origin

* **Erdős 1988** — *Some Old and New Problems in Combinatorial Geometry*, in Applications
  of Discrete Mathematics (Clemson 1986), SIAM 1988, pp. 32–37. **Question (6), printed
  p. 35.** Hypotheses "no four on a circle and every circle whose center is one of the
  x_i contains at most two of our points"; asks whether `max d(x_i) > (1+c)n/2` and
  `Σ d(x_i) > (1+c)n²/2`; remarks the cocircularity assumption is needed "since otherwise
  the regular polygon gives a counterexample".
  `users.renyi.hu/~p_erdos/1988-32.pdf`
  **Two things Chojecki omits: Erdős offers $25, and he adds a fourth caveat that not too
  many points lie on a line.**
* **Erdős 1987** [Er87b] — Colloq. Math. Soc. J. Bolyai 48, pp. 167–177, verified pp.
  167–168: the `n/3`-scale general-position questions, `D(n) > (1+c)n/3`, the sum version,
  and an `A3` weakening.
* **Altman** — convex global `D_C(n) = ⌊n/2⌋` proved (1963 Monthly and 1972 Canad. Math.
  Bull.); convex **pinned** genuinely open (Sheffer's Problem 7).
* **Aletheia = [Fe26]** — Feng et al., arXiv:2601.22401, *Semi-Autonomous Mathematics
  Discovery with Gemini*. Construction `{(0,±3^k)} ∪ {(±2^j,0)}`, `n = 4m`, giving
  `M(X) ≲ 3n/4` with no four cocircular. **On two lines**, so it fails `N3` and is not
  claimed to satisfy `A2`. It touches neither the `G ∩ A2` variant nor Erdős's 1988
  question.

## 4. Assessment of the one piece of prior work

Chojecki's Theorem 3.1 is **correct but trivial**: one line of pigeonhole
(`X ∈ A_m ⟹ d_X(x) ≥ ⌈(n−1)/m⌉`, so `m=2` gives `⌊n/2⌋`) plus the regular `n`-gon for
sharpness. Both directions are complete and I found no error, but it contains no new
mathematics — it is Hunter's counterexample plus a bound the website already stated. It is
an AI-assisted survey note (Chojecki says he used GPT-5.4 Pro). **No replies, no citations,
no endorsement or contradiction anywhere.**

Its real gap: `[Er97e]` — the source erdosproblems.com actually cites for #655 — appears
in its bibliography but is **cited nowhere in the body**, and the note never mentions that
the site attributes #655 to *Erdős and Pach*, nor `[ErPa90, p.267]`. For a document
subtitled "Historical Sources" that is a material omission.

## 5. Is the live #655 variant vacuous? No.

A generic `n`-point set has all `C(n,2)` distances distinct, so every circle centred at a
point contains exactly **one** other point — that is `A1 ⊂ A2` — and generically no three
collinear and no four cocircular. So `G ∩ A2` is non-empty for every `n`, indeed of full
measure. **The variant's entire content is the lower bound.** (Flagged: this is a reading
of the definitions, not a cited result.)

## 6. What our #98 results already give, for free

`G ∩ A2 ⊆ G`, so `D_{G∩A2}(n) ≥ D_G(n) = D_gen(n)`. Our computed values therefore apply
immediately:

| n | `D_gen(n)` (proved) | `⌊n/2⌋` | conclusion |
|---|---|---|---|
| 5 | 3 | 2 | `D_{G∩A2}(5) ≥ 3 > 2` |
| 6 | 4 | 3 | `≥ 4 > 3` |
| 7 | 5 | 3 | `≥ 5 > 3` |

So at every size we have settled, the #655 general-position variant's conclusion **holds
with room to spare**, and for a reason that has nothing to do with `A2`: general position
alone already forces more than `n/2`. Whether that persists is exactly the `n−2` question
from #98, which is unresolved at `n = 8`.

## 7. Novelty (the L53 check), and what would be new

**No exact small-`n` values are known for `D`, `M` or `Σ` under `G ∩ A2`, or for `M_G(n)`
(#654).** OEIS has nothing; both pages show "OEIS: Possible". Under `A2`, `N3 ∩ A2` and
`C ∩ A2` everything is already exact (trivially), so **those are dead** — computing them
would be rediscovery.

The live computable targets, if we go ahead:

1. `M_G(n)` for small `n` — the #654 quantity. Our existing verified witnesses already
   bound it (`M ≤ 4` at `n = 8`), but they were optimised for *total* distances, so the
   objective must be changed to minimise the per-vertex maximum.
2. `D_{G∩A2}(n)` and `M_{G∩A2}(n)` for small `n` — the live #655 variant.

Both are the same shape as #98 and the machinery transfers: the Gram rank-2 decider, the
augmentation framework, and lemmas **L2, L3, L4, L5** (which need no cocircularity
hypothesis). **L1 changes**: under `A2` the per-class degree cap tightens from 3 to 2,
which makes it *stronger*, and the `⌈(n−1)/3⌉` bound becomes `⌈(n−1)/2⌉`.

## 8. Traps to avoid, recorded before starting

1. **Do not "solve" a disproved statement.** Both literal statements are false.
2. **State which variant.** #655 is officially ambiguous and the maintainer declined to
   pick one. Any claim must name its hypotheses precisely.
3. **Do not conflate global / pinned / sum**, nor `N4` alone with full `G`. The four-way
   distinction is where every error in this area lives.
4. **`A2 + N3` and `A2 + C` are already exactly settled.** Computing there is rediscovery.
5. **The 1988 question carries a $25 Erdős prize** and an extra caveat (not too many
   points on a line) that Chojecki's summary drops.
6. There is an **open formal-conjectures issue (#4298)** about the solved/open discrepancy;
   the repo's `answer(False)` is its own judgement, not the database's.

## 9. A DISCREPANCY ON THE #654 PROBLEM PAGE (one of three sources unverified)

[Er87b] p.168, read from page images (printed folio confirmed), states:

> "A related problem states as follows. Let x_1,...,x_n be in general position. Denote by
> d(x_i) the number of distinct distances from x_i. Trivially, d(x_i) >= (n-1)/3 for every
> i. I am sure that there is an absolute constant c > 0 ... so that
> **(3)  D(n) = max_i d(x_i) > (1 + c)n/3.**
> Is it true that there is a set x_1,...,x_n (in general position) for which
> **(4)  D(n) < (1 - c)n ?**
> It is rather frustrating that I got nowhere with (3) and (4). Perhaps (3) remains true if
> we only assume that no four of our points are on a circle or even if no circle whose
> center is one of the x_i's goes through more than **three** of the other x_j's. It would
> also be of interest to prove or disprove
> **(5)  Sum_i d(x_i) > (1 + c)n^2/3.**"

The website says: *"They suggest the lower bound (1-o(1))n is true under the assumption
that any circle around a point x_i contains at most 2 other x_j."* Against the primary:

1. **Erdős writes THREE, not two.** ("goes through more than three of the other x_j's")
2. **He attaches it to (1+c)n/3, not (1-o(1))n.** The weakened hypothesis is offered for
   statement (3), which is the n/3-scale claim.
3. **Direction reversal.** Erdős's (4) asks whether a set with `D(n) < (1-c)n` **exists** —
   he is probing for a counterexample, not conjecturing `(1-o(1))n` as a lower bound.

**HOW STRONG THIS IS.** The discrepancy is established against [Er87b] p.168 ONLY. The
page attaches three citations to the problem, `[Er87b,p.168] [ErPa90,p.267] [Er97e,p.530]`,
and [ErPa90] could not be obtained: it is Erdos and Pach, *Variations on the theme of
repeated distances*, Combinatorica 10 (1990) 261-269, DOI 10.1007/BF02122780, paywalled at
Springer, absent from the Renyi archive, and zbMATH returned 403. [Er97e] was likewise not
obtained. **If [ErPa90] p.267 states the condition with "two", the page is correctly
sourced there and only the attribution to [Er87b] is loose.** So this is a "please check",
not an established error, and it must not be reported as one. See PAGE_NOTES.md.

**The at-most-TWO condition comes from 1988, not 1987.** Erdős, SIAM Clemson 1988, p.35,
question (6) — the site has merged two distinct sources into one sentence.

**A name collision to watch.** On [Er87b] p.167 the symbol `f(n)` denotes the **global**
general-position count. The website's `f(n)` for #654 is the **pinned** quantity. Same
letter, different objects.

## 10. Sheffer's verdict on #654's quantity

Sheffer's survey (arXiv:1406.1949v2, **p.6**) defines exactly this pinned general-position
quantity `D̂_gen(n)`, quotes Erdős's "It is rather frustrating...", and states flatly:

> "**No non-trivial bound is known for D̂_gen(n) (neither a lower nor an upper bound).**"

and poses "**Problem 10.** Find the exact value of D̂_gen(n)."

A survey author saying, in 2015, that nothing is known either side. That is a stronger
statement of openness than the problem page conveys, and it is the single best argument
that small exact values here would be worth having.

## 11. A finding that belongs to #98, not to these two

Erdős 1988 p.35 also records:

> "Pach just told me that h(2^n) <= 3^n. The projection of the n-dimensional cube shows
> this."

`h(2^n) <= 3^n` is exactly `h(N) <= N^{log_2 3}`. **This is the origin of the
`n^{log_2 3}` bound on the #98 page**, and it names the construction (projection of the
`n`-cube) — which is precisely the argument Erdős-Hickerson-Pach 1989 Theorem 1 writes up
(their proof starts "let P be the set of all vertices of the unit cube in R^k"). So #98's
citation trail is now complete: an attributed remark in 1988, written up in 1989.

## 12. Aletheia identified

**Aletheia is a Google DeepMind AI system** (Gemini Deep Think; Superhuman Reasoning team,
led by Thang Luong). [Fe26] = Feng, Trinh, Bingham et al., *Semi-Autonomous Mathematics
Discovery with Gemini: A Case Study on the Erdős Problems*, arXiv:2601.22401, **§3.1**,
with a complete proof. Construction: `n = 4m`, `K = {10,...,m+9}`,
`P = {(0, ±3^k)}` on the y-axis, `Q = {(±2^j, 0)}` on the x-axis. No four cocircular
because a circle meets each axis twice and power-of-a-point forces `3^{k1+k2} = 2^{j1+j2}`;
same-axis distances are integers and cross-axis distances irrational, so the two distance
sets are disjoint, giving about `(3/4)n` from every point.

**Chojecki is wrong** to say this "has not been traced to a primary published source" — it
is in the preprint the problem page itself cites. Feng et al. themselves classify it as a
*partial* solution precisely because it says nothing about general position.
