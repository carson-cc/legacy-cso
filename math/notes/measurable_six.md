# Notes toward the measurable chromatic number of the plane being at least 6

Status: research notes. Lemmas 1 and 2 and Observations 5 and 6 are proved here.
Everything under "Program" is conjecture or open. Nothing in this file is a theorem
about the plane beyond what is explicitly proved.

## Setting

R^2 = A_1 ∪ ... ∪ A_k, the A_i measurable, pairwise disjoint, each 1-avoiding
(no two points of A_i at distance exactly 1). Replace each A_i by
A_i ∩ {Lebesgue density points of A_i}. This removes a null set and keeps
1-avoidance (a subset of a 1-avoiding set is 1-avoiding). So WLOG every point of
A_i is a density point of A_i and ∪ A_i has full measure.

Notation. B(x,r) is the open disc. C(y) is the unit circle about y. σ is arc length.
x is (η,r)-dense in A if μ(A ∩ B(x,r)) ≥ (1-η) π r^2.
The ε-unit-distance graph (ε-UDG) on a set S joins two points of S whose distance
lies in (1-ε, 1+ε).

## Lemma 1 (scale-matched exclusion)

Let A be measurable and 1-avoiding. If x and y are both (η,r)-dense in A with
η ≤ 1/100 and r ≤ 1/4, then | |x-y| - 1 | ≥ r/2.

Proof. Suppose |x-y| = 1+t with |t| < r/2. Count unit-distance pairs (a,b) with
a ∈ B(x,r), b ∈ B(y,r) by the measure ν(S) = ∫_{a∈B(x,r)} σ(C(a) ∩ S) da.
Lower bound on all pairs: for a ∈ B(x, r/4) we have | |a-y| - 1 | < 3r/4, so
C(a) crosses B(y,r) in an arc of length at least 2 sqrt(r^2 - (3r/4)^2) > 1.3 r.
Hence ν(B(y,r)) ≥ π (r/4)^2 · 1.3 r > 0.25 r^3.
Upper bound on pairs that touch the complement of A: a unit circle meets a disc of
radius r ≤ 1/4 in arcs of total length at most 4r. So pairs with a ∉ A contribute
at most μ(B(x,r) \ A) · 4r ≤ η π r^2 · 4r, and by the symmetric count (Fubini in the
other order) pairs with b ∉ A contribute at most the same. Total ≤ 8 π η r^3 < 0.25 r^3
when η ≤ 1/100. So a positive-measure set of unit pairs has both ends in A,
contradicting 1-avoidance. ∎

## Lemma 2 (thick circle about a density point)

Let A be measurable and 1-avoiding and x a density point of A. Let
Ann_r = { y : 1 - r/2 < |y-x| < 1 + r/2 }. Then μ(A ∩ Ann_r) / μ(Ann_r) → 0 as r → 0.

Proof. Write η(r) for the density deficiency of A in B(x,r); η(r) → 0.
For y ∈ A, C(y) ∩ A = ∅ exactly, so C(y) ∩ B(x,r) ⊂ B(x,r) \ A. For y ∈ Ann_r the
arc C(y) ∩ B(x,r) has length at least sqrt(3) r. Fubini gives
∫_y σ(C(y) ∩ (B(x,r) \ A)) dy = 2π μ(B(x,r) \ A) ≤ 2π^2 η(r) r^2.
So μ(A ∩ Ann_r) · sqrt(3) r ≤ 2π^2 η(r) r^2, while μ(Ann_r) = 2π r.
The ratio is at most (π/sqrt 3) η(r). ∎

Reading: a density point x of A_i is, in measure, adjacent to its whole thick unit
circle. This is the one place where a measurable coloring says more than a finite
graph does, because the thick circle is a set of positive measure that an exact
unit-distance graph never sees.

## Proposition 3 (exactly what measurability buys)

For r > 0 let E_r be the set of points x that are (1/100, s)-dense in their own
class for every s ≤ r. Then:
(i) ∪_r E_r has full measure (every density point lies in some E_r);
(ii) by Lemma 1, the coloring restricted to E_r is a proper coloring of the
(r/2)-UDG on E_r.

So a measurable k-coloring of the plane is a proper k-coloring of the ε-UDG on a set
E_{2ε} whose density tends to 1 as ε → 0. Conversely the finite exact unit-distance
constraints give nothing more: for almost every rigid placement of a finite
unit-distance graph, every vertex is a density point and the induced coloring is
proper, which is precisely the finite statement.

## Corollary 4 (a sufficient condition, and the obstruction)

Fix a measurable 5-coloring and write δ(ε) = 1 - (density of E_{2ε}) in a large disc.
If for some ε there is a finite ε-UDG G with χ(G) ≥ 6 and |V(G)| · δ(ε) < 1, then a
random translate of G lies inside E_{2ε} with positive probability, and Proposition 3
gives a proper 5-coloring of G. Contradiction. Hence

    χ_m(R^2) ≥ 6  if  6-chromatic ε-UDGs G_ε exist with |V(G_ε)| ≤ 1/δ(ε) for some ε.

Obstruction. δ(ε) depends on the coloring and has no rate. And |V(G_ε)| → ∞ as ε → 0
unless a 6-chromatic exact unit-distance graph exists: a bounded family of
6-chromatic ε-UDGs has, by compactness, a limit embedding with unit edges; vertices
that collide are non-adjacent, so the limit is a quotient graph, which is a unit-distance
graph with chromatic number at least 6. So random placement alone cannot close the
argument. Whatever Falconer used in 1981 to get from 4 to 5 colors must beat random
placement, and I could not reconstruct it from memory. Reading that proof is the first
task of the program below.

