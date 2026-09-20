#!/bin/bash
# 4-colorability at small tolerance (Exoo-type bound check), finer lattice.
cd /home/user/legacy-cso/math
LOG=notes/sweep_k4.log
run(){ python3 eps_udg.py "$@" >> $LOG 2>&1; }
run 0.1 1.6 0.05 4 3000000
run 0.1 1.6 0.03 4 3000000
run 0.05 1.3 0.02 4 3000000
echo SWEEP4_DONE >> $LOG
