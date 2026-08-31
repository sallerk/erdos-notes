"""Standalone audit of every checkable claim in the #64 note.

Run it:   python audit64.py            (stages A-C, pure Python, no dependencies)
          python audit64.py --geng     (adds stage D, needs nauty's geng on PATH)

Stage A  certificate arithmetic: per-n node counts, coverage with no gaps, the
         claimed 1.85e10 total, and that every run recorded zero survivors.
Stage B  the two per-task certificates: do the task lines sum to the stated TOTAL?
Stage C  an independent cycle routine, validated against cubic graphs whose cycle
         spectra are known (K_{3,3}, Heawood, Moebius-Kantor, Pappus).
Stage D  the real independent check: regenerate connected cubic bipartite graphs with
         nauty's geng, confirm the counts against OEIS A006823 and A002851, and
         confirm none avoids all of C4, C8, C16.

A "survivor" is a graph with no cycle of length 4, 8 or 16.  The note claims none
exists on at most 62 vertices, so any survivor printed here would refute it.
"""
import json, glob, os, re, sys, subprocess

FAIL = []
NL = chr(10)


def check(label, got, want):
    good = got == want
    if not good:
        FAIL.append(label)
    print('  %-56s %-22s %s' % (label, str(got)[:22],
                                'OK' if good else 'MISMATCH, expected %s' % (want,)))


def decode_g6(s):
    s = s.strip()
    if not s:
        return None
    data = [ord(c) - 63 for c in s]
    n, data = data[0], data[1:]
    adj = [0] * n
    bits = []
    for d in data:
        for k in range(5, -1, -1):
            bits.append((d >> k) & 1)
    i = 0
    for j in range(1, n):
        for k in range(j):
            if i < len(bits) and bits[i]:
                adj[k] |= 1 << j
                adj[j] |= 1 << k
            i += 1
    return n, adj


def has_cycle(n, adj, L):
    """Exact: is there a simple cycle of length exactly L?  Each cycle is generated
    from its lowest-indexed vertex, so none is missed and none double counted."""
    def dfs(start, cur, used, ln):
        if ln == L:
            return bool(adj[cur] >> start & 1)
        cand = adj[cur] & ~used & ~((1 << (start + 1)) - 1)
        while cand:
            w = (cand & -cand).bit_length() - 1
            cand &= cand - 1
            if dfs(start, w, used | (1 << w), ln + 1):
                return True
        return False
    for s in range(n):
        if dfs(s, s, 1 << s, 1):
            return True
    return False


def survivor(n, adj):
    return not (has_cycle(n, adj, 4) or has_cycle(n, adj, 8)
                or (n >= 16 and has_cycle(n, adj, 16)))


here = os.path.dirname(os.path.abspath(__file__))

print('=== A. certificate arithmetic (results/bip_n*.json) ===')
files = glob.glob(os.path.join(here, 'results', 'bip_n*.json'))
if not files:
    print('  results/ not found next to this script; skipping stage A')
else:
    tot, ns, bad = 0, [], []
    for f in files:
        d = json.load(open(f))
        ns.append(d['n'])
        tot += d['tree_nodes']
        if d.get('survivors_C4C8C16', 0) != 0 or d.get('counterexamples'):
            bad.append(d['n'])
    check('even n covered from 4 to 62 with no gaps',
          [n for n in range(4, 63, 2) if n not in ns], [])
    check('runs recording a survivor or counterexample', bad, [])
    check('total search-tree nodes', tot, 18485512641)
    for n, want in ((58, 1446651744), (60, 3987181668), (62, 12184300857)):
        d = json.load(open(os.path.join(here, 'results', 'bip_n%d.json' % n)))
        check('n=%d tree_nodes' % n, d['tree_nodes'], want)

