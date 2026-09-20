#!/usr/bin/env python3
"""Independent re-verification of an eps-UDG lattice-patch verdict.
 - edges recomputed EXACTLY: lattice point (i,j) -> coordinates s*(i+j/2, j*sqrt3/2);
   squared distance = s^2 * (di^2 + di*dj + dj^2) with integer N = di^2+di*dj+dj^2;
   edge iff (1-eps)^2 < s^2*N < (1+eps)^2, tested with Fractions (s, eps rational).
 - solved with Glucose4 (different solver), NO symmetry breaking.
 - solved again with CaDiCaL emitting a DRAT proof; DIMACS + proof written to notes/.
"""
import sys, math
from fractions import Fraction as Fr
from pysat.solvers import Glucose4, Cadical153
s=Fr(sys.argv[1]); R=Fr(sys.argv[2]); eps=Fr(sys.argv[3]); k=int(sys.argv[4])
n=int(R/s)+2; pts=[]
for i in range(-n,n+1):
    for j in range(-n,n+1):
        # |p|^2 = s^2 (i^2 + i j + j^2) <= R^2  exactly
        if s*s*(i*i+i*j+j*j) <= R*R: pts.append((i,j))
lo=(1-eps)**2; hi=(1+eps)**2
edges=[]
for a in range(len(pts)):
    for b in range(a+1,len(pts)):
        di=pts[a][0]-pts[b][0]; dj=pts[a][1]-pts[b][1]
        d2=s*s*(di*di+di*dj+dj*dj)
        if lo<d2<hi: edges.append((a,b))
V=len(pts); var=lambda v,c: v*k+c+1
cl=[[var(v,c) for c in range(k)] for v in range(V)]
for a,b in edges:
    for c in range(k): cl.append([-var(a,c),-var(b,c)])
g=Glucose4(bootstrap_with=cl); r1=g.solve(); g.delete()
c=Cadical153(bootstrap_with=cl, with_proof=True); r2=c.solve()
proof=c.get_proof() if not r2 else None; c.delete()
tag="s%s_R%s_eps%s_k%d"%(sys.argv[1],sys.argv[2],sys.argv[3],k)
print("exact edges: |V|=%d |E|=%d   Glucose4(no symbreak)=%s   CaDiCaL=%s"%(V,len(edges),r1,r2))
if proof is not None:
    with open("notes/%s.cnf"%tag,"w") as f:
        f.write("p cnf %d %d\n"%(V*k,len(cl)))
        for c_ in cl: f.write(" ".join(map(str,c_))+" 0\n")
    with open("notes/%s.drat"%tag,"w") as f:
        for line in proof: f.write(line+"\n")
    print("wrote notes/%s.cnf and .drat (%d proof lines)"%(tag,len(proof)))