## Observation 5 (exact thickening gains nothing)

Let G be a finite unit-distance graph and G^ρ the union of ρ-discs about its vertices.
The exact unit-distance graph restricted to G^ρ has the same chromatic number as G,
even for measurable colorings: color each disc by the color of its center in an optimal
coloring of G. Discs at non-unit center distance are far from unit distance for small ρ,
and each disc is an independent set. So the gain in Lemma 2 cannot come from "thick
vertices". It comes from ε-tolerance, that is from long chains inside thick annuli.

## Observation 6 (thickness gains one color on a circle)

(a) The exact unit-distance graph on a unit circle is bipartite: unit chords subtend 60°.
(b) The ε-UDG on a unit circle is not 2-colorable, for any coloring, measurable or not.
    A 2-coloring g satisfies g(φ) = g(φ + s) for every s in an open interval about 120°,
    so g is invariant under an open set of rotations, so g is constant, so not proper.
(c) Three colors suffice for tolerance below 20° of angle: color nine 40° sectors
    cyclically 1,2,3. Any two points at angular separation in (40°, 80°) lie in sectors
    of different color.

Caution (rate obstruction). One would like to conclude that a density point x plus
its thick unit circle needs four colors, killing measurable 3-colorings without the
Moser spindle. That does NOT follow. The odd cycles inside an annulus of width r have
about 1/r vertices, and Lemma 2 only gives A-density at most (π/√3) η(r) in the annulus,
with η(r) → 0 at no particular rate. A union bound over the cycle needs η(r) ≲ r, and
there are measurable sets whose density points all have η(r) ~ 1/log(1/r). The same
obstruction reappears in Corollary 4 as δ(ε) versus |V(G_ε)|. So the thick-circle
mechanism is real but every use of it must beat a rate, and random placement or union
bounds do not. This is the precise technical gap between Lemma 2 and any theorem.

## Program

P1. For each fixed ε the chromatic number of the plane's ε-UDG is a finite question
    (de Bruijn–Erdős). Known: at least 5 for every ε > 0 (Exoo, 2005). At most 7.
    Whether it is at least 6 for small ε is, as far as I know, open. Finding a
    6-chromatic ε-UDG for a concrete small ε is a SAT search, not a theorem, and it
    is the experiment run in this folder (see eps_udg.py and the log below).
P2. Reconstruct Falconer's 4 → 5 mechanism from the 1981 paper, then ask whether it
    composes with 5-chromatic structure instead of the Moser spindle.
P3. Fallback: the closures of the density-point sets are closed sets covering the plane
    whose boundary behaviour is what Townsend's map-coloring proof of 6 analyses.

## Experiment log

(filled in by the runs below)

### Run 1: 5-colorability of eps-UDG lattice patches (eps_udg.py, CaDiCaL, symmetry-broken)

Triangular lattice, spacing s, disc radius R, edges at distance in (1-eps, 1+eps).

| s   | R   | eps  | V   | E      | 5-colorable? | time  |
|-----|-----|------|-----|--------|--------------|-------|
| 0.2 | 2.0 | 0.30 | 367 | 13506  | UNSAT        | 0.1s  |
| 0.2 | 2.0 | 0.25 | 367 | 11802  | UNSAT        | 0.1s  |
| 0.2 | 2.0 | 0.20 | 367 | 8479   | UNSAT        | 0.1s  |
| 0.2 | 2.0 | 0.15 | 367 | 7578   | UNSAT        | 0.2s  |
| 0.2 | 2.0 | 0.10 | 367 | 4542   | UNSAT        | 285s  |
| 0.2 | 2.0 | 0.05 | 367 | 1500   | SAT (only the exact unit shell survives at this spacing) | 0.0s |
| 0.1 | 1.6 | 0.30 | 931 | 117396 | UNSAT        | 1.3s  |
| 0.1 | 1.6 | 0.15 | 931 | 63036  | UNSAT        | 0.6s  |
| 0.1 | 1.6 | 0.10 | 931 | 38938  | UNSAT        | 6.6s  |

Independent re-verification of (s,R,eps)=(0.2,2.0,0.15), k=5 (verify_eps.py): edges recomputed
with exact rational arithmetic on lattice coordinates (same |E| = 7578); Glucose4 with no
symmetry breaking: UNSAT; CaDiCaL DRAT proof (548028 lines) checked by drat-trim: "s VERIFIED"
(14.2 s). The .cnf/.drat files are not committed (40 MB); regenerate with verify_eps.py.

4-colorability probe (sweep4): eps=0.05 (s=0.1, 931 pts) UNSAT; eps=0.02 (s=0.05, 2381 pts) UNSAT.
Consistent with Exoo's bound of at least 5 for every eps.

Literature check (after the fact): these UNSAT results are reproductions, not new. The
chromatic number of the plane with an interval of forbidden distances is known to be at
least 6 and, per arXiv:2304.10163 (2023), at least 7. See the literature section below.

## Literature (from search summaries; full texts unreachable from this sandbox)

- Exoo 2005 (DCG): the ε-unit-distance graph needs at least 5 colors for every ε > 0.
- arXiv:2201.04499 (Coloring distance graphs on the plane) and Parts, arXiv:2303.14722:
  chromatic number with an interval of forbidden distances is at least 6 on wide ranges.
