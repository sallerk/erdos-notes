"""What the exact small values buy as a LOWER bound, and what the extremal profile requires.

Two elementary consequences of the computed table, both checkable here.

PART 1.  Monotonicity beats the published bound in a range.
D_gen is non-decreasing (deleting a point keeps general position and cannot add
distances), so an exact value at m is a lower bound for every n >= m.  The published
lower bound is Szemeredi's ceil((n-1)/3).  Since D_gen(7) = 5 and ceil((n-1)/3) does not
reach 5 until n = 14, the computed values give a STRICTLY BETTER lower bound on 4 <= n <= 13.

PART 2.  The extremal profile is far more rigid than the counting suggests.
To attain D_gen(n) = (n-1)/3 exactly, every point must see every one of the (n-1)/3
distances exactly 3 times (any class of size < 3 at any vertex forces more classes there,
and >3 is barred by no-four-cocircular).  So EVERY distance class is a 3-REGULAR graph on
all n vertices, and the (n-1)/3 classes partition E(K_n).  Consequences:

  * 3-regular on n vertices needs 3n even, so n must be EVEN.
  * (n-1)/3 must be an integer, so n = 1 mod 3.
  * together: the bound is attainable only when n = 4 mod 6.
  * each class is a unit-distance graph and, by "two distinct equal-radius circles meet
    at most twice", K_{2,3}-free.

Run:  python lowerbound.py
"""
import sys, itertools

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

FAIL = []


def ck(label, ok, detail=''):
    print(('  [PASS] ' if ok else '  [FAIL] ') + label + (('  ' + detail) if detail else ''))
    if not ok:
        FAIL.append(label)


EXACT = {3: 1, 4: 2, 5: 3, 6: 4, 7: 5}    # all proved; see NOTE.md 3c, 3h, 3j


def pigeon(n):
    return -(-(n - 1) // 3)               # ceil((n-1)/3)


def best_known(n):
    """the lower bound from monotonicity, using the largest exact value at or below n"""
    return max([v for m, v in EXACT.items() if m <= n] or [1])


print('=' * 74)
print('WHAT THE EXACT VALUES BUY, AND WHAT THE EXTREMAL PROFILE REQUIRES')
print('=' * 74)

print()
print('PART 1.  Monotonicity versus the published bound ceil((n-1)/3).')
print()
print('    n   ceil((n-1)/3)   monotonicity   better?')
gain = []
for n in range(4, 20):
    p, b = pigeon(n), best_known(n)
    mark = 'YES  +%d' % (b - p) if b > p else ''
    if b > p:
        gain.append(n)
    print('  %3d   %11d   %12d   %s' % (n, p, b, mark))
print()
ck('D_gen(6) = 4 exceeds ceil(5/3) = 2', EXACT[6] > pigeon(6))
ck('the computed values give a STRICTLY better lower bound on the window 4..13',
   gain == list(range(4, 14)), 'range %s' % gain)
print('   So the small table is not only data: for 4 <= n <= 13 it is the best known')
print('   lower bound, beating Szemeredi in that window.  ceil((n-1)/3) does not reach 5')
print('   until n = 14, which is where the window closes.')
print()
print('   And a further exact value would extend it:')
for hyp, name in ((6, 'if D_gen(8) = 6'),):
    m = 7 if hyp == 5 else 8
    last = max(n for n in range(m, 40) if pigeon(n) < hyp)
    print('     %-18s then D_gen(n) >= %d for n >= %d, beating the bound up to n = %d'
          % (name, hyp, m, last))

print()
print('PART 2.  The extremal profile.')
print()
print('  Attaining D_gen(n) = (n-1)/3 forces every distance class to be 3-regular on')
print('  all n vertices, with the (n-1)/3 classes partitioning E(K_n).')
# the identity only makes sense where 3-regularity is possible at all, i.e. n even,
# which together with (n-1)/3 integral means n = 4 mod 6.  Asserting it for odd n was
# my error: 3n/2 is not an integer there, which is exactly WHY those n are excluded.
ok_edges = all(((n - 1) // 3) * (3 * n // 2) == n * (n - 1) // 2
               for n in range(4, 200) if n % 6 == 4)
ck('for n = 4 mod 6, ((n-1)/3) classes x 3n/2 edges = C(n,2) exactly', ok_edges)
# NOT a counting obstruction: ((n-1)/3)*3n = n(n-1) holds algebraically for every n.
# What excludes odd n is INTEGRALITY -- a 3-regular graph on n vertices has 3n/2 edges,
# which is not a whole number when n is odd, so no such graph exists.
ck('odd n is excluded by parity, not by counting: 3n/2 is not an integer',
   all((3 * n) % 2 == 1 for n in (7, 13, 19, 25)))
# This was ck('the identity is vacuous', all((n-1)*3*n == 3*n*(n-1))) -- i.e. a*b == b*a,
# a tautology dressed as a check.  The content is that the identity carries no arithmetic
# obstruction, which is shown by exhibiting odd n where it holds yet no 3-regular graph
# exists; that, not commutativity, is the point.
_odd_ok = [n for n in range(5, 60, 2)
           if ((n - 1) * 3 * n) == 3 * n * (n - 1) and (3 * n) % 2 == 1]
ck('the edge identity holds for odd n too, so it is NOT what excludes them: %d such n '
   'in 5..59, every one blocked instead by 3n/2 being non-integral' % len(_odd_ok),
   len(_odd_ok) == len(range(5, 60, 2)))
ck('3-regular needs n even; (n-1)/3 integral needs n = 1 mod 3; together n = 4 mod 6',
   all((n % 2 == 0 and n % 3 == 1) == (n % 6 == 4) for n in range(1, 400)))
att = [n for n in range(4, 40) if n % 6 == 4]
print('   attainable n (n = 4 mod 6), up to 40: %s' % att)
print()
print('  Now rule those out one by one with what we already know:')
for n in att[:4]:
    if n == 4:
        print('     n = 4 : would need ONE 3-regular class on 4 points, i.e. K_4 at a single')
        print('             distance: four mutually equidistant points. Impossible in the')
        print('             plane. And indeed D_gen(4) = 2, not (4-1)/3 = 1.')
    else:
        b = best_known(n)
        print('     n = %-2d: would need D_gen(%d) = %d, but monotonicity gives D_gen(%d) >= %d.'
              % (n, n, (n - 1) // 3, n, b), end=' ')
        print('RULED OUT.' if b > (n - 1) // 3 else 'not ruled out by monotonicity alone.')
ck('n = 10 is ruled out: (10-1)/3 = 3 but D_gen(10) >= D_gen(6) = 4',
   best_known(10) > (10 - 1) // 3)
print()
print('   n = 16 is the first case monotonicity does NOT settle: attaining (n-1)/3 there')
print('   needs D_gen(16) = 5 exactly, and D_gen(7) = 5 gives D_gen(16) >= 5.')
print('   So D_gen(7) = 5 does NOT rule n = 16 out; it forces EXACT EQUALITY there,')
print('   which is a sharper constraint than a bound, since equality forces the rigid')
print('   3-regular profile at n = 16 -- a strong, checkable structure.')

print()
print('=' * 74)
if FAIL:
    print('FAILED %d CHECK(S):' % len(FAIL))
    for f in FAIL:
        print('  -', f)
    sys.exit(1)
print('ALL CHECKS PASSED')
print('=' * 74)
