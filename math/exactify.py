#!/usr/bin/env python3
"""Turn a float point list (points of the translate union, i.e. p - g for exact 510 vertices p, g) into
exact coordinates, recompute the exact unit-distance graph, re-prove non-4-colorability with a fresh
CaDiCaL run + DRAT, and check the proof with drat-trim.  Usage: exactify.py <xyfile> <vtx> <drat-trim>"""
import sys, math, subprocess
from udg import F, P
from vtx_exact import parse_vtx_exact
from surgery import exact_unit_edges
from pysat.solvers import Cadical153
xyfile,vtx,DT=sys.argv[1],sys.argv[2],sys.argv[3]
G=parse_vtx_exact(vtx); Gf=[p.to_float() for p in G]
pts=[tuple(map(float,l.split())) for l in open(xyfile)]
# index differences p - g by rounded float
diff={}
for i,(px,py) in enumerate(Gf):
    for j,(gx,gy) in enumerate(Gf):
        diff.setdefault((round(px-gx,7),round(py-gy,7)),(i,j))
exact=[]
for (x,y) in pts:
    key=(round(x,7),round(y,7)); assert key in diff, "point not a difference of 510 vertices: %r"%(key,)
    i,j=diff[key]; exact.append(G[i]-G[j])
E=exact_unit_edges(exact); n=len(exact)
print("exact points: %d, exact unit edges: %d"%(n,len(E)),flush=True)
k=4; var=lambda u,c: u*k+c+1
cl=[[var(u,c) for c in range(k)] for u in range(n)]
for a,b in E:
    for c in range(k): cl.append([-var(a,c),-var(b,c)])
adj={}
for a,b in E: adj.setdefault(a,set()).add(b); adj.setdefault(b,set()).add(a)
for a,b in E:                       # symmetry pin: one triangle gets colours 0,1,2 (valid up to colour permutation)
    com=adj[a]&adj[b]
    if com:
        for c,u in enumerate((a,b,min(com))): cl.append([var(u,c)])
        break
s=Cadical153(bootstrap_with=cl,with_proof=True); r=s.solve(); pr=s.get_proof() if not r else None; s.delete()
print("4-colorable (exact graph): %s"%r,flush=True)
if r is False:
    base=xyfile.rsplit('.',1)[0]
    open(base+".cnf","w").write("p cnf %d %d\n"%(n*k,len(cl))+"".join(" ".join(map(str,c))+" 0\n" for c in cl))
    open(base+".drat","w").write("\n".join(pr)+"\n")
    out=subprocess.run([DT,base+".cnf",base+".drat"],capture_output=True,text=True).stdout
    print("drat-trim:", [l for l in out.splitlines() if l.startswith("s ")], "(%d proof lines)"%len(pr),flush=True)
    with open(base+"_exact.txt","w") as f:
        f.write("# exact coordinates (udg.F repr); edges = all pairs at exact unit distance\n")
        for p in exact: f.write("%r\n"%p)
    print("wrote", base+"_exact.txt")
