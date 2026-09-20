#!/usr/bin/env python3
"""Is the unit-distance graph on the union points inside the annulus {r_in < |x| < r_out} 4-colorable?
UNSAT => a 5-chromatic UDG lives in that annulus (float edges; certify exactly if it happens)."""
import sys, math, time
from pysat.solvers import Cadical153
from star_on_graph import load_edges
edgefile=sys.argv[1]; r_in=float(sys.argv[2]); r_out=float(sys.argv[3]); budget=int(sys.argv[4]) if len(sys.argv)>4 else 5000000
xy=[tuple(map(float,l.split())) for l in open(edgefile+".xy")]; n,E=load_edges(edgefile)
keep=[i for i,(x,y) in enumerate(xy) if r_in<math.hypot(x,y)<r_out]; idx={v:i for i,v in enumerate(keep)}
E2=[(idx[a],idx[b]) for a,b in E if a in idx and b in idx]; m=len(keep); k=4; var=lambda u,c: u*k+c+1
cl=[[var(u,c) for c in range(k)] for u in range(m)]
for a,b in E2:
    for c in range(k): cl.append([-var(a,c),-var(b,c)])
adj={}
for a,b in E2: adj.setdefault(a,set()).add(b); adj.setdefault(b,set()).add(a)
for a,b in E2:
    com=adj[a]&adj[b]
    if com:
        for c,u in enumerate((a,b,min(com))): cl.append([var(u,c)])
        break
solver=sys.argv[5] if len(sys.argv)>5 else "cadical"
if solver=="glucose":
    from pysat.solvers import Glucose4
    s=Glucose4(bootstrap_with=cl); s.conf_budget(budget); t=time.time(); r=s.solve_limited(); pr=None; s.delete()
else:
    s=Cadical153(bootstrap_with=cl,with_proof=True); s.conf_budget(budget); t=time.time(); r=s.solve_limited()
    pr=s.get_proof() if r is False else None; s.delete()
if r is False and pr is not None:
    tag="disc_%s_%g_%g"%(edgefile.split('/')[-1].split('.')[0],r_in,r_out)
    open("notes/%s.cnf"%tag,"w").write("p cnf %d %d\n"%(m*k,len(cl))+"".join(" ".join(map(str,c))+" 0\n" for c in cl))
    open("notes/%s.drat"%tag,"w").write("\n".join(pr)+"\n"); print("DRAT written: notes/%s.drat (%d lines)"%(tag,len(pr)),flush=True)
print("annulus (%.3f, %.3f) of %s: |V|=%d |E|=%d  4-colorable: %s (%.0fs)"%(r_in,r_out,edgefile.split('/')[-1],m,len(E2),{True:'SAT',False:'UNSAT',None:'UNKNOWN'}[r],time.time()-t),flush=True)