- arXiv:2304.10163 (2023): "The chromatic number of the plane with an interval of
  forbidden distances is at least 7." If this covers every interval, then P1 is closed:
  the ε-UDG is 7-chromatic for every ε > 0, and Run 1 above is a reproduction.
- Falconer 1981 (JCTA 31, 184–189): measurable chromatic number of R^n is at least n+3.
  Polymath16 describes the mechanism as: fix an origin that is an "edge" point taking two
  colors, rotate a Moser spindle about it, the two far vertices must take the two origin
  colors in different ways, and the spindle angle being an irrational multiple of π
  contradicts measurability. Polymath16 "built on Falconer's main idea ... using a
  5-chromatic graph with a bichromatic origin and a lemma derived from Falconer that was a
  simple modification of a lemma of Croft". I could not read what they concluded.

## Reconstruction of Falconer's mechanism, and the finite criterion it reduces to

Lemma 3 (Croft-type, rate-free). Let A be measurable and 1-avoiding, and suppose A has
upper density at least c at x along scales r_n → 0. Then every point y with |x-y| = 1 has
A-deficiency at least c/5 in B(y, 2r_n), so y is not a density point of A.
Proof. For a ∈ B(x,r) the circle C(a) crosses B(y,2r) in an arc of length ≥ 2√3 r, and
C(b) ∩ B(x,r) has length ≤ 4r for every b. Fubini on unit pairs gives
μ{ b ∈ B(y,2r) : C(b) meets A ∩ B(x,r) } ≥ (√3/2) c π r^2, and those b are not in A. ∎

Definition. A point O is (i,j)-bichromatic if A_i and A_j both have upper density ≥ c > 0
at O along a common sequence of scales. Such points exist: the essential boundary of any
class has positive H^1 measure (Federer), and a nested-ball argument produces a point where
A_1 and its complement both have density ≥ 1/8 along a sequence; pigeonhole picks j.

Falconer's argument in this language. Take a (1,2)-bichromatic O and the unit rhombus
(O,p,q,z), |Oz| = √3, rotated by θ. For a.e. θ (see the caveat below) p, q, z are density
points of single classes. Lemma 3 applied to both A_1 and A_2 forces c(p), c(q) ∉ {1,2},
so in a 4-coloring {c(p),c(q)} = {3,4} and c(z) ∈ {1,2}. The far vertices z(θ) and
z(θ+α), cos α = 5/6, are at unit distance, so h(θ) = c(z(θ)) is a measurable {1,2}-valued
function with h(θ+α) ≠ h(θ) a.e.; then h(θ+2α) = h(θ) a.e., and 2α/π is irrational
(Niven), so h is a.e. constant: contradiction.

Combinatorial core. Double the origin into adjacent vertices O_1, O_2 and join z to both:
the rhombus becomes K_5. Falconer's theorem is "K_5 is not 4-colorable" plus two
measurable realizations of virtual edges: the doubled vertex is a bichromatic boundary point,
and the two O–z edges are the ergodic argument on the circle of radius |Oz|.

Criterion (★). Let G be a finite unit-distance graph with vertices v, z, |vz| = d, and let
G'' be G with v doubled (v_1, v_2 adjacent, same neighborhood) and z joined to v_1, v_2.
If χ(G'') ≥ 6 and the unit-chord angle β_d = 2 arcsin(1/(2d)) is an irrational multiple
of π, then the argument above, run with G in place of the rhombus, shows that no measurable
5-coloring of the plane exists in which the bichromatic point can be chosen well
(next paragraph). Equivalently (★) is one SAT call: 5-color G − v with N(v) forbidden
colors {1,2} and z forbidden {1,2}; UNSAT means (★).
Necessary condition: if G is 4-colorable then every 4-coloring has c(v) = c(z)
(a forced-equal pair at distance d). Such pairs are exactly what spindles into a
5-chromatic graph, so (★) lives at the scale of the 5-chromatic constructions, not below.

Caveat (null sets on circles). The vertices p(θ), q(θ), z(θ) lie on circles about the
specific point O, and the null set N of non-density points may contain whole circles.
Resolution when some class has locally finite perimeter: its reduced boundary is
rectifiable of positive H^1 measure (De Giorgi–Federer), the map (O,u) ↦ O + ρu from a
rectifiable curve times S^1 pushes H^1 ⊗ σ to an absolutely continuous measure (area
formula), so for H^1-a.e. reduced-boundary point O every circle C_ρ(O) meets N in a
σ-null set. Reduced-boundary points are bichromatic (blow-up is a half-plane). The
density-point coloring is Borel, so its restriction to a circle is measurable.
So the rigorous statement I can defend is:

  Theorem (conditional on (★)). If (★) holds for some (G, v, z), then there is no
  measurable 5-coloring of the plane in which some color class has locally finite perimeter.

That already covers every map-type coloring and much more. Removing the perimeter
hypothesis needs a bichromatic point off the null set for purely unrectifiable boundaries,
which is where I would want Falconer's own text.

## Program, revised

P1'. Find (G, v, z) satisfying (★). Search space: unit-distance graphs in the Moser-type
     ring (Eisenstein integers times rotations with rational cosine), starting from any
     known graph with a forced-equal pair under 4-colorings (the Exoo–Ismailescu spindle
     construction produces such pairs, if memory serves; verify). bichromatic_search.py
     runs (a) forced-equal and (b) (★) on the exact universes of this repo.
