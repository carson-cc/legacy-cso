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
