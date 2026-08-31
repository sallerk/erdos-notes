#!/bin/bash
# Small single-process ladder for Erdos #217 at n = 9.
#
# An earlier version began with `source "../tools/env.sh"`, which set up a MinGW and
# nauty PATH on the author's machine.  That file is not part of this repository, so the
# script failed with exit 2 for anyone who cloned it.  It is now self-contained: build
# the binary yourself (see REPRODUCE.md) and run this from the directory containing it.
#
# For the real sharded ladder use super217.py instead, which runs shards as independent
# processes and records a health checkpoint:
#     python super217.py 9 5 100 144 196 256 324 400
#
# Usage: ./ladder.sh [R2 ...]     default: 25 64 81 100

set -u

if [ ! -x ./crescent2.exe ] && [ ! -x ./crescent2 ]; then
    echo "crescent2 binary not found. Build it first:" >&2
    echo "    gcc -O3 -march=native -o crescent2.exe crescent2.c" >&2
    exit 1
fi
BIN=./crescent2.exe
[ -x "$BIN" ] || BIN=./crescent2

for R2 in "${@:-25 64 81 100}"; do
    "$BIN" 9 "$R2" "c2_n9_R$R2.txt" 0 1 2>&1 | tail -1 | tee -a ladder.log
done
