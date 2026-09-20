#!/usr/bin/env python3
"""Grow exact-ring balls (Minkowski powers of the hexagon seed rotated by cos 5/6, 7/8) and test
4-colorability with CaDiCaL. UNSAT = a 5-chromatic unit-distance graph built from scratch."""
import sys, time
from bichromatic_search import build_universe
from surgery import exact_unit_edges
from pysat.solvers import Cadical153
depth=int(sys.argv[1]); nb=float(sys.argv[2]); k=int(sys.argv[3]) if len(sys.argv)>3 else 4
t0=time.time(); U=build_universe(depth,nb); E=exact_unit_edges(U); n=len(U)
print("depth=%d norm<=%g: |V|=%d |E|=%d  (built in %.0fs)"%(depth,nb,n,len(E),time.time()-t0),flush=True)
import pickle; pickle.dump((U,E),open("notes/ball_d%d_n%g.pkl"%(depth,nb),"wb"))
var=lambda v,c: v*k+c+1
cl=[[var(v,c) for c in range(k)] for v in range(n)]
for a,b in E:
    for c in range(k): cl.append([-var(a,c),-var(b,c)])
adj={}
for a,b in E: adj.setdefault(a,set()).add(b); adj.setdefault(b,set()).add(a)
for a,b in E:
    com=adj[a]&adj[b]
    if com: 
        for c,v in enumerate((a,b,min(com))): cl.append([var(v,c)])
        break
s=Cadical153(bootstrap_with=cl, with_proof=True); t1=time.time(); r=s.solve()
print("%d-colorable: %s  (solve %.0fs)"%(k,r,time.time()-t1),flush=True)
if r is False:
    pr=s.get_proof(); open("notes/ball_d%d_k%d.drat"%(depth,k),"w").write("\n".join(pr)+"\n")
    open("notes/ball_d%d_k%d.cnf"%(depth,k),"w").write("p cnf %d %d\n"%(n*k,len(cl))+"".join(" ".join(map(str,c))+" 0\n" for c in cl))
    print("DRAT written: %d lines"%len(pr),flush=True)
s.delete()
