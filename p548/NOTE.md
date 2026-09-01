# Erdos #548 (Erdos-Sos conjecture): a convention mismatch, and where the frontier is

Problem page: https://www.erdosproblems.com/548

This note contains **no new mathematics**. It reports that the problem statement and
the literature summarised in the thread use two different meanings of `k`, differing by
one, and works out where the first open instance actually falls. Every quotation is
verified at source; see `REFERENCES.md`. The arithmetic is checked by `audit548.py`.

## The mismatch

The page says, verbatim:

> "Let n >= k+1. Every graph on n vertices with at least ((k-1)/2)n + 1 edges contains
> every tree on k+1 vertices."

A tree on k+1 vertices has k edges, so **the page's k counts edges**.

The papers listed in the thread use the other convention. Yuan and Zhang open: "The
Erdős-Sós Conjecture states that if G is a simple graph of order n with average degree
more than k-2, then G contains every tree of **order** k". Tiner's thesis: "every simple
graph with average degree greater than k − 2 contains every tree on k **vertices**".
Tiner and Tomlin: "G contains every tree on k **vertices** ... we prove that the Erdős
and Sós conjecture holds for k = 9".

**The page's k and the literature's k differ by exactly one.**

Item (vii) of the thread is the internal tell. Zhou's result is quoted there as the case
where G "has a number of vertices k". Under the page's convention the tree would have
k+1 vertices and could not embed in a graph on k vertices at all, and the page's own
hypothesis n >= k+1 excludes that case anyway. So the k of items (vii) to (xi) is tree
order, as in the source papers.

## Where the frontier actually is

Reading the thread against the statement without noticing this, one concludes the first
open instance is n = 15 with trees on 11 vertices. It is not: an 11-vertex tree has
order k = 11, so n = 15 is exactly n = k+4, which Yuan and Zhang settled.

Re-indexed, the first open instance is **n = 15, at least 61 edges, some tree on 10
vertices**. `audit548.py` check 3 tabulates which (n, tree order) pairs the listed
results cover and confirms this one is not among them: order 10 exceeds the k <= 9
settled by Eaton-Tiner and Tiner-Tomlin, and n = 15 = k+5 exceeds the n = k+4 of
Yuan-Zhang.

## The tightness check, which confirms the re-indexing independently

The page threshold at n = 15 for a tree on 10 vertices (k = 9 edges) is
((9-1)/2)(15) + 1 = 61 edges. An 8-regular graph on 15 vertices has 15*8/2 = 60 edges
and maximum degree 8, so it cannot contain the star K_{1,9}, which is a tree on 10
vertices. Hence no threshold below 61 can work there, and **the tightness lands on order
10, not order 11** — which is the re-indexed reading and not the naive one.

Such a graph exists: `audit548.py` check 4 exhibits the circulant C15(1,2,3,4) and
verifies it is 8-regular, connected, has 60 edges and maximum degree 8.

## The one link that was unverified, and now is not

An earlier draft said item (vi), Tiner and Tomlin for k = 9, could not be obtained, and
took its k to be tree order by inference from neighbouring items. The paper is open
access and has now been read. Its abstract:

> "Let G be a graph with average degree greater than k−2. Erdős and Sós conjectured
> that G contains every tree on k vertices. The conjecture is known to be true for
> values of k up to 8. In this paper, we prove that the Erdős and Sós conjecture holds
> for k = 9."

Alabama Journal of Mathematics 45(1) (2022), 37-45. So its k is tree order, the
inference was right, and every link in the chain is now checked against a primary
source.

Worth noting that the conclusion never depended on that reading. Had Tiner-Tomlin meant
9 edges, trees of order 10 would be covered and the frontier would move to n = 16,
11-vertex trees, at least 73 edges — which `audit548.py` check 3 shows is likewise open.
Both readings land on an open case; only which one differs.

## A correction made while auditing

An earlier draft dated Tiner's dissertation 2010. It is **2007**; 2010 is the year of
the derived papers [EaTi10] and [Ti10]. In a note about citation accuracy that mattered.

## What this is not

Not a correction to the thread summary, which reports its papers accurately. Not a
result about the conjecture. It is only that two conventions sit on one page without a
note, and the difference is one vertex.

Disclosure: the literature search and the drafting of this note were done with AI
assistance.

## Files in this directory

`REFERENCES.md` with every quotation and its provenance, `audit548.py` (the arithmetic
and the tightness witness), `RESULTS.md` and `LITERATURE.md` (the fuller search record),
and `es_core.py`, `gen_trees.py`, `verify_containment.py` from an exploratory search for
extremal graphs near the frontier that produced nothing worth reporting and is not cited
in the comment.
