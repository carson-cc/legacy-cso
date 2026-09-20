#!/usr/bin/env python3
"""Symmetry-closed disc set with vectorized edges. Unit vectors: all edge vectors of the translate union
and their images under the 36 symmetries; edges = pairs (p, p+u) with both in the set. This edge set is a
subset of the true unit-distance graph, so an UNSAT verdict on it is valid for the true graph."""
import sys, math, numpy as np
edgefile,R,out=sys.argv[1],float(sys.argv[2]),sys.argv[3]
xy=np.loadtxt(edgefile+".xy"); E=[]
for line in open(edgefile):
    t=line.split()
    if t and t[0]=='e': E.append((int(t[1])-1,int(t[2])-1))
E=np.array(E); V=np.vstack([xy[E[:,1]]-xy[E[:,0]], xy[E[:,0]]-xy[E[:,1]]])
def dedupe(A):
    K=np.round(A*1e8).astype(np.int64); _,i=np.unique(K[:,0]*(1<<40)+K[:,1],return_index=True); return A[i]
V=dedupe(V)
syms=[]
for k in range(6):
    for refl in (1,-1):
        for j in (-1,0,1):
            a=k*math.pi/3+j*math.acos(5/6); syms.append((math.cos(a),math.sin(a),refl))
def apply(A,s):
    c,sn,r=s; X=A[:,0]; Y=A[:,1]*r; return np.stack([X*c-Y*sn, X*sn+Y*c],1)
U=dedupe(np.vstack([apply(V,s) for s in syms])); print("unit vectors: %d (from %d)"%(len(U),len(V)),flush=True)
base=xy[np.hypot(xy[:,0],xy[:,1])<R]
S=dedupe(np.vstack([apply(base,s) for s in syms])); n=len(S); print("points: %d"%n,flush=True)
K=np.round(S*1e8).astype(np.int64); keys=K[:,0]*(1<<40)+K[:,1]; order=np.argsort(keys); skeys=keys[order]
edges=set()
for u in U:
    Q=np.round((S+u)*1e8).astype(np.int64); qk=Q[:,0]*(1<<40)+Q[:,1]
    pos=np.searchsorted(skeys,qk); pos[pos>=n]=n-1; hit=skeys[pos]==qk
    a=np.nonzero(hit)[0]; b=order[pos[hit]]
    for x,y in zip(a.tolist(),b.tolist()):
        if x<y: edges.add((x,y))
        elif y<x: edges.add((y,x))
# sanity: all edges are unit to 1e-8
d=np.array([math.hypot(*(S[a]-S[b])) for a,b in list(edges)[:2000]]); assert np.all(np.abs(d-1)<1e-7)
with open(out,"w") as f:
    f.write("p edge %d %d\n"%(n,len(edges)))
    for a,b in sorted(edges): f.write("e %d %d\n"%(a+1,b+1))
np.savetxt(out+".xy",S,fmt="%.15f")
print("symmetric disc set R=%.2f: |V|=%d |E|=%d"%(R,n,len(edges)),flush=True)
