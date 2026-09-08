# Prior-art scan: Erdős problems #831 (distinct circumradii) and #100 (Erdős-diameter)

Compiled 2026-09-07. Every claim carries a source. Markers:
- **[VERIFIED AT SOURCE]** = I fetched and read the primary text/page myself (file path or URL given).
- **[SECONDHAND]** = I only saw it cited/quoted by someone else, or saw only a publisher abstract.
- **[COMPUTED HERE]** = I derived/checked it numerically in this session (scripts noted); not from literature.

Local copies of everything fetched are in this directory (`scan/`).

---

# PROBLEM A — erdosproblems.com #831: h(n) = min number of distinct circumradii

## A.0 Statement and site metadata

Site text, verbatim:

> "Let $h(n)$ be maximal such that in any $n$ points in $\mathbb{R}^2$ (with no three on a line and no four on a circle) there are at least $h(n)$ many circles of different radii passing through three points. Estimate $h(n)$."
> `#831 : [Er75h] [Er92e]` — tag `geometry` — "See also [104] and [506]."

**[VERIFIED AT SOURCE]** https://www.erdosproblems.com/831 (curl w/ browser UA; local `831.html`). Status **OPEN**; site notes "This is open, and cannot be resolved with a finite computation." Formalised statement: **No**. OEIS: **"Possible"** (i.e. no OEIS sequence is attached; the maintainers judge one could exist). Reactions: `SamKorsky`, `Maximilian113` under both *Likes* and **"Currently working on"**.

Cross-check in the community database `teorth/erdosproblems` `data/problems.yaml`: entry `- number: "831"`, `prize: "no"`, `informal_status: open (2025-08-31)`, `formal_status: unformalized`, `oeis: ["possible"]`, `formalized: no`, `tags: ["geometry"]`. **[VERIFIED AT SOURCE]** https://raw.githubusercontent.com/teorth/erdosproblems/main/data/problems.yaml

## A.1 (Q5) What Erdős's own sources say

### [Er75h] = P. Erdős, *Some problems on elementary geometry*, Austral. Math. Soc. Gaz. **2** (1975), 2–3.

I obtained the full scanned paper from the Rényi Institute Erdős archive (item **1975-41**): https://users.renyi.hu/~p_erdos/1975-41.pdf (local `1975-41.pdf` / `1975-41.txt`). **[VERIFIED AT SOURCE]**

The relevant paragraph is short and is the *entire* content of #831 in Erdős's own words (OCR, lightly cleaned — the scan is a typewritten page):

> "Let there be given n points in the plane in general position. Denote by h(n) the largest integer so that there are at least h(n) circles of different radii passing through three of our points. Estimate or if possible determine h(n). How does h(n) get modified if we only assume that not all our points are on a circle?"

**Erdős gives no bound at all — neither upper nor lower — and no small values.** He immediately follows it with the (different) Ramsey-type question:

> "Finally I state a problem of a slightly different character. Is it true that to every k there is an n_k so that if there are given n_k points in the plane in general position one can always find k of them so that all the [C(k,3)] triples determine circles of different radii? At present I cannot even prove that n_k exists."

Two further things in this same paper matter for #831:

1. **The Esther Szekeres orthocentre observation** — the opening paragraph, verbatim:
   > "Mrs. E. Szekeres observed that there always is a unique point x₄ so that x₁, x₂, x₃, x₄ are not on a circle and so that the radii of the four circles determined by the four triples ... are the same. It suffices to choose x₄ as the orthocentre of the triangle x₁, x₂, x₃."

   This is the extremal gadget for the smallest case: **an orthocentric system is 4 points in general position with only 1 distinct circumradius, so h(4) = 1.** (The statement "h(4)=1" is not written by Erdős, but it follows immediately from his sentence.) **[VERIFIED AT SOURCE]** for the quote; **[COMPUTED HERE]** for the h(4)=1 reading — I checked numerically (`/tmp/orth2.py`) that for three sample triangles the orthocentre H = A+B+C−2·(circumcentre) gives all four circumradii equal to 12 decimal places and four *distinct* circumcentres (so no four of the points are concyclic), for three sample scalene non-right triangles.

