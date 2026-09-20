#!/bin/bash
cd /home/user/legacy-cso/math
LOG=notes/sweep_k5_small_eps.log
run(){ python3 eps_udg.py "$@" >> $LOG 2>&1; }
run 0.1 1.6 0.08 5 4000000
run 0.1 1.6 0.06 5 4000000
run 0.1 2.0 0.06 5 4000000
run 0.05 1.4 0.05 5 4000000
run 0.05 1.4 0.04 5 4000000
run 0.05 1.4 0.03 5 4000000
echo SWEEP2_DONE >> $LOG