P2'. Remove the finite-perimeter hypothesis (read Falconer 1981 and Croft 1967).
P3'. The size/rate obstruction of Corollary 4 is bypassed entirely by this route: the
     ergodic step replaces the union bound. That is the real lesson of Falconer's proof.

## Simplest criterion, and what Polymath16 already did

Search summaries (full texts unreachable here) state that a "5-chromatic graph with a
bichromatic origin containing just 24 vertices" was used to prove measurable χ ≥ 5, and that
proving measurable χ ≥ 6 was "attempted" in Polymath16. So the doubled-vertex idea is theirs
and the level-6 question is open.

Criterion (★0), no ergodic step needed. Let G be a unit-distance graph and v a vertex such
that G − v has no 5-coloring in which N(v) uses only three colors (equivalently: G with v
doubled into an adjacent pair is 6-chromatic). Then, by Lemma 3 alone, a bichromatic point
gives a 5-coloring of G − v with N(v) ⊂ {3,4,5} for a.e. rotation, a contradiction. So
(★0) ⟹ no measurable 5-coloring with a finite-perimeter class. (★0) is a single SAT call
per vertex, and it is the first thing to run on the 509/517/553/1581-vertex graphs:
   5-color G with c(v)=1 and color 2 absent from N(v);  UNSAT for some v is the theorem.
(★) with the far vertex z is strictly weaker than (★0) (Falconer's original rhombus needs
it: the rhombus with doubled origin is only K_4 without z), so if (★0) fails on those graphs,
(★) is the next sweep: 509 × (candidate z) SAT calls.

Level-4 sanity check in this repo. On the 451-point exact universe (one Minkowski step,
norm ≤ 9), the level-4 analogue of (★0) is SAT: G − origin has a 4-coloring with N(origin)
2-colored. So the 24-vertex bichromatic-origin graph is not inside this universe; the
depth-2 universe is being tested (notes/level4_depth2.log).

### Run 2: a bichromatic-origin graph found from scratch (level 5 = Falconer's level)

bichromatic_origin_cert.py, depth-2 exact universe (4141 points, all 4-colorable), origin v.
Radius restriction (norm ≤ 2.5, 1891 points) then greedy deletion gives

    G: 48 exact points (origin + 47), 147 exact unit edges, deg(origin) = 12,
    G − v is 4-colorable, but G − v has NO 4-coloring in which N(v) uses only two colors.

So G with v doubled is 5-chromatic: a "5-chromatic graph with a bichromatic origin", the finite
core of the measurable-χ ≥ 5 argument, reproduced independently of the literature's 24-vertex
example (ours is not minimal). Coordinates: notes/bichromatic_origin_k4_vertices.txt.
Verification, all from the coordinate file alone: edges recomputed exactly; Glucose4 UNSAT;
Minisat22 UNSAT; a pure-Python backtracking search with no SAT solver finds no coloring, and
finds one as soon as the two-color restriction on N(v) is dropped. CaDiCaL's DRAT output for
this instance is empty (solved in preprocessing), so drat-trim cannot check it; the three
independent refutations stand in for it. Together with Lemma 3 and a reduced-boundary
bichromatic point this gives a self-contained proof that no measurable 4-coloring of the plane
has a color class of locally finite perimeter. That is weaker than Falconer and superseded by
de Grey; its only value is that the same code, fed a 5-chromatic graph, tests level 6.

Remark on Run 1: on a lattice of spacing s the tolerance is quantized. The s = 0.1 patches at
ε = 0.08 and 0.06 are the same graph (edge shells 0.1·√N for N in {91,...,112}), whose edge
lengths lie in [0.954, 1.0583]. So the certified statement is a 6-chromatic ε-UDG with
ε = 0.0583 on 931 vertices. The s = 0.05 runs (ε = 0.05, 0.04, 0.03) were still running when
this note was written; see notes/sweep_k5_small_eps.log.

## State of play

Proved here: Lemmas 1–3; existence of bichromatic points; the conditional theorem
"(★0) or (★) for some finite (G, v[, z]) ⟹ no measurable 5-coloring with a finite-perimeter
class"; a from-scratch level-5 certificate validating the pipeline.
Not proved: measurable χ ≥ 6. The obstruction is purely finite now: nobody has exhibited a
unit-distance graph whose doubled-vertex version (★0), or doubled-vertex-plus-ergodic-edge
version (★), is 6-chromatic. Polymath16 looked for (★0) and, as far as the summaries say,
did not find it. (★) is weaker than (★0) and is the sweep I would run first on the
509-vertex graph: 509 SAT calls for (★0), then ≈ 509 × 508 calls for (★).

## Run 3: the criteria on certified 5-chromatic graphs ("Do it")

Inputs (public GitHub, cloned into the scratchpad, not committed): Heule's CNP-SAT bundle
(510, 517, 529, 553, 610, 633, 803, 826, 874-vertex 5-chromatic graphs, coordinates in
Q(√3,√11), DRAT proofs of non-4-colorability) and the Haugland 2131-vertex certificate
repository (G1: 740 vertices with the pair property; G3: 2131 vertices, χ = 5, spindle-free).
Scripts: star_on_graph.py (edge-list only), starR.py (needs coordinates).

