"""Turn every search output into artifacts/*.json objects that
verify_artifacts.py can re-check independently.

Run after the searches.  Every claim in RESULTS.md must point at one of these.
"""
import json, glob, os, sys, math
import artifact

OUT = []


def add(*a, **k):
    p = artifact.write(*a, **k)
    OUT.append(p)
    print("  wrote", os.path.basename(p))


# ---------------------------------------------------------------- 1. references
def references():
    print("reference objects (regular n-gons, Harborth H_8):")
    from mpmath import mp, mpf, cos, sin, pi
    mp.dps = 60
    for n in (5, 6, 7, 8, 9, 12, 13, 20, 21):
        P = [[str(cos(2 * pi * t / n)), str(sin(2 * pi * t / n))] for t in range(n)]
        add(f'regular_{n}gon', P, coords_kind='mp', claim='reference',
            producer='python export_artifacts.py  (mpmath, mp.dps=60)',
            notes=f'regular {n}-gon; ground truth: every vertex sees exactly '
                  f'floor(n/2)={n//2} distinct distances.  HIGH-PRECISION object '
                  f'(60 dps); the exact statement is proved by index arithmetic '
                  f'in Z_n (core.regular_ngon_per_vertex, checked in '
                  f'verify_machinery.py TEST 1).',
            convex=True, extra={'precision_dps': 60})
    # Harborth H_8, exact in Q(sqrt3) -- NOT convex; included so the verifier
    # demonstrates it is rejected on convexity, which is why #1082's refutation
    # does not touch #982.
    H8 = [['1', '1'], ['-1', '1'], ['-1', '-1'], ['1', '-1'],
          ['0', '1+sqrt(3)'], ['0', '-1-sqrt(3)'],
          ['1+sqrt(3)', '0'], ['-1-sqrt(3)', '0']]
    add('harborth_H8_nonconvex', H8, coords_kind='sympy', claim='reference',
        producer='python export_artifacts.py',
        notes='Harborth 8-point set: every point sees 3 distinct distances '
              '(so it refutes the second question of Erdos #1082) but it is NOT '
              'in convex position, so it says nothing about #982.',
        convex=False)


# ------------------------------------------------------------------ 2. lattice
def lattices():
    print("lattice search objects:")
    for fn in sorted(glob.glob('lattice_*.json')):
        d = json.load(open(fn))
        if not isinstance(d, dict) or d.get('lattice') != 'Z2':
            continue   # A2 coords are not Euclidean-integer; handled below
        base = os.path.basename(fn)[:-5]
        for i, rec in enumerate(d.get('counterexamples', [])):
            mx, pts = rec
            add(f'{base}_CEX{i}', pts, claim='counterexample',
                producer=f"python lattice.py {d['n']} {d['R']} Z2 "
                         f"{d['workers']} {d['search_budget']}",
                notes='CLAIMED COUNTEREXAMPLE from the lattice search', convex=True)
        for i, rec in enumerate(d.get('best_near_misses', [])[:3]):
            add(f'{base}_near{i}', rec['points'], claim='near_miss',
                producer=f"python lattice.py {d['n']} {d['R']} Z2 "
                         f"{d['workers']} {d['search_budget']}",
                notes=f"best lattice near-miss: max per-vertex "
                      f"{rec['max_per_vertex']}, counterexample needs "
                      f"<= {d['counterexample_threshold']}", convex=True)
    # A2 objects: map the triangular lattice into the plane exactly
    for fn in sorted(glob.glob('lattice_A2_*.json')):
        d = json.load(open(fn))
        if not isinstance(d, dict):
            continue
        base = os.path.basename(fn)[:-5]
        def embed(p):
            return [str(p[0]) + '+' + str(p[1]) + '/2',
                    str(p[1]) + '*sqrt(3)/2']
        for i, rec in enumerate(d.get('counterexamples', [])):
            mx, pts = rec
            add(f'{base}_CEX{i}', [embed(p) for p in pts], coords_kind='sympy',
                claim='counterexample',
                producer=f"python lattice.py {d['n']} {d['R']} A2 "
                         f"{d['workers']} {d['search_budget']}",
                notes='CLAIMED COUNTEREXAMPLE (triangular lattice, embedded '
                      'exactly as x*(1,0)+y*(1/2,sqrt3/2))', convex=True)
        for i, rec in enumerate(d.get('best_near_misses', [])[:3]):
            add(f'{base}_near{i}', [embed(p) for p in rec['points']],
                coords_kind='sympy', claim='near_miss',
                producer=f"python lattice.py {d['n']} {d['R']} A2 "
                         f"{d['workers']} {d['search_budget']}",
                notes=f"triangular-lattice near-miss: max per-vertex "
                      f"{rec['max_per_vertex']}, counterexample needs "
                      f"<= {d['counterexample_threshold']}", convex=True)


