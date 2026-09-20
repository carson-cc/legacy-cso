#!/usr/bin/env python3
"""Exact parser for Mathematica-style .vtx files ({x, y} with Sqrt[..]) into udg.F points, plus an
exact check that a .edge file is the complete unit-distance graph of the point set."""
import sys, re, math
from fractions import Fraction as Fr
from udg import F, P
from surgery import exact_unit_edges
from star_on_graph import load_edges
def SQRT(q):
    q=Fr(q); p,r=q.numerator,q.denominator
    return F.root(p*r, Fr(1,r))
def parse_expr(e):
    e=e.strip().replace("Sqrt[","SQRT(").replace("]",")")
    e=re.sub(r"(?<![\w.])(\d+)(?![\w.])", r"Fr(\1)", e)   # integers -> Fractions (exact division)
    return eval(e,{"SQRT":SQRT,"Fr":Fr,"F":F})
def parse_vtx_exact(path):
    pts=[]
    for line in open(path):
        line=line.strip()
        if not line: continue
        inner=line[1:-1]
        # split on the top-level comma
        depth=0
        for i,ch in enumerate(inner):
            if ch in "([": depth+=1
            elif ch in ")]": depth-=1
            elif ch=="," and depth==0: x,y=inner[:i],inner[i+1:]; break
        X=parse_expr(x); Y=parse_expr(y)
        X=X if isinstance(X,F) else F.const(X); Y=Y if isinstance(Y,F) else F.const(Y)
        pts.append(P(X,Y))
    return pts
if __name__=="__main__":
    pts=parse_vtx_exact(sys.argv[1]); n,E=load_edges(sys.argv[2])
    assert len(pts)==n
    Ex=set(exact_unit_edges(pts)); Ef=set(E)
    print("%s: %d points; exact unit pairs=%d, edge file=%d, missing-from-file=%d, non-unit-in-file=%d"%(
        sys.argv[1].split('/')[-1],n,len(Ex),len(Ef),len(Ex-Ef),len(Ef-Ex)))
    # float sanity of the parse
    bad=sum(1 for a,b in E if abs(math.dist(pts[a].to_float(),pts[b].to_float())-1)>1e-9); print("float mismatches:",bad)
