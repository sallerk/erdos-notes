# Adversarial mathematical audit of p831

Auditor: an independent agent instructed to break the claims, not to confirm them. All
checks below were written from scratch in this session (scratch code lives in the
session scratchpad, not in this directory) and share no code with `common.py`,
`penum.py`, `lemmas.py`, `verify.py` or any other script here. Nothing in this report
rests on re-running a script of this directory.

**Snapshot audited.** `NOTE.md` md5 `b2b14314bd3552b63d238a8a50cc3ea3` (14,298 bytes,
mtime 10:30). The directory was being edited *while* this audit ran: `NOTE.md` grew
from 11,238 to 14,298 bytes, `verify.py` gained a section 4c, and `ctrlB.py`, `fgp.py`,
`AUDIT_SELF.py`, `results/ctrlB.json`, `results/fgp.json` appeared between 10:27 and
10:30; `NOTE.md` was then rewritten again at 11:56 (17,286 bytes). Defects recorded
against the 02:27 and 10:30 texts were repaired by those edits *mid-audit*; they are
kept below, because they show what the earlier text asserted, and the **Appendix**
gives the status of every one of them against the 11:56 revision. Roughly half are
already repaired there; the other half, including the one SERIOUS item in the code
(S5) and every lemma-level item, are not.

**Headline.** No FATAL defect. The three lemmas that carry the n=5 case analysis
survive every attack I could mount, the pattern enumeration reproduces exactly from an
independently written enumerator, all three witnesses verify in exact rational
arithmetic, and the lower-bound proposition is sound under *both* readings of the
A003829 definition. What breaks is a layer of overstatement on top: one false
mathematical equivalence, one numerical-rank claim that is simply wrong and whose
conclusion runs the wrong way, several search results stated as facts, and several
quoted numbers that no script or artifact in this directory produces.

Counts: **FATAL 0, SERIOUS 5, MINOR 12, WORDING 3.**

---

## SERIOUS

### S1. "`f(n) = o(n^2)` is equivalent to `h(n) = omega(n)`" is false as stated
*Location:* NOTE.md section 3a, last paragraph.

