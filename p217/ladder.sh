#!/bin/bash
source "../tools/env.sh"
for R2 in 25 64 81 100; do
  ./crescent2.exe 9 $R2 c2_n9_R$R2.txt 0 1 2>&1 | tail -1 | tee -a ladder.log
done
