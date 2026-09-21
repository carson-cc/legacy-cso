#!/usr/bin/env python3
"""Certify that a pinned 4-colouring CNF exported by export_cnf.py is the unit-distance graph of an exact
point set: take the points of <exact_file> (udg.F repr, one P(...) per line) whose float image lies in
r_in < |x| < r_out, recompute the exact unit-distance edges, and check that, under the bijection given
by float coordinates, they coincide with the binary clauses of <cnf> (whose vertex order is that of
<edgefile>.xy restricted like export_cnf.py). Writes the exact subset to <out_exact>.
Usage: exact_subset.py <exact_file> <edgefile> <r_in> <r_out> <cnf> <subset.xy> <out_exact>"""
import sys, math, re
from fractions import Fraction as Fr
from udg import F, P
from surgery import exact_unit_edges
ex,edgefile,r_in,r_out,cnf,subxy,out=sys.argv[1],sys.argv[2],float(sys.argv[3]),float(sys.argv[4]),sys.argv[5],sys.argv[6],sys.argv[7]
def parse_F(s):
    c={}
    for term in s.split(" + "):
        term=term.strip()
        if "*sqrt(" in term:
            coef,d=term.split("*sqrt("); c[int(d[:-1])]=Fr(coef)
        else: c[1]=Fr(term)
    return F(c)
def parse_P(line):
    m=re.match(r"P\((.*), (.*)\)$",line.strip()); assert m, line
    return P(parse_F(m.group(1)),parse_F(m.group(2)))
pts=[parse_P(l) for l in open(ex) if l.startswith("P(")]
xy=[tuple(map(float,l.split())) for l in open(edgefile+".xy")]
key=lambda x,y:(round(x,7),round(y,7))
sub={key(*map(float,l.split())) for l in open(subxy)}
keep=[i for i,(x,y) in enumerate(xy) if r_in<math.hypot(x,y)<r_out and key(x,y) in sub]
sel=[p for p in pts if (lambda x,y: r_in<math.hypot(x,y)<r_out and key(x,y) in sub)(*p.to_float())]
assert len(sel)==len(keep), (len(sel),len(keep))
assert {key(*p.to_float()) for p in sel}=={key(*xy[i]) for i in keep}, "point sets differ"
E=exact_unit_edges(sel)
Eex={frozenset((key(*sel[a].to_float()),key(*sel[b].to_float()))) for a,b in E}
k=4; Ecnf=set(); nv=None
for line in open(cnf):
    t=line.split()
    if t and t[0]=='p': nv=int(t[2]); continue
    if len(t)==3 and t[2]=='0':
        a,b=int(t[0]),int(t[1]); assert a<0 and b<0
        Ecnf.add(frozenset((key(*xy[keep[(-a-1)//k]]),key(*xy[keep[(-b-1)//k]]))))
assert nv==k*len(keep)
print("exact points %d, exact edges %d, CNF edges %d, equal: %s"%(len(sel),len(Eex),len(Ecnf),Eex==Ecnf))
assert Eex==Ecnf
with open(out,"w") as f:
    f.write("# exact coordinates (udg.F repr); edges = all pairs at exact unit distance\n")
    for p in sel: f.write("%r\n"%p)
print("wrote",out)
