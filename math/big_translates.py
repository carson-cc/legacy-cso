#!/usr/bin/env python3
"""Union of all translates G - g (g over the vertices of G) of a 5-chromatic graph, optionally times the
12 dihedral symmetries about the origin. Every vertex of G is thereby moved to the origin, so star0 at the
origin of this union dominates star0 at every vertex of G (monotonicity). Float merge; search mode."""
import sys, math
from chord_angle import parse_vtx
vtx=sys.argv[1]; out=sys.argv[2]; syms=int(sys.argv[3]) if len(sys.argv)>3 else 1
G=parse_vtx(vtx); pts={}
S=[]
for k in range(6 if syms else 1):
    for refl in ((1,-1) if syms else (1,)):
        S.append((math.cos(k*math.pi/3),math.sin(k*math.pi/3),refl))
for gx,gy in G:
    for x,y in G:
        X,Y=x-gx,y-gy
        for c,s,r in S:
            X2,Y2=X*c-(Y*r)*s, X*s+(Y*r)*c
            key=(round(X2,8),round(Y2,8))
            if key not in pts: pts[key]=(X2,Y2)
P=list(pts.values()); n=len(P)
o=next(i for i,(x,y) in enumerate(P) if abs(x)<1e-9 and abs(y)<1e-9); P[0],P[o]=P[o],P[0]
g={}
for i,(x,y) in enumerate(P): g.setdefault((int(math.floor(x)),int(math.floor(y))),[]).append(i)
E=[]
for (cx,cy),idx in g.items():
    for dx in (-1,0,1):
        for dy in (-1,0,1):
            for b in g.get((cx+dx,cy+dy),()):
                for a in idx:
                    if a<b and abs(math.hypot(P[a][0]-P[b][0],P[a][1]-P[b][1])-1)<1e-8: E.append((a,b))
with open(out,"w") as f:
    f.write("p edge %d %d\n"%(n,len(E)))
    for a,b in E: f.write("e %d %d\n"%(a+1,b+1))
with open(out+".xy","w") as f:
    for x,y in P: f.write("%.15f %.15f\n"%(x,y))
print("translate union (%s, syms=%d): |V|=%d |E|=%d deg(origin)=%d"%(vtx.split('/')[-1],syms,n,len(E),sum(1 for a,b in E if 0 in (a,b))),flush=True)
