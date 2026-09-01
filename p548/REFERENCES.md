# References for the #548 note

Every quotation below was read at its source on 2026-08-31. The note is entirely about
a citation convention, so the provenance of the quotations is the substance of it.

## The two conventions

* **erdosproblems.com/548**, verbatim:

  > "Let n >= k+1. Every graph on n vertices with at least ((k-1)/2)n + 1 edges
  > contains every tree on k+1 vertices."

  Page citations `#548: [Er64c][Er74c,p.78][Er78,p.30][Er93,p.345][Va99,3.55]`, status
  FALSIFIABLE, $100. A tree on k+1 vertices has k edges, so **here k counts edges**.
  *[VERIFIED AT SOURCE]*

* **Long-Tu Yuan and Xiao-Dong Zhang**, "On the Erdos-Sos Conjecture for Graphs on
  n=k+4 Vertices", arXiv:1403.5430. Abstract, verbatim:

  > "The Erdős-Sós Conjecture states that if G is a simple graph of order n with
  > average degree more than k-2, then G contains every tree of order k. In this paper,
  > we prove that Erdős-Sós Conjecture is true for n=k+4."

  **"tree of order k" means k vertices.** *[VERIFIED AT SOURCE]*

* **Gary F. Tiner**, "On the Erdos-Sós conjecture", PhD dissertation, University of
  Rhode Island, **2007**. Abstract, verbatim in the relevant parts:

  > "The Erdős-Sós conjecture states that every simple graph with average degree
  > greater than k − 2 contains every tree on k vertices as a subgraph (k is a positive
  > integer). ... We use this to prove the conjecture holds if the graph has minimum
  > degree k − 4. From this result, we obtain that the conjecture holds for all k ≤ 8.
  > ... In the third manuscript, we prove the conjecture holds if G has at most k + 3
  > vertices."

  https://digitalcommons.uri.edu/oa_diss/2182/
  *[VERIFIED AT SOURCE]*

  **A correction.** An earlier draft of the comment dated this thesis 2010. It is 2007;
  2010 is the year of the derived papers, Eaton-Tiner [EaTi10] and Tiner [Ti10]. In a
  note whose whole subject is citation accuracy that mattered, and it is fixed.

## The link the frontier turns on

* **Gary Tiner and Zachery Tomlin**, "On the Erdős-Sós Conjecture for k = 9", Alabama
  Journal of Mathematics **45**(1) (2022), 37-45, Faulkner University. Abstract,
  verbatim:

  > "Let G be a graph with average degree greater than k−2. Erdős and Sós conjectured
  > that G contains every tree on k vertices. The conjecture is known to be true for
  > values of k up to 8. In this paper, we prove that the Erdős and Sós conjecture holds
  > for k = 9."

  https://www.ajmonline.org/wp-content/uploads/2022/11/On-the-Erdos-Sos-Conjecture.pdf
  *[VERIFIED AT SOURCE]*

  **So its k is tree order**, like every neighbouring item. An earlier draft could not
  obtain this paper and inferred the convention from Tiner's own earlier work; the paper
  is open access and the inference is now confirmed. This was the single unverified link
  in the argument and it is closed.

## The thread items quoted

From the forum thread on #548 (Alfaiz), verbatim, read 2026-08-31:

* (v) "This result has been improved by N. Eaton and G. Tiner in [EaTi10] to include
  every tree with a vertex having at least ceil(k/2) − 2 leaf-neighbours. They have also
  showed that this conjecture holds for values of k at most 8."
* (vi) "G. Tiner and Z. Tomlin in [TiTo22] has proved that the conjecture holds for
  k = 9."
* (vii) "B. Zhou in [Zh84] has proved the conjecture in the case when graph G has a
  number of vertices k."
* (viii) Slater, Teo and Yap [STY85], n = k+1.
* (ix) Woźniak [Wo96], n = k+2.
* (x) Tiner [Ti10], n = k+3.
* (xi) Yuan and Zhang [YuZh17], n = k+4.

*[VERIFIED AT SOURCE]*

Item (vii) is the internal tell the note relies on: under the page's convention a tree
on k+1 vertices cannot embed in a graph on k vertices at all, and the page's own
hypothesis n >= k+1 excludes that case, so the k of items (vii) to (xi) must be tree
order.

## What is checked mechanically

`audit548.py` verifies the arithmetic rather than the prose: the page threshold
evaluates to 61 edges at n = 15 for a 10-vertex tree and 73 at n = 16 for an 11-vertex
tree; which (n, order) pairs the listed results cover; and the tightness witness, an
8-regular graph on 15 vertices with 60 edges and no K_{1,9}, exhibited explicitly as
the circulant C15(1,2,3,4) and checked to be 8-regular, connected, and of maximum
degree 8.

## Not claimed

No new mathematics. The note reports a convention mismatch and re-locates the frontier;
it proves nothing about the conjecture. The `p548` working directory also contains an
unrelated exploratory search for extremal graphs near the frontier, which produced no
result worth reporting and is not cited in the comment.
