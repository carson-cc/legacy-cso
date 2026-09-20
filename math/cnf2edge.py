#!/usr/bin/env python3
"""Recover the edge list from a k-coloring CNF (variables v*k+c+1) by reading binary all-negative clauses."""
import sys
path,k,out=sys.argv[1],int(sys.argv[2]),sys.argv[3]
E=set(); nv=0
for line in open(path):
    t=line.split()
    if not t or t[0] in ('c','p'): 
        if t and t[0]=='p': nv=int(t[2])//k
        continue
    lits=[int(x) for x in t if x!='0']
    if len(lits)==2 and lits[0]<0 and lits[1]<0:
        a,ca=divmod(-lits[0]-1,k); b,cb=divmod(-lits[1]-1,k)
        if ca==cb and a!=b: E.add((min(a,b),max(a,b)))
E=sorted(E)
with open(out,"w") as f:
    f.write("p edge %d %d\n"%(nv,len(E)))
    for a,b in E: f.write("e %d %d\n"%(a+1,b+1))
print("cnf %s -> %d vertices, %d edges"%(path.split('/')[-1],nv,len(E)))