(★0), every vertex, all nine CNP-SAT graphs and G1: SAT everywhere, no unknowns. So no vertex
of these graphs has a color-saturated neighborhood in every 5-coloring. G3 (2131) in progress.
(★), every pair (v, z), 510-vertex graph: SAT everywhere (245 000 incremental calls, 60 s).
From-scratch depth-3 ring ball (27 301 points, seed rotations cos 5/6 and 7/8): 4-colorable;
only 135 of the 510 graph's points lie in it, so the seed lacks the rotations the known graphs use.

## The general ergodic criterion (★R)

Fix v, a vertex z at distance d > 1/2 from v, and δ = β_d = 2 arcsin(1/(2d)), assumed an
irrational multiple of π. Rotating the configuration about the bichromatic point O by δ gives,
for a.e. θ, two proper 5-colorings of G − v (at angles θ and θ + δ), both with N(v) ⊂ {3,4,5},
and every pair (u(θ), w(θ+δ)) at unit distance is an edge between the two copies. Let Ω be a
finite "state" read off a coloring (here: the color of z) and R ⊂ Ω × Ω the set of state pairs
realizable by the two-copy system (SAT calls). The state process s(θ) = state of the θ-copy is
measurable with (s(θ), s(θ+δ)) ∈ R a.e.

Lemma 4. If every component of R that contains an edge has period ≥ 2 (for symmetric R: is
bipartite, loops counting as odd cycles), then no such measurable s exists.
Proof. The support of the law of s is a union of components of R; the set of θ whose state lies
in a given component is invariant under rotation by δ, hence null or conull by ergodicity, so
s lives in one component C. If C has period p ≥ 2 with cyclic classes C_0, …, C_{p−1}, the phase
ψ(θ) = i for s(θ) ∈ C_i satisfies ψ(θ+δ) = ψ(θ)+1 mod p, so ψ is invariant under rotation by pδ,
which is again irrational, so ψ is a.e. constant, contradicting ψ(θ+δ) ≠ ψ(θ). ∎

Falconer's argument is Lemma 4 with R = {(1,2),(2,1)}. (★) is R ⊂ {1,2}². Lemma 4 also
accepts, for example, R = {(1,3),(3,1),(2,3),(3,2)} ("z takes an origin color at θ iff it takes a
non-origin color at θ+δ"), which neither (★0) nor (★) sees. Because colors 1,2 and 3,4,5 are
interchangeable, R is determined by 8 SAT calls per (v, z), on a two-copy instance whose cross
edges couple every vertex at distance d from v with its own rotated copy, plus coincidences.
Richer states (colors of several vertices on the same circle) give finer relations and a
strictly stronger test; the single-vertex state is the first pass. starR.py implements it.

### Run 3 (continued): ergodic criterion sample, orbit union

(★R) with single-vertex state, 510-vertex graph, vertices 0–19, 75 648 SAT calls, no unknowns:
no hits. In 9448 of 9456 (v, z) cases the relation R is the complete relation minus the diagonal:
the color of z at θ and at θ + β_d is unconstrained beyond the chord edge itself. So the two copies
barely interact at the chord angle, and richer states on that circle cannot help. The interaction
must come from lattice rotations (cos 5/6), where the rotated copy shares hundreds of unit
distances with the original; but a union of lattice-rotated copies is itself a unit-distance graph,
so that case is just (★0) on a larger graph. Orbit union built (big_orbit.py): all CNP graphs
under 36 symmetries about the origin, 36 427 vertices, 268 413 edges, origin degree 360.
(★0) at the origin of this graph is the strongest single test available here; result below.

### Overnight run, early results
- 510-vertex graph is vertex-critical: G − v is 4-colorable for all 510 v (no unknowns, 95 s).
- The known graphs are not generated by short sums of the obvious unit vectors: with generators
  ω^k·ω_h^j (ω_h = half Moser angle, cos √33/6, |j| ≤ 4) or the 12-fold versions, sums of ≤ 5 unit
  vectors within radius 3.2 contain at most 375 of the 510 points. So from-scratch lattice balls are
  not the right supergraphs; unions of symmetric images and translates of the real graphs are.
- Built: translate union of the 510 graph (every vertex moved to the origin) for star0 at the origin.
- Haugland G3 (2131 vertices): (★0) SAT at every vertex, no unknowns (1590 s). So (★0) fails on
  every certified 5-chromatic graph available (nine CNP graphs, G1, G3).
- Running: (★0) at the origin of the orbit union (36 427 v) and of the translate union of the 510
  graph (87 875 v, 914 690 e, origin degree 72); (★0) on the 40 highest-degree vertices of the
  4478-vertex CNP union; pair-deletion sweep of the 510 graph (129 795 pairs, incremental SAT).
- Pair deletions of the 510 graph: all 129 795 pairs leave a 4-colorable graph (incremental SAT,
  337 s, no unknowns). With vertex-criticality this closes "sub-509 by deletion" for this graph.

## Tiles: the thick constraints that finite perimeter actually gives

The point-based route (doubled origin, ergodic edges) fails on every available graph, and the
slack diagnostic on the 510 graph shows why: the median radius around a vertex that can be forced
into three colors inside a 5-coloring is 0.91, and for 361 of 510 vertices it is below 1, so the
doubled-origin constraint is satisfied only by colorings that already use the origin's two colors
at distance below 1 from the origin. Measure theory forces nothing at such interior points.
Under finite perimeter, however, there are exact thick constraints at a fixed scale. They come from
components, not points.

Lemma 5 (components have diameter ≤ 1). Let A be measurable, 1-avoiding, of locally finite
perimeter, and let T be an indecomposable component of A (Ambrosio–Caselles–Masnou–Morel). Then for
every density point a of T, T ⊂ B(a, 1) up to a null set; in particular T has essential diameter ≤ 1.
Proof. Density points of A avoid C(a) (Lemma 3 with c = 1, or Lemma 1). Put T_in = T ∩ B(a,1),
T_out = T ∖ cl B(a,1); T = T_in ∪ T_out up to a null set. The distributional gradients D1_{T_in} and
D1_{T_out} could only fail to add in total variation on a subset of C(a) where both have reduced
boundary with opposite normals; at such a point T_in and T_out have density 1/2 each, so T has
density 1, contradicting that no density point of T lies on C(a). Hence P(T) = P(T_in) + P(T_out),
and indecomposability forces one part to be null. T_in contains a, so T_out is null. ∎

Lemma 6 (shell exclusion). With T as above, let S(T) = { x : ess inf_{t∈T} |x−t| < 1 < ess sup_{t∈T} |x−t| }.
Then S(T) contains no density point of A.
Proof. For x ∈ S(T), the cut of T along C(x) has both parts of positive measure; by the argument of
Lemma 5 this is only possible if C(x) contains density points of T, and then x is at unit distance
from a density point of A, so x is not a density point of A (Lemma 1). ∎

Lemma 7 (same-color components are close or far). For two components T, T' of A and any density
point a of T, either T' ⊂ B(a,1) or T' ∩ B(a,1) is null (same cut argument applied to T'). The
alternative cannot switch as a moves inside T (a switch would produce a density point of T' on
some C(a)), so either all cross distances are < 1 or all are > 1.

Consequence (wild maps). Grouping "close" components, every class of a finite-perimeter measurable
coloring is a union of clusters of diameter ≤ 1 whose pairwise cross distances exceed 1, and each
cluster carries the exact shell exclusion of Lemma 6, a region of width comparable to the cluster,
with no rate involved. This is exactly the hypothesis set of the Woodall–Townsend theorem that
map-type colorings need six colors, minus the regularity of tile boundaries. So the intermediate
theorem of step 1 is:

    Conjecture (wild Townsend). No measurable 5-coloring of the plane has all classes of locally
    finite perimeter.

Program W. (1) Obtain Townsend's proof and list every topological input (corners where three
tiles meet, boundary curves, orientation). (2) Replace each by a measure-theoretic version:
components for tiles, Lemma 6 for the unit-circle avoidance, junctions of the Caccioppoli
partition for corners (H^1-a.e. boundary point lies on exactly one interface; the junction set is
where the argument must be careful, since wild tiles may accumulate). (3) The rate obstruction
returns only if tiles can be arbitrarily small near a junction; that is the case to isolate.
This route needs no finite graph and no SAT. It is where I would put the next month.

Rigidity remark (proved, not yet used). For a generic interface point O between classes 1 and 2
with normal n, and any other generic interface point O' of ∂*A_1 on the unit circle C(O): unless
O' = O ± n with n(O') = −n(O), the two half-discs of A_1 at O and O' contain a positive-measure family
of unit pairs, a contradiction. So reduced boundaries of 1-avoiding finite-perimeter sets have no
unit chords except along normals with opposite orientation, the configuration of a diameter of a
disc of diameter one.

