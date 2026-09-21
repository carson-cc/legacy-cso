#!/usr/bin/env python3
"""Minimal cube-and-conquer driver with certificates.
Cubes come from an icnf file ('a lits 0' lines); each cube is solved by kissat on CNF+units with a time
limit, W workers in parallel. Any SAT cube => SAT (model saved). If a drat-trim binary is given, every
UNSAT cube is solved with a DRAT proof that drat-trim checks against CNF+cube (proof deleted after a
successful check); a cube counts as UNSAT only if drat-trim prints VERIFIED.
Cubes that time out are refined: if a deeper cube file <refine.icnf> is given (same greedy order, so its
cubes extend the base cubes), an undecided base cube is replaced by the deeper cubes extending it; the
leftovers after that get one more pass with 4x the time limit. The decided leaf cubes are written to
<workdir>/leaves.icnf; together with cube_cover_check.py (which checks that the leaves cover every
admissible assignment) and the per-cube verdicts this is the certificate. Verdicts are appended to
<workdir>/verdicts.txt keyed by the cube literals, so a run can be resumed.
Usage: cc.py <cnf> <cubes.icnf> <workdir> <workers> <time_per_cube_s> <kissat> [drat-trim|-] [refine.icnf]"""
import sys, os, subprocess, time, concurrent.futures as cf
cnf,cubes,wd,W,T,K=sys.argv[1],sys.argv[2],sys.argv[3],int(sys.argv[4]),int(sys.argv[5]),sys.argv[6]
DT=sys.argv[7] if len(sys.argv)>7 and sys.argv[7]!="-" else None
REF=sys.argv[8] if len(sys.argv)>8 else None
os.makedirs(wd,exist_ok=True)
hdr=None; body=[]
for line in open(cnf):
    if line.startswith('p'): hdr=line.split()
    elif line.strip() and not line.startswith('c'): body.append(line)
nv,nc=int(hdr[2]),int(hdr[3])
rd=lambda f:[tuple(int(x) for x in l.split()[1:-1]) for l in open(f) if l.startswith('a')]
base=rd(cubes); deep=rd(REF) if REF else []
print("cubes: %d  (refinement cubes: %d)"%(len(base),len(deep)),flush=True)
done={}
vf="%s/verdicts.txt"%wd
if os.path.exists(vf):
    for l in open(vf):
        t=l.split()
        if len(t)>=3 and t[-2] in ("UNSAT","SAT"): done[tuple(int(x) for x in t[:-2])]=t[-2]
    print("resuming: %d cubes already decided"%len(done),flush=True)
def solve(lits,tl):
    tag="%s/c_%d"%(wd,abs(hash(lits))%10**12); f=tag+".cnf"; pf=tag+".drat"
    with open(f,"w") as g:
        g.write("p cnf %d %d\n"%(nv,nc+len(lits))); g.writelines(body)
        for x in lits: g.write("%d 0\n"%x)
    t=time.time()
    r=subprocess.run([K,"-q","--time=%d"%tl,f]+([pf] if DT else []),capture_output=True,text=True)
    out=r.stdout
    if "s UNSATISFIABLE" in out:
        v="UNSAT"
        if DT:
            d=subprocess.run([DT,f,pf],capture_output=True,text=True)
            v="UNSAT" if "VERIFIED" in d.stdout else "UNVERIFIED"
    elif "s SATISFIABLE" in out: v="SAT"; open(tag+".model","w").write(out)
    else: v="UNKNOWN"
    os.remove(f)
    if os.path.exists(pf) and v!="UNVERIFIED": os.remove(pf)
    dt=time.time()-t
    with open(vf,"a") as g: g.write(" ".join(map(str,lits))+" %s %.0f\n"%(v,dt))
    return lits,v,dt
t0=time.time(); res=dict(done); leaves=[]
def run(pending,tl,label):
    with cf.ThreadPoolExecutor(max_workers=W) as ex:
        for n,(lits,v,dt) in enumerate(ex.map(lambda c: solve(c,tl), pending)):
            res[lits]=v
            print("%s cube %s: %s (%.0fs) [%d/%d, %.0fs]"%(label," ".join(map(str,lits)),v,dt,n+1,len(pending),time.time()-t0),flush=True)
            if v=="SAT": print("SAT CUBE FOUND -> instance SATISFIABLE",flush=True)
pending=[c for c in base if c not in res]
run(pending,T,"base")
und=[c for c in base if res.get(c) not in ("UNSAT","SAT")]
leaves=[c for c in base if res.get(c)=="UNSAT"]
if und and deep:
    kids=[d for d in deep if any(set(c)<=set(d) for c in und)]
    print("refining %d undecided cubes into %d deeper cubes"%(len(und),len(kids)),flush=True)
    run([c for c in kids if c not in res],T,"deep")
    und=[c for c in kids if res.get(c) not in ("UNSAT","SAT")]
    leaves+=[c for c in kids if res.get(c)=="UNSAT"]
if und:
    print("final pass: %d cubes at %ds"%(len(und),4*T),flush=True)
    run(und,4*T,"final")
    leaves+=[c for c in und if res.get(c)=="UNSAT"]
    und=[c for c in und if res.get(c) not in ("UNSAT","SAT")]
with open("%s/leaves.icnf"%wd,"w") as f:
    for c in leaves: f.write("a "+" ".join(map(str,c))+" 0\n")
sat=[c for c,v in res.items() if v=="SAT"]
print("DONE leaves=%d undecided=%d sat=%d => %s (%.0fs)"%(len(leaves),len(und),len(sat),
      "SAT" if sat else ("UNSAT" if not und else "UNKNOWN"),time.time()-t0),flush=True)
