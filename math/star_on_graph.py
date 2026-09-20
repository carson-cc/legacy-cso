#!/usr/bin/env python3
"""
Run the doubled-vertex criteria on a certified 5-chromatic unit-distance graph given by its edge list.

  (star0) for vertex v:  5-color G - v with N(v) restricted to colors {2,3,4}  -> UNSAT means:
          G with v doubled is 6-chromatic  =>  (with Lemma 3 + a reduced-boundary bichromatic point)
          no measurable 5-coloring of the plane with a finite-perimeter class.
  (star)  for (v, z), z not in N(v) u {v}:  additionally z restricted to {2,3,4}  -> UNSAT means:
          every such coloring has c(z) in {0,1}; with the irrational unit-chord rotation on the
          circle of radius |vz| this gives the same conclusion.

Purely combinatorial: only the edge list is used. Coordinates matter only to report |vz| for hits.
Verdicts: SAT / UNSAT / UNKNOWN (conflict budget). UNKNOWN is never treated as UNSAT.
"""
import sys, time, argparse
from pysat.solvers import Cadical153

def load_edges(path):
    n=m=None; E=[]
    for line in open(path):
        t=line.split()
        if not t: continue
        if t[0]=='p': n=int(t[2]); m=int(t[3])
        elif t[0]=='e': E.append((int(t[1])-1,int(t[2])-1))
    assert n is not None and len(E)==m, (n,m,len(E))
    return n,E

def base_clauses(n,E,v,k,adj):
    var=lambda u,c: u*k+c+1
    cl=[[var(u,c) for c in range(k)] for u in range(n) if u!=v]
    for a,b in E:
        if v in (a,b): continue
        for c in range(k): cl.append([-var(a,c),-var(b,c)])
    for u in adj[v]:
        cl.append([-var(u,0)]); cl.append([-var(u,1)])
    # symmetry pin inside N(v): an adjacent pair of neighbours takes colours 2,3 (colours 2,3,4 are interchangeable)
    Nv=sorted(adj[v])
    for a in Nv:
        nb=[b for b in adj[a] if b in adj[v] and b>a]
        if nb: cl.append([var(a,2)]); cl.append([var(nb[0],3)]); break
    return cl,var

def verdict(r): return {True:"SAT",False:"UNSAT",None:"UNKNOWN"}[r]

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("edgefile"); ap.add_argument("--k",type=int,default=5)
    ap.add_argument("--budget",type=int,default=200000)
    ap.add_argument("--star",action="store_true",help="also run the (v,z) sweep for vertices where star0 is SAT")
    ap.add_argument("--vertices",default="all")
    ap.add_argument("--zbudget",type=int,default=20000)
    a=ap.parse_args()
    n,E=load_edges(a.edgefile); k=a.k
    adj={u:set() for u in range(n)}
    for x,y in E: adj[x].add(y); adj[y].add(x)
    verts=range(n) if a.vertices=="all" else [int(x) for x in a.vertices.split(",")]
    print("graph %s: |V|=%d |E|=%d  k=%d"%(a.edgefile.split('/')[-1],n,len(E),k),flush=True)
    t0=time.time(); hits0=[]; unk0=[]; star_hits=[]
    for v in verts:
        cl,var=base_clauses(n,E,v,k,adj)
        s=Cadical153(bootstrap_with=cl); s.conf_budget(a.budget); r=s.solve_limited()
        if r is False: hits0.append(v); print("  STAR0 HIT at v=%d (deg %d)"%(v,len(adj[v])),flush=True)
        elif r is None: unk0.append(v)
        if a.star and r is True:
            zs=[z for z in range(n) if z!=v and z not in adj[v]]
            nunk=0
            for z in zs:
                s.conf_budget(a.zbudget); rz=s.solve_limited(assumptions=[-var(z,0),-var(z,1)])
                if rz is False: star_hits.append((v,z)); print("  STAR HIT at (v=%d, z=%d)"%(v,z),flush=True)
                elif rz is None: nunk+=1
            if nunk: print("  v=%d: %d of %d z-calls UNKNOWN"%(v,nunk,len(zs)),flush=True)
        s.delete()
        if (v+1)%50==0 or v==verts[-1] if isinstance(verts,list) else (v+1)%50==0:
            print("  progress: %d vertices, star0 hits=%d unknown=%d star hits=%d (%.0fs)"%(v+1,len(hits0),len(unk0),len(star_hits),time.time()-t0),flush=True)
    print("DONE star0: hits=%s unknown=%d ; star hits=%s  (%.0fs)"%(hits0,len(unk0),star_hits[:20],time.time()-t0),flush=True)
