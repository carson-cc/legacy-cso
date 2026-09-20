# Overnight summary (autonomous run, 2026-09-20 05:00–15:07 UTC) — FINAL

## Headline
A fully certified 5-chromatic unit-distance graph of diameter 2.296 (the 510-vertex graph has 4.864).
Chain of certified versions, all subsets of the same exact point set (points p − g for vertices p, g of
Heule's 510-vertex graph, coordinates in Q(√3,√11); exact edge set identical to the float edge set):
| radius | vertices | edges | diameter | solver | proof | checker |
|---|---|---|---|---|---|---|
| 1.15  | 4341 | 21 378 | 2.296 | kissat 4.0.4 | 2.6 GB DRAT | drat-trim VERIFIED (5865 s) |
| 1.18  | 4493 | 22 770 | 2.356 | kissat | 919 MB | VERIFIED (1620 s) |
| 1.2074| 4655 | 24 167 | 2.415 | kissat | 462 MB | VERIFIED (921 s) |
| 1.3553| 5453 | 31 138 | 2.710 | kissat | 82 MB | VERIFIED (127 s) |
| 1.5 (26 translates) | 4064 | 22 202 | < 3 | CaDiCaL | 671 068 lines | VERIFIED |
| 1.5 | 6344 | 39 962 | < 3 | CaDiCaL | 4 999 248 lines | VERIFIED |
Radius 1.10 of the same set is 4-colorable (kissat SAT), so this set's threshold is in (1.10, 1.15].
Files: notes/small5_r115_exact.txt (and r118, r1207, r1355, tr15, r15), *.SHA256 checksums; the
CNF/DRAT files are regenerable (export_cnf.py + kissat, or exactify.py). Literature: nothing found on
the minimum diameter of a 5-chromatic unit-distance graph; verify before claiming novelty.

## The six mission: where it stands
- Doubled-origin criteria (★0), (★), (★R): fail on every certified 5-chromatic graph available
  (nine CNP-SAT graphs 510–874, Haugland G1 740 and G3 2131), with zero unknowns. On unions
  (4478-vertex CNP union, 36k orbit union, 88k translate union) the instances become very hard and
  gave no verdict in 1–2 h. Per-vertex slack radii on the 510 graph (median 0.91) show why: the
  colorings that satisfy the doubled origin already use the origin's colors inside the unit disc.
- Theory added tonight: Lemmas 5–7 (finite-perimeter classes are unions of tiles of diameter ≤ 1,
  same-color tiles close or far, exact shell exclusion). Program W ("wild Townsend") is the
  recommended route to "no measurable 5-coloring with finite-perimeter classes".
- The disc program is the finite lever for Program W: a 5-chromatic graph inside the punctured
  unit disc would force tiles to have diameter ≥ δ (locally finite map). Achieved radius 1.5 (above);
  radius ≤ 0.85 is 4-colorable; 0.9–1.36 undecided within budgets.

## The 508 mission
510 graph is vertex-critical; all 129 795 pair deletions are 4-colorable. No sub-509 by deletion.

## Step-2 literal test (forced-equal pairs under 5-colorings)
forced5.py: on the 510, 517, 529, 553, 610, 633, 803, 826, 874-vertex graphs and Haugland's G1, every
non-adjacent pair can be colored differently in some 5-coloring (about 2.2 million pairs, zero unknowns,
seconds per graph). So none of these graphs spindles to six. The 4064-vertex graph's sweep was stopped incomplete after 75 min (no hits in the portion run);
G2347 and G3 were not run.

## Literature status
Searches reachable from the sandbox (arXiv, ScienceDirect and the Polymath blogs are blocked by the
proxy; only search summaries were available): Falconer 1981 (measurable ≥ 5), Polymath16 used a
24-vertex "5-chromatic graph with a bichromatic origin" for measurable 5 and attempted 6; the ε-unit
distance graph is known to need ≥ 6, and arXiv:2304.10163 claims ≥ 7 for a forbidden interval; nothing
found on the minimum diameter of a 5-chromatic unit-distance graph. Verify before citing.

## Files (math/)
- notes/measurable_six.md: all lemmas (1–7), criteria (★0)/(★)/(★R), Program W, every run with numbers.
- notes/small5_tr15_exact.txt, small5_tr15.xy, small5_tr15.xy.translates, small5_tr15.SHA256,
  data/small5_tr15.edge: the certified 4064-vertex diameter<3 graph. cnf/drat regenerable via exactify.py.
- notes/small5_r15_exact.txt, small5_r15.xy, small5_r15.SHA256: the 6344-vertex version.
- notes/bichromatic_origin_k4_vertices.txt: the 48-vertex level-5 (Falconer-level) certificate.
- Scripts: surgery.py, udg.py (exact field incl. division), vtx_exact.py, star_on_graph.py, starR.py,
  bichromatic_search.py, big_orbit.py, big_translates.py, big_sym_disc2.py, disc_test.py,
  core_iterate.py, translate_min.py, chunk_min.py, radius_min.py, exactify.py, forced5.py, pairs.py,
  critical.py, slack510.py, eps_udg.py, verify_eps.py.
- Logs: notes/*.log (re-added at the end of the run).
External inputs (not committed; cloned into the scratchpad): github.com/marijnheule/CNP-SAT,
github.com/Amberlogy/haugland-2131-certificates, github.com/marijnheule/drat-trim.

## Final state of the disc program
|x| < 1.5 (translate union): 5-chromatic, certified (the headline). |x| ≤ 0.85: 4-colorable.
0.93–1.46: undecided within budgets. Symmetry-closed sets at R = 1.0 (100 872 points) and 1.25
(151 399) and the punctured unit disc: undecided after 4–5 h each with 20M-conflict budgets.

## What to do next (my recommendation)
1. Literature check on the diameter result (minimum diameter of a 5-chromatic unit-distance graph);
   if new, write it up with the certificate files (coordinates, cnf, drat, checksums, regeneration script).
2. Program W (wild Townsend): get Townsend's paper, list its topological inputs, replace them with
   Lemmas 5–7 (tiles, close/far, shell exclusion). This is the route to "no measurable 5-coloring
   with finite-perimeter classes" and needs no SAT.
3. The finite lever for W is a 5-chromatic graph in a punctured unit disc. The gap is radius 1.5 → 1.0.
   Cube-and-conquer (march_cu + kissat) on the symmetric unit-disc instance is the natural next attempt;
   the sandbox solver could not decide it in 5 h.
4. Bichromatic-origin criteria on known graphs are exhausted (all negative, zero unknowns); do not
   spend more compute there without a graph designed for saturation.
5. The 510 graph: vertex-critical, no deletable pair, no forced-equal pair under 5-colorings.
