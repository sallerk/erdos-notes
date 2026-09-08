"""Check the two draft comments sentence by sentence against the artifacts.

Every number, closed form and count that appears in the drafts is recomputed here, and
the bibliographic details are matched against REFERENCES.md.  The drafts live outside the
repository, so this script skips quietly when it cannot find them.

Usage: python comment_check.py
"""
import io
import os
import re
import sys
import json

import sympy as sp

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

DIR = os.path.join('..', '_internal_backup', 'p100')
C1 = os.path.join(DIR, 'DRAFT_COMMENT_1_RESULT.md')
C2 = os.path.join(DIR, 'DRAFT_COMMENT_2_SOURCES.md')
FAIL = []


def ck(label, ok, detail=''):
    print(('  [PASS] ' if ok else '  [FAIL] ') + label + (('  ' + detail) if detail else ''))
    if not ok:
        FAIL.append(label)


if not os.path.exists(C1):
    print('drafts not present (they are kept outside the repository); nothing to check')
    sys.exit(0)

t1 = io.open(C1, encoding='utf-8').read()
t2 = io.open(C2, encoding='utf-8').read()
s2, s3, s5, s6 = sp.sqrt(2), sp.sqrt(3), sp.sqrt(5), sp.sqrt(6)

print('1. Every number quoted in the drafts, recomputed')
NUM = [
    ('4.663902460', (2 + s3) / (1 + s3 - sp.sqrt(2 + s3)), t1),
    ('2.073132', (s6 + s2) / (s6 + s2 - 2), t1),
    ('8.290859', 2 * sp.sin(sp.Rational(4, 9) * sp.pi) / (2 * sp.sin(sp.Rational(4, 9) * sp.pi)
                                                          - 2 * sp.sin(sp.Rational(3, 9) * sp.pi)), t1),
    ('1.2496', sp.sqrt(6 - 3 * s3 + 4 * s2 - 2 * s6), t2),
]
for txt, expr, src in NUM:
    # every number in the drafts is written as a TRUNCATION followed by dots, never as a
    # rounding, so the quoted digits must be a prefix of the true decimal expansion
    val = str(sp.N(expr, 30))
    ck('%s appears and is a truncation of the computed value' % txt,
       txt in src and val.startswith(txt), 'computed %s' % sp.N(expr, 12))
ck('the two closed forms given for delta(9) agree exactly',
   abs(sp.N((2 + s3) / (1 + s3 - sp.sqrt(2 + s3))
            - sp.sqrt(6 + 3 * s3 + 4 * s2 + 2 * s6), 80)) < sp.Float('1e-70', 80))
ck('delta(5) = (3+sqrt5)/2 = phi^2', sp.simplify((3 + s5) / 2 - ((1 + s5) / 2) ** 2) == 0
   and '(3+\\sqrt5)/2' in t1)
ck('delta(6) = 2+sqrt2 appears', '2+\\sqrt2' in t1)
ck('6+3sqrt3 = 3/(2-sqrt3) appears as the n = 11, 12 bound',
   sp.simplify(6 + 3 * s3 - 3 / (2 - s3)) == 0 and '6+3\\sqrt3' in t1)

print()
print('2. Piepmeyer\'s four distances, as quoted in the second draft')
d = [sp.sqrt(6 - 3 * s3 + 4 * s2 - 2 * s6), 1 + s2, 2 + s2, sp.sqrt(6 + 3 * s3 + 4 * s2 + 2 * s6)]
gaps = [sp.simplify(b - a) for a, b in zip(d, d[1:])]
ck('the middle gap is exactly 1', sp.simplify(gaps[1] - 1) == 0)
ck('the smallest gap is exactly 1', min(float(sp.N(g, 30)) for g in gaps) == 1.0)
ck('the smallest distance exceeds the smallest gap, so this is Kanold\'s hard case',
   float(sp.N(d[0], 30)) > 1.0, 'd_1 = %s' % sp.N(d[0], 12))
ck('the draft quotes 1+sqrt2 and 2+sqrt2 as the middle two distances',
   '1+\\sqrt2' in t2 and '2+\\sqrt2' in t2)

