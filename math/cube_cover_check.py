#!/usr/bin/env python3
"""Independent check that a cube set is a complete case split for a pinned k-colouring CNF:
(1) every cube assigns exactly the same set of split vertices; (2) the cubes are pairwise distinct;
(3) every assignment of colours to the split vertices that is consistent with the CNF's binary
(edge) clauses among split/pinned vertices, and with the CNF's unit clauses, appears as a cube.
Assignments that violate such a clause are refuted by the CNF itself, so (1)-(3) imply that
"every cube UNSAT" => "CNF UNSAT". Usage: cube_cover_check.py <cnf> <cubes.icnf> [k=4]"""
import sys, itertools
cnf,cubes=sys.argv[1],sys.argv[2]; k=int(sys.argv[3]) if len(sys.argv)>3 else 4
units={}; bins=set()
for line in open(cnf):
    t=line.split()
    if not t or t[0] in ('p','c'): continue
    lits=[int(x) for x in t[:-1]]
    if len(lits)==1: units[lits[0]]=True
    elif len(lits)==2: bins.add(tuple(sorted(lits)))
vertex=lambda lit:(abs(lit)-1)//k; colour=lambda lit:(abs(lit)-1)%k
pin={vertex(l):colour(l) for l in units if l>0}
C=[[int(x) for x in l.split()[1:-1]] for l in open(cubes) if l.startswith('a')]
S=sorted({vertex(l) for l in C[0]})
assert all(sorted({vertex(l) for l in c})==S and len(c)==len(S) and all(l>0 for l in c) for c in C), "cubes not uniform"
assert len({tuple(sorted(c)) for c in C})==len(C), "duplicate cubes"
assert not set(S)&set(pin), "cube touches a pinned vertex"
cubeset={tuple(sorted(c)) for c in C}; n_ok=0
rel=set(S)|set(pin)
bins=[(a,b) for a,b in bins if vertex(a) in rel and vertex(b) in rel]
# backtracking enumeration over the split vertices in order S, checking binary clauses as we go
by_v={}
for a,b in bins: by_v.setdefault(vertex(a),[]).append((a,b)); by_v.setdefault(vertex(b),[]).append((a,b))
def sat(lit,asg): return (asg[vertex(lit)]==colour(lit))==(lit>0)
def rec(i,asg):
    global n_ok
    if i==len(S):
        n_ok+=1
        assert tuple(sorted(v*k+asg[v]+1 for v in S)) in cubeset, "missing cube for %r"%(asg,)
        return
    v=S[i]
    for c in range(k):
        asg[v]=c
        if all(sat(a,asg) or sat(b,asg) for a,b in by_v.get(v,[]) if vertex(a) in asg and vertex(b) in asg):
            rec(i+1,asg)
        del asg[v]
rec(0,dict(pin))
print("cover OK: %d split vertices, %d admissible assignments, %d cubes"%(len(S),n_ok,len(C)))
assert n_ok==len(C)
