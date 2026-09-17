"""Independent check of veljjanoski's Nullstellensatz certificates for Erdos #97 (k = 4), n = 7, 8, 9.

Source: github.com/veljjanoski/erdos97, folder n7/ (forum thread 97, post of 14 Sep 2026).  The
input files are NOT redistributed here (the repository has no licence); download them and pass
their folder.  None of that repository's code is run or imported.

What is checked, with code written from the README's definitions only:
  1. each structure is valid: Q_i is 4 distinct vertices other than i;
  2. n = 7: |Q_i & Q_j| = 2 for every i != j (the 54 classes of the counting-tight case,
     no convexity); n = 8, 9: every pair inside Q_i & Q_j is separated by i and j in the cyclic
     order (condition C3, which implies C1 and C2);
  3. the cases are pairwise inequivalent under the dihedral group D_n;
  4. the polynomials f are rebuilt from Q (gauge p_0 = (0,0), p_1 = (1,0); for each i and each
     consecutive a, b in the listed order of Q_i, f = |p_i - p_a|^2 - |p_i - p_b|^2) and
     compared with the stored ones;
  5. sum c_i f_i = 1 exactly, with the stored multipliers c_i and the REBUILT f_i.
Polynomials are dicts {exponent tuple: Fraction}, parsed by a small parser that accepts only
integers, the variables x2.. and y2.., + - * / ** and parentheses; no CAS is used.

What is NOT checked: that the case lists are complete (the enumeration), the five n = 9
classes decided by Groebner bases instead of certificates, and anything about n = 10.

Usage: python check_veljjanoski_certificates.py <folder with the downloaded files>
Writes check_veljjanoski_certificates.json next to this script.
"""
import hashlib
import json
import os
import re
import sys
from fractions import Fraction
from itertools import combinations

TOKEN = re.compile(r'\s*(?:(\d+)|([xy]\d+)|(\*\*|[-+*/()]))')


def poly_parse(s, var_index):
    if not re.fullmatch(r'[0-9xy+\-*/() ]*', s):
        raise ValueError('unexpected character in %r' % s[:60])
    toks = []
    pos = 0
    while pos < len(s):
        m = TOKEN.match(s, pos)
        if not m or m.end() == pos:
            if s[pos:].strip() == '':
                break
            raise ValueError('cannot tokenise %r' % s[pos:pos + 20])
        toks.append(m.groups())
        pos = m.end()
    k = [0]
    nv = len(var_index)

    def peek():
        return toks[k[0]] if k[0] < len(toks) else (None, None, None)

    def expr():
        sign = 1
        if peek()[2] in ('+', '-'):
            sign = -1 if peek()[2] == '-' else 1
            k[0] += 1
        acc = scale(term(), sign)
        while peek()[2] in ('+', '-'):
            op = peek()[2]
            k[0] += 1
            acc = add(acc, scale(term(), 1 if op == '+' else -1))
        return acc

    def term():
        acc = factor()
        while peek()[2] in ('*', '/'):
            op = peek()[2]
            k[0] += 1
            f = factor()
            if op == '*':
                acc = mul(acc, f)
            else:
                if len(f) != 1 or () not in f and tuple([0] * nv) not in f:
                    raise ValueError('division by a non-constant')
                acc = scale(acc, 1 / list(f.values())[0])
        return acc

    def factor():
        b = base()
        if peek()[2] == '**':
            k[0] += 1
            e = peek()[0]
            if e is None:
                raise ValueError('non-integer exponent')
            k[0] += 1
            r = const(1, nv)
            for _ in range(int(e)):
                r = mul(r, b)
            return r
        return b

    def base():
        num, var, op = peek()
        if num is not None:
            k[0] += 1
            return const(Fraction(int(num)), nv)
        if var is not None:
            k[0] += 1
            e = [0] * nv
            e[var_index[var]] = 1
            return {tuple(e): Fraction(1)}
        if op == '(':
            k[0] += 1
            r = expr()
            if peek()[2] != ')':
                raise ValueError('missing )')
            k[0] += 1
            return r
        if op == '-':
            k[0] += 1
            return scale(base(), -1)
        raise ValueError('unexpected token %r' % (peek(),))

    out = expr()
    if k[0] != len(toks):
        raise ValueError('trailing tokens')
    return out


def const(c, nv):
    return {tuple([0] * nv): Fraction(c)} if c else {}


def add(p, q):
    r = dict(p)
    for m, c in q.items():
        r[m] = r.get(m, 0) + c
        if r[m] == 0:
            del r[m]
    return r


def scale(p, s):
    return {m: c * s for m, c in p.items() if c * s != 0}


def mul(p, q):
    r = {}
    for m1, c1 in p.items():
        for m2, c2 in q.items():
            m = tuple(a + b for a, b in zip(m1, m2))
            r[m] = r.get(m, 0) + c1 * c2
            if r[m] == 0:
                del r[m]
    return r


