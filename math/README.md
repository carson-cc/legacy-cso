# 508 attack: certified delete-and-replace surgery

`surgery.py` is a standalone, validated tool for trying to beat the 509-vertex record
(smallest known 5-chromatic unit-distance graph, Parts 2020) by producing a 508-or-smaller
graph that is still not 4-colorable.

## What it does
Delete d vertices, add r exact unit-distance replacement points (net size r-d), and check
by SAT whether the result stays non-4-colorable. Every unit edge is recomputed from exact
coordinates. Candidates are filtered by whether they break a surviving 4-coloring of the
deleted graph (a point that can't break the coloring can't restore the obstruction).

## Validated
Runs on the Moser spindle (k=4 analog): correctly classifies colorability, emits DRAT,
enumerates and filters candidates, and finds a certified delete-1/add-1 restoration.

## To actually attempt 508 you need two things this sandbox does not have
1. The exact Parts-509 coordinates (arXiv:2010.12665 / Parts's data), loaded as exact
   `P` points. The tool operates on whatever exact graph you hand it; it does not ship the
   Parts graph.
2. Real hardware and days of compute. On a single core this cannot finish the interesting
   sweeps. For a real attempt:
   - swap the oracle to kissat + march_cu (cube-and-conquer) instead of pysat,
   - run `want_proof=True` and check every UNSAT with drat-trim / cake_lpr,
   - parallelize the candidate loop across workers,
   - the highest-value unfinished sweep on record is the ~385 filtered two-point restorations
     of G509 minus vertex 100 (delete 1, add 2); `delete_replace(..., add=2)` is that search.

## Honest odds
Delete-2/add-1 is reported closed (all 4-colorable) in prior work. The live front is the
two-point restorations. No sub-509 graph is known. A result only counts with a machine-checked
non-4-colorability certificate plus a verified exact embedding.

## Running
```
pip install -r requirements.txt
python3 udg.py        # exact-arithmetic self-checks
python3 surgery.py    # Moser spindle validation run
```

`udg.py` supplies the exact geometry (`F` = elements of Q(sqrt d), `P` = exact points,
rotations via `unit_from_cos`, `HEX7`, `OMEGA`, `minkowski`). Do not add an `__init__.py`
to this folder: as a plain directory it cannot shadow the standard-library `math` module.

Note: in the validation run the single certified restoration is the deleted vertex itself
being re-added, since the candidate universe contains it. For a real sweep, exclude the
deleted vertices from the universe or the trivial hit will always appear.
