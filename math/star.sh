#!/bin/bash
cd /home/user/legacy-cso/math
LOG=notes/star_search.log
python3 bichromatic_search.py 1 16 >> $LOG 2>&1
python3 bichromatic_search.py 1 25 >> $LOG 2>&1
echo STAR_DONE >> $LOG
