"""The third shape of n = 5, attacked by the method that decided Case A, without an exact result.

OUTCOME (2026-09-16 correction of this docstring, which said "decided exactly").  No exact
run over Q finished for any of the seven patterns.  All seven have no solution modulo 32003
and modulo 32749, and six of them none modulo 1073741827; that is evidence, not a proof
(NOTE.md section 5b).

THE PATTERNS.  results/penum_n5_k3.json lists the radius patterns of 5 points with three
classes that survive Lemmas 1, 3 and 4; twelve also respect f(5) = 4.  Sorted by the shape
of their size-4 classes: 2 have a class that is all four triples of a 4-set (Case A,
caseA_exact.py), 3 have a class of four triples through one point (the common-point
branch), and 7 have neither.  Those 7, patterns 5, 7, 8, 9, 10, 11 and 13, are the third
shape, and are recomputed from the artifact and asserted below.

THE ALGEBRA.  Five points, two of them fixed by a similarity, and one squared radius per
class: for each of the ten triples T in class c,  N_T = 4 * r_c * K_T^2,  with N_T the
product of the squared sides and K_T the cross product.  Ten equations, nine unknowns.
A collinear triple of distinct points cannot satisfy its equation (K = 0 forces N = 0).

WHAT ADMISSIBILITY FORCES, AND WHY IT IS ENOUGH.  Distinct points: the ten squared
distances are non-zero.  Three classes: r0, r1, r2 pairwise different.  No four
concyclic: in a third-shape pattern no class contains all four triples of any 4-set
(asserted below), so four concyclic points would put two classes on one radius, which the
previous condition already excludes.  So a real solution with all of these non-zero IS an
admissible 5-point set with exactly three circumradii, and a pattern is refuted when the
system plus t*g = 1 (Rabinowitsch) for some of these g has no solution at all.  Imposing
only SOME of them is still a valid refutation; that is what makes the exact run feasible.

GAUGES.  G1 fixes P0 = (0,0), P1 = (1,0); G2 fixes P3 = (0,0), P4 = (1,0).  Every labelled
configuration can be moved into either, and the patterns are canonical representatives
under relabelling, so deciding each pattern in one gauge decides its whole orbit.

Usage:
  python third_exact.py gen                    full systems, pinned controls
  python third_exact.py run ENGINE JOBS [THREADS] [TIMEOUT]   ENGINE msolve | singrab
  python third_exact.py greedy GAUGE PATTERN [THREADS]
  python third_exact.py genreduced GAUGE PATTERN KEEP
Runs in the container cas831 (docker/Dockerfile).  Log: logs/third_exact.log.
"""
import io
import json
import os
import re
import subprocess
import sys
import time
from fractions import Fraction
from itertools import combinations

import sympy as sp

import caseA_exact as CA          # low-level writers and helpers only

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

TRI = list(combinations(range(5), 3))
EXD = CA.EXD
LOG = os.path.join('logs', 'third_exact.log')
MAN = os.path.join(EXD, 'manifest3.json')
THIRD = [5, 7, 8, 9, 10, 11, 13]


def log(msg):
    line = time.strftime('%Y-%m-%d %H:%M:%S ') + msg
    print(line, flush=True)
    with io.open(LOG, 'a', encoding='utf-8') as f:
        f.write(line + '\n')


# ---------------------------------------------------------------- the patterns
def shape(cl):
    if len(set().union(*cl)) == 4:
        return 'four-set'
    if set.intersection(*[set(t) for t in cl]):
        return 'common-point'
    return 'other'


def patterns():
    """the third-shape patterns, recomputed from the artifact and checked"""
    d = json.load(open(os.path.join('results', 'penum_n5_k3.json')))['patterns']
    out = {}
    for i, p in enumerate(d):
        if not p['f104_ok']:
            continue
        cls = [[t for j, t in enumerate(TRI) if p['labels'][j] == c] for c in range(3)]
        if all(shape(c) == 'other' for c in cls if len(c) == 4):
            out[i] = p['labels']
    assert sorted(out) == THIRD, sorted(out)
    for i, lab in out.items():
        for q in combinations(range(5), 4):
            classes = {lab[TRI.index(t)] for t in combinations(q, 3)}
            assert len(classes) >= 2, 'pattern %d: a class holds all of %s' % (i, q)
    return out


