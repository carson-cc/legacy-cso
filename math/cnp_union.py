#!/usr/bin/env python3
"""Union of all CNP-SAT graphs (same coordinate field Q(sqrt3,sqrt11)): merge vertices by float
coordinates (tol 1e-9), recompute ALL unit pairs by float tolerance (search mode; any hit is to be
re-verified exactly), write a 'p edge' file plus a coordinate map."""
import sys, math, glob, os
from chord_angle import parse_vtx
import numpy as np
D=sys.argv[1]; out=sys.argv[2]
pts={}; src={}
for f in sorted(glob.glob(D+"/*.vtx")):
    for x,y in parse_vtx(f):
        key=(round(x,9),round(y,9))
        if key not in pts: pts[key]=(x,y); src[key]=os.path.basename(f)
P=np.array(list(pts.values())); n=len(P)
g={}
for i,(x,y) in enumerate(P): g.setdefault((int(math.floor(x)),int(math.floor(y))),[]).append(i)
E=[]
for (cx,cy),idx in g.items():
    for dx in (-1,0,1):
        for dy in (-1,0,1):
            nb=g.get((cx+dx,cy+dy))
            if not nb: continue
            for a in idx:
                for b in nb:
                    if a<b and abs(math.hypot(P[a,0]-P[b,0],P[a,1]-P[b,1])-1)<1e-9: E.append((a,b))
with open(out,"w") as f:
    f.write("p edge %d %d\n"%(n,len(E)))
    for a,b in E: f.write("e %d %d\n"%(a+1,b+1))
with open(out+".xy","w") as f:
    for (x,y) in P: f.write("%.15f %.15f\n"%(x,y))
print("union: |V|=%d |E|=%d from %d files"%(n,len(E),len(glob.glob(D+"/*.vtx"))))
