"""Tally the n = 7 decision records into RESULT_n7_c3.json, and check the class lists passed
between passes.

Reads c123_n7_survivors.npy (from c123.py), the pass records res_n7_c3_*.jsonl and
skip_n7_c3_*.txt (k3super.py ... _c3), res_n7_c3b_*.jsonl and skip_n7_c3b_*.txt (_c3b), and
sing7/singular.json and sing7/z3.json (k3sing.py).  Asserts that:
  * the classes undecided after each pass are exactly the lists the next pass was given
    (c123_n7_undecided_pass1.npy, c123_n7_undecided_pass2.npy);
  * no class gets two different verdicts, and no record lies outside the survivors;
  * every survivor has a refutation.
Usage: python k3tally.py
"""
import glob
import json
from collections import Counter

import numpy as np


def records(tag):
    out = {}
    for f in sorted(glob.glob('res_n7_%s_*.jsonl' % tag)):
        for line in open(f):
            line = line.strip()
            if line:
                r = json.loads(line)
                out[r['idx']] = r['v']
    skipped = set()
    for f in sorted(glob.glob('skip_n7_%s_*.txt' % tag)):
        for line in open(f):
            if line.strip():
                skipped.add(int(line.split()[0]))
    return out, skipped


def main():
    surv = [int(x) for x in np.load('c123_n7_survivors.npy')]
    verdict = {}

    def put(k, v, src):
        assert k not in verdict or verdict[k][0] == v, ('conflicting verdicts', k, verdict.get(k), v)
        verdict[k] = (v, src)

    name = {'unit_ideal': 'refuted_unit_ideal', 'unsat': 'refuted_z3_unsat'}
    left = set(surv)
    for tag, listfile in (('c3', None), ('c3b', 'c123_n7_undecided_pass1.npy')):
        if listfile:
            given = set(int(x) for x in np.load(listfile))
            assert given == left, ('pass %s was not given exactly the undecided classes' % tag)
        res, skipped = records(tag)
        assert set(res) | skipped == left, ('pass %s did not cover its classes exactly' % tag)
        for k, v in res.items():
            put(k, name.get(v, v), 'sympy pass ' + tag)
        left = {k for k in left if verdict.get(k, (None,))[0] not in ('refuted_unit_ideal', 'refuted_z3_unsat')}
    given = set(int(x) for x in np.load('c123_n7_undecided_pass2.npy'))
    assert given == left, 'the Singular pass was not given exactly the undecided classes'
    s = json.load(open('sing7/singular.json'))
    z = json.load(open('sing7/z3.json'))
    assert set(int(k) for k in s) == left
    for k, v in s.items():
        if v['status'] == 'UNIT':
            put(int(k), 'refuted_unit_ideal', 'singular')
        elif v['status'] == 'NONUNIT' and z.get(k, {}).get('verdict') == 'unsat':
            put(int(k), 'refuted_z3_unsat', 'singular + z3')
    c = Counter(v for v, _ in verdict.values())
    missing = sorted(set(surv) - {k for k, (v, _) in verdict.items() if v.startswith('refuted')})
    extra = sorted(set(verdict) - set(surv))
    summary = {
        'question': 'is there a strictly convex 7-gon in which every vertex has 3 other vertices at one common distance?',
        'classes_before_filter': int(json.load(open('c123_n7.json'))['classes']),
        'filter': 'C1-C3 (c123.py, c123_n7.json)',
        'classes_after_filter': len(surv),
        'verdicts': dict(c),
        'survivors_without_a_refutation': missing,
        'records_outside_survivors': extra,
        'by_source': dict(Counter(src for _, src in verdict.values())),
        'passes': [
            'sympy grevlex + z3 (k3worker.py), budget 25 s / 20 s, 5 workers, 922 s: 1,839 unit + 422 unsat, 79 over budget',
            'same, budget 300 s / 60 s, 5 workers, 3,482 s: 21 unit + 20 unsat, 38 over budget',
            'Singular 4.3.2 slimgb over Q (k3sing.py, 10 jobs) on the 38: 29 unit, 9 non-unit; z3 on the 9: all unsat',
        ],
        'controls': 'Singular on 6 classes sympy had decided (3 unit, 3 non-unit then z3 unsat): same verdicts (sing7ctl/)',
        'what_it_rests_on': 'the enum2.py enumeration and obtuse-middle prune (RESULTS.md controls), the C1-C3 proofs (c123.py), '
                            'and the correctness of sympy, Singular and z3; no certificate was produced',
    }
    assert not missing and not extra
    json.dump(summary, open('RESULT_n7_c3.json', 'w'), indent=1)
    print('refuted %d of %d: %s' % (sum(c.values()), len(surv), dict(c)))
    print('ALL %d SURVIVORS REFUTED' % len(surv))


if __name__ == '__main__':
    main()