# ---------------------------------------------------------------- systems
def gauge(g):
    if g == 'G1':
        x2, y2, x3, y3, x4, y4 = sp.symbols('x2 y2 x3 y3 x4 y4')
        return [(0, 0), (1, 0), (x2, y2), (x3, y3), (x4, y4)], [x2, y2, x3, y3, x4, y4]
    if g == 'G2':
        x0, y0, x1, y1, x2, y2 = sp.symbols('x0 y0 x1 y1 x2 y2')
        return [(x0, y0), (x1, y1), (x2, y2), (0, 0), (1, 0)], [x0, y0, x1, y1, x2, y2]
    raise ValueError(g)


R = sp.symbols('r0 r1 r2')


def system(g, labels, lam=None):
    """equations, saturated factors, variables; LAM rescales each triple's constant"""
    pts, co = gauge(g)
    vs = co + list(R)
    eqs = []
    for n, (i, j, k) in enumerate(TRI):
        rho = R[labels[n]] * (lam[n] if lam is not None else 1)
        eqs.append(CA.rad_eq(pts[i], pts[j], pts[k], rho))
    sat = [CA.d2(pts[i], pts[j]) for i, j in combinations(range(5), 2)]
    sat += [R[0] - R[1], R[0] - R[2], R[1] - R[2]]
    return eqs, CA.factors(sat, vs), vs


# a planted rational configuration in G1 coordinates, checked admissible below
PLANT = [(Fraction(0), Fraction(0)), (Fraction(1), Fraction(0)), (Fraction(2, 7), Fraction(5, 7)),
         (Fraction(9, 8), Fraction(13, 10)), (Fraction(-1, 2), Fraction(3, 5))]


def plant_in(g):
    if g == 'G1':
        return PLANT
    a, b = PLANT[3], PLANT[4]               # z -> (z - P3) / (P4 - P3)
    w = (b[0] - a[0], b[1] - a[1])
    den = w[0] ** 2 + w[1] ** 2
    out = []
    for z in PLANT:
        u = (z[0] - a[0], z[1] - a[1])
        out.append(((u[0] * w[0] + u[1] * w[1]) / den, (u[1] * w[0] - u[0] * w[1]) / den))
    return out


def plant_checks():
    P = PLANT
    for i, j in combinations(range(5), 2):
        assert P[i] != P[j]
    for i, j, k in TRI:
        assert CA.cr(P[i], P[j], P[k]) != 0, 'collinear planted triple'
    for q in combinations(range(5), 4):
        M = sp.Matrix([[P[t][0] ** 2 + P[t][1] ** 2, P[t][0], P[t][1], 1] for t in q])
        assert M.det() != 0, 'four planted points concyclic'


def pinned_control(g, i, labels):
    """pattern i with each triple's constant rescaled so the planted configuration solves
    it, and one point pinned: same equations, same saturated factors, few solutions"""
    pts = plant_in(g)
    rho = [Fraction(CA.d2(pts[b], pts[c]) * CA.d2(pts[c], pts[a]) * CA.d2(pts[a], pts[b]))
           / (4 * Fraction(CA.cr(pts[a], pts[b], pts[c])) ** 2) for a, b, c in TRI]
    first = {}
    for n in range(10):
        first.setdefault(labels[n], n)
    lam = [sp.Rational(*(rho[n] / rho[first[labels[n]]]).as_integer_ratio()) for n in range(10)]
    eqs, fac, vs = system(g, labels, lam)
    _, co = gauge(g)
    free = [2, 3, 4] if g == 'G1' else [0, 1, 2]           # the points not fixed by the gauge
    full = {co[2 * k + e]: sp.Rational(*pts[free[k]][e].as_integer_ratio())
            for k in range(3) for e in range(2)}
    for c in range(3):
        full[R[c]] = sp.Rational(*rho[first[c]].as_integer_ratio())
    for e in eqs:
        assert sp.expand(e.subs(full)) == 0
    for f in fac:
        assert sp.expand(f.subs(full)) != 0
    pin = [co[0] - full[co[0]], co[1] - full[co[1]]]
    return eqs + pin, fac, vs, {str(a): str(b) for a, b in full.items()}


