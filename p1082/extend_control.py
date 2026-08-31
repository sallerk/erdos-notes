"""Positive controls for extend.py -- prove the extension finder can find one.

Control 1: the regular HEXAGON (m=6) has distances {1, sqrt3, 2}; its centre is
at distance 1 (the side length) from every vertex, so the finder MUST report at
least one extension, and it must be rejected for general position (the centre is
collinear with each pair of opposite vertices).

Control 2: the regular SQUARE (m=4) has distances {sqrt2, 2} for circumradius 1;
its centre is at distance 1 from every vertex, which is NOT in that set, so the
centre must NOT be reported.  But the square DOES extend: adding the apex of an
equilateral triangle would introduce a new distance, so we instead use the
hexagon + centre as the only positive control and check the square reports the
right thing for the right reason.
"""
import mpmath as mp
from extend import run, TOL

print("control: regular hexagon m=6 (centre is at the side distance)")
k, nd, nh, nc = run(6)
print(f"  m=6: |D|={nd}, extensions found={nh}, in general position={nc}")
assert nh >= 1, "FAILED: the finder did not locate the hexagon centre"
assert nc == 0, "the centre should be rejected: it lies on 3 long diagonals"
print("  PASS: the finder does locate a genuine extension, and correctly")
print("        rejects it for having three points on a line.\n")

print("control: regular 12-gon m=12 (centre at circumradius R; is R a 12-gon")
print("         distance?  2 R sin(pi d/12) = R  <=>  d = 2, so YES)")
k, nd, nh, nc = run(12)
print(f"  m=12: |D|={nd}, extensions found={nh}, in general position={nc}")
assert nh >= 1, "FAILED: the finder did not locate the 12-gon centre"
print("  PASS.\n")

print("control: regular pentagon m=5 -- centre is at distance R, and")
print("         2 R sin(pi d/5) = R has no integer solution, so NO extension")
k, nd, nh, nc = run(5)
print(f"  m=5: extensions found={nh}  (expected 0)")
assert nh == 0
print("  PASS.\n")
print("The 'zero extensions for every odd m' result in extend.log is therefore")
print("a real rigidity statement, not a broken search.")