2. **The neighbouring functions in the same paper**: f(n) = max number of unit circles through 3 of n points (this is erdosproblems **#104**), and g(n) = max number of triples whose circumcircle has unit radius. So #831 was posed as one of a family, and Erdős's remark about f(n) ("I am fairly sure that it will be very difficult to give an asymptotic formula ... and the exact determination of f(n) may not be possible") shows the register he had in mind.

### Erdős's 1978 follow-up (not cited on the #831 page but directly relevant)

P. Erdős, *Some more problems on elementary geometry*, Austral. Math. Soc. Gaz. **5** (1978), no. 2, 52–54. Rényi archive item **1978-44**: https://users.renyi.hu/~p_erdos/1978-44.pdf (local `1978-44.pdf`/`.txt`). **[VERIFIED AT SOURCE]**

> "In the May 1975 issue of this Gazette I published a paper on geometric problems. I here solve one of them and state a few new ones. ... I overlooked at that time that a simple and straightforward argument gives [n_k ≤ k + C(k−1,2)C(k−1,3)]."

Important: the one he "solves" is the **Ramsey-type n_k question, not h(n)**. h(n) is *not* mentioned again in the 1978 paper (the symbol `h(n)` does appear there, but for an unrelated quantity — the number of empty convex subsets). So **Erdős never published any bound on h(n)**.

### [Er92e] = P. Erdős, *Some unsolved problems in geometry, number theory and combinatorics*, Eureka **52** (1992), 44–48.

**NOT OBTAINED.** Eureka (the Cambridge Archimedeans' journal) is not on the Rényi archive (which ends at 1990) and archim.org.uk currently 404s on its archive paths. Bibliographic details confirmed from the erdosproblems bib endpoint `https://www.erdosproblems.com/bibs/Er92e` **[VERIFIED AT SOURCE]** and from an independent search hit giving "Eureka, 52:44–48, 1992" **[SECONDHAND]**. Content of the #831 passage in [Er92e]: **unknown to me**. Note that the #104 page says of the *same* paper: "In [Er92e] Erdős offered £100 for a proof or disproof that the answer is O(n^{3/2})" — that prize attaches to #104, not #831.

## A.2 (Q1) Published exact small values h(4), h(5), h(6), h(7)?

**No published values found, for any n.** Searched: arXiv full-text API, OEIS, Google/Bing via WebSearch, Semantic Scholar, GitHub, the erdosproblems forum. Nothing.

What *is* determinable from sources:
- **h(4) = 1** — immediate from Erdős's quotation of E. Szekeres (§A.1 above). Lower bound h(4) ≥ 1 trivial; upper bound h(4) ≤ 1 by the orthocentric system.
- The generic double-counting bound (§A.3) gives **h(5) ≥ 2, h(6) ≥ 2, h(7) ≥ 3**, but nobody has published matching constructions.

## A.3 (Q2) Published lower/upper bounds beyond trivial?

**Nothing in any refereed publication.** The only bounds anywhere are in a **single forum comment**, by user **SamKorsky, 04:34 on 16 Jun 2026**, on https://www.erdosproblems.com/forum/thread/831 (local `f831.html`). **[VERIFIED AT SOURCE]** — the thread has exactly 1 comment. Its content:

- **Lower bound** `h(n) ≥ (n−2)/2`, described as "the same simple double-counting lower bound from #104". (Reconstruction of the argument, which I checked: with no 4 concyclic, each radius value r is realised by circles each containing exactly 3 points; each pair lies on ≤2 circles of radius r, each such circle uses 3 pairs, so ≤ 2·C(n,2)/3 triples per radius; hence h ≥ C(n,3)·3/(2·C(n,2)) = (n−2)/2. **[COMPUTED HERE]**, consistent with the #104 page's statement that the analogous count gives n(n−1)/3 rather than n(n−1) — Harborth–Mengerson [HaMe86].)
- **Upper bound** `h(n) ≤ n² exp(O(√log n))`, via: generic linear projection from R^D preserving "no 3 collinear / no 4 concyclic", paraboloid lift of Z^m ∩ R·B_m, and counting translation classes of ordered triples τ(S); optimising m ~ 2√(log n / log M) with M = 3√3/2 gives log(h(n)/n²) ≤ 4√(log M)·√(log n) + o(√log n).
- The comment carries an explicit AI acknowledgement: "*While the projection argument and use of paraboloid lifting to avoid collinearity was developed without AI assistance, GPT-5.5 was used to optimize the constant in the exponent and write the final comment.*"

Caveat printed by the site itself: "All comments are the responsibility of the user. Comments appearing on this page are not verified for correctness."

### Closest published relative (different function, same problem family)

**L. Martínez and E. Roldán-Pensado, "Points defining triangles with distinct circumradii", Acta Math. Hungar. 145 (2015); arXiv:1402.6276 (25 Feb 2014), DOI 10.1007/s10474-014-0443-z.** **[VERIFIED AT SOURCE]** (local `mrp.pdf`/`mrp.txt`).

This solves the **Ramsey-type** problem (Erdős's n_k), **not** h(n):
- They point out Erdős's 1978 proof of n_k's existence **has a gap**: a point X outside the maximal set can satisfy R(ABX) = R(CDX) without lying on any of the circles Erdős counts. "It seems that Erdős remained unaware of this and even restated the result in 1985 [Discrete geometry and convexity, Ann. NY Acad. Sci. 440 (1985), 1–11] giving partial credit to E. Straus."
- **Theorem 1.1**: n_k = O(k⁹), via Bézout. (They also redefine general position to "no four on a line or circle", noting "a line is just a circle of infinite radius".)
- **Theorem 1.2**: **n₄ ≤ 9 and n₅ ≤ 37.** Proofs are essentially combinatorial pigeonhole + "if 3 triangles have the same circumradius and share an edge then 4 of their vertices are concyclic".

These are the only published *finite numbers* anywhere near #831. Note n₄ ≤ 9 means: any 9 points in general position contain 4 points whose 4 circumradii are all distinct — which is a statement about h restricted to 4-subsets, not about h(n) itself.

Semantic Scholar lists only **3 citations** of this paper ("Triangle areas in line arrangements" ×2, 2019; "A sunflower anti-Ramsey theorem and its applications", 2015) — **none** about h(n). **[VERIFIED AT SOURCE]** (S2 graph API).

### Sibling erdosproblems entries (for context, both fetched **[VERIFIED AT SOURCE]**)

- **#104** (https://www.erdosproblems.com/104): max number of *unit* circles through ≥3 of n points is o(n²)? — $100 prize; Elekes [El84] gives ≫ n^{3/2}; upper bound n(n−1)/3 corrected by Harborth–Mengerson [HaMe86]; **OEIS A003829** is attached to *that* problem (maximal number of unit circles). Cites the same [Er75h, p.2] and [Er92e, p.46].
- **#506**: min number of circles determined by n points not all on a circle — status **DECIDABLE** ("Resolved up to a finite check"), Elliott [El67] corrected by Purdy–Smith to C(n−1,2)+1−⌊(n−1)/2⌋ for n > 393, "The problem appears to remain open for small n."

## A.4 (Q3) OEIS

**No OEIS sequence exists for distinct circumradii of point configurations.** **[VERIFIED AT SOURCE]** — searches on oeis.org for `distinct circumradii`, `circumradii`, `circles of different radii three points`:
- `circumradii` → 10 hits, all irrelevant (decimal expansions, dodecahedron circumradius, etc.) except A128006/A128007 (**numerators/denominators of rational circumradii of triangles with integer coordinates in the plane**, Heinrich Ludwig 2007) and A128008–A128011 (same in 3-D/4-D). These enumerate *achievable rational radii*, nothing to do with h(n).
- The erdosproblems metadata field for #831 is literally `OEIS: Possible` — no sequence linked.
- Contrast: #104 has OEIS **A003829** attached.

## A.5 (Q4) Anyone currently working on it? (arXiv 2024–2026, forum, GitHub)

- **arXiv**: full-text/abstract queries `all:"circumradii"`, `all:"distinct circumradii"`, `all:"different radii" AND all:"Erdos"` return **exactly one relevant paper ever: arXiv:1402.6276 (2014)**. Nothing 2024–2026. **[VERIFIED AT SOURCE]** (arXiv API).
- **Forum**: 1 comment total, SamKorsky, 16 Jun 2026 (§A.3).
- **Reactions**: SamKorsky and Maximilian113 both flagged "Currently working on" on the problem page.
- **GitHub**: `api.github.com/search/repositories?q=erdos+831` returns 2 results, **both under `vibemathing/`** (`problem-um-ep-831-erd-s-problem-831-00afdae2`, plus an unrelated 1068 repo whose id happens to contain "831"). Queries `circumradii erdos`, `distinct circumradii` → 0 results. Per instructions, vibemathing is disregarded. `google-deepmind/formal-conjectures` has **no** `ErdosProblems/831.lean` (404). **[VERIFIED AT SOURCE]**
- **AI-search papers**: I downloaded and grepped arXiv:2511.02864 ("Mathematical exploration and discovery at scale", AlphaEvolve, 67 problems) and arXiv:2511.16072 ("Early science acceleration experiments with GPT-5"). Neither mentions circumradii or erdosproblems #831 or #100. **[VERIFIED AT SOURCE]**
- The `teorth/erdosproblems` wiki page "AI contributions to Erdős problems" contains **no** entry for 831 or 100. **[VERIFIED AT SOURCE]** (WebFetch).

## A.6 Summary for #831

| Question | Answer |
|---|---|
| Published exact small values | **None.** h(4)=1 is immediate from Erdős's quotation of E. Szekeres but is not stated as a value anywhere. |
| Published bounds | **None in print.** Only a single 2026 forum comment: (n−2)/2 ≤ h(n) ≤ n²e^{O(√log n)}. |
| OEIS | **None.** Site field says "Possible". |
| Active work | 2 users self-flagged "currently working on"; 1 forum comment; no arXiv 2024–2026; no non-vibemathing GitHub. |
| Erdős's own text | [Er75h] read in full: poses h(n) with **zero** bounds. [Er92e] not obtained. |

---

# PROBLEM B — erdosproblems.com #100: Erdős-diameter

## B.0 Statement and site metadata

Site text, verbatim:

> "Let $A$ be a set of $n$ points in $\mathbb{R}^2$ such that all pairwise distances are at least $1$ and if two distinct distances differ then they differ by at least $1$. Is the diameter of $A$ $\gg n$?"
> `#100 : [Er90] [Er92e] [Er95] [Er97f]` — tags `geometry | distances`
> "Perhaps the diameter is even $\geq n-1$ for sufficiently large $n$. Piepmeyer has an example of $9$ such points with diameter $<5$. Kanold proved the diameter is $\geq n^{3/4}$. The bounds on the distinct distance problem [89] proved by Guth and Katz [GuKa15] imply a lower bound of $\gg n/\log n$."
> "Additional thanks to: Shengtong Zhang, Boris Alexeev, and Dustin Mixon"

**[VERIFIED AT SOURCE]** https://www.erdosproblems.com/100 (local `100.html`). Status **OPEN**. Formalised statement: **Yes**. Comments: **0** (forum thread https://www.erdosproblems.com/forum/thread/100 is empty — local `f100.html`). OEIS field: **N/A**. No reactions at all.

Community DB entry: `- number: "100"`, `prize: "no"`, open, `formal_status: unformalized`, `oeis: ["N/A"]`, `formalized: yes (2026-01-25)`, `tags: ["geometry","distances"]`. **[VERIFIED AT SOURCE]**

Bib entries (all **[VERIFIED AT SOURCE]** from `erdosproblems.com/bibs/<key>`):
- **[Er90]** Erdős, *Some of my favourite unsolved problems*, in *A Tribute to Paul Erdős* (1990), 467–478. MR 1117038.
- **[Er92e]** Erdős, *Some unsolved problems in geometry, number theory and combinatorics*, Eureka **52** (1992), 44–48.
- **[Er95]** Erdős, *Some of my favourite problems in number theory, combinatorics, and geometry*, Resenhas (1995), 165–186. MR 1370501.
- **[Er97f]** Erdős, *Some unsolved problems*, in *Combinatorics, geometry and probability (Cambridge, 1993)* (1997), 1–10. MR 1476428.
- **[GuKa15]** Guth & Katz, Ann. of Math. (2) (2015), 155–190. MR 3272924.

## B.1 (Q1) Piepmeyer's 9-point example — exact reference and coordinates

### Erdős's own verbal description — the primary source

**[Er95]** = Paul Erdős, "Some of my favourite problems in number theory, combinatorics, and geometry", *Resenhas* **2** (1995), 165–186. Free PDF: https://www.ime.usp.br/~yoshi/resenhas/abstracts/Erdos.pdf (local `er95.pdf`/`er95.txt`). **[VERIFIED AT SOURCE]** — I read the passage.

Verbatim (§ geometry, part 4; OCR, with the mangled radicals restored — see verification below):

> "Let x₁, …, xₙ be n distinct points in the plane. Assume that if two distances d(xᵢ,xⱼ) and d(x_k,x_l) differ then they differ by at least 1. Is it then true that the diameter D(x₁,…,xₙ) is greater than cn? Perhaps if n > n₀ the diameter is in fact ≥ n − 1. **Lothar Piepmeyer** has a nice example of 9 points for which the diameter is < 5. Here it is: let first x = (1 + √2)·√(2 − √3). Then take 2 equilateral triangles, one of them with side length x, and the second 'around' the first, containing it, with parallel sides, and distances x between corresponding vertices. The 3 remaining points are the centres of the 3 circles determined by the 4 endpoints of the three pairs of parallel sides of the two equilateral triangles."
>
> "It is perhaps not uninteresting to try to determine the smallest diameter for each n, but this will already be difficult for n = 9."

That last sentence is Erdős himself flagging the finite/computational question as open and hard.

### Piepmeyer's own publication

**L. Piepmeyer, *Punktmengen mit minimaler Anzahl verschiedener Abstände*, Dissertation, TU Braunschweig, 1993** (supervisor H. Harborth). **[VERIFIED AT SOURCE]** as a bibliography entry in the reference list of the chapter "Distance Problems" of Brass–Moser–Pach, *Research Problems in Discrete Geometry* (Springer 2005), read via link.springer.com/chapter/10.1007/0-387-29929-7_6 (the body is paywalled; the reference list is public and I extracted it from the live DOM). Brass's 1996 paper cites the same item with year **1992** (Crossref reference list, **[VERIFIED AT SOURCE]** via api.crossref.org for DOI 10.1016/0012-365X(95)00208-E) — so 1992 vs 1993 is a submission-vs-award-year discrepancy. **I did not obtain the dissertation itself.**
Related: H. Harborth & L. Piepmeyer, *Three distinct distances in the plane*, Geometriae Dedicata **61** (1996), 315–327. **[SECONDHAND]** (BMP reference list + search).

### Reconstruction and numerical verification **[COMPUTED HERE]**

I rebuilt the set literally from Erdős's sentence (script `/tmp/pp.py`, `/tmp/pp2.py`): inner equilateral triangle of circumradius R_in = x/√3 with vertices at 90°/210°/330°; outer triangle same angles at R_out = R_in + x; the three extra points are the circumcentres of the three isosceles trapezoids formed by each pair of parallel sides. Results:

- x = (1+√2)√(2−√3) = **1.2496888978** (also = (√3−1)(1+√2)/√2)
- inner side = x; outer side = x(1+√3) = **2 + √2** = 3.4142135624
- the three trapezoid circumradii are all exactly **1 + √2** = 2.4142135624 (spread < 5e-16)
- the three extra points form a third equilateral triangle at radius 2.6927053408, rotated 60° (angles 30°/150°/270°)
- **The 36 pairwise distances take exactly 4 values:**
  | value | exact form |
  |---|---|
  | 1.2496888978 | √(6 − 3√3 + 4√2 − 2√6) = (1+√2)√(2−√3) |
  | 2.4142135624 | 1 + √2 |
  | 3.4142135624 | 2 + √2 |
  | 4.6639024601 | √(6 + 3√3 + 4√2 + 2√6) |
- gaps between consecutive values: 1.1645246646, **exactly 1.0**, 1.2496888978 — all ≥ 1 ✓
- minimum distance 1.2497 ≥ 1 ✓ ; **diameter = 4.6639024601 < 5** ✓ ; n − 1 = 8, so the example is far below the conjectured n−1.

### Independent confirmation: explicit algebraic coordinates exist in Lean

`google-deepmind/formal-conjectures` has **`FormalConjectures/ErdosProblems/100.lean`** (**[VERIFIED AT SOURCE]**, raw.githubusercontent). It formalises `DistancesSeparated`, the main open question, the `n−1` strong variant, the Kanold n^{3/4} variant, the Guth–Katz n/log n variant, and

```lean
theorem erdos_100_piepmeyer :
    ∃ A : Finset ℝ², A.card = 9 ∧ DistancesSeparated A ∧ diam (A : Set ℝ²) < 5
```

tagged `formal_proof using formal_conjectures at "https://github.com/theaustinhatfield/formal-conjectures/blob/solve-erdos-100-piepmeyer/FormalConjectures/ErdosProblems/100.lean"`. I fetched that branch file (**[VERIFIED AT SOURCE]**). It contains **exact closed-form coordinates** for the 9 points, with s2=√2, s3=√3, s6=√6:

```
P1 = ( 0,                              (3s2 − s6 + 6 − 2s3)/6 )
P2 = ( −(s6 − s2 + 2s3 − 2)/4,        −(3s2 − s6 + 6 − 2s3)/12 )
P3 = (  (s6 − s2 + 2s3 − 2)/4,        −(3s2 − s6 + 6 − 2s3)/12 )
P4 = ( 0,                              (2s3 + s6)/3 )
P5 = ( −(2 + s2)/2,                   −(2s3 + s6)/6 )
P6 = (  (2 + s2)/2,                   −(2s3 + s6)/6 )
P7 = ( 0,                             −(s6 + 3s2 + 6 + 2s3)/6 )
P8 = (  (3s2 + 3s6 + 6s3 + 6)/12,      (s6 + 3s2 + 6 + 2s3)/12 )
P9 = ( −(3s2 + 3s6 + 6s3 + 6)/12,      (s6 + 3s2 + 6 + 2s3)/12 )
```
with declared squared distances
`d1² = 6 − 3√3 + 4√2 − 2√6`, `d2² = 3 + 2√2`, `d3² = 6 + 4√2`, `d4² = 6 + 3√3 + 4√2 + 2√6`.

**[COMPUTED HERE]** I checked (`/tmp/verify.py`) that the multiset of all 36 distances from these Lean coordinates is **identical to 1e-9** with the multiset from my reconstruction of Erdős's verbal description. So the two derivations agree exactly; the coordinates above can be used with confidence.

**Bottom line for Q1:** the reference is **Erdős [Er95], Resenhas 2 (1995), 165–186** (verbal construction, quoted above), with Piepmeyer's own account presumably in his 1993 TU Braunschweig dissertation (not obtained). Explicit coordinates are **not** in either; they are in the Hatfield Lean branch and are independently reproduced above.

## B.2 (Q3) The Kanold reference and its exact statement

**H.-J. Kanold, *Über Punktmengen im k-dimensionalen euklidischen Raum*, Abhandlungen der Braunschweigischen Wissenschaftlichen Gesellschaft **32** (1981), 55–65, Verlag Erich Goltze KG, Göttingen. Received 10.7.1981.**

Full PDF obtained (the live TU-Braunschweig repository is behind a proof-of-work wall; I pulled it from the Wayback Machine): `http://web.archive.org/web/20251018163626if_/https://leopard.tu-braunschweig.de/servlets/MCRFileNodeServlet/dbbs_derivate_00031004/Kanold_Punktmengen.pdf` (local `kanold.pdf`, `kanold.txt`, page images `kanold_p2.png`, `kanold_p3.png`). Canonical landing page: https://leopard.tu-braunschweig.de/receive/dbbs_mods_00052443 (= digibib.tu-bs.de/?docid=00052443). **[VERIFIED AT SOURCE]** — I read pages 55–56 from the rendered page images (the raw OCR mangles the fractions, so I read the images directly).

### The problem's true origin

Kanold's opening paragraph, verbatim (p. 55):

> "In den „Elementen der Mathematik", Bd. **36** (1981), stellte P. Erdös die folgende Aufgabe: Es sei M = {P₁,…,Pₙ} eine Menge von n Punkten in einer Ebene. Bezeichnet d(Pᵢ,Pⱼ) die euklidische Distanz von Pᵢ,Pⱼ, so gelte
> (1) d(Pᵢ,Pⱼ) ≠ d(P_k,P_l) ⟹ |d(Pᵢ,Pⱼ) − d(P_k,P_l)| ≥ ε bei vorgegebenem ε > 0. Dann läßt sich für den Durchmesser δ(M) := max d(Pᵢ,Pⱼ) die Abschätzung
> (2) δ(M) > C_ε n^{2/3}
> gewinnen. Läßt sich (2) verschärfen?
> Die Lösung dieser Aufgabe (siehe Elem. d. Math. …) und zugleich eine Verschärfung von (2) lautet:
> (3) Für n ≥ 16 gilt δ(M) > (ε/4)·n^{3/4}."

So the **original venue for #100 is Erdős, Problem 856A, Elem. Math. 36 (1981), 22**, and the **published solution is H.-J. Kanold, "Lösung zu Problem 856A", Elem. Math. 37 (1982), 56**. Both of these appear in Brass 1996's bibliography (Crossref) — **[VERIFIED AT SOURCE]** for the bibliographic data, **[SECONDHAND]** for the content of the two Elem. Math. items themselves (I could not get past e-periodica's WASM challenge; the correct e-periodica IDs, for anyone who wants to try: journal UID `edm-001`; the Aufgaben section containing p.22 is `edm-001:1981:36::24`, and the one containing p.56 is `edm-001:1982:37::67`; PDF URL pattern `https://www.e-periodica.ch/cntmng?pid=<pid>`). Note that Kanold quotes his own solution's statement (3) verbatim, so its content is reliable.

### The theorems in the 1981 paper (all **[VERIFIED AT SOURCE]** from the page images)

Notation: d = min distance, δ = diameter, s = number of *distinct* distance values, ε = separation.

- **Eq. (8)** (this is the whole few-distance connection, in print since 1981):
  δ = d + (d₂−d) + … + (d_s − d_{s−1}) ≥ d + (s−1)ε = ε·(d/ε + s − 1).
- **Satz 1** (k = 1, n ≥ 3): d ≥ ε; and δ/ε ≥ δ/d ≥ n − 1.
- **Satz 2** (k = 2, n ≥ 4): **from d ≤ ε it follows that δ/ε > n/2**, and **from d > ε it follows that δ/ε > 0.366·n^{3/4}**.
- **Satz 3** (k ≥ 4): δ/ε > n^{1/(k−1)}/√(1.5k).
- **Satz 4** (k = 3, n ≥ 5): d ≤ ε ⟹ δ/ε > n^{3/4}/√14; d > ε ⟹ δ/ε > n^{1/2}/√14.
- Closing remark (p. 65): "Es ist noch eine offene Frage, ob in den Sätzen 2 bis 4 die Exponenten von n verbessert werden können. Die Beweise stützen sich weitgehend auf das einfache Dirichletsche Schubfachprinzip und die Dreiecksungleichung."

**Two things worth flagging that the erdosproblems page does not say:**
1. Kanold's planar bound has an explicit constant: **δ > 0.366·ε·n^{3/4}** (and his earlier Elem. Math. solution gave ε/4 · n^{3/4} for n ≥ 16).
2. **Satz 2 already gives a linear bound δ > (n/2)·ε whenever the minimum distance d ≤ ε.** So the *entire* difficulty of #100 sits in the regime **min distance > 1** — which is exactly Piepmeyer's regime (his min distance is 1.2497 > 1). The proof method is pigeonhole (packing) + triangle inequality + eq. (8), i.e. δ/d ≫ √n combined with δ ≥ (s−1)ε.

## B.3 (Q4) Is the few-distance-set connection in the literature?

**Yes, the asymptotic form is — since 1981 — and the site itself states one version. The specific finite table (g(1..6) = 3,5,7,9,12,13) I could not find applied to #100 anywhere.**

What's in print:
- **Erdős's own original formulation** in Elem. Math. 36 (1981) already asserted δ(M) > C_ε n^{2/3} — which is precisely "diameter ≥ ε·(number of distinct distances)" plugged into Moser's 1952 n^{2/3} distinct-distance bound. Quoted verbatim by Kanold (§B.2). **[VERIFIED AT SOURCE]** (as quoted by Kanold) / **[SECONDHAND]** (the Elem. Math. original).
- **Kanold 1981, eq. (8)**: δ ≥ d + (s−1)ε explicitly. **[VERIFIED AT SOURCE]**
- **erdosproblems #100** applies exactly this with Guth–Katz: "The bounds on the distinct distance problem [89] proved by Guth and Katz [GuKa15] imply a lower bound of ≫ n/log n." Credited on-page to Shengtong Zhang, Boris Alexeev, Dustin Mixon. **[VERIFIED AT SOURCE]**
- The Lean file encodes this as `erdos_100.variants.guth_katz`. **[VERIFIED AT SOURCE]**

What I could **not** find anywhere: the finite consequence, i.e. "n points with diameter < n−1 need fewer than n−1 distinct distances, so use g(k)". For the record the numbers are:
- **g(1..6) = 3, 5, 7, 9, 12, 13** (max size of a planar k-distance set). Erdős–Fishburn, *Maximum planar sets that determine k distances*, Discrete Math. **160** (1996), 115–125 settled k ≤ 5 (with classification of extremal configurations for k ≤ 4); Shinohara did the planar 3-distance classification and uniqueness of the maximum 5-distance set (*Uniqueness of maximum planar five-distance sets*, Discrete Math., 2008); **Wei, *A Proof of Erdős–Fishburn's Conjecture for g(6)=13*, Electron. J. Combin. 19(4) (2012), #P38**. **[SECONDHAND]** — I did not read Erdős–Fishburn or Wei; the values and attributions come from multiple consistent search results and the EJC listing.
- Immediate consequences (not found in print, **[COMPUTED HERE]** from those values plus Kanold eq. (8)): a #100-admissible set of n points has ≥ k distinct distances where k is minimal with g(k) ≥ n, hence diameter ≥ 1 + (k−1) = k. So diam ≥ 5 for 10 ≤ n ≤ 12, diam ≥ 6 for n = 13, diam ≥ 7 for n ≥ 14. These are weak asymptotically but are the sharpest known *finite* constraints, and they exactly explain why Piepmeyer stops at 9.
- **Piepmeyer's example is itself an extremal few-distance set**: 9 points, exactly 4 distinct distances, and g(4) = 9. **[COMPUTED HERE]** (the 4-value count), **[SECONDHAND]** (g(4)=9). I did **not** verify whether it is one of the Erdős–Fishburn extremal 4-distance configurations — worth checking, and it is suggestive that the person who found it wrote a dissertation titled "Punktmengen mit minimaler Anzahl verschiedener Abstände".

## B.4 (Q2) Examples for n ≥ 10, or any table of minimum diameter δ(n)?

**None found. Nothing beyond n = 9 exists in the literature I could reach.**

- Erdős [Er95] explicitly poses the tabulation as an open task and says it is already hard at n = 9 (quoted §B.1). **[VERIFIED AT SOURCE]**
- **Peter Brass, *On the Erdős-diameter of sets*, Discrete Math. **150** (1996), 415–419**, DOI 10.1016/0012-365X(95)00208-E, is the one dedicated paper on the planar problem. Publisher abstract (identical text returned by two independent searches; **[SECONDHAND]** — ScienceDirect blocks every fetcher I have, including the browser pane, and there is no Wayback snapshot, no preprint, no OA mirror):
  > "Let δ(n) denote the minimum diameter of a set of n points in the plane in which any two positive distances, if they are different, differ by at least one. Erdős conjectured that for n sufficiently big δ(n) = n − 1, the extremal configuration being n equidistant points on a line. We prove an asymptotic version of this conjecture for the special case of sets which lie in a parallel half-strip."
  So Brass introduces the notation **δ(n)** and resolves only the half-strip case asymptotically. Its bibliography (Crossref, **[VERIFIED AT SOURCE]**) is: Baron (LNM 1452, 1990); Brass DCG 7 (1992) 371; Chung DCG 7 (1992) 1; Croft–Falconer–Guy *Unsolved Problems in Geometry* p.154; **Erdős, Problem 856A, Elem. Math. 36 (1981) 22**; Erdős, Ann. NY Acad. Sci. 440 (1985) 1; Erdős, *A Tribute to Paul Erdős* (1990) 467; Erdős, Rostocker Math. Kolloq. 38 (1989) 6; **Kanold, Abh. Braunschw. Wiss. Ges. 32 (1981) 55**; **Kanold, Lösung zu Problem 856A, Elem. Math. 37 (1982) 56**; **Piepmeyer (1992)**; Schade (1993). **No table of δ(n) values is referenced anywhere.**
- **G. Baron, *On point sets with differences of distances not less than the minimum distance*, in *Number-theoretic Analysis*, Lecture Notes in Math. **1452** (1990), 1–…** — cited by Brass; title indicates it is squarely on this problem. **[SECONDHAND]** — bibliographic entry only, obtained from Crossref; I could not locate the text. **This is the one item I would most want that I did not get.**
- **C. Schade, *Exakte Maximalzahlen gleicher Abstände*, Diploma thesis (H. Harborth), TU Braunschweig 1993** — cited by Brass and by BMP. **[SECONDHAND]**
- Brass–Moser–Pach, *Research Problems in Discrete Geometry* (Springer 2005), chapter "Distance Problems": its public reference list contains Brass 1996, Kanold 1981, Piepmeyer's 1993 dissertation, Harborth–Piepmeyer 1996, Schade 1993. **[VERIFIED AT SOURCE]** for the reference list (extracted from the live page DOM); **the chapter body is paywalled and I could not read the problem statement or any table.**
- The Handbook of Discrete and Computational Geometry chapter 1 ("Finite Point Configurations", Pach) at csun.edu/~ctoth/Handbook/chap1.pdf: I fetched it; no discussion of circumradii or the Erdős-diameter surfaced from the text extraction. **[VERIFIED AT SOURCE — negative result, but the extraction was poor (mostly PDF stream noise), so treat this as inconclusive rather than as evidence of absence.]**
- **No OEIS sequence.** oeis.org searches for the minimum diameter under these constraints return nothing relevant (2 hits, both about minimal-area non-obtuse lattice triangles). The erdosproblems OEIS field for #100 is **"N/A"**. **[VERIFIED AT SOURCE]**

### Adjacent, much better-developed literature: *integral* point sets

Sets with all distances integers automatically satisfy #100's hypothesis, so results there are lower bounds for a sub-case (and the hard non-integral regime is exactly what Piepmeyer exploits). This literature *does* have tables:
- d(2,n) for plane integral point sets: (n=3..9) = 1, 4, 7, 8, 17, 21, 29; semi-general position 1, 4, 8, 8, 33, 56, 56; general position 1, 8, 73, 174 for n=3..6, and **d̄(2,7) = 22270** determined by exhaustive search. S. Kurz & A. Wassermann, *On the minimum diameter of plane integral point sets*, arXiv:0804.1307. **[VERIFIED AT SOURCE]** (local `kurz2.pdf`/`.txt`)
- J. Solymosi, *Note on integral distances*, Discrete Comput. Geom. **30** (2003), 337–342 — linear lower bound c·n for the diameter. Full text at https://personal.math.ubc.ca/~solymosi/sajatcikkek/integraldist.pdf. **[VERIFIED AT SOURCE]** (local `soly.pdf`)
- N. N. Avdeev, *On existence of integral point sets and their diameter bounds*, Australas. J. Combin. **77**(1) (2020), 100–116 — improves the constant to **c = 5/11**; notes Solymosi's proof gives 1/24, improved to 1/8 and then 3/8. https://ajc.maths.uq.edu.au/pdf/77/ajc_v77_p100.pdf **[VERIFIED AT SOURCE]** (local `ajc77.pdf`)
- S. Kurz & R. Laue, *Bounds for the minimum diameter of integral point sets*, Australas. J. Combin. **39** (2007), 233–240, arXiv:0804.1296 — Theorem 1 attributes to Kanold [8] the bounds **(3/2m)·n^{1/m} < d(m,n)** and **(1/14)·n^{1/2} < d(3,n) for n ≥ 5**. **[VERIFIED AT SOURCE]** (local `kurz.pdf`) — note these are Kanold's *ε=d* specialisations, i.e. exactly the "d ≤ ε" branches of his Sätze; they are **not** the n^{3/4} planar bound.

## B.5 (Q5) Current work, 2024–2026

- **arXiv:2604.15305 — Boon Suan Ho, "Erdős's diameter conjecture for separated distances fails in high dimensions", 16 Apr 2026, 6 pages, math.CO/math.MG, MSC 52C10.** **[VERIFIED AT SOURCE]** — I read the abstract page and the full HTML including §5 and the reference list. This is about the **sibling problem #670, not #100**: the variant where *all* C(n,2) pairwise distances are mutually ≥1 apart (so all distinct), in arbitrary dimension, and Erdős conjectured diam ≥ (1+o(1))n². Ho constructs, for each prime power q, a set X_q ⊂ R^{q²+q} of n = q+1 points with all pairwise distances mutually ≥1 apart and diam(X_q) ≤ (1 − 1/π² + o(1))n² ≈ 0.898n², via Singer difference sets and a weighted product of regular m-gons. Lean 4 formalization at https://github.com/boonsuan/erdos670 (last push 2026-04-17). Acknowledgement: "GPT-5.4 Pro was used to discover the construction of this paper, and Harmonic Aristotle was used to formalize the proof in Lean 4."
  - Ho's Remark 9: it remains open whether for each **fixed** d ≥ 2 the (1+o_d(1))n² bound holds; Remark 10 pushes the constant to (π+√(π²−4))/(2π) = 0.885589…, with numerics suggesting ≈ 0.85411.
  - Ho's intro explicitly locates the planar problem: "*The closest earlier work seems to be Brass's study of the planar 'Erdős-diameter' [2], which assumes that distinct positive distances are separated by at least 1 and asks for the minimum possible diameter.*" — i.e. **#100 is untouched by this paper.**
  - erdosproblems #670 was updated 17 Apr 2026 to record Ho's disproof. **[VERIFIED AT SOURCE]** https://www.erdosproblems.com/670
- **Nothing else.** arXiv API queries for `"separated distances" + Erdos`, `"Piepmeyer"`, and abstract queries combining distinct distances / diameter / "differ by at least" return no relevant 2024–2026 work on #100. **[VERIFIED AT SOURCE]**
- **GitHub outside vibemathing**: `google-deepmind/formal-conjectures` `ErdosProblems/100.lean` (present, statements only, all `sorry`) plus the `theaustinhatfield/formal-conjectures` branch `solve-erdos-100-piepmeyer` (79 KB, explicit coordinates and a worked-out proof of the 9-point statement). Both files carry `TODO: find reference` next to the Kanold and Piepmeyer attributions and say "**[Kanold](No references found)**" / "**[Piepmeyer](No references found)**" — **both references are supplied above.** **[VERIFIED AT SOURCE]**
- **Forum #100: zero comments; zero reactions.** **[VERIFIED AT SOURCE]**
- Related but distinct 2026 work that is *not* about #100: arXiv:2605.06621 (Goenka–Moore, point sets avoiding near-integer distances — a different Erdős/Sárközy question); arXiv:2601.09102 (Grayzel, Erdős #659). Both checked and ruled out. **[VERIFIED AT SOURCE]**
- Nearly-equal-distances line of work (adjacent, not #100): Erdős–Makai–Pach–Spencer (DIMACS 4, 1991); Erdős–Makai–Pach, CPC **2** (1993) 401–408; Makai–Pach–Spencer (Bolyai Soc. Math. Stud. 11, 2002); **Pach, Radoičić, Vondrák, *On the diameter of separated point sets with many nearly equal distances*, European J. Combin. **27** (2006), 1321–1332** — separated n-point set in R^d with ≥ γn² nearly-equal distances has diameter ≥ C(d,γ)·n^{2/(d−1)}, confirming an Erdős conjecture for d = 3 **[SECONDHAND — abstract via search; ScienceDirect blocked]**; Frankl & Kupavskii, *Nearly k-distance sets*, DCG **70** (2023), 455–494, arXiv:1906.02574 **[VERIFIED AT SOURCE]** (local `fk.pdf`) — I checked it: it does **not** mention Brass's Erdős-diameter, Piepmeyer, or Kanold.

## B.6 Summary for #100

| Question | Answer |
|---|---|
| Piepmeyer reference | **Erdős [Er95], Resenhas 2 (1995), 165–186** — verbal construction, quoted in full above; Piepmeyer's dissertation TU Braunschweig 1993 (not obtained). |
| Piepmeyer coordinates | Reconstructed and verified here; exact algebraic coordinates also exist in the `theaustinhatfield` Lean branch and agree exactly. 4 distances; min 1.2497; gaps 1.1645/1.0000/1.2497; **diam = √(6+3√3+4√2+2√6) = 4.66390246**. |
| n ≥ 10 examples / δ(n) table | **None anywhere.** Erdős himself flags it as open and hard at n = 9. Brass 1996 names δ(n) but only handles the half-strip case. |
| Kanold reference | **Abh. Braunschw. Wiss. Ges. 32 (1981), 55–65**, Satz 2: d ≤ ε ⟹ δ/ε > n/2; d > ε ⟹ **δ/ε > 0.366 n^{3/4}**. Origin of the problem: **Erdős, Problem 856A, Elem. Math. 36 (1981), 22**; solution **Kanold, Elem. Math. 37 (1982), 56** (δ > (ε/4)n^{3/4} for n ≥ 16). |
| Few-distance connection | The **asymptotic** form is in print (Erdős's own n^{2/3}; Kanold eq. (8); Guth–Katz version on erdosproblems). The **finite** form using g(k) = 3,5,7,9,12,13 appears **nowhere** I could find. |
| Current work | Only Ho arXiv:2604.15305 (Apr 2026), which disproves the **high-dimensional sibling #670** and explicitly leaves the planar #100 alone. |

---

# Things I could not obtain (open loose ends)

1. **Erdős, Eureka 52 (1992), 44–48 [Er92e]** — cited by both #831 and #100. Not digitized anywhere I could reach; archim.org.uk archive paths 404.
2. **Brass, Discrete Math. 150 (1996), 415–419** full text — ScienceDirect Cloudflare-blocks curl, WebFetch and the browser pane; no Wayback snapshot; no preprint. I have only the publisher abstract and the complete Crossref reference list.
3. **G. Baron, LNM 1452 (1990), 1–…** — on exactly this problem, not located.
4. **Elem. Math. 36 (1981) p.22 and 37 (1982) p.56** originals — e-periodica now uses a WASM proof-of-work challenge. Content known via Kanold's verbatim quotation of both.
5. **Piepmeyer's dissertation (TU Braunschweig 1993)** and **Schade's 1993 diploma thesis**.
6. **Brass–Moser–Pach chapter body** (paywalled; reference list only).
7. Whether Piepmeyer's 9-point set coincides with one of the Erdős–Fishburn extremal 4-distance configurations — not checked.