# ---------------------------------------------------------------- manifest, files
def update_manifest(name, entry):
    lock = MAN + '.lock'
    while True:
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            break
        except FileExistsError:
            time.sleep(0.2)
    try:
        man = json.load(open(MAN)) if os.path.exists(MAN) else {'jobs': {}}
        man['jobs'][name] = entry
        json.dump(man, open(MAN, 'w'), indent=1)
    finally:
        os.close(fd)
        os.remove(lock)


def set_prime(name):
    path = os.path.join(EXD, name + '.ms')
    lines = io.open(path, encoding='ascii').read().split('\n')
    lines[1] = str(CA.PRIME)
    io.open(path, 'w', encoding='ascii', newline='\n').write('\n'.join(lines))


def gen():
    plant_checks()
    for i, lab in patterns().items():
        for g in ('G1', 'G2'):
            eqs, fac, vs = system(g, lab)
            name = '%s_p%d' % (g, i)
            allv = CA.write_msolve(name, eqs, fac, vs)
            update_manifest(name, dict(gauge=g, pattern=i, labels=lab, vars=allv,
                                       nvars=len(vs), nfactors=len(fac)))
            eqs, fac, vs, planted = pinned_control(g, i, lab)
            name = '%s_pin%d' % (g, i)
            allv = CA.write_msolve(name, eqs, fac, vs)
            update_manifest(name, dict(gauge=g, pattern=i, labels=lab, vars=allv,
                                       nvars=len(vs), nfactors=len(fac), planted=planted))
    log('gen: full systems and pinned controls for patterns %s in G1 and G2' % THIRD)


def genreduced(g, i, keep):
    lab = patterns()[i]
    eqs, fac, vs = system(g, lab)
    sub = [fac[k] for k in keep]
    name = '%s_red%d' % (g, i)
    allv = CA.write_msolve(name, eqs, sub, vs)
    CA.write_singular_rab(name, eqs, sub, vs)
    update_manifest(name, dict(gauge=g, pattern=i, labels=lab, vars=allv, nvars=len(vs),
                               nfactors=len(sub), kept=list(keep),
                               factors=[str(f) for f in sub]))
    log('genreduced: %s keeps factors %s of %d' % (name, list(keep), len(fac)))


# ---------------------------------------------------------------- running
def docker(cmd, live):
    return subprocess.run(['docker', 'exec', CA.CONTAINER, 'bash', '-c',
                           'stdbuf -oL -eL %s > /work/%s 2>&1' % (cmd, live)],
                          capture_output=True, text=True)


