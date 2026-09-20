# Overnight autonomous run (started 2026-09-20 ~05:15 UTC, ends ~15:15 UTC)

Mission: make progress toward measurable chi(plane) >= 6 via the bichromatic-origin route
(criteria star0 / star / starR on 5-chromatic unit-distance graphs), and secondarily toward a
sub-509 5-chromatic graph with the surgery tool. Decide autonomously; commit and push as results
land; leave a summary in notes/overnight_summary.md.

## Queue (highest value first)
1. [running] star0 at the origin of the 36k-vertex orbit union (notes/star_orbit.log), then the
   slack radius measurement (notes/slack_orbit.log).
2. [running] star0 on every vertex of Haugland G3 (notes/star_haugland.log) and of the 4478-vertex
   CNP union (notes/star_big.log, then G2347).
3. [todo] Correct Moser-lattice ball: seed unit vectors w^k w1^j, |j|<=2, depth 4-5, radius cap;
   verify it contains the 510 graph; 4-colorability (expect UNSAT = from-scratch 5-chromatic, DRAT);
   star0 at its origin and at sampled vertices. This is the definitive test in this ring.
4. [todo] star0 on orbit unions centered at other vertices (sample of centers).
5. [running, 1 core] 508 program on the 510 graph: vertex-criticality (each G-v 4-colorable?),
   then pair deletions with a conflict budget (a non-4-colorable G-{u,v} would be a 508-vertex
   record), then delete-3/add-1 with the deletion-coloring filter if time permits.
6. [always] every check-in: read logs, record results in measurable_six.md, commit, push,
   re-arm the next check-in (send_later, ~50 min) until the end time.

## Decision rules
- UNKNOWN is never reported as UNSAT. Any UNSAT that matters gets an independent re-check
  (second solver + DRAT when available) before being called a result.
- Prefer finishing a running high-value job over starting a new one; keep all 4 cores busy.
- If a star0/starR hit appears anywhere: stop everything else, re-verify exactly, write it up.
