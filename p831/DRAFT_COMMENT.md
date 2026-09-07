DRAFT for https://www.erdosproblems.com/forum/thread/831
NOT POSTED.

Checked against the page of 2026-09-07: the statement, [Er75h], [Er92e], "See also [104]
and [506]", OEIS field "Possible", and the single comment by SamKorsky.

FORMATTING, checked against the raw HTML of existing comments on the site: comments carry
NO markdown. Blank lines become <br><br>; asterisks would appear literally; there is no
table syntax. LaTeX is rendered, inline with $...$ and display with $$...$$, so the table
below is a LaTeX array kept on a SINGLE line, because newlines inside a display block are
turned into <br> before MathJax sees them. Post the text between the rules verbatim.

---

Adding to SamKorsky's comment above: small exact values, and one remark from Erdős's own paper that this page does not carry.

h(4) = 1, and it is Erdős's. [Er75h] opens by quoting E. Szekeres: "there always is a unique point $x_4$ so that $x_1, x_2, x_3, x_4$ are not on a circle and so that the radii of the four circles determined by the four triples ... are the same. It suffices to choose $x_4$ as the orthocentre of the triangle $x_1x_2x_3$." An orthocentric system is therefore four admissible points with a single circumradius. Erdős never writes it as a value. Witness $(0,0),(0,3),(1,1),(2,1)$, all four with $R^2 = 5/2$.

The lower bound with exact values. The double count above is really $h(n)f(n)\ge\binom n3$, where $f(n)$ is the maximum number of unit circles through three of $n$ points, the subject of [104]: rescaling by $1/r$ turns the triples of circumradius $r$ into unit circles, and no four concyclic puts exactly three points on each. Using the known values $f(3),\ldots,f(8) = 1,4,4,8,12,16$ (OEIS A003829; Harborth and Mengersen, with $f(8)$ due to Harborth) in place of $f(n)\le n(n-1)/3$:

$$\begin{array}{c|ccccc} n & 4 & 5 & 6 & 7 & 8 \\ \hline \left\lceil \binom{n}{3}\big/f(n)\right\rceil & 1 & 3 & 3 & 3 & 4 \\ \left\lceil (n-2)/2\right\rceil & 1 & 2 & 2 & 3 & 3 \end{array}$$

so the exact values win at $n = 5, 6$ and $8$. Also $h$ is non-decreasing, both hypotheses being hereditary and deleting a point never adding a radius, so $h(n)\ge 4$ for every $n\ge 8$; that helps only until $\lceil (n-2)/2\rceil$ passes $4$ at $n = 11$.

Upper bounds, from exact integer witnesses: $h(5)\le 4$ at $(0,0),(0,7),(2,6),(4,3),(6,9)$; $h(6)\le 6$ on adding $(6,2)$; $h(7)\le 12$; $h(8)\le 16$. So $h(5)\in\{3,4\}$. I could not settle which, but two things point to $4$: no admissible 5-point set on the $17\times 17$ integer grid has three or fewer radii, and every exact solution of each of the fifteen radius patterns that survive the combinatorial constraints places four of the five points on a circle.

Two notes on the page text. [Er75h] asks a second question that the statement here omits: "How does $h(n)$ get modified if we only assume that not all our points are on a circle?" And Erdős writes "in general position", which this page renders as no three on a line and no four on a circle, whereas Martínez and Roldán-Pensado (Acta Math. Hungar. 145 (2015)), treating the companion Ramsey-type quantity from the same paper, read general position as no four on a line or circle.

Code, exact witnesses, the lemmas behind the $n = 5$ analysis, and three adversarial audits of my own work, which found two fatal defects in my instruments, both since fixed: https://github.com/sallerk/erdos-notes/tree/main/p831

Disclosure: the computations and the drafting of this comment were done with AI assistance.
