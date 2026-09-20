# Overnight summary (autonomous run, 2026-09-20 ~05:00–15:00 UTC) — DRAFT, finalized at the last check-in

## Headline
A fully certified 5-chromatic unit-distance graph of diameter < 3. Two certified versions:
- 4064 vertices: 26 translates G − g of Heule's 510-vertex graph, restricted to |x| < 1.5; exact
  coordinates in Q(√3,√11) (notes/small5_tr15_exact.txt), 22 202 exact unit edges, radius 1.4999,
  diameter < 3; refutation of 4-colorability by CaDiCaL with a triangle pin, 671 068-line DRAT proof,
  drat-trim "s VERIFIED". Checksums notes/small5_tr15.SHA256; translate list notes/small5_tr15.xy.translates.
- 6344 vertices (earlier, larger version): notes/small5_r15_exact.txt, 39 962 edges, 4 999 248-line DRAT,
  verified. A sub-disc of radius 1.4583 of this set is also refuted (budgeted), diameter ≤ 2.917.
For comparison the 510-vertex graph itself has diameter 4.864. Regenerate proofs with
python3 exactify.py <xy> <510.vtx> <drat-trim>. The construction is big_translates.py + disc_test.py,
then core_iterate.py / translate_min.py / chunk_min.py.

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
seconds per graph). So none of these graphs spindles to six. (4064-vertex graph, 2347, G3: see
notes/forced5_all.log for the final entries.)

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