def run(engine, jobs, threads=6, tmo=3600):
    man = json.load(open(MAN))['jobs']
    resf = os.path.join('results', 'third_exact_%s.json' % engine)
    for name in jobs:
        job = man[name]
        live = '%s/%s.%s.live' % (EXD, name, engine)
        if engine == 'msolve':
            cmd = 'timeout -s KILL %d msolve -t %d -v 2 -f /work/%s/%s.ms -o /work/%s/%s.ms.out' % (
                tmo, threads, EXD, name, EXD, name)
        else:
            cmd = "script -qfec 'timeout -s KILL %d Singular -q /work/%s/%s.rab.sing' /dev/null" % (
                tmo, EXD, name)
        log('%s %s: start (timeout %d s); progress in %s' % (engine, name, tmo, live))
        t0 = time.time()
        p = docker(cmd, live)
        dt = time.time() - t0
        out = io.open(live, encoding='utf-8', errors='replace').read()
        rec = dict(engine=engine, job=name, seconds=round(dt, 1), returncode=p.returncode)
        if p.returncode != 0:
            rec['status'] = 'KILLED at timeout' if p.returncode in (124, 137) else 'ERROR'
        elif engine == 'msolve':
            rec['squarefree_eliminant'] = 'not squarefree' not in out
            status, boxes = CA.parse_msolve(io.open(os.path.join(EXD, name + '.ms.out')).read())
            rec['status'] = status
            rec['n_real'] = None if boxes is None else len(boxes)
            if boxes and 'planted' in job:
                nv = job['nvars']
                pl = [Fraction(job['planted'][v]) for v in job['vars'][:nv]]
                rec['planted_found'] = any(all(lo <= c <= hi for (lo, hi), c in zip(b[:nv], pl))
                                           for b in boxes)
        else:
            res = dict(re.findall(r'RESULT (\w+) (-?\d+)', out))
            rec.update({k: int(v) for k, v in res.items()})
            d = rec.get('dim')
            rec['status'] = ('no complex solution' if d == -1 else
                             'zero dimensional' if d == 0 else 'positive dimensional')
        allres = json.load(open(resf)) if os.path.exists(resf) else {}
        allres[name] = rec
        json.dump(allres, open(resf, 'w'), indent=1)
        log('%s %s: %s  (%.1f s)%s%s' % (engine, name, rec['status'], dt,
                                         '  real roots: %s' % rec['n_real'] if 'n_real' in rec else '',
                                         '  planted found: %s' % rec['planted_found']
                                         if 'planted_found' in rec else ''))


def greedy(g, i, threads=6, tmo=240, order=None, memkb=5000000):
    """drop saturated factors one at a time while the system stays inconsistent mod p;
    only a guide to which smaller system to decide exactly.  An inconsistent trial takes
    seconds; a trial with solutions can take gigabytes (one reached 13 GB), so each trial
    runs under a memory cap MEMKB and a time limit TMO, and hitting either counts as
    'keep the factor'.  That errs towards imposing more, which is always valid."""
    lab = patterns()[i]
    eqs, fac, vs = system(g, lab)
    keep = list(range(len(fac)))
    order = order if order is not None else list(keep)
    resf = os.path.join('results', 'third_greedy_%s_%d.json' % (g, i))
    hist = []

    def trial_run(trial, tag):
        name = '%s_gr%d_%s' % (g, i, tag)
        CA.write_msolve(name, eqs, [fac[k] for k in trial], vs)
        set_prime(name)
        cmd = ('ulimit -v %d; timeout -s KILL %d msolve -t %d -f /work/%s/%s.ms '
               '-o /work/%s/%s.ms.out' % (memkb, tmo, threads, EXD, name, EXD, name))
        t0 = time.time()
        p = subprocess.run(['docker', 'exec', CA.CONTAINER, 'bash', '-c', cmd],
                           capture_output=True, text=True)
        out = (io.open(os.path.join(EXD, name + '.ms.out')).read().strip()
               if p.returncode == 0 and os.path.exists(os.path.join(EXD, name + '.ms.out')) else '')
        return out.startswith('[-1]'), time.time() - t0, p.returncode

    unit, dt, rc = trial_run(keep, 'all')
    hist.append(dict(try_drop=None, unit_mod_p=unit, seconds=round(dt, 1), returncode=rc,
                     keep=list(keep)))
    log('greedy %s pattern %d: all %d factors -> %s (%.1f s)'
        % (g, i, len(fac), 'no solution mod p' if unit else
           ('KILLED' if rc else 'SOLUTIONS mod p'), dt))
    if unit:
        for j in order:
            trial = [k for k in keep if k != j]
            u, dt, rc = trial_run(trial, 'x' + '_'.join(map(str, trial)))
            if u:
                keep = trial
            hist.append(dict(try_drop=j, factor=str(fac[j]), unit_mod_p=u, seconds=round(dt, 1),
                             returncode=rc, keep=list(keep)))
            json.dump(dict(gauge=g, pattern=i, prime=CA.PRIME, factors=[str(f) for f in fac],
                           history=hist, keep=keep), open(resf, 'w'), indent=1)
    json.dump(dict(gauge=g, pattern=i, prime=CA.PRIME, factors=[str(f) for f in fac],
                   history=hist, keep=keep, all_unit=unit), open(resf, 'w'), indent=1)
    # a killed baseline is UNDECIDED, not "has solutions"; say which it was
    base_rc = hist[0]['returncode']
    log('greedy %s pattern %d: %s; keeping %s'
        % (g, i, 'done' if unit else
           ('UNDECIDED: the all-factor trial was killed (cap or limit)' if base_rc else
            'the all-factor trial has solutions mod p'), keep))
    return keep if unit else None


