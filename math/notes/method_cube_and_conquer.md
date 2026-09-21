# Method note: cube-and-conquer with per-cube checked proofs for unit-distance colouring instances

## Status and scope
This note records the one thing from the disc program that is worth keeping: a small, fully
checkable cube-and-conquer pipeline that decided colouring instances which single-run CDCL left
undecided for hours. The geometric results it produced (5-chromatic unit-distance graphs inside discs
of radius 1.15 and, if the final run completes, 1.125) are NOT new: Polymath16 tracked the radius of
5-chromatic graphs and its record is below radius 1.10 (checked by the user on the Polymath pages,
which are unreachable from this machine). The certificates remain valid computations; no novelty is
claimed for them.

## The instances
Pinned 4-colouring CNFs of unit-distance graphs (variable v*4+c+1 = "vertex v has colour c", one
at-least-one clause per vertex, one binary clause per edge and colour, one triangle pinned to colours
0,1,2 to kill the colour symmetry). Typical sizes: 4 000–20 000 vertices, 20 000–100 000 edges.
Single-run kissat 4.0.4 refuted the radius-1.15 instance (4341 vertices) in 52 min with a 2.6 GB DRAT
proof, and was still undecided on the radius-1.125 instance (4196 vertices) after 3 h 20 min, when its
9.4 GB proof file filled the disk.

## The split (cube_manual.py)
march_cu (the standard cuber) crashed or stalled on these instances. Instead the cubes are colourings
of a small dense induced subgraph: starting from the pinned triangle, repeatedly add the vertex with the
most edges into the set chosen so far (ties by degree). The cubes are all proper colourings of the
induced subgraph on the s chosen vertices (enumerated by backtracking). Choosing high-degree vertices
without the density criterion gives 4^s free cubes with no pruning and no useful propagation.
| instance | s | cubes | mean time per cube |
|---|---|---|---|
| radius 1.125, 4196 vertices | 12 | 1 688 | 2.7 s (a few cubes take minutes) |
| radius 1.125 | 20 | 27 383 | (used only to refine the hard cubes) |
| radius 1.10 on the unminimised 18 348-vertex set | 16 | 9 670 | most 1–10 s, some > 15 min |

## The driver (cc.py)
- W workers; each cube is solved by kissat on CNF + the cube's unit clauses with a time limit.
- With drat-trim given, every cube is solved with a DRAT proof and the proof is checked by drat-trim
  against CNF + cube; the cube counts as UNSAT only on "VERIFIED", and the proof is deleted afterwards,
  so disk use stays bounded (the monolithic proof would have exceeded the disk).
- Cubes that time out are refined: they are replaced by the cubes of a deeper split file (same greedy
  order, so deeper cubes extend shallower ones) and solved again; leftovers get one pass at 4x the limit.
- Verdicts are appended to verdicts.txt keyed by the cube's literals, so a run can be stopped and
  resumed; the decided leaf cubes are written to leaves.icnf.

## The certificate and its independent check (cube_cover_check.py)
The refutation of the whole CNF consists of (a) the CNF, (b) leaves.icnf, (c) a drat-trim VERIFIED
verdict for CNF + each leaf. What has to be checked independently is that the leaves cover every case:
cube_cover_check.py re-enumerates, by backtracking over the CNF's own unit and binary clauses, every
assignment of colours to the union of the split vertices that violates no such clause, and asserts that
each one satisfies some leaf cube. Assignments that violate a clause are refuted by the CNF itself, so
"all leaves UNSAT" implies "CNF UNSAT". The check runs in under a second for 12–20 split vertices.
Geometry is certified separately: exact_subset.py recomputes the exact unit-distance edges of the exact
coordinates (multiquadratic field arithmetic, udg.py) and checks they coincide with the CNF's binary
clauses under the float-coordinate bijection.

## Numbers observed
- radius 1.125 (4196 vertices): single kissat run undecided at 3 h 20 min; cube-and-conquer on 3 cores
  refuted and proof-checked 1 200+ of 1 688 cubes in the first 100 min, no SAT cube. (Final tally: see
  notes/measurable_six.md.)
- radius 1.10 on the 18 348-vertex unminimised translate union (single-run status unknown): pilot cubes
  refuted in 1–10 s each, with a minority of hard cubes; run stopped after 120 refuted cubes when the
  prior-art check made the target moot.
- unit disc, 15 431 vertices: pilot cubes undecided at 15 min each; not pursued.

## What to reuse
cube_manual.py, cc.py, cube_cover_check.py, exact_subset.py, export_cnf.py. Usage lines are in the
docstrings. Solver binaries: kissat (github.com/arminbiere/kissat), drat-trim (github.com/marijnheule/drat-trim).
