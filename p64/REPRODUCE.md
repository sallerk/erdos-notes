# Reproducing the #64 results

Everything below was executed from a fresh copy of this directory on 2026-08-31 and
the outputs quoted are what it actually printed.

## 1. Verify the recorded results without recomputing anything

    python audit64.py

Checks the per-n node counts, that every even n from 4 to 62 is covered with no gaps,
that the total is 18,485,512,641, that no run recorded a survivor, that the task lines
in the n=60 and n=62 certificates sum to their stated TOTALs, and that the cycle
routine gives the right answers on K(3,3), Heawood, Moebius-Kantor and Pappus.
Pure Python, no dependencies. Takes a second.

Add `--geng` to also regenerate small cases with nauty and compare against OEIS
A002851 and A006823. That needs nauty on PATH.

## 2. Validate the generator itself

    python test_gen.py        # counts against A002851; n=12 takes about 2 minutes
    python test_cycles.py     # the cycle checker against brute force
    python test_fastgen.py    # the numba engine against the pure-Python generator

`test_gen.py` output on this machine:

    ok   n=4: got 1, expected 1
    ok   n=6: got 2, expected 2
    ok   n=8: got 5, expected 5
    ok   n=10: got 19, expected 19
    ok   n=12: got 85, expected 85

## 3. Reproduce a certificate from scratch

    python run.py N SPLIT_DEPTH WORKERS bip

**The fourth argument `bip` is required for the bipartite class** and is easy to miss;
without it you get the all-cubic search instead.

**To match a stored node count you must use the same SPLIT_DEPTH and WORKERS**, which
are recorded in each `results/bip_nN.json`. The count includes the shared prefix above
SPLIT_DEPTH once per worker, so different splits give different counts for the same
search. The verdict (survivors, CERTIFIED) does not depend on them.

Worked example, n = 30. `results/bip_n30.json` records `split_depth: 20`,
`workers: 1`, `tree_nodes: 46828`. So:

    python run.py 30 20 1 bip

printed

    TOTAL nodes=46828 (includes the shared prefix above split_depth, counted once per
    worker) survivors_of_C4C8C16=0  wall=0.6s
    CERTIFIED: no connected cubic bipartite graph on 30 vertices avoids all of [4, 8, 16].

which matches the stored count exactly. Running the same n with `24 5 bip` instead
gives 64,128 nodes and the same verdict, which is the parameter dependence above, not
a discrepancy.

## 4. Cost of going further

n = 30 is under a second. The stored runs took 1490 s at n = 58, 5535 s at n = 60
(5 workers) and 11221 s at n = 62 (10 workers). The tree grows by a factor of about
2.8 per two vertices, so n = 64 is roughly 3.5e10 nodes.

## 5. The generator comparison

`prune64.c` reproduces the measurement in NOTE.md showing that nauty's geng with a
C4/C8/C16 prune is about 100x slower than this search at n = 30. Build instructions
are in NOTE.md.
