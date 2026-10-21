#!/bin/bash
# Launch one part of the experiment suite in the background (GNU Octave), e.g.
#   tools/run_parallel.sh A "RUN=[2 6];"
#   tools/run_parallel.sh B "RUN=[4 12]; MC_PART='certain';"
# Each part writes its own CSVs to matlab/results/ and its log to matlab/results/run_log_<tag>.txt.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/matlab" || exit 1
nohup octave --no-gui -q --eval "LOGTAG='_$1'; $2 run('main_run_all.m');" > "$ROOT/matlab/results/stdout_$1.txt" 2>&1 &
echo "part $1 started (pid $!)"
