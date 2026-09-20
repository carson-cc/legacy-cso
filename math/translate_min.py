#!/usr/bin/env python3
"""Shrink the radius-R translate-union graph by removing whole translates G - g (g a vertex of G).
Vertex set for an active set S of translates: union over g in S of (G - g) intersected with |x| < R.
Chunked removal (outer translates first... order by |g|), fresh budgeted solves; UNKNOWN = keep.
Usage: translate_min.py <vtx> <R> <budget> <out.xy>"""
import sys, math, time
from pysat.solvers import Cadical153
from chord_angle import parse_vtx
vtx,R,budget,out=sys.argv[1],float(sys.argv[2]),int(sys.argv[3]),sys.argv[4]
G=parse_vtx(vtx); n=len(G)
def pts_of(S):
    P={}
    for g in S:
        gx,gy=G[g]
        for x,y in G:
            X,Y=x-gx,y-gy
            if X*X+Y*Y<R*R: P.setdefault((round(X,8),round(Y,8)),(X,Y))
    return list(P.values())
def edges_of(P):
    grid={}
    for i,(x,y) in enumerate(P): grid.setdefault((int(math.floor(x)),int(math.floor(y))),[]).append(i)
    E=[]
    for (cx,cy),idx in grid.items():
        for dx in (-1,0,1):
            for dy in (-1,0,1):
                for b in grid.get((cx+dx,cy+dy),()):
                    for a in idx:
                        if a<b and abs(math.hypot(P[a][0]-P[b][0],P[a][1]-P[b][1])-1)<1e-8: E.append((a,b))
    return E
def unsat(S):
    P=pts_of(S); E=edges_of(P); k=4; var=lambda u,c: u*k+c+1
    cl=[[var(u,c) for c in range(k)] for u in range(len(P))]
    for a,b in E:
        for c in range(k): cl.append([-var(a,c),-var(b,c)])
    adj={}
    for a,b in E: adj.setdefault(a,set()).add(b); adj.setdefault(b,set()).add(a)
    for a,b in E:
        com=adj[a]&adj[b]
        if com:
            for c,u in enumerate((a,b,min(com))): cl.append([var(u,c)])
            break
    s=Cadical153(bootstrap_with=cl); s.conf_budget(budget); r=s.solve_limited(); s.delete()
    return r,len(P),len(E)
S=list(range(n)); t0=time.time()
r,np_,ne=unsat(S); print("all %d translates: |V|=%d |E|=%d -> %s (%.0fs)"%(n,np_,ne,{True:'SAT',False:'UNSAT',None:'UNKNOWN'}[r],time.time()-t0),flush=True)
assert r is False
order=sorted(S,key=lambda g:-math.hypot(*G[g])); chunk=64
while chunk>=1:
    pos=0
    while pos<len(order):
        block=[g for g in order[pos:pos+chunk] if g in S]
        if block:
            trial=[g for g in S if g not in set(block)]
            r,np_,ne=unsat(trial)
            if r is False: S=trial; print("  removed %d translates -> %d left, |V|=%d (%.0fs)"%(len(block),len(S),np_,time.time()-t0),flush=True)
        pos+=chunk
    print("chunk %d pass done: %d translates (%.0fs)"%(chunk,len(S),time.time()-t0),flush=True)
    chunk//=2
r,np_,ne=unsat(S); assert r is False
P=pts_of(S); print("final: %d translates, |V|=%d |E|=%d, radius %.4f (%.0fs)"%(len(S),len(P),ne,max(math.hypot(*p) for p in P),time.time()-t0),flush=True)
open(out,"w").write("".join("%.15f %.15f\n"%p for p in P)); open(out+".translates","w").write(" ".join(map(str,S))+"\n"); print("wrote",out,flush=True)