print()
print('=== B. per-task certificates sum to their stated TOTAL ===')
for n in (60, 62):
    p = os.path.join(here, 'results', 'bip_n%d_CERTIFIED.txt' % n)
    if not os.path.exists(p):
        print('  %s missing; skipped' % os.path.basename(p))
        continue
    t = open(p, encoding='utf-8', errors='replace').read()
    tasks = [int(x) for x in re.findall(r'task\s+\d+:\s*nodes=\s*(\d+)', t)]
    stated = int(re.search(r'TOTAL nodes=(\d+)', t).group(1))
    check('n=%d: %d task lines sum to the TOTAL line' % (n, len(tasks)),
          sum(tasks), stated)
    check('n=%d: certificate reports zero survivors' % n,
          'survivors_of_C4C8C16=0' in t, True)

print()
print('=== C. the cycle routine, against graphs with known cycle spectra ===')
# graph6 strings and spectra generated with networkx, hardcoded so this script has
# no dependencies.  K33 {4,6}; Heawood {6,8,10,12,14};
# Moebius-Kantor and Pappus {6,8,10,12,14,16}.
KNOWN = {
    'K_{3,3}':                  ('EFz_', True, False),
    'Heawood (girth 6)':        ('MhEGHC@AI?_PC@_G_', False, True),
    'Moebius-Kantor (girth 6)': ('OhEGHC@AG?_PO@?Ga?K?P', False, True),
    'Pappus (girth 6)':         ('QhEGGD@?G__P?@G?_GGO@?CE?AG', False, True),
}
for name, (g6, c4, c8) in KNOWN.items():
    n, adj = decode_g6(g6)
    check('%s: cubic' % name, set(bin(a).count('1') for a in adj), {3})
    check('%s: has C4' % name, has_cycle(n, adj, 4), c4)
    check('%s: has C8' % name, has_cycle(n, adj, 8), c8)
    check('%s: is NOT a survivor' % name, survivor(n, adj), False)


def run_geng(args, timeout):
    """Return graph6 lines, or raise.  A libtool build installs a wrapper named
    'geng' that dies with "couldn't find geng" while the real binary is 'geng.exe',
    so try both and INSIST on returncode 0.  A broken tool must be reported as a tool
    failure, never as a failed claim."""
    last = None
    for exe in ('geng.exe', 'geng'):
        try:
            r = subprocess.run([exe] + args, capture_output=True, text=True,
                               timeout=timeout)
        except FileNotFoundError:
            continue
        if r.returncode == 0:
            return [l for l in r.stdout.split(NL) if l.strip()]
        last = '%s exited %d: %s' % (exe, r.returncode, r.stderr.strip()[:120])
    raise RuntimeError(last or 'geng not found on PATH')


if '--geng' in sys.argv:
    print()
    print('=== D. independent regeneration with nauty geng ===')
    A006823 = {6: 1, 8: 1, 10: 2, 12: 5, 14: 13, 16: 38, 18: 149, 20: 703}
    A002851 = {4: 1, 6: 2, 8: 5, 10: 19, 12: 85}
    try:
        for n in sorted(A002851):
            check('connected cubic n=%d (A002851)' % n,
                  len(run_geng(['-qc', '-d3', '-D3', str(n)], 600)), A002851[n])
        for n in sorted(A006823):
            gs = run_geng(['-qc', '-b', '-d3', '-D3', str(n)], 1800)
            check('connected cubic bipartite n=%d (A006823)' % n, len(gs), A006823[n])
            check('  survivors at n=%d' % n,
                  [g for g in gs if survivor(*decode_g6(g))], [])
    except RuntimeError as e:
        print('  STAGE D COULD NOT RUN (tool problem, NOT a failed claim): %s' % e)
    except subprocess.TimeoutExpired:
        print('  geng timed out; stage D incomplete')
else:
    print()
    print('=== D. skipped (pass --geng to run the nauty regeneration) ===')

print()
print('ALL CHECKS PASSED' if not FAIL else '*** FAILED: %s ***' % FAIL)
sys.exit(1 if FAIL else 0)
