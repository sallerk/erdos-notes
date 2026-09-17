"""Build candidate patterns for D_gen(n+1) > k without trusting hard.py at any level (2026-09-17).

hard.py was found to emit false unsat verdicts (ASSUMPTIONS.md A8), and every earlier seed
set was pruned with it.  This rebuilds the candidates from seeds that no decider has touched:

  k = 3:  n=5 seeds = every canonical 5-point pattern with at most 3 classes that survives the
          proved lemmas (lemmas.survives); aug.py 5 3 gives the n=6 candidates.
  k = 4:  n=5 seeds = the 99 xcheck sat + all 152 inconclusive patterns + the 2 patterns hard.py
          wrongly rejected (sing98_weak96.json indices 49, 70): 253.  The other 196 of xcheck's
          198 unsat are refuted soundly: 45 by a trivial ideal inside hard.py, 57 in A8's table,
          94 by sing98.py.  aug.py 5 4 gives 1,141 n=6 candidates, which are ALL kept as seeds
          (none decided), and aug.py 6 4 gives the n=7 candidates.

aug.py applies only the proved lemmas and the subset test.  Outputs, in the current directory:
  k=3: exposure_n5_k3_seeds.json, exposure_n6_k3_cand.json
  k=4: exposure_n5_k4_seeds.json, exposure_n6_k4_cand.json, exposure_n7_k4_cand.json
Usage: python exposure98.py 3 | 4          (k = 4 takes about 13 minutes, almost all at n = 6 -> 7)
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def aug(nf, k, seedfile, outfile):
    subprocess.run([sys.executable, os.path.join(HERE, 'aug.py'), str(nf), str(k), seedfile, outfile], check=True)
    return json.load(open(outfile))['candidates']


def main():
    k = int(sys.argv[1])
    if k == 3:
        sys.path.insert(0, HERE)
        from hdecide import enumerate_patterns
        from lemmas import survives
        seeds = [list(p) for p in enumerate_patterns(5, 3) if survives(p, 5)]
        json.dump({'undecided': seeds}, open('exposure_n5_k3_seeds.json', 'w'))
        print('n=5, k<=3 seeds surviving the lemmas: %d' % len(seeds))
        c6 = aug(5, 3, 'exposure_n5_k3_seeds.json', 'exposure_n6_k3_cand.json')
        print('n=6, k<=3 candidates: %d' % len(c6))
    elif k == 4:
        r = json.load(open('xcheck_n5_k4.json'))['robust']
        w = json.load(open('sing98_weak96.json'))['patterns']
        seeds = [list(p) for p in r['sat']] + [list(p) for p in r['inconclusive']] + [w[49], w[70]]
        assert len({tuple(p) for p in seeds}) == 253
        json.dump({'undecided': seeds}, open('exposure_n5_k4_seeds.json', 'w'))
        c6 = aug(5, 4, 'exposure_n5_k4_seeds.json', 'exposure_n6_k4_cand.json')
        json.dump({'undecided': c6}, open('exposure_n6_k4_seeds.json', 'w'))
        c7 = aug(6, 4, 'exposure_n6_k4_seeds.json', 'exposure_n7_k4_cand.json')
        print('n=5 seeds 253, n=6 candidates %d, n=7 candidates %d' % (len(c6), len(c7)))
    else:
        sys.exit(__doc__)


if __name__ == '__main__':
    main()
