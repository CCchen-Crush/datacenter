#!/bin/bash
# Collect the experiment parts, regenerate paper/numbers.md and the figures (all, or the ones given: refresh.sh 5 9 10).
# PY selects the Python interpreter (needs numpy, pandas, scipy, matplotlib, tabulate).
cd "$(dirname "$0")" || exit 1
PY=${PY:-python3}
$PY collect_results.py
$PY paper_numbers.py > ../paper/numbers.md
$PY plot_paper.py "$@"
