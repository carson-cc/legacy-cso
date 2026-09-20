#!/bin/bash
# 5-colorability sweep of eps-UDG lattice patches. Each line of the log is one verdict.
cd /home/user/legacy-cso/math
LOG=notes/sweep_k5.log
run(){ python3 eps_udg.py "$@" >> $LOG 2>&1; }
for eps in 0.30 0.25 0.20 0.15 0.10 0.05; do
  run 0.2 2.0 $eps 5 3000000
done
for eps in 0.30 0.25 0.20 0.15 0.10; do
  run 0.1 1.6 $eps 5 3000000
done
echo SWEEP_DONE >> $LOG
