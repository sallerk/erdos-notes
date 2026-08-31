"""Independent exact verifier, sharing no code with crescent.c.
Reads 'SOLUTION (a,b) (a,b) ...' lines, checks in exact integer/Fraction arithmetic:
  * no three collinear, * no four concyclic,
  * exactly n-1 distinct distances,
  * multiplicities are exactly the multiset {1,...,n-1}.
Uses the embedding (a,b) -> a*(1,0) + b*(1/2, sqrt3/2), i.e. x = a + b/2, y = b*sqrt3/2.
To stay exact, works with X = 2a+b and Y = b, so x = X/2 and y = Y*sqrt3/2.
"""
import sys, re
from fractions import Fraction as F
from itertools import combinations
from collections import Counter

def check(pts, verbose=False):
    n = len(pts)
    X = [2*a+b for a,b in pts]; Y = [b for a,b in pts]
    N = [a*a+a*b+b*b for a,b in pts]
    # squared distance, exact integer
    def d2(i,j):
        p = pts[i][0]-pts[j][0]; q = pts[i][1]-pts[j][1]
        return p*p+p*q+q*q
    # collinear: det[[X,Y,1]] == 0   (columns scaled by 2 and 2/sqrt3; scaling cannot
    # change vanishing)
    for i,j,k in combinations(range(n),3):
        det = (X[j]-X[i])*(Y[k]-Y[i]) - (Y[j]-Y[i])*(X[k]-X[i])
        if det == 0: return False,'collinear %s'%str((i,j,k))
    # concyclic: det[[N,X,Y,1]] == 0
    for q4 in combinations(range(n),4):
        M=[[N[i],X[i],Y[i],1] for i in q4]
        d=0
        for r in range(4):
            sub=[row[:3] for s,row in enumerate(M) if s!=r]
            v=(sub[0][0]*(sub[1][1]*sub[2][2]-sub[1][2]*sub[2][1])
              -sub[0][1]*(sub[1][0]*sub[2][2]-sub[1][2]*sub[2][0])
              +sub[0][2]*(sub[1][0]*sub[2][1]-sub[1][1]*sub[2][0]))
            d += (1 if r%2 else -1)*v
        if d == 0: return False,'concyclic %s'%str(q4)
    c = Counter(d2(i,j) for i,j in combinations(range(n),2))
    if len(c) != n-1: return False,'got %d distinct distances, want %d'%(len(c),n-1)
    if sorted(c.values()) != list(range(1,n)): return False,'multiplicities %s'%sorted(c.values())
    if verbose:
        print('   distances (squared -> multiplicity):', dict(sorted(c.items())))
    return True,'OK'

if __name__=='__main__':
    fn=sys.argv[1]; lim=int(sys.argv[2]) if len(sys.argv)>2 else 5
    lines=[l for l in open(fn) if l.startswith('SOLUTION')]
    print('%s: %d solution lines'%(fn,len(lines)))
    ok=bad=0
    for idx,l in enumerate(lines[:lim]):
        pts=[tuple(map(int,m)) for m in re.findall(r'\((-?\d+),(-?\d+)\)',l)]
        good,msg=check(pts, verbose=(idx==0))
        if good: ok+=1
        else: bad+=1; print('   FAIL:',msg,pts)
    print('   verified %d, failed %d (of first %d)'%(ok,bad,min(lim,len(lines))))