def record_live(name, seconds=None):
    """record a Singular run whose driver was stopped while Singular kept going: the
    verdict is read from its live file, exactly as run() would have read it"""
    out = io.open('%s/%s.singrab.live' % (EXD, name), encoding='utf-8', errors='replace').read()
    res = dict(re.findall(r'RESULT (\w+) (-?\d+)', out))
    rec = dict(engine='singrab', job=name, seconds=seconds, recorded_from_live_file=True)
    rec.update({k: int(v) for k, v in res.items()})
    d = rec.get('dim')
    rec['status'] = ('no complex solution' if d == -1 else 'zero dimensional' if d == 0 else
                     'positive dimensional' if d is not None else 'ERROR or stopped')
    resf = os.path.join('results', 'third_exact_singrab.json')
    allres = json.load(open(resf)) if os.path.exists(resf) else {}
    allres[name] = rec
    json.dump(allres, open(resf, 'w'), indent=1)
    log('singrab %s: %s  (recorded from the live file)' % (name, rec['status']))


def batch(g, pats, threads=6, parallel=2):
    """all the mod-p screens first, then the exact runs PARALLEL at a time, so one slow
    exact run no longer holds up every other pattern"""
    from concurrent.futures import ThreadPoolExecutor
    ready = []
    for i in pats:
        keep = greedy(g, i, threads)
        if keep is not None:
            genreduced(g, i, keep)
            ready.append(i)

    def one(i):
        run('singrab', ['%s_red%d' % (g, i)], 1, 21600)
        run('msolve', ['%s_red%d' % (g, i)], 1, 3600)
    with ThreadPoolExecutor(max_workers=parallel) as ex:
        list(ex.map(one, ready))


def prove(g, pats, threads=6):
    for i in pats:
        keep = greedy(g, i, threads)
        if keep is None:
            continue
        genreduced(g, i, keep)
        run('singrab', ['%s_red%d' % (g, i)], 1, 21600)
        run('msolve', ['%s_red%d' % (g, i)], 1, 3600)


if __name__ == '__main__':
    a = sys.argv
    if a[1] == 'gen':
        gen()
    elif a[1] == 'run':
        run(a[2], a[3].split(','), int(a[4]) if len(a) > 4 else 6, int(a[5]) if len(a) > 5 else 3600)
    elif a[1] == 'greedy':
        greedy(a[2], int(a[3]), int(a[4]) if len(a) > 4 else 6)
    elif a[1] == 'genreduced':
        genreduced(a[2], int(a[3]), [int(x) for x in a[4].split(',')])
    elif a[1] == 'prove':
        prove(a[2], [int(x) for x in a[3].split(',')], int(a[4]) if len(a) > 4 else 6)
    elif a[1] == 'batch':
        batch(a[2], [int(x) for x in a[3].split(',')], int(a[4]) if len(a) > 4 else 6,
              int(a[5]) if len(a) > 5 else 2)
    elif a[1] == 'record':
        record_live(a[2], float(a[3]) if len(a) > 3 else None)
