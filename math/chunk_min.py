#!/usr/bin/env python3
"""Chunked vertex deletion with fresh pinned solves on a float point set (edges from the translate union).
UNKNOWN = keep. Usage: chunk_min.py <edgefile> <xyfile> <budget> <out.xy>"""
import sys, math, time
from pysat.solvers import Cadical153
from star_on_graph import load_edges
edgefile,xyfile,budget,out=sys.argv[1],sys.argv[2],int(sys.argv[3]),sys.argv[4]
allxy=[tuple(map(float,l.split())) for l in open(edgefile+".xy")]; n,E=load_edges(edgefile)
key={(round(x,7),round(y,7)):i for i,(x,y) in enumerate(allxy)}
cur=[key[(round(x,7),round(y,7))] for x,y in (tuple(map(float,l.split())) for l in open(xyfile))]
adjall={}
for a,b in E: adjall.setdefault(a,set()).add(b); adjall.setdefault(b,set()).add(a)
k=4
def unsat(vs):
    vset=set(vs); idx={v:i for i,v in enumerate(vs)}; var=lambda u,c: u*k+c+1
    cl=[[var(u,c) for c in range(k)] for u in range(len(vs))]
    Es=[(idx[a],idx[b]) for a in vs for b in adjall.get(a,()) if b in vset and a<b]
    for a,b in Es:
        for c in range(k): cl.append([-var(a,c),-var(b,c)])
    for a,b in Es:
        com=[w for w in adjall[vs[a]] if w in vset and w in adjall[vs[b]]]
        if com:
            for c,u in enumerate((a,b,idx[min(com)])): cl.append([var(u,c)])
            break
    s=Cadical153(bootstrap_with=cl); s.conf_budget(budget); r=s.solve_limited(); s.delete(); return r is False
t0=time.time(); assert unsat(cur), "start not UNSAT within budget"
order=sorted(cur,key=lambda v:-math.hypot(*allxy[v])); chunk=max(1,len(cur)//32)
while chunk>=1:
    pos=0
    while pos<len(order):
        block=set(u for u in order[pos:pos+chunk] if u in set(cur))
        if block:
            trial=[u for u in cur if u not in block]
            if unsat(trial): cur=trial
        pos+=chunk
    print("chunk %d pass: %d vertices (%.0fs)"%(chunk,len(cur),time.time()-t0),flush=True)
    if chunk==1: break
    chunk//=2
    if time.time()-t0>3.5*3600: print("time cap reached",flush=True); break
assert unsat(cur)
print("final: %d vertices, radius %.4f (%.0fs)"%(len(cur),max(math.hypot(*allxy[v]) for v in cur),time.time()-t0),flush=True)
open(out,"w").write("".join("%.15f %.15f\n"%allxy[v] for v in cur)); print("wrote",out,flush=True)