*Claim.* "Two conditional consequences, stated as implications and not as progress on
either problem: #104's conjecture `f(n) = o(n^2)` **is equivalent to** `h(n) =
omega(n)` ..."

*Why it is wrong.* The only relation this directory establishes (or that the forum
comment establishes) is `h(n) >= C(n,3)/f(n)`. That gives exactly one direction:
`f = o(n^2)` implies `h(n) >= n^3/(6 f(n)) = omega(n)`. The converse requires an UPPER
bound on `h` in terms of `f`, and no such bound exists anywhere in the directory. A
set realising `f(n) = Omega(n^2)` has one radius class of size `~n^2`; that says
nothing about how many classes it has, still less about the minimising admissible set.
Concretely: from `f(n) >= c n^2` one can only deduce `h(X_n) >= C(n,3)/(c n^2) =
Omega(n)` for that particular set — a *lower* bound, the wrong direction for the
contrapositive — and the extremal set for `f` need not even be admissible (the
published extremal set at n = 7 is not: see the exact check in "What I could not
break", item 8).

The sentence also contradicts itself: it announces "stated as implications" and then
states an equivalence.

*Severity:* SERIOUS. It is the only asymptotic statement the note makes about the
relation between two named open problems, and it is false as written. The fix is one
word: "would imply".

### S2. The `ctrlB` Jacobian rank is 4, not 5, and the conclusion drawn from it runs the wrong way
*Location:* NOTE.md section 5, the "limitation of that screen" paragraph;
`results/ctrlB.json`; `verify.py`'s check "the harder control is genuinely
rank-deficient ... 6 equations, Jacobian rank 5".

*Claim.* "... an admissible configuration whose radius pattern has four classes of
sizes 4,2,2,2, and whose six constraint equations have Jacobian rank **5**: one
equation is dependent, so the solution set has positive codimension relative to the
naive count. ... So the optimiser demonstrably finds solutions that exist only through
a rank deficiency of one."

*Why it is wrong.* `ctrlB.py` computes the Jacobian by a **forward** difference of step
`eps = 1e-6` and then calls `np.linalg.matrix_rank(Jc, tol=1e-6)` — an *absolute*
tolerance of the same order as the differencing error, so a genuinely zero singular
value (which shows up at `~1e-6`) is counted as nonzero. I recomputed the same
6x6 constraint Jacobian at the same stored configuration with **exact symbolic
derivatives** (sympy, 30-digit evaluation). Singular values:

    3.2848e+01   2.8189e+00   2.2157e+00   6.9956e-01   5.9684e-16   1.0867e-16

Two singular values are zero to machine precision, with a gap of sixteen orders of
magnitude. **Rank = 4** at every tolerance from 1e-3 down to 1e-10. Two equations are
dependent, not one.

This is exactly what the structure predicts, and the note has the ingredients to see
it: the type-III family is cut out by 3 independent equations (I checked: the rank of
the four class equations alone is exactly 3), and *both* Lemma-6 identities
`R(123)=R(234)` and `R(124)=R(134)` vanish identically on that family, so both their
gradients lie in the span of those three. 3 + 1 (the imposed `R(014)=R(023)`) = 4.

*Consequence, and why the direction matters.* Rank 4 in 6 unknowns means the control's
solution set is **2-dimensional**, not the 1-dimensional set implied by rank 5. A
2-dimensional solution variety is *easier* for random-restart least squares to hit, so
the control is weaker than advertised, not stronger. The sentence "the optimiser
demonstrably finds solutions that exist only through a rank deficiency of one" is
wrong twice over: the deficiency is two, and the demonstration therefore proves less
about the screened patterns (which the note says would need "a rank deficiency of one
in a seven-equation system") than claimed. `verify.py` propagates the wrong number.

*Severity:* SERIOUS. A numerical rank computed at an unnormalised absolute tolerance is
stated as an exact structural fact, and it is the sole quantitative support for the
paragraph that decides how much weight the n=5 negative should carry.

### S3. "It does not, in the admissible region" — a non-existence assertion produced by a search, plus a supporting number no script here computes
*Location:* NOTE.md section 5, second bullet.

*Claim.* "... which is two equations in three angles — a one-parameter family should
exist. **It does not, in the admissible region**: `obstruction433.py` minimises
max(|f1|,|f2|) ... so the equations are satisfiable only in the limit where two centres
coincide ... A **110^3 grid** over the region with separation above 0.25 contains **no**
point with both residuals below **0.02**."

*Two problems.*

1. "It does not" is a flat existence claim resting on Nelder-Mead from 1200 random
   starts per separation level. The document says "Nothing here proves it" three
   paragraphs later, so it contradicts itself locally.
2. `grep` over every `.py` and every `results/*.json` in this directory finds **no
   110^3 grid and no 0.02 threshold**. `slice433.py` is a 60 x 120 slicing search;
   `results/slice433.json` records only `{"roots_found": 0, "admissible": 0}`. That
   number is not reproducible from this directory, contrary to the opening line of
   NOTE.md.

*What I found when I tested it myself* (this part supports the mathematics, not the
wording). I rebuilt the parametrisation from the definitions and attacked the system
three independent ways, all in a **pole-free** formulation — writing `R^2 = N/S` with
`N = a2 b2 c2 >= 0` and `S = 16*Area^2 >= 0`, so that `G(T,U) = N_T S_U - N_U S_T` is a
polynomial whose sign is the sign of `R^2(T) - R^2(U)`; sign changes of `G` genuinely
bracket roots, sign changes of the ratio used by `obstruction433.py` do not.

* a 400^3 sign sweep of the 3-torus: 21,816 cells with a sign change of both equations,
  6,778 of them at angular separation > 0.20. Polishing all 6,778 by least squares gave
  **0 roots** at machine precision; the best residual over all of them was 3.9e-9, at
  `t = (2e-6, 5*pi, ~0)`, i.e. **three** coincident centres.
* a trace of the surface `g1 = 0`: for each of 260 x 260 values of the first two angles
  I root-found every zero of `g1` in the third angle from a 1200-point scan plus 60
  bisections, giving 211,668 points on the surface. On that surface the minimum of
  `|f2|` is **5.0e-2** at separation > 0.25, 2.5e-2 at > 0.15, 1.1e-2 at > 0.10 and
  2.9e-4 as separation -> 0.
* `f2` does take both signs on that surface (86,508 negative, 125,160 positive), but it
  changes sign only through **+-1**, never through 0 — i.e. as one of the two radii
  passes through infinity at a collinear triple. That is a cleaner statement of the
  obstruction than the `s^2/2` fit, and it is what makes the negative credible.

So the mathematics survives; the defect is that a search result is written as a
theorem, and one of its numbers has no provenance.

*Severity:* SERIOUS (overclaiming on the load-bearing step of the n=5 case analysis).

### S4. Load-bearing numbers quoted in NOTE.md are absent from `results/`
*Location:* NOTE.md opening ("Every number below is reproducible from this directory;
see REPRODUCE.md") vs the artifacts.

Checked one by one:

| number in NOTE.md | artifact | present? |
|---|---|---|
| Case A "best relative residual 7e-8" | `results/caseA_n5.json` | **NO** — the file is `{"restarts":150,"seed":2,"nsplits":9,"hits":[],"seconds":142.1,"completed":true}`; no residual is stored, and there is no `logs/caseA*` |
| "110^3 grid ... no point with both residuals below 0.02" | none | **NO** — no script computes it (see S3) |
| ctrlB "the screen recovers it at 8.5e-16 from only 100 restarts" | `results/ctrlB.json` | **NO** — the file stores only `control`, `equations`, `rank` |
| "three encodings ... all three timed out at thirty seconds" | none | **NO** — `enc_test.py` writes no artifact |
| orthobranch "80,000 restarts" | `results/orthobranch.json` | partial — the file is `{"found": [], "completed": true}`; 80,000 is inferable from the code (4 x 20000) but not recorded |

`REPRODUCE.md`'s "What was actually run" table points at `results/caseA_n5.json` for
"Case A negative", but that artifact cannot support the quoted residual. Nor does
`REPRODUCE.md` mention `ctrlB.py`, `fgp.py`, `target433.py`, `slice433.py` or
`enc_test.py`, all of which NOTE.md now cites.

*Severity:* SERIOUS. The directory's central methodological promise is that every
number is backed by a stored artifact; five of them are not, and one of them (the 7e-8)
is the entire quantitative content of the Case A negative.

### S5. `caseA.py`'s objective omits every degeneracy penalty, contrary to the directory's own LESSONS P7
*Location:* `caseA.py::residual`, versus `LESSONS.md` P7 and P2, and versus
`typeIII.py::resid` / `pscreen.py::make_residual` which do it properly.

`LESSONS.md` P7 says: "Concyclicity penalties belong INSIDE the objective, not in a
post-filter, or every restart lands in the same worthless basin." `caseA.py`'s
residual contains only (i) a penalty for `|cy| < 0.05` and (ii) a soft box at 40. It
has **no** concyclicity penalty, **no** minimum-pairwise-distance penalty, and — most
importantly — **no** penalty forcing the two new class radii to differ from each other
and from the orthocentric radius. Those checks are applied only in a post-filter,
after a hit (`info['distinct']`), which is precisely the pattern P7 forbids. So the
optimiser is free to be captured by the branch where the six P-triples collapse onto
ONE radius (or onto the orthocentric radius), which has strictly smaller residual than
any genuine 3-class solution, and a genuine solution can be missed for exactly the
reason the directory itself documented.

Two further weaknesses in the same search: the restarts are drawn from a box
(`cx in (-1,2), cy in (0.2,2), p in (-2,3)^2`) that is a small part of the shape space
at a fixed scale `|AB| = 1`; and `caseA.py`'s docstring says "Every hit is re-verified
in exact arithmetic by **verifyA.py**", a file that **does not exist** in this
directory.

**The conclusion nevertheless survives.** I re-ran Case A in a different
parametrisation (orthocentric system with circumcentre at the origin and R = 1, so
`A = (1,0)`, `B = (cos b, sin b)`, `C = (cos g, sin g)`, `H = A+B+C`, `P = (px,py)`),
with pole-free residuals and with the degeneracy filters `caseA.py` omits: a
200 x 200 sweep of the base angles, each with a 241 x 241 sweep of P over
`[-6,6]^2`, then 1,500 grid seeds plus 4,000 random restarts polished per split. All
**nine** splits: grid minimum 1.238e-4, best polished residual between **2.5e-9 and
1.1e-8**, and **0 admissible roots** everywhere. So the negative is real; the criticism
is of the method, not of the answer.

I also confirmed the combinatorial side of that bullet: of the 25 splits of the six
P-triples into classes of sizes (4,2) or (3,3), exactly **9** survive Lemma 1, and the
same 9 survive Lemma 1 + Lemma 4, so "all nine admissible splits" is right. And I
killed the one obvious structured family by hand: if the triangle is isosceles and P is
placed on its axis of symmetry (the only symmetric ansatz compatible with Lemma 1), then
A, H and P all lie on that axis, so three points are collinear — no symmetric Case A
solution can exist.

*Severity:* SERIOUS (the weakest search in the directory carries the most weight in
section 5, and it violates the directory's own stated methodology).

---

## MINOR

### M1. Lemma 1's proof and the degenerate cases (repaired mid-audit; a residue remains)
The 02:27 text read "*Exactly* two circles of radius r pass through two given points."
That is false: with `|PQ| = d`, the centres are `(d/2, +- sqrt(r^2 - d^2/4))`, so there
are two circles for `d < 2r`, **one** for `d = 2r`, and **none** for `d > 2r`. The
10:30 text fixes the sentence. Two residues:

* the conclusion still reads "two of c1,c2,c3 would lie on the same one of **those two
  circles**"; in the `d = 2r` case there is only one circle, and all three would lie on
  it.
* nowhere is it noted that for a *diametral* pair the true bound is degree **<= 1**, not
  2. Lemma 1 as used is therefore not tight, and `penum.py`'s `pair_ok` (degree <= 2) is
  a strict **relaxation** in that case. This is harmless — a relaxation makes the
  surviving pattern list a superset, so "0 patterns survive" conclusions stand and "15
  patterns" is an upper bound — but the note does not say so.

*Verified:* the lemma's conclusion holds a fortiori in both degenerate cases (`d = 2r`
gives four concyclic points already at degree 2; `d > 2r` gives degree 0).

### M2. Lemma 2's uniqueness proof skips two steps
"Both reflections pass through A and through H, and two distinct circles meet twice, so
D = H" needs (i) that the two reflected circles ARE distinct — true, because
`refl_AB(O) = refl_AC(O)` would force `O = A`, but it is not said; and (ii) that the
second common point is not A itself, i.e. `D != A`. It also silently excludes the case
where a "reflected circle" is the circumcircle: if the triangle is right-angled at C,
then `AB` is a diameter, `refl_AB(Omega) = Omega`, and there is only ONE circle of
radius r through A and B. The note handles right triangles for the *admissibility* half
of Lemma 2 but not for the *uniqueness* half.

*Verified:* I solved the full system `R(ABD) = R(ACD) = R(BCD) = R(ABC)` exactly (sympy,
pole-free polynomial form) for six triangles with `A = (0,0)`, `B = (4,0)`:

| triangle | C | H | solution set for D |
|---|---|---|---|
| scalene | (1,3) | (1,1) | circumcircle, plus (0,0), (4,0), **(1,1) = H** |
| isosceles | (2,5) | (2,4/5) | circumcircle, plus (0,0), (4,0), **(2,4/5) = H** |
| right at A | (0,3) | (0,0) = A | circumcircle, plus (0,0), (0,3) — **no new point** |
| right at B | (4,3) | (4,0) = B | circumcircle, plus (0,0), (4,0) — **no new point** |
| right at C | (2,2) | (2,2) = C | **the circumcircle only** |
| obtuse at A | (-2,1) | (-2,-12) | circumcircle, plus (0,0), (4,0), **(-2,-12) = H** |

Off the circumcircle the only solution is always H, so uniqueness holds; and the right
at C row is exactly the degeneracy the written proof glosses over — there `AB` is a
diameter, the "reflection of the circumcircle in AB" IS the circumcircle, and the
system has no solution off the circle at all. `h(4) = 1` stands.

### M3. Lemma 5's labelling "{012, 013, 024, 034}" is a WLOG that is never justified
Four triples through a common point `P0` are four edges on the other four points. Up to
isomorphism a 4-edge subgraph of `K4` is either a **4-cycle** (the labelling used) or a
**paw** (triangle plus pendant edge). The paw is excluded because its degree-3 vertex
puts a pair in three triples of the class (Lemma 1) — and independently by Lemma 4 —
but Lemma 5 as stated carries no admissibility hypothesis at all, so **as literally
written the lemma is false**. One clause fixes it.

*Completeness of the parametrisation, checked against every gap the brief names:*
- second intersection point: forced. Two unit circles through the origin with centres
  `o_i, o_j` meet exactly at `0` and `o_i + o_j`; `P_k != P_0`, so `P_k = o_i + o_j`.
  No sign choice exists.
- coincident centres: `o_i = o_j` merges two class circles and puts four points on one
  circle — inadmissible, and correctly outside the family.
- `o_i + o_j = 0` (tangent at the origin): forces `P_k = P_0`; excluded by distinctness.
- orientation/rotation: the only gauge freedom, fixed by `theta_1 = 0`; reflection is an
  isometry and maps solutions to solutions.
- the common point lying on the circles: true by construction.
I found **no** configuration with a common-point class that this parametrisation cannot
represent. I verified numerically that all four class triples have `R^2 = 1` identically
on the family, that `P1 + P4 = P2 + P3` holds to 1.7e-16, and that
`R(123) = R(234)`, `R(124) = R(134)` hold to 1e-13 at random parameter values.

### M4. "Its size-4 class has support 5" is false for the witness it appears to describe
*Location:* NOTE.md section 4, last paragraph.

"... the n=6 witness has a class of size 8 = f(6) and so is extremal for #104 there too.
**Its** size-4 class has support 5 ..."

Exact computation of the n=6 witness `(0,0),(0,7),(2,6),(4,3),(6,2),(6,9)`: class sizes
are `8,4,2,2,2,2`, and the unique size-4 class is `R^2 = 65/2 = {015, 045, 123, 234}`,
whose support is **all six points**. Support 5 is a property of the *n=5* witness, whose
size-4 class is `R^2 = 25/2 = {012, 013, 124, 134}` (support `{0,1,2,3,4}`, all four
triples containing point 1 — a common-point class, so the Lemma-3 remark that follows is
right for that witness). As written the antecedent is the n=6 witness and the sentence
is false.

### M5. "All three lemmas are checked in exact arithmetic by `lemmas.py`" overstates what `lemmas.py` does
Three separate problems in one sentence:
* the section is headed "## 2. Three lemmas" and contains **six**;
* `lemmas.py` does **not** check Lemma 1. Its "LEMMA 1 support" block constructs the two
  candidate centres `(1, +-1)` for `r^2 = 2` through `(0,0),(2,0)` and verifies they are
  equidistant from both points. That is not the content of Lemma 1 — it never checks
  that there are at most two such circles, which is the whole argument;
* Lemma 4 is "demonstrated on an instance" (one triangle), not checked; Lemmas 3 and 5
  are not touched; Lemma 6 lives in `lemma6.py`, not `lemmas.py`.

### M6. The lemma numbering in NOTE.md does not match the numbering in the code, and section 1 cites the code's numbering
NOTE.md section 1: "`h(5) >= 2` | PROVED, from **Lemmas 1, 3, 5** alone". Under NOTE.md's
own numbering `h(5) >= 2` follows from **Lemma 1 alone** (a single class holding all ten
triples puts the pair `{0,1}` in three of them); Lemma 3 (saturated 4-sets) and Lemma 5
(the parametrisation) play no part whatever. The citation matches the *old* numbering
still used in the code: `penum.py` calls NOTE's Lemma 4 "LEMMA 5"; `lemmas.py` prints
NOTE's Lemma 2 as "LEMMA 3" and its reflection support as "LEMMA 5 support"; `caseA.py`
calls NOTE's Lemma 2 + 3 "L3". A reader chasing the citations lands on the wrong
statements.

### M7. "15 patterns remain to be decided" is inconsistent with the document's own use of f(5) = 4
Section 1 says 15; sections 3a and 5 use `f(5) = 4` to prove `h(5) >= 3`, and under that
same input three of the fifteen (size profiles `(5,4,1)` once and `(5,3,2)` twice) are
already excluded, leaving **12** — the number section 5 itself works with. Confirmed by
my own enumeration (profiles among the 15: `(4,3,3)` x 7, `(4,4,2)` x 5, `(5,3,2)` x 2,
`(5,4,1)` x 1).

### M8. Lemma 1 and its consequence are not new, and are not attributed
NOTE.md says of Lemma 1 "*Proof.* ..." and `penum.py` says "The first is **proved
here**". But `ep104.html`, saved in this directory, states the same count verbatim:
"every pair of points determines at most 2 unit circles, and the claimed bound follows
from double counting ... Harborth and Mengerson note that in fact this delivers an upper
bound of `n(n-1)/3`." Lemma 1 plus its consequence `m <= n(n-1)/3` is exactly that
observation applied to one radius class. Section 3 hedges the *proposition*'s novelty
with real care; the lemma's is not hedged at all.

### M9. `typeIII.py` is prescribed in REPRODUCE.md but its stored run never finished
`results/typeIII_n5.json` has `"completed": false` with 3 of its splits done after 829 s.
Its first entry, split `[[0,1],[2,3,4,5]]`, carries `best = 8.98e-10` — a number an order
of magnitude below the `1.5e-7`..`1.0e-3` band NOTE.md quotes for `pscreen` and reported
nowhere. REPRODUCE.md lists `python typeIII.py 10 10` under "The n = 5 case analysis"
without saying the artifact is a partial run.

### M10. "so the obstacle is the algebra, not the time limit" does not follow
Three encodings timing out at **thirty seconds** cannot distinguish "the algebra is
hard" from "thirty seconds is short". What supports the claim is the separate 1800 s
run, and even that bounds one solver at one budget on one encoding family. The
inference as written is a non sequitur, and the 30 s benchmark has no artifact (S4).

### M11. `caseA.py` names a verification script that does not exist
"Every hit is re-verified in exact arithmetic by `verifyA.py`" — there is no
`verifyA.py` in the directory. Harmless in fact (the search returned zero hits) but the
claimed exact-verification path for Case A does not exist.

### M12. The case analysis covers 5 of the 12 patterns structurally; the closing sentence does not say so
The three-bullet case split IS exhaustive (I verified there are exactly three shapes of
size-4 class). But when the 12 patterns within `f(5) = 4` are sorted by the shapes of
their size-4 classes, the tally is:

| shapes of the size-4 class(es) | sizes | count | treatment in NOTE.md |
|---|---|---|---|
| A and B | (4,4,2) | 1 | Case A search + killed by Lemma 6 |
| A only | (4,3,3) | 1 | Case A search |
| B only | (4,3,3) | 2 | one killed by Lemma 6, one is the surviving pattern |
| B and C | (4,4,2) | 1 | killed by Lemma 6 |
| C only | (4,4,2) x 3, (4,3,3) x 4 | **7** | **nothing but `pscreen`** |

So **7 of 12** patterns have no structural treatment at all. The note discloses this
("covered only by the general numerical screen") but its closing sentence — "The
evidence is: no admissible solution in any of the structured subcases" — reads as
though the structured subcases are the bulk of the work; they are 5 of 12, and the
remaining 7 rest entirely on the screen whose control the note itself admits is too
easy (and which S2 shows is easier still).

---

## WORDING

### W1. "the only bounds anywhere are in a single 2026 forum comment"
Stated flatly in the opening paragraph. `REFERENCES.md` and `LITERATURE.md` record that
Harborth-Mengersen 1986, Erdos-Purdy (Handbook of Combinatorics ch. 17) and
Brass-Moser-Pach were **NOT OBTAINED**, and that "nothing below is asserted about them".
Section 3 restores the caveat; the opening sentence does not, and it is the sentence a
reader will quote.

### W2. "the prized form `f(n) = O(n^{3/2})`"
`ep104.html` reads: "In [Er75h] and [Er92e] Erdos also asks how many such unit circles
there must be if the points are in **general position**. In [Er92e] Erdos offered GBP 100
for a proof or disproof that **the answer** is `O(n^{3/2})`." The antecedent of "the
answer" is ambiguous — it may be the general-position question of the preceding
sentence rather than `f(n)` — and the page's own headline prize is attached to the
`o(n^2)` statement. The attribution is made without hedge, in a directory whose
`REFERENCES.md` is otherwise scrupulous about provenance.

### W3. "the orthocentric route is a dead end above n = 4"
Supported by one witness whose size-4 class is not orthocentric, plus a beam-search
anecdote (LESSONS P4). Case A — the orthocentric case at n = 5 — is recorded as
undecided in section 5 of the same document. "Dead end" is stronger than the evidence.

---

## What I could not break (one line each)

1. **Lemma 1's conclusion.** Holds in every degenerate case; `penum.py`'s degree <= 2
   filter is a valid relaxation. Only the proof's wording was ever at issue (M1).
2. **Lemma 2 / uniqueness of the orthocentre.** Solved the full system symbolically for
   scalene, isosceles, obtuse and all three right triangles: the solution set is always
   `{A,B,C} u {H} u circumcircle`; no exception found.
3. **`h(4) = 1`.** `(0,0),(0,3),(1,1),(2,1)` is admissible (0 collinear triples, 0
   concyclic quadruples) with a single `R^2 = 5/2`, in exact `Fraction` arithmetic;
   `h(4) >= 1` is trivial. The value is exactly right and no case is hidden.
4. **Lemma 4.** No counterexample. The reflection argument survives the right-triangle
   cases (there the fourth point is forced onto the circumcircle, so no admissible
   configuration exists at all — see the table in M2), and 40,000 restarts of an
   optimiser explicitly rewarded for "three radii equal, fourth different by at least
   5%, not concyclic, points at least 0.05 apart" bottomed out at **1.19e-4**: its best
   configuration has `R^2 = 2.187729, 2.188249, 2.187209, 2.418016`, i.e. three radii
   agreeing only to four digits. `penum.py`'s `quad_ok` filter is exactly the lemma
   (reject a class holding exactly 3 of the 4 triples of a 4-set), neither stronger nor
   weaker; it does not need the triangle to be non-right.
5. **Lemma 6 and the parallelogram.** `P1 + P4 = P2 + P3` verified to 1.7e-16 on random
   parameters and exactly on the n=5 witness (`(0,0)+(6,9) = (2,6)+(4,3)`); the two
   congruences verified to 1e-13. Independently: for a parallelogram with sides p, q and
   diagonals `d1, d2`, the two triangle circumradii are `d1/(2 sin theta)` and
   `d2/(2 sin theta)`, equal iff `d1 = d2` iff rectangle iff concyclic — so "exactly
   two radii" is right and does not even need the orthocentric branch. "No parallelogram
   is orthocentric" checks out symbolically (`H = P4` forces a repeated vertex).
6. **Completeness of the type-III parametrisation.** See M3: every candidate gap in the
   brief is closed; the only real gap is that the 4-cycle labelling is not justified in
   the text.
7. **The lower-bound proposition and its table.** Valid, and valid under **both**
   readings of A003829's "each circle containing 3 of the points": in an admissible set
   no circle carries four points, so the count of unit circles through exactly three
   points equals the count through at least three, and both are bounded by whichever
   maximum A003829 records (`f_exactly3 <= f_at-least-3` always). Arithmetic checked:
   `ceil(C(n,3)/f(n)) = 1,3,3,3,4` for n = 4..8; `ceil((n-2)/2) = 1,2,2,3,3`; the two
   coincide at 4 and 7 and the reduction wins at 5, 6, 8; and
   `C(n,3)/(n(n-1)/3) = (n-2)/2` identically. `f(n) = O(n^{3/2}) => h(n) =
   Omega(n^{3/2})` is correct.
8. **The `f_gp(n) = f(n)` claim for n <= 6, and the secondhand degeneracy report.** A
   size-m class in an admissible witness does certify `f_gp >= m` (distinct triples give
   distinct circles, else four concyclic), so the argument is sound. I checked the
   secondhand literature claim myself against `A003829.svg`: the OEIS n=7 extremal set
   `(-2/3,0), (0,0), ((-1+sqrt7)/3, +-sqrt2/3), (2/3,0), ((1+sqrt7)/3, +-sqrt2/3)` has,
   in exact arithmetic, exactly 12 unit circles each through exactly three points, one
   collinear triple `(0,1,4)` and one concyclic quadruple `(2,3,5,6)` — the claimed
   collinear triple and concyclic rectangle, confirmed at source.
9. **The witnesses.** Exact `Fraction` arithmetic, circumcentres solved from the
   perpendicular-bisector equations (not from a Heron formula): n=4 -> 1 radius
   (`5/2`); n=5 -> 4 radii, class sizes `4,2,2,2`, largest class `25/2` of size 4; n=6
   -> 6 radii, class sizes `8,4,2,2,2,2`, largest class `25/2` of size 8. All three
   admissible: 0 collinear triples and 0 concyclic quadruples. The beam witnesses at
   n=7 (12 radii) and n=8 (16 radii) also verify.
10. **The pattern enumeration.** A from-scratch generate-and-test enumerator over all
    set partitions, canonicalised under S_5, reproduces `penum.py` exactly: k=1 -> 0
    patterns; k=2 -> 1 pattern with sizes `(5,5)`; k=3 -> 124 raw orbits, **35** after
    Lemma 1, **15** after Lemma 1 + Lemma 4, **12** with all classes <= f(5) = 4.
    Lemma 3's filter removes nothing at k = 3.
11. **"Exactly three shapes of size-4 class (Lemma 4 kills a fourth)".** Correct. There
    are 6 orbits of 4-subsets of the ten triples under S_5; Lemma 1 kills two, Lemma 4
    kills one more, leaving exactly the three named: all four triples of a 4-set
    (support 4); four triples through a common point (support 5); and the no-common-
    point shape `{012,013,024,134}` (support 5).
12. **"The ONLY surviving pattern" in the common-point case.** Re-derived independently:
    given the parallelogram's forced pairing `{123,234}` and `{124,134}` into different
    classes, the four ways of distributing `014` and `023` are cut to one by Lemma 1
    (pair `{2,3}` and pair `{1,4}` reach degree 3 in the other three), giving
    `{012,013,024,034} | {014,123,234} | {023,124,134}`, sizes (4,3,3) — exactly the
    note's pattern. I also checked that this is one of the 12 canonical patterns and
    that the other three patterns carrying a common-point class are each killed by
    Lemma 6 (two put `123` and `234` in different classes; the `(A,B)` one puts all four
    parallelogram triples in one class).
13. **The size-5 class, i.e. `f(5) = 4` where it matters.** I attacked the external input
    directly: the dimension count (10 coordinates - 3 for the isometry group = 7
    unknowns, 5 equations) says a size-5 equal-radius class *should* be realisable, so
    `f(5) = 4` needs a real obstruction. There are exactly 2 orbits of 5-subsets of the
    ten triples with pair-degree <= 2; **both are realisable** (residuals 8.6e-17 and
    6.9e-17), but every one of the ~7,600 roots I found has `min|det4| <= 1.9e-13` —
    four concyclic points, usually all five on one circle. So no *admissible* 5-point
    set has a radius class of size 5, and `h(5) >= 3` is safe. (Worth noting: this means
    `h(5) >= 3` need not depend on the published `f(5) = 4` at all.)
14. **The n=5 obstruction.** See S3: three independent global methods agree with
    `obstruction433.py`; the `s^2/2` fit is remarkably clean (measured/predicted ratios
    1.020, 1.010, 1.004, 1.001, 1.000 at s = 0.35, 0.25, 0.15, 0.08, 0.03).
15. **The third shape, which NOTE.md leaves to the numerical screen.** I derived the
    parametrisation the note does not (`P0 = 0`; `a, b, c` on the unit circle;
    `P1 = a+b`, `P2 = a+c`, `d = P1 + (cos delta, sin delta)`, `P3 = d-a`, and `P4` one
    of the two points of `C_c n C_d` — a genuine two-way branch), verified it puts
    `R^2 = 1` on all four class triples, and swept `170^3` x 2 branches for all 15
    admissible splits. Every machine-zero hit is a coincident-point degeneracy
    (min pairwise distance ~1e-16); the smallest non-degenerate value is 3.0e-4. Note
    this case is **4** equations in 3 angles, one more overdetermined than the
    common-point case, which is why it is the least likely of the three — a remark the
    note could make instead of leaving the case bare.
16. **`lath.py`.** An independently written exhaustive DFS with the same monotone prune
    reproduces its results exactly, including node counts: n=4 on 6x6 -> best 1,
    witness `(0,0),(0,3),(1,1),(2,1)`, **732** nodes; n=5 on 11x11 -> best 4, witness
    `(0,0),(0,7),(2,6),(4,3),(6,9)`, **651,094** nodes. I also ran the 17x17 statement
    on a sub-grid I could finish independently: n=5 over **13x13** (1,705,998 nodes)
    returns **no** admissible 5-point set with three or fewer distinct circumradii; and
    n=6 over 11x11 returns best 6 with the same witness and **7,968,042** nodes, the
    identical count `results/lath_n6_11x11.json` records. Its prune and its admissibility
    tests are correct (the concyclicity check is applied to every quadruple as its last
    point is added; the radius count is monotone, so pruning on it is sound).
17. **`pdecide.py`'s encoding.** The similarity frame `p0 = (0,0)`, `p1 = (1,0)`,
    `y2 > 0` is legitimate, the constraints match the definitions, and every verdict is
    `unknown` — recorded honestly as contributing nothing.
18. **The novelty framing of the lower bound.** `thread831.html` does contain
    "Note that the same simple double-counting lower bound from #104 gives
    `h(n) >= (n-2)/2`", and `C(n,3)/(n(n-1)/3) = (n-2)/2` identically, so the note's
    "NOT new" is correct and correctly placed first. (The unhedged item is Lemma 1
    itself — M8.)

---

## Appendix: status of each defect against the 11:56 revision of NOTE.md

`NOTE.md` was rewritten again at 11:56 (md5 `32263b30a588ff4a59053c1113b4ae1c`,
17,286 bytes) while this report was being written, apparently in response to a separate
audit (it now points at an `AUDIT_SUMMARY.md`). To keep this report honest I re-checked
every item against that newer text. **The findings above stand as written against the
10:30 snapshot**; here is what survives at 11:56.

| # | status at 11:56 |
|---|---|
| S1 equivalence | **repaired** — now "would imply ... That direction only", with an explicit retraction |
| S2 ctrlB rank | **repaired in NOTE.md** — now "its Jacobian rank is 4, not the 5 an earlier draft claimed". **But `results/ctrlB.json` still stores `"rank": 5`**, and `verify.py`'s check reads the artifact, so the auditor still passes on the wrong number. My exact-derivative computation is stronger than the note's new explanation: the two smallest singular values are not "falling as eps^2", they are **exactly zero** (5.97e-16, 1.09e-16 against a leading 32.8) |
| S3 "It does not" | **partly repaired** — softened to "It does not have one away from degeneracy", and the unsupported 110^3 / 0.02 sentence is **gone**. Still an existence claim from a search, but now labelled as such |
| S4 missing artifacts | **partly repaired** — the 7e-8 is now explicitly said to "carry no meaning", the 30 s encoding comparison is now "recorded here as a note, not as a measurement". Still: the header "Every number below is reproducible from this directory" remains, `results/caseA_n5.json` still stores no residual, `results/ctrlB.json` still stores no restart figures, and the new numbers (47/500, 51/500, 0.33% hit rate) have no artifact I can find |
| S5 caseA.py objective | **STILL PRESENT** — `caseA.py` is byte-identical (md5 `c901c143...`); its residual still has no concyclicity, no minimum-distance and no class-separation penalty, contrary to LESSONS P7. The note now says the Case A case is OPEN, which is the right conclusion, but for a different reason (a broken `ctrlA.py`) than this one |
| M1 Lemma 1 proof | repaired at 10:30; the "those two circles" residue and the degree-<=1 remark remain |
| M2 Lemma 2 proof | **STILL PRESENT** — the uniqueness proof is unchanged |
| M3 Lemma 5 labelling | **STILL PRESENT** — Lemma 5's text is unchanged; the 4-cycle-vs-paw step is still missing |
| M4 "support 5" | **repaired** — a parenthetical now says the n=6 witness's size-4 class has support 6 |
| M5 "three lemmas" / lemmas.py | **STILL PRESENT** — heading still "## 2. Three lemmas" over six lemmas, and "All three lemmas are checked in exact arithmetic by `lemmas.py`" is unchanged although `lemmas.py` still does not check Lemma 1 |
| M6 lemma numbering | **STILL PRESENT** — section 1 still reads "PROVED, from Lemmas 1, 3, 5 alone"; `penum.py` and `lemmas.py` still use the old numbering |
| M7 "15 patterns" | **repaired** — the status row no longer quotes a count |
| M8 Lemma 1 novelty | **STILL PRESENT** — `penum.py` still says "The first is proved here" / "LEMMA 1 (proved here…)" with no reference to the identical count on the #104 page saved in this directory |
| M9 typeIII artifact | **STILL PRESENT** — `REPRODUCE.md` is byte-identical and `results/typeIII_n5.json` still has `completed: false` |
| M10 "the algebra, not the time limit" | **repaired** — now recorded as a note, not a measurement |
| M11 verifyA.py | **STILL PRESENT** — `caseA.py` still names a file that does not exist |
| M12 5 of 12 patterns | **STILL PRESENT** — the third shape is still "covered only by the numerical screen" with no indication that it is 7 of the 12 patterns |
| W1 "only bounds anywhere" | **STILL PRESENT** (line 6) |
| W2 "the prized form" | **STILL PRESENT** (line 145) |
| W3 "dead end" | **repaired** — now "a dead end … for the SEARCH that starts from it, not as a theorem about h" |

One new claim appears at 11:56 that I did **not** audit and that is not covered above:
that `ctrlA.py` was broken because it "normalised by the mean of all six radii while
constraining only some", and that its SOLVED rungs were violating their equations by up
to 61%. `ctrlA.py` has been rewritten (md5 changed) but `results/ctrlA.json` still holds
the old ladder. Anything written after 11:56 is outside this audit.

## Two remarks that are not defects

* **`pscreen`'s reported minima sit on the degeneracy boundary.** The best two
  residuals (1.48e-7 and 1.71e-7) are attained at configurations that are nearly
  concyclic — e.g. `v = (7.2e-7, 3.4372, 0.99999894, 3.4372239, 0.5, 0.0743)` is four
  points forming a near-rectangle. The concyclicity guard uses a normalised threshold of
  `1e-6`, which is permissive enough that "nearly concyclic" passes. The note's own
  self-criticism about the control is the more important limitation, but this one
  compounds it: the screen's floor is set by how close to degenerate it is willing to go.
* **A free improvement the note does not take.** `h` is non-decreasing (any n-subset of
  an admissible (n+1)-set is admissible), so `h(5) >= 3` already gives `h(6), h(7) >= 3`
  without `f(6)` or `f(7)`, and `h(n) >= 4` for all `n >= 8`. It does not beat the table,
  but it makes n = 6 and n = 7 independent of two more external values.
