#!/bin/bash
# Run a list of experiment parts with at most P concurrent GNU Octave processes.
#   tools/run_queue.sh P jobs.txt     (each line: <tag>|<octave settings before run('main_run_all.m')>)
# Logs: matlab/results/stdout_<tag>.txt ; the queue itself waits until every job has finished.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; P=$1; JOBS="$(realpath "$2")"
cd "$ROOT/matlab" || exit 1
grep -v '^\s*#' "$JOBS" | grep -v '^\s*$' | while IFS='|' read -r tag cmd; do printf '%s\0%s\0' "$tag" "$cmd"; done |
  xargs -0 -r -n 2 -P "$P" bash -c 'octave --no-gui -q --eval "LOGTAG='"'"'_$0'"'"'; $1 run('"'"'main_run_all.m'"'"');" > "'"$ROOT"'/matlab/results/stdout_$0.txt" 2>&1; echo "job $0 finished ($?)"'
echo "queue done"