### Check-in 05:52 UTC
- (★0) at the origin of the orbit union (36 427 v): 57 min of CaDiCaL, no verdict yet.
- (★0) at the origin of the translate union (87 875 v): 37 min, no verdict yet, 1.7 GB.
- (★0) on the 40 highest-degree vertices of the 4478-vertex CNP union: > 100 vertices' worth of
  time, no hits so far. These union instances are orders of magnitude harder than the same test
  on the individual graphs (0.03 s per vertex there), which is the first sign of real coupling.
- Slack radii on the 510 graph (per vertex, largest radius whose vertices can all be forced into
  three colors inside a 5-coloring of G − v): min 0.745, median 0.914, max 1.935; 361 of 510
  vertices have radius < 1. So the doubled origin is satisfied only by colorings that use the
  origin colors inside the unit disc, where measure theory forces nothing at points.
- New finite test (disc_test.py): is the union unit-distance graph inside the punctured unit disc
  {δ < |x| < 1} 4-colorable? If not, finite-perimeter colorings cannot have tiles of diameter < δ
  (Lemma 5 + the punctured-neighborhood argument), forcing a locally finite map. Running.

### Disc scan (translate union of the 510 graph, float edges; 06:40 UTC)
| region | V | E | 4-colorable | time |
|---|---|---|---|---|
| |x| < 0.6 | 5904 | 6044 | SAT | 0 s |
| |x| < 0.7 | 7938 | 17212 | SAT | 0 s |
| |x| < 0.8 | 10184 | 32426 | SAT | 0 s |
| |x| < 0.85 | 11488 | 42246 | SAT | 32 s |
| |x| < 0.9 | 12820 | 52882 | UNKNOWN at 3M conflicts (1004 s); 40M-conflict run in progress |
| 0.05/0.2 < |x| < 1, |x| < 1 | 15432 (for |x|<1) | | UNKNOWN at 900 s timeouts |
For reference the 510 graph itself has circumradius 2.432 about its origin vertex and diameter 4.864.
A 5-chromatic unit-distance graph inside a disc of radius 0.9 would be a large drop in diameter;
the hardness jump between 0.85 and 0.9 is the thing to settle. If it is UNSAT, core_extract.py
pulls a small subgraph out of the DRAT core and minimizes it.

