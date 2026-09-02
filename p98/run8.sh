#!/bin/bash
# 7 shards of the n=8 hunt. A witness from ANY shard settles the upper bound;
# a NEGATIVE requires every shard to write its completion artefact (L63).
cd "$(dirname "$0")"
for s in 0 1 2 3 4 5 6; do
  python -u latmin2.py 8 49 a2 7 $s 7 > lat2_n8_s$s.log 2>&1 &
done
wait
echo "=== all shards exited ==="
ls lat2_n8_a2_R49_s*.json 2>/dev/null | wc -l
