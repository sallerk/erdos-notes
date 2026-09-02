"""Decide ONE pattern with the Gram method. Run as a separate process so the driver can
impose a hard wall-clock timeout; sympy.solve has no interruptible timeout on Windows.

Usage: python decide1.py <n> <k> <comma-separated pattern>
Prints one line: sat|unsat|inconclusive|error  <detail>
"""
import sys, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from gram import decide
n = int(sys.argv[1]); k = int(sys.argv[2])
pat = tuple(int(x) for x in sys.argv[3].split(','))
try:
    r, vv, pts = decide(pat, n, k)
    print(json.dumps({'r': r, 'vals': str(vv) if vv is not None else None,
                      'pts': str(pts) if pts else None}))
except Exception as ex:
    print(json.dumps({'r': 'error', 'vals': repr(ex)[:300], 'pts': None}))