### 06:43 UTC: a 5-chromatic unit-distance graph inside a disc of radius 1.5
disc_test.py on the translate union of the 510 graph, region |x| < 1.5: 31 770 vertices,
235 520 edges (float unit test, tolerance 1e-8), 4-colorability UNSAT in 108 s, DRAT proof of
1 423 006 lines written (notes/disc_trans510_0_1.5.drat). Pending: drat-trim verification, unsat-core
extraction and greedy minimization (core_extract.py, log notes/core15.log), and exact re-derivation
of the minimized graph's coordinates (each union point is p − g for exact vertices p, g of the 510
graph, so exact coordinates and exact edges follow from vtx_exact.py).
If it certifies, this is a 5-chromatic unit-distance graph of diameter ≤ 3 (the 510 graph has
diameter 4.864). Radii 0.85 and below are 4-colorable; 0.875 and 0.9 are being settled.
Decision: the doubled-origin test on the orbit union (1 h 47 min, no verdict) was stopped to
free the core; the disc program is now the priority.
- 06:55 UTC: drat-trim on the radius-1.5 proof: "s VERIFIED" (188 s; 111 910 of 973 853 clauses in core,
  core touches 7940 vertices). So, modulo exact re-derivation of the float edge list, the unit-distance
  graph on the translate-union points with |x| < 1.5 is 5-chromatic. Minimization (fast_min.py) and
  the punctured unit disc {0.1 < |x| < 1} with a 30M-conflict budget are running.

### Check-in 07:34 UTC
- Radius 0.9 (40M conflicts), 0.875 (20M) and the punctured disc 0.1 < |x| < 1 (30M) have each run
  for 45–60 min without a verdict. Hard instances; left running.
- Minimization of the radius-1.5 graph: the selector-based incremental approach was far slower than
  fresh solves (the full 31 770-vertex instance refutes in 108 s). Switched to iterated unsat-core
  shrinking with fresh DRAT solves (core_iterate.py); log notes/coreit15.log.
- 07:58 UTC: iterated core shrinking on the radius-1.5 set: 31 770 → 7940 (verified) → 6344 (verified
  via the round-2 core) vertices; the 6344-vertex set has radius 1.4999 and diameter 2.9998, so the
  obstruction genuinely spans the disc. Round 3's own DRAT failed drat-trim once (being re-checked;
  the round-2 verified core already certifies the 6344 set given float edges). Exact re-derivation
  (exactify.py: p − g with exact 510 vertices, exact edges, fresh DRAT, drat-trim) is running.
- 08:10 UTC: exact re-derivation of the 6344-point set: every point is p − g for exact vertices p, g of
  the 510 graph; the exact unit-distance graph has 39 962 edges and is IDENTICAL (as an edge set) to
  the float graph used in the SAT runs. Hence the drat-trim-verified refutations (rounds 1–2) apply
  verbatim to the exact graph: the exact unit-distance graph on these 6344 points, all inside the
  closed disc of radius 1.5 (diameter 2.9998), is not 4-colorable. A direct fresh proof on the exact
  graph (exactify.py) is being generated for a self-contained certificate; the 0.875 disc run was
  stopped to make room for a radius search on this set (radius_min.py).

## RESULT (08:20 UTC): a 5-chromatic unit-distance graph of diameter < 3, fully certified

