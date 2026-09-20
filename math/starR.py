#!/usr/bin/env python3
"""
(starR): the general ergodic criterion.  Rotate G about v by delta = beta_d (unit-chord angle on the circle
of radius d = |vz|, irrational multiple of pi).  Two copies of G-v (both with N(v) restricted to {3,4,5},
the doubled origin) plus all cross unit edges between copy 1 and copy 2 rotated by delta.  Let
R = {(a,b): some valid pair of colorings has c1(z)=a, c2(z)=b}.  A measurable coloring of the plane
gives a measurable state function s(theta)=c(z(theta)) with (s(theta),s(theta+delta)) in R a.e.;
by ergodicity of the irrational rotation the process lives in one recurrent component of R, and a
component of period >= 2 (for symmetric R: a bipartite component) is impossible.  So:
      every component of R (dropping isolated states) bipartite  =>  contradiction.
Falconer's proof is the case R = {(1,2),(2,1)}.  (star) is the case R subset of {1,2}^2.
Colours 1,2 (origin colours) are interchangeable, and 3,4,5 are interchangeable, so R is computed
from 8 representative SAT calls and completed by symmetry.
"""
import sys, math, time, argparse, itertools
from pysat.solvers import Cadical153
from star_on_graph import load_edges
from chord_angle import parse_vtx
from fractions import Fraction

def rot(p,c,ang):
    x,y=p[0]-c[0],p[1]-c[1]; ca,sa=math.cos(ang),math.sin(ang)
    return (c[0]+x*ca-y*sa, c[1]+x*sa+y*ca)

def cross_edges(P,v,delta,tol=1e-9):
    """pairs (u,w), u,w != v, with |P[u] - rot(P[w])| = 1 (float)."""
    Q=[rot(p,P[v],delta) for p in P]
    g={}
    for i,(x,y) in enumerate(Q):
        if i!=v: g.setdefault((int(math.floor(x)),int(math.floor(y))),[]).append(i)
    out=[]
    for u,(x,y) in enumerate(P):
        if u==v: continue
        cx,cy=int(math.floor(x)),int(math.floor(y))
        for dx in (-1,0,1):
            for dy in (-1,0,1):
                for w in g.get((cx+dx,cy+dy),()):
                    if abs(math.hypot(x-Q[w][0],y-Q[w][1])-1)<tol: out.append((u,w))
    return out

def sym_complete(R):
    perms=[]
    for p12 in ((0,1),(1,0)):
        for p345 in itertools.permutations((2,3,4)):
            perms.append({0:p12[0],1:p12[1],2:p345[0],3:p345[1],4:p345[2]})
    S=set()
    for a,b in R:
        for p in perms: S.add((p[a],p[b])); S.add((p[b],p[a]))
    return S

def bipartite_components(R):
    """R symmetric relation on {0..4}. Return (all components with an edge are bipartite?, components)."""
    adj={a:set() for a in range(5)}
    for a,b in R: adj[a].add(b); adj[b].add(a)
    seen={}; ok=True
    for s in range(5):
        if s in seen or not adj[s]: continue
        seen[s]=0; stack=[s]
        while stack:
            a=stack.pop()
            for b in adj[a]:
                if b not in seen: seen[b]=1-seen[a]; stack.append(b)
                elif seen[b]==seen[a]: ok=False
    return ok

if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("edgefile"); ap.add_argument("vtxfile")
    ap.add_argument("--vertices",default="all"); ap.add_argument("--budget",type=int,default=50000)
    a=ap.parse_args()
    n,E=load_edges(a.edgefile); P=parse_vtx(a.vtxfile); assert len(P)==n
    bad=sum(1 for x,y in E if abs(math.dist(P[x],P[y])-1)>1e-9); assert bad==0, "vtx/edge mismatch"
    adj={u:set() for u in range(n)}
    for x,y in E: adj[x].add(y); adj[y].add(x)
    k=5; var1=lambda u,c: u*k+c+1; var2=lambda u,c: (n+u)*k+c+1
    verts=range(n) if a.vertices=="all" else [int(x) for x in a.vertices.split(",")]
    t0=time.time(); hits=[]; ncalls=0; nunk=0; stats={}
    print("graph %s |V|=%d |E|=%d"%(a.edgefile.split('/')[-1],n,len(E)),flush=True)
    for v in verts:
        # group candidate z by distance
        byd={}
        for z in range(n):
            if z==v or z in adj[v]: continue
            d=math.dist(P[v],P[z])
            if d<=0.5+1e-9: continue
            byd.setdefault(round(d,9),[]).append(z)
        for d,zs in byd.items():
            beta=2*math.asin(1/(2*d)); fr=Fraction(beta/math.pi).limit_denominator(2000)
            if abs(beta/math.pi-fr)<1e-9: continue   # rational rotation (numerically): skip
            base=[]
            for u in range(n):
                if u==v: continue
                base.append([var1(u,c) for c in range(k)]); base.append([var2(u,c) for c in range(k)])
            for x,y in E:
                if v in (x,y): continue
                for c in range(k): base.append([-var1(x,c),-var1(y,c)]); base.append([-var2(x,c),-var2(y,c)])
            for u in adj[v]:
                for c in (0,1): base.append([-var1(u,c)]); base.append([-var2(u,c)])
            for u,w in cross_edges(P,v,beta):
                for c in range(k): base.append([-var1(u,c),-var2(w,c)])
            s=Cadical153(bootstrap_with=base)
            for z in zs:
                R=set()
                for aa in (0,2):
                    for bb in (0,1,2,3):
                        s.conf_budget(a.budget); r=s.solve_limited(assumptions=[var1(z,aa),var2(z,bb)]); ncalls+=1
                        if r is True: R.add((aa,bb))
                        elif r is None: nunk+=1; R.add((aa,bb))   # unknown counts as possible (conservative)
                Rf=sym_complete(R)
                key=tuple(sorted(Rf)); stats[key]=stats.get(key,0)+1
                if Rf and bipartite_components(Rf):
                    hits.append((v,z,d,sorted(Rf))); print("  STARR HIT v=%d z=%d d=%.6f R=%s"%(v,z,d,sorted(Rf)),flush=True)
            s.delete()
        if (list(verts).index(v)+1)%10==0:
            print("  progress: %d vertices, %d calls, %d unknown, hits=%d (%.0fs)"%(list(verts).index(v)+1,ncalls,nunk,len(hits),time.time()-t0),flush=True)
    print("DONE hits=%d calls=%d unknown=%d (%.0fs)"%(len(hits),ncalls,nunk,time.time()-t0),flush=True)
    top=sorted(stats.items(),key=lambda kv:-kv[1])[:6]
    for key,cnt in top: print("  relation pattern x%d: %s"%(cnt,[ (a+1,b+1) for a,b in key]))
