#!/bin/bash
# Off-lattice n=8 hunt, done properly.
#  - TIME-BOUNDED (5400 s per seed), so it always completes and records how many
#    restarts it actually managed. No more predicting the restart count.
#  - FRESH SEEDS. numpy seeding is deterministic, so reusing 101..606 would redraw the
#    identical configurations the previous capped run already covered.
#  - shell cap 7200 s, giving 33% headroom over the internal budget.
cd "$(dirname "$0")"
for s in 1301 1302 1303 1304 1305 1306; do
  python -u numsearch.py 8 6 1000000 $s 5400 > off8b_$s.log 2>&1 &
done
wait
echo "=== all seeds exited ==="
grep -h "restarts actually done" off8b_*.log
grep -h "genuine polished hits" off8b_*.log
grep -h "best raw objective" off8b_*.log
