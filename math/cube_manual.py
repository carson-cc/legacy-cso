#!/usr/bin/env python3
"""Manual cubes for a k-coloring CNF (variables v*k+c+1): choose the s highest-degree vertices of the
graph (from the edge file, restricted the same way export_cnf.py did), enumerate colour assignments
consistent with the edges among them, and write icnf cubes ('a lits 0'). The pin (units in the CNF)
is respected by unit-propagating the CNF's unit clauses first.
Usage: cube_manual.py <edgefile> <r_in> <r_out> <cnf> <s> <out.icnf> [subset.xy]"""
import sys, math, itertools
from star_on_graph import load_edges
edgefile,r_in,r_out,cnf,s,out=sys.argv[1],float(sys.argv[2]),float(sys.argv[3]),sys.argv[4],int(sys.argv[5]),sys.argv[6]
xy=[tuple(map(float,l.split())) for l in open(edgefile+".xy")]; n,E=load_edges(edgefile)
keep=[i for i,(x,y) in enumerate(xy) if r_in<math.hypot(x,y)<r_out]
if len(sys.argv)>7:
    key={(round(x,7),round(y,7)):i for i,(x,y) in enumerate(xy)}
    sub={key[(round(x,7),round(y,7))] for x,y in (tuple(map(float,l.split())) for l in open(sys.argv[7]))}
    keep=[i for i in keep if i in sub]
idx={v:i for i,v in enumerate(keep)}; E2=[(idx[a],idx[b]) for a,b in E if a in idx and b in idx]
k=4; var=lambda u,c: u*k+c+1
deg=[0]*len(keep)
for a,b in E2: deg[a]+=1; deg[b]+=1
units={}
for line in open(cnf):
    t=line.split()
    if t and t[0] not in ('p','c') and len(t)==2:
        lit=int(t[0]); units[(abs(lit)-1)//k]=(abs(lit)-1)%k if lit>0 else None
pinned=[u for u,c in units.items() if c is not None]
cand=[u for u in sorted(range(len(keep)),key=lambda u:-deg[u]) if u not in units][:s]
adj={u:set() for u in range(len(keep))}
for a,b in E2: adj[a].add(b); adj[b].add(a)
fixed={u:c for u,c in units.items() if c is not None}
cubes=[]
for cols in itertools.product(range(k),repeat=len(cand)):
    asg=dict(fixed); asg.update(zip(cand,cols)); ok=True
    for u in cand:
        for w in adj[u]:
            if w in asg and asg[w]==asg[u]: ok=False; break
        if not ok: break
    if ok: cubes.append([var(u,asg[u]) for u in cand])
with open(out,"w") as f:
    for c in cubes: f.write("a "+" ".join(map(str,c))+" 0\n")
print("split vertices %s (degrees %s); cubes: %d"%(cand,[deg[u] for u in cand],len(cubes)))