# ------------------------------------------------------------------ 3. two-ring
def tworings():
    print("two-ring objects:")
    from mpmath import mp, mpf, cos, sin, pi
    mp.dps = 60
    for fn in sorted(glob.glob('tworing_m*.json')):
        d = json.load(open(fn))
        for rec in d['hits']:
            m, r = rec['m'], mpf(repr(rec['r']))
            pts = ([[str(cos(2*pi*j/m)), str(sin(2*pi*j/m))] for j in range(m)] +
                   [[str(r*cos(pi*(2*j+1)/m)), str(r*sin(pi*(2*j+1)/m))]
                    for j in range(m)])
            add(f'tworing_m{m}_CEX', pts, coords_kind='mp', claim='counterexample',
                producer=f"python tworing_par.py {d['m_lo']} {d['m_hi']} "
                         f"{d['workers']}",
                notes=f"CLAIMED two-ring counterexample, m={m}, r={rec['r']!r}",
                convex=True, extra={'precision_dps': 60})
        # a representative near-miss: the m that gets closest
        for rec in d['per_m']:
            if rec['m'] in (7, 21, 50, 100):
                m, r = rec['m'], mpf(repr(rec['best_r']))
                pts = ([[str(cos(2*pi*j/m)), str(sin(2*pi*j/m))] for j in range(m)] +
                       [[str(r*cos(pi*(2*j+1)/m)), str(r*sin(pi*(2*j+1)/m))]
                        for j in range(m)])
                add(f'tworing_m{m}_best', pts, coords_kind='mp', claim='near_miss',
                    producer=f"python tworing_par.py {d['m_lo']} {d['m_hi']} "
                             f"{d['workers']}",
                    notes=f"best two-ring radius for m={m}: r={rec['best_r']!r}, "
                          f"max per-vertex {rec['best_max']}, counterexample "
                          f"needs <= {rec['target']}; convex range "
                          f"({rec['convex_lo']!r}, {rec['convex_hi']!r})",
                    convex=True, extra={'precision_dps': 60})


# ------------------------------------------------------------------ 4. nsearch
def nsearches():
    print("numerical-search objects:")
    for fn in sorted(glob.glob('nsearch_n*.json')):
        d = json.load(open(fn))
        n = d['n']
        pts = [[repr(x), repr(y)] for x, y in d['best_points']]
        add(f'nsearch_n{n}_best', pts, coords_kind='mp', claim='near_miss',
            producer=f"python nsearch.py {n} {d['trials']} {d['workers']}",
            notes=f"best numerical near-miss for n={n}: rho={d['best_rho']:.6e} "
                  f"(rho = max over vertices of the largest within-cluster spread "
                  f"of its distances, divided by the SHORTEST SIDE, when its n-1 "
                  f"distances are optimally split into floor(n/2)-1 clusters; "
                  f"rho=0 would be a counterexample).  seed={d['best_seed']}. "
                  f"FLOATING POINT (double), NOT exact.",
            convex=True, extra={'precision_dps': 15, 'rho': d['best_rho'],
                                'regular_ngon_rho': d['regular_ngon_rho'],
                                'min_side_over_diameter':
                                    d['best_degeneracy_min_side_over_diameter']})


if __name__ == '__main__':
    which = sys.argv[1:] or ['ref', 'lat', 'ring', 'ns']
    if 'ref' in which:
        references()
    if 'lat' in which:
        lattices()
    if 'ring' in which:
        tworings()
    if 'ns' in which:
        nsearches()
    print(f"\n{len(OUT)} artifacts written to artifacts/")