print()
print('3. The claims about attainment, against the stored classification')
e9 = json.load(open('results/e9_k4.json'))
e78 = json.load(open('results/e78_k4.json'))
best = 4.66390246014701
ck('delta(9) is attained by exactly one of the four 9-point 4-distance sets',
   sum(1 for v in e9['sets'].values() if abs(float(v['delta_num']) - best) < 1e-9) == 1)
for tag in ('E7', 'E8'):
    att = [r for r in e78[tag] if abs(float(r['delta']) - best) < 1e-9]
    ck('%s: every set attaining the minimum has Piepmeyer\'s distance ratios' % tag,
       att and all(abs(float(r['ratios'][1]) - float(sp.N(sp.sqrt(2 + s3), 20))) < 1e-9 and
                   abs(float(r['ratios'][2]) - float(sp.N(1 + s3, 20))) < 1e-9 and
                   abs(float(r['ratios'][3]) - float(sp.N(2 + s3, 20))) < 1e-9 for r in att),
       '%d attaining sets' % len(att))
ck('the first draft says the minimum is attained only by Piepmeyer and its subsets',
   'attained only by Piepmeyer' in t1)

print()
print('4. Bibliographic details, against REFERENCES.md')
ref = io.open('REFERENCES.md', encoding='utf-8').read()
BIB = [('Discrete Math. 160 (1996) 115-125', '160** (1996) 115-125', t1),
       ('Discrete Math. 308 (2008) 3048-3055', '308** (2008) 3048-3055', t1),
       ('Mat. Zametki 93 (2013) 492-508', '93**:4 (2013) 492-508', t1),
       ('European J. Combin. 25 (2004) 1039-1058', '25** (2004) 1039-1058', t1),
       ('Abh. Braunschw. Wiss. Ges. 32 (1981) 55-65', '32** (1981) 55-65', t1),
       ('Discrete Math. 150 (1996) 415-419', '150** (1996) 415-419', t2),
       ('Electron. J. Combin. 19 (2012) #P38', '19(4) (2012) #P38', t1)]
for shown, inref, src in BIB:
    ck('%s is cited in the draft and matches REFERENCES.md' % shown,
       shown.replace('#P38', '#P38') in src.replace('19 (2012) #P38', '19 (2012) #P38') and inref in ref,
       '' if inref in ref else 'not found in REFERENCES.md')

print()
print('5. Claims that must NOT be made')
ck('the drafts do not claim the page quotes the "smallest diameter" sentence',
   'page quotes' not in t1)
ck('the drafts do not claim priority over Brass',
   'only been able to see its abstract' in t2 or 'only its abstract' in t2)
ck('the count of 8-point sets is attributed to what the theorem allows, not to Shinohara',
   'fifteen' not in t1 or 'theorem allows' in t1)
ck('the caveat about the figure in Wei\'s classification is present',
   'only as a figure' in t1)
ck('nothing claims that Erdos 1995 mentions Erdos and Fishburn',
   'neither paper' not in t1)

print()
print('6. Formatting for the site')
for name, txt in (('draft 1', t1), ('draft 2', t2)):
    body = txt.split('---', 2)[-1]
    ck('%s: no markdown emphasis or headers in the body' % name,
       not re.search(r'^\s*#|\*\*', body, re.M))
    for m in re.finditer(r'\$\$(.+?)\$\$', body, re.S):
        ck('%s: display math is on a single line' % name, '\n' not in m.group(1),
           m.group(1)[:40])
    ck('%s: no LaTeX macro that the site may not define' % name,
       '\\text' not in body and '\\qquad' not in body and '\\begin' not in body)
    words = len(re.findall(r'\S+', body))
    print('     %s: %d words' % (name, words))
    ck('%s: under 450 words' % name, words < 450, '%d' % words)

print()
if FAIL:
    print('FAILED %d CHECK(S):' % len(FAIL))
    for f in FAIL:
        print('  -', f)
    sys.exit(1)
print('ALL COMMENT CHECKS PASSED')