def rebuild_f(Q, n):
    names = ['x%d' % i for i in range(2, n)] + ['y%d' % i for i in range(2, n)]
    idx = {v: t for t, v in enumerate(names)}
    nv = len(names)

    def coord(i, axis):
        if i == 0:
            return {}
        if i == 1:
            return const(1, nv) if axis == 0 else {}
        e = [0] * nv
        e[idx[('x' if axis == 0 else 'y') + str(i)]] = 1
        return {tuple(e): Fraction(1)}

    def d2(i, a):
        dx = add(coord(i, 0), scale(coord(a, 0), -1))
        dy = add(coord(i, 1), scale(coord(a, 1), -1))
        return add(mul(dx, dx), mul(dy, dy))

    fs = []
    for i, q in enumerate(Q):
        for a, b in zip(q, q[1:]):
            fs.append(add(d2(i, a), scale(d2(i, b), -1)))
    return fs, idx


def separated_ok(Q, n):
    S = [set(q) for q in Q]
    for i, j in combinations(range(n), 2):
        for a, b in combinations(sorted(S[i] & S[j]), 2):
            side = lambda x: 0 < (x - i) % n < (j - i) % n
            if side(a) == side(b):
                return False
    return True


def canonical(Q, n):
    forms = []
    for r in range(n):
        for s in (1, -1):
            g = lambda v: (s * v + r) % n
            img = [None] * n
            for i, q in enumerate(Q):
                img[g(i)] = tuple(sorted(g(v) for v in q))
            forms.append(tuple(img))
    return min(forms)


def main():
    folder = sys.argv[1]
    report = {'source': open(os.path.join(folder, 'SOURCE.txt')).read().splitlines()
              if os.path.exists(os.path.join(folder, 'SOURCE.txt')) else None}
    all_ok = True
    for n in (7, 8, 9):
        cases = json.load(open(os.path.join(folder, 'n%d_cases.json' % n)))
        certs = json.load(open(os.path.join(folder, 'n%d_certificates.json' % n)))
        r = {'cases': len(cases), 'certificate_entries': len(certs)}
        r['structures_valid'] = all(len(q) == 4 and len(set(q)) == 4 and i not in q and
                                    all(0 <= v < n for v in q)
                                    for Q in cases for i, q in enumerate(Q))
        if n == 7:
            r['all_intersections_exactly_2'] = all(len(set(Q[i]) & set(Q[j])) == 2
                                                   for Q in cases for i, j in combinations(range(n), 2))
        else:
            r['C3_holds_for_every_case'] = all(separated_ok(Q, n) for Q in cases)
        r['cases_pairwise_inequivalent_under_Dn'] = len({canonical(Q, n) for Q in cases}) == len(cases)
        checked, failed, no_cert = [], [], []
        for key in sorted(certs, key=int):
            e = certs[key]
            ci = int(key)
            if 'c' not in e or not e.get('c'):
                no_cert.append(ci)
                continue
            assert e['Q'] == cases[ci], 'certificate %s is for a different structure' % key
            fs, idx = rebuild_f(e['Q'], n)
            stored_f = [poly_parse(s, idx) for s in e['f']]
            cs = [poly_parse(s, idx) for s in e['c']]
            same_f = stored_f == fs
            total = {}
            for c, f in zip(cs, fs):
                total = add(total, mul(c, f))
            one = total == const(1, len(idx))
            (checked if (one and same_f and len(cs) == len(fs)) else failed).append(ci)
        r['certificates_verified'] = checked
        r['certificates_failing'] = failed
        r['entries_without_certificate'] = no_cert
        for k in ('structures_valid', 'all_intersections_exactly_2', 'C3_holds_for_every_case',
                  'cases_pairwise_inequivalent_under_Dn'):
            if k in r and not r[k]:
                all_ok = False
        if failed:
            all_ok = False
        report['n%d' % n] = r
        print('n=%d: %d cases; %d certificates verified, %d failing, entries without one: %s; %s'
              % (n, len(cases), len(checked), len(failed), no_cert,
                 {k: v for k, v in r.items() if isinstance(v, bool)}))
    # Mutant controls: the identity test must be able to fail.
    e = json.load(open(os.path.join(folder, 'n7_certificates.json')))['0']
    fs, idx = rebuild_f(e['Q'], 7)
    cs = [poly_parse(s, idx) for s in e['c']]
    nv = len(idx)

    def total_of(cs_, fs_):
        t = {}
        for c, f in zip(cs_, fs_):
            t = add(t, mul(c, f))
        return t

    mut_c = [add(cs[0], const(1, nv))] + cs[1:]
    Q_swapped = [list(q) for q in e['Q']]
    Q_swapped[2][0], Q_swapped[3][0] = Q_swapped[3][0], Q_swapped[2][0]
    fs_swapped, _ = rebuild_f(Q_swapped, 7)
    report['controls'] = {
        'unchanged_certificate_gives_1': total_of(cs, fs) == const(1, nv),
        'c_0_plus_1_is_rejected': total_of(mut_c, fs) != const(1, nv),
        'wrong_structure_is_rejected': total_of(cs, fs_swapped) != const(1, nv),
        'terms_in_c_0': len(cs[0]),
    }
    print('controls:', report['controls'])
    if not (report['controls']['unchanged_certificate_gives_1'] and report['controls']['c_0_plus_1_is_rejected']
            and report['controls']['wrong_structure_is_rejected']):
        all_ok = False
    report['all_checks_passed'] = all_ok
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'check_veljjanoski_certificates.json')
    json.dump(report, open(out, 'w'), indent=1)
    print('ALL CHECKS PASSED' if all_ok else 'SOME CHECKS FAILED')


if __name__ == '__main__':
    main()
