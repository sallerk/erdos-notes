"""Verify the CIRCUMRADIUS IDENTITY symbolically, then test it as a redundant
lemma for the solver.

If v_i is equidistant (distance r) from v_j,v_k,v_l then r is the circumradius of
triangle jkl.  With a^2=D_jk, b^2=D_kl, c^2=D_jl and R^2=D_ij, from R = abc/(4A)
and 16A^2 = 2a^2b^2+2b^2c^2+2c^2a^2-a^4-b^4-c^4 (Heron) we get a relation that is
POLYNOMIAL IN SQUARED DISTANCES ALONE, with no coordinates:

    D_ij * (2 D_jk D_kl + 2 D_kl D_jl + 2 D_jl D_jk - D_jk^2 - D_kl^2 - D_jl^2)
        = D_jk * D_kl * D_jl

It is implied by the coordinate equations, so adding it changes nothing
logically -- but it may give nlsat a much shorter refutation.
"""
import sympy as sp

# ---- symbolic proof of the identity from coordinates -----------------------
xi,yi,xj,yj,xk,yk,xl,yl = sp.symbols('xi yi xj yj xk yk xl yl', real=True)
P = {'i':(xi,yi),'j':(xj,yj),'k':(xk,yk),'l':(xl,yl)}
D = lambda a,b: (P[a][0]-P[b][0])**2 + (P[a][1]-P[b][1])**2
Dij, Djk, Dkl, Djl = D('i','j'), D('j','k'), D('k','l'), D('j','l')
lhs = Dij*(2*Djk*Dkl + 2*Dkl*Djl + 2*Djl*Djk - Djk**2 - Dkl**2 - Djl**2)
rhs = Djk*Dkl*Djl
# under the hypotheses D_ij = D_ik = D_il, substitute yi,xi by solving the two
# linear perpendicular-bisector equations, then check lhs-rhs vanishes.
e1 = sp.expand(D('i','j') - D('i','k'))
e2 = sp.expand(D('i','k') - D('i','l'))
sol = sp.solve([e1,e2],[xi,yi], dict=True)
print("solved circumcentre:", len(sol), "solution(s)")
s = sol[0]
diff = sp.simplify(sp.together(sp.expand((lhs-rhs).subs(s))))
print("lhs - rhs under the equidistance hypotheses simplifies to:", diff)
assert diff == 0, diff
print("IDENTITY VERIFIED SYMBOLICALLY (exact, over Q)")

# ---- numeric cross-check on Danzer's 9-gon --------------------------------
import json
d=json.load(open('danzer_ccw.json')); pts=d['ccw_points']; n=9
tri={int(k):v for k,v in d['ccw_triples'].items()}
dd=lambda a,b:(pts[a][0]-pts[b][0])**2+(pts[a][1]-pts[b][1])**2
worst=0
for i in range(n):
    j,k,l = sorted(tri[i], key=lambda x:(x-i)%n)
    A=dd(j,k); B=dd(k,l); C=dd(j,l); R=dd(i,j)
    v = R*(2*A*B+2*B*C+2*C*A-A*A-B*B-C*C) - A*B*C
    worst=max(worst,abs(v)/max(1e-9,abs(A*B*C)))
print(f"Danzer 9-gon: max relative residual of the identity = {worst:.3e}")
