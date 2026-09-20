#!/usr/bin/env python3
"""Export a pinned 4-coloring DIMACS CNF for a disc/annulus subset of an edge file, optionally restricted
to the points of an .xy file. Usage: export_cnf.py <edgefile> <r_in> <r_out> <out.cnf> [subset.xy]"""
import sys, math
from star_on_graph import load_edges
edgefile,r_in,r_out,out=sys.argv[1],float(sys.argv[2]),float(sys.argv[3]),sys.argv[4]
xy=[tuple(map(float,l.split())) for l in open(edgefile+".xy")]; n,E=load_edges(edgefile)
keep=[i for i,(x,y) in enumerate(xy) if r_in<math.hypot(x,y)<r_out]
if len(sys.argv)>5:
    key={(round(x,7),round(y,7)):i for i,(x,y) in enumerate(xy)}
    sub={key[(round(x,7),round(y,7))] for x,y in (tuple(map(float,l.split())) for l in open(sys.argv[5]))}
    keep=[i for i in keep if i in sub]
idx={v:i for i,v in enumerate(keep)}; E2=[(idx[a],idx[b]) for a,b in E if a in idx and b in idx]
m=len(keep); k=4; var=lambda u,c: u*k+c+1
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
with open(out,"w") as f:
    f.write("p cnf %d %d\n"%(m*k,len(cl)))
    for c in cl: f.write(" ".join(map(str,c))+" 0\n")
print("%s: |V|=%d |E|=%d vars=%d clauses=%d"%(out,m,len(E2),m*k,len(cl)))
