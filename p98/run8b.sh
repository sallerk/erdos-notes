#!/bin/bash
cd "$(dirname "$0")"
for s in 0 1 2 3 4 5 6; do
  python -u latmin2.py 8 121 a2 7 $s 7 > lat2_n8b_s$s.log 2>&1 &
done
wait
echo "=== all shards exited ==="
