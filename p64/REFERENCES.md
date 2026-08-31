# References for the #64 note

## The bound this note extends

* **Julius Tranquilli**, "A 60-Vertex Lower Bound for Cubic Bipartite Counterexamples
  to the Erdős-Gyárfás Conjecture", arXiv:2608.02675. Abstract, verbatim: "A certified
  exhaustive computation shows that every simple cubic bipartite graph on at most 58
  vertices contains a cycle of length 4, 8, or 16. Consequently, any cubic bipartite
  counterexample to the Erdos-Gyarfas conjecture has at least 60 vertices... The proof
  begins with a Moore-bound observation: below 62 vertices, a cubic bipartite graph
  avoiding 4- and 8-cycles must contain a 6-cycle. Viewing the graph as the Levi graph
  of a linear symmetric v3-configuration turns this 6-cycle into a Berge triangle."
  He covers n <= 58 (giving >= 60); this note covers n <= 62 (giving >= 64), which is
  the two further steps, and n = 62 sits just outside the range his Moore-bound
  observation covers.  *[VERIFIED AT SOURCE: arXiv abstract read 2026-08-31]*

## The two published bounds cited on the problem page

Both appear in Alfaiz's comment on https://www.erdosproblems.com/forum/thread/64,
quoted verbatim there as:

* **[Ma04]** "K. Markstrom in [Ma04] has shown that any cubic counterexample to this
  conjecture must have at least 30 vertices."
* **[NoEs11]** "Nowbandegani and H. Esfandiari in [NoEs11] has shown that any bipartite
  counterexample must have at least 32 vertices."

*[VERIFIED AT SOURCE: comment thread read 2026-08-31. These are erdosproblems.com
citation keys; resolve them to full bibliographic entries from the problem page.]*

* **arXiv:1403.5636** (Exoo) is cited in the note only as the route by which an
  unpublished Markström bound was reported secondhand. The note labels that figure
  hearsay and claims nothing from it.  *[secondary]*

## OEIS sequences used to validate the generator

**A002851** connected cubic graphs (reproduced exactly for n = 4, 6, 8, 10, 12 as
1, 2, 5, 19, 85); **A006823** connected bicubic graphs; **A006924** connected cubic
graphs of girth exactly 4.  *[VERIFIED: checked against the generator's own output]*

## Artifacts here

`RESULTS.md`, `LITERATURE.md`, and the certified outputs `bip_n60_CERTIFIED.txt`,
`bip_n62_CERTIFIED.txt`.
