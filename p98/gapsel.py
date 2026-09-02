"""Recover, as a checked-in script, how gap_residual.json was selected.

The 153 n=5,k=4 patterns that `hard.py` called unsat are the ones whose rejection rests
on assumption A8 (completeness of hard.py's chain enumeration).  Two independent methods
were then applied to them:

    z3_gap_n5k4.json   z3 nlsat on the coordinate encoding (a decision procedure for RCF,
                       so its unsat is a proof)                    -> 67 unsat, 86 unknown
    gap_trivial.json   lex Groebner basis == [1], i.e. the ideal is trivial and there is
                       no solution even over C                     -> 11 of those 86

    gap_residual.json  = the 86 z3-unknowns minus the 11 trivial-ideal ones = 75

Usage:  python gapsel.py           # rebuild gap_residual.json and print the tally
"""
import sys, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

gap = json.load(open('z3_gap_n5k4.json'))
triv = set(tuple(p) for p in json.load(open('gap_trivial.json'))['trivial_ideal'])
unk = [tuple(p) for p in gap.get('unknown', [])]
rest = [list(p) for p in unk if tuple(p) not in triv]
json.dump({'candidates': rest}, open('gap_residual.json', 'w'), indent=1)

n_total = len(gap.get('unsat', [])) + len(unk)
print('A8-dependent n=5,k=4 unsats: %d' % n_total)
print('  settled by z3 run 1 (unsat) : %d' % len(gap.get('unsat', [])))
print('  settled by trivial ideal    : %d' % len(triv))
print('  residual written            : %d  -> gap_residual.json' % len(rest))
try:
    res = json.load(open('z3_residual.json'))
    print('  settled by z3 run 2 (unsat) : %d' % len(res.get('unsat', [])))
    settled = len(gap.get('unsat', [])) + len(triv) + len(res.get('unsat', []))
    print('  ------------------------------')
    print('  independently settled       : %d' % settled)
    print('  still resting on A8         : %d' % (n_total - settled))
    print('  SAT found anywhere          : %d'
          % (len(gap.get('sat', [])) + len(res.get('sat', []))))
except FileNotFoundError:
    print('  (z3_residual.json not present yet)')
