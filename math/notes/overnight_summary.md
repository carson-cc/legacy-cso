# Overnight summary (autonomous run, 2026-09-20 ~05:00–15:00 UTC) — DRAFT, finalized at the last check-in

## Headline
A fully certified 5-chromatic unit-distance graph of diameter < 3: 6344 exact points in Q(√3,√11),
all within the closed disc of radius 1.5, 39 962 exact unit edges, 4-colorability refuted by CaDiCaL
with a 4 999 248-line DRAT proof verified by drat-trim. Files: notes/small5_r15_exact.txt (exact
coordinates), notes/small5_r15.xy (float), notes/small5_r15.SHA256 (checksums of cnf/drat/coords).
Regenerate cnf/drat with: python3 exactify.py notes/small5_r15.xy <510.vtx> <drat-trim>.
Construction: union over all vertices g of Heule's 510-vertex graph of the translates G − g, restricted
to |x| < 1.5 (big_translates.py + disc_test.py), then iterated unsat-core shrinking (core_iterate.py).

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

## Literature status
(filled at the end)

## Everything else (files, scripts, logs)
(filled at the end)