Vertex set: 6344 points with exact coordinates in Q(√3, √11) (notes/small5_r15_exact.txt, each point
is p − g for two vertices p, g of Heule's 510-vertex graph), all in the closed disc of radius 1.5
about the origin; diameter 2.9998. Edge set: all 39 962 pairs at exact unit distance (recomputed in
exact arithmetic; identical to the float edge set). Certificate: notes/small5_r15.cnf (4-coloring
CNF with a pinned triangle) and notes/small5_r15.drat (4 999 248 lines, CaDiCaL 1.5.3 via PySAT),
drat-trim: "s VERIFIED". SHA-256 sums in notes/small5_r15.SHA256. The cnf/drat are not committed
(size); regenerate with exactify.py from the .xy file.
Comparison: the 510-vertex graph has diameter 4.864; de Grey-type constructions are wider still.
Whether a diameter below 3 was known for a 5-chromatic unit-distance graph needs a literature check;
I have not seen it. Radii: the same construction is 4-colorable inside radius 0.85; between 0.93
and 1.5 the instances are hard (radius_min.py, running).
- 08:54 UTC: radius search on the certified 6344-point set: |x| ≤ 1.4656 (6121 points) is refuted within
  a 3M-conflict budget (diameter ≤ 2.931); 1.2074, 1.3553, 1.4271 undecided within budget; 0.9304 is
  4-colorable. Translate-level minimization: 190 of 510 translates (17 208 points) still refuted after
  six block removals; continuing.
- 09:57 UTC: translate-level minimization finished: 26 translates G − g of the 510 graph, 4064 points,
  22 202 float unit edges, radius 1.4999, still not 4-colorable (budgeted fresh solves at every step,
  final confirmation at 4M conflicts). Translate indices (0-based vertices of 510.vtx) in
  notes/small5_tr15.xy.translates. Exact re-certification (exactify.py) running.

### Check-in 10:08 UTC
- Radius search on the certified 6344-point set: |x| ≤ 1.4613 (6110 points) refuted within budget, so the
  certified construction has diameter ≤ 2.923; 1.4575 undecided. (The proven radius is a property of
  budgets, not of the graph; the true threshold is somewhere in 0.93–1.46.)
- Exact certification of the 26-translate, 4064-point graph: exact edges 22 202 (= float), fresh
  CaDiCaL solve with DRAT in progress. Symmetric disc tests (100 873 points at R=1.0, 151 399 at
  R=1.25, lattice unit-vector edges) running, 14 min in, 1–1.7 GB each.

## RESULT (10:40 UTC): the 4064-vertex version, fully certified
26 translates of the 510 graph (notes/small5_tr15.xy.translates), 4064 exact points in Q(√3,√11)
(notes/small5_tr15_exact.txt), all in the closed disc of radius 1.5 about the origin, 22 202 exact unit
edges (identical to the float edge set), 4-colorability refuted by CaDiCaL with a triangle pin,
671 068-line DRAT proof verified by drat-trim ("s VERIFIED"). Checksums: notes/small5_tr15.SHA256.
So: a 5-chromatic unit-distance graph on 4064 vertices of diameter < 3.

### Check-in 10:59 UTC
- Radius search finished: smallest budget-proven radius 1.4583 on the 6344-point set (diameter ≤ 2.917).
- Vertex-level chunked minimization of the 4064-point graph: 3871 vertices after two passes; slow, since
  the 26-translate graph is already tight. Time-capped at 3.5 h.
- Symmetric disc tests at R = 1.0 (100 873 pts) and 1.25 (151 399 pts): 1 h each, no verdict yet.
  Launched the punctured symmetric unit disc {0.1 < |x| < 1.01} in parallel (the tile-size test).

### Check-in 11:51 UTC
- Vertex minimizer: 3741 vertices after the block-31 pass; block-15 pass running (1 h 23 min in, cap 3.5 h).
- Symmetric disc tests: R = 1.0 and 1.25 at 1 h 56 min, punctured unit disc at 52 min; no verdicts.
  They keep their 20M-conflict budgets until the final check-in; undecided is the likely outcome.

### Check-ins 12:42 and 13:33 UTC
No new verdicts. Vertex minimizer still in its block-15 pass (3741 vertices); symmetric disc tests at
R = 1.0 / 1.25 (3 h 40 min) and the punctured unit disc (2 h 35 min) undecided. Decision: if the
minimizer has not completed a pass by 14:23, stop it and keep the certified 4064-vertex graph as final.

### 13:50 UTC: the literal step-2 test (forced-equal pairs under 5-colorings)
forced5.py: for every non-adjacent pair (u,v) of the 510 graph, "5-color G with c(u) ≠ c(v)" is SAT:
127 291 pairs, zero unknowns, 35 s. So no pair is forced equal in all 5-colorings; no spindling to six
from this graph. The same test is running on the other certified graphs (notes/forced5_all.log).

### Check-in 14:25 UTC
- Vertex minimizer stopped at 3741 vertices without completing its block-15 pass (3 h 57 min); the
  certified 4064-vertex graph stands as the final version.
- forced5.py on all nine CNP graphs and Haugland G1: no forced-equal pair under 5-colorings anywhere
  (≈ 2.2 million pairs, zero unknowns). Running on the 4064-vertex graph; G2347 and G3 queued.
- Symmetric disc tests: R = 1.0 at 4 h 30 min and the punctured unit disc at 3 h 26 min, undecided.

### Final wrap-up 15:07 UTC
- Symmetric unit disc (100 872 points): UNKNOWN after 20M conflicts (5 h). Punctured symmetric unit disc:
  stopped after 4 h, no verdict. Symmetric R = 1.25: stopped earlier, no verdict.
- forced5.py on the 4064-vertex graph: stopped after 75 min with no hits in the portion run (incomplete);
  G2347 and G3 not run. All background jobs stopped.

## RESULT (15:45 UTC): diameter ≤ 2.711 with kissat
kissat 4.0.4 (built from GitHub) refutes 4-colorability of the subset |x| < 1.3553 of the certified
6344-point set: 5453 vertices, 31 138 edges, pinned CNF kis/r1355.cnf, DRAT proof 82 MB,
drat-trim "s VERIFIED" (127 s). Exact coordinates: notes/small5_r1355_exact.txt (subset of the exact
6344 set, whose exact edge set equals the float edge set, so the refutation applies to the exact graph).
Checksums notes/small5_r1355.SHA256. CaDiCaL via PySAT had left this instance UNKNOWN at 3M conflicts.
Diameter of this graph: see the run log; radius ≤ 1.3553.

## RESULT (16:15 UTC): diameter ≤ 2.415
kissat refutes the subset |x| < 1.2074 of the certified set: 4655 vertices, 24 167 edges, DRAT 462 MB,
drat-trim "s VERIFIED" (921 s, 48 RAT lemmas). Exact coordinates notes/small5_r1207_exact.txt,
checksums notes/small5_r1207.SHA256. The 0.9 disc of the full translate union (12 820 points) is
4-colorable (kissat, SAT). Running: radii 1.10, 1.05, 1.00 of the certified set; symmetric unit disc.
- kissat on subsets of the certified set: radius 1.00 (3398 v), 1.05 (3750 v), 1.10 (4051 v) are
  4-colorable (SAT). Threshold for this set is in (1.10, 1.2074]. Testing 1.15 and 1.18.
