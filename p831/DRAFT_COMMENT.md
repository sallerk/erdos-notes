DRAFT for https://www.erdosproblems.com/forum/thread/831
NOT POSTED. Checked against the page of 2026-09-07: the statement, [Er75h], [Er92e],
"See also [104] and [506]", OEIS field "Possible", and the single comment by SamKorsky.

---

Adding to SamKorsky's comment above: small exact values, and one remark from Erdős's own
paper that this page does not carry.

**$h(4) = 1$, and it is Erdős's.** [Er75h] opens by quoting E. Szekeres: "there always is
a unique point $x_4$ so that $x_1, x_2, x_3, x_4$ are not on a circle and so that the
radii of the four circles determined by the four triples ... are the same. It suffices to
choose $x_4$ as the orthocentre of the triangle $x_1x_2x_3$." An orthocentric system is
therefore four admissible points with a single circumradius. Erdős never writes it as a
value. Witness $(0,0),(0,3),(1,1),(2,1)$, all four $R^2 = 5/2$.

**The lower bound with exact values.** The double count above is really
$h(n)f(n)\ge\binom n3$, with $f(n)$ the maximum number of unit circles through three of
$n$ points ([104]): rescaling by $1/r$ turns the triples of radius $r$ into unit circles,
and no four concyclic puts exactly three points on each. Using the known
$f(3..8)=1,4,4,8,12,16$ (OEIS A003829, Harborth–Mengersen, $f(8)$ Harborth) rather than
$f(n)\le n(n-1)/3$:

| $n$ | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|
| $\lceil\binom n3/f(n)\rceil$ | 1 | **3** | **3** | 3 | **4** |
| $\lceil (n-2)/2\rceil$ | 1 | 2 | 2 | 3 | 3 |

Also $h$ is non-decreasing, both hypotheses being hereditary, so $h(n)\ge 4$ for $n\ge 8$
— useful only until $\lceil (n-2)/2\rceil$ passes 4 at $n=11$.

**Upper bounds** from exact integer witnesses: $h(5)\le 4$ at $(0,0),(0,7),(2,6),(4,3),(6,9)$;
$h(6)\le 6$ adding $(6,2)$; $h(7)\le 12$; $h(8)\le 16$. So $h(5)\in\{3,4\}$. I could not
settle it, but two things point to 4: no admissible 5-point set on the $17\times17$
integer grid has three or fewer radii, and every exact solution of each of the fifteen
radius patterns surviving the combinatorial constraints puts four of the five points on a
circle.

**Two notes on the page.** [Er75h] asks a second question omitted here: "How does $h(n)$
get modified if we only assume that not all our points are on a circle?" And Erdős writes
"in general position", rendered on this page as no three collinear and no four concyclic,
whereas Martínez and Roldán-Pensado (Acta Math. Hungar. **145** (2015)), treating the
companion Ramsey-type quantity from the same paper, read it as no four on a line or
circle.

Code, witnesses, the lemmas behind the $n=5$ analysis, and three adversarial audits of my
own work (two fatal defects found in my instruments, both fixed):
https://github.com/sallerk/erdos-notes/tree/main/p831

Disclosure: the computations and the drafting of this comment were done with AI
assistance.
