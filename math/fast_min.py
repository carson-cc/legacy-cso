#!/usr/bin/env python3
"""Fast minimization of a non-4-colorable point set: one incremental CaDiCaL instance with a selector
per vertex (assumed true = vertex deleted). Steps: (1) radius restriction by binary search;
(2) chunked deletion, halving chunk size on failure; UNKNOWN (budget) means keep.
Usage: fast_min.py <edgefile> <r_in> <r_out> <core.cnf|none> <out.xy>"""
import sys, math, time
from pysat.solvers import Cadical153
from star_on_graph import load_edges
edgefile,r_in,r_out,corefile,out=sys.argv[1],float(sys.argv[2]),float(sys.argv[3]),sys.argv[4],sys.argv[5]
xy=[tuple(map(float,l.split())) for l in open(edgefile+".xy")]; n,E=load_edges(edgefile)
keep=[i for i,(x,y) in enumerate(xy) if r_in<math.hypot(x,y)<r_out]; idx={v:i for i,v in enumerate(keep)}
E2=[(idx[a],idx[b]) for a,b in E if a in idx and b in idx]; m=len(keep); k=4
alive=set(range(m))
if corefile!="none":
    cv=set()
    for line in open(corefile):
        if line[0] in "cp": continue
        for lit in line.split():
            if lit!="0": cv.add((abs(int(lit))-1)//k)
    alive={v for v in cv if v<m}
var=lambda u,c: u*k+c+1; sel=lambda u: m*k+u+1
cl=[[var(u,c) for c in range(k)]+[sel(u)] for u in range(m)]
for a,b in E2:
    for c in range(k): cl.append([-var(a,c),-var(b,c)])
s=Cadical153(bootstrap_with=cl)
def unsat(aliveset,budget=400000):
    assum=[(sel(u) if u not in aliveset else -sel(u)) for u in range(m)]
    s.conf_budget(budget); r=s.solve_limited(assumptions=assum); return r is False
t0=time.time(); assert unsat(alive,5000000), "start set not proven UNSAT"
print("start: %d alive vertices, UNSAT confirmed (%.0fs)"%(len(alive),time.time()-t0),flush=True)
rad={u:math.hypot(*xy[keep[u]]) for u in range(m)}
# (1) radius restriction
radii=sorted(set(round(rad[u],4) for u in alive)); lo,hi=0,len(radii)-1; best=None
while lo<=hi:
    mid=(lo+hi)//2; r=radii[mid]; trial={u for u in alive if rad[u]<=r+1e-9}
    if unsat(trial,1500000): best=r; hi=mid-1
    else: lo=mid+1
if best is not None: alive={u for u in alive if rad[u]<=best+1e-9}; print("radius restricted to %.4f: %d vertices (%.0fs)"%(best,len(alive),time.time()-t0),flush=True)
# (2) chunked deletion, outermost first
order=sorted(alive,key=lambda u:-rad[u]); chunk=max(1,len(order)//16); pos=0
while chunk>=1:
    pos=0; progress=False
    while pos<len(order):
        block=[u for u in order[pos:pos+chunk] if u in alive]
        if block:
            trial=alive-set(block)
            if unsat(trial): alive=trial; progress=True
        pos+=chunk
    print("chunk %d done: %d vertices (%.0fs)"%(chunk,len(alive),time.time()-t0),flush=True)
    if chunk==1: break
    chunk=max(1,chunk//2)
assert unsat(alive,5000000)
Es=[(a,b) for a,b in E2 if a in alive and b in alive]
print("minimized: %d vertices, %d edges, radius %.4f (%.0fs)"%(len(alive),len(Es),max(rad[u] for u in alive),time.time()-t0),flush=True)
with open(out,"w") as f:
    for u in sorted(alive): f.write("%.15f %.15f\n"%xy[keep[u]])
print("wrote",out)
