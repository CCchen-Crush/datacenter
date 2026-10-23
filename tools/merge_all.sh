#!/bin/bash
# Merge the parallel parts of all sweeps into one file per study (parts that are missing are skipped).
cd "$(dirname "$0")" || exit 1
R=../matlab/results
m12() { out=$1; shift; ls $R/exp12_capacity$1.csv >/dev/null 2>&1 && python3 merge_parts.py "$out" "$@"; }
m12 _S1 _S1_a _S1_b
m12 _S2 _S2_a _S2_b
m12 _S3 _S3_a _S3_b _S3_c _S3_d
m14() { st=$1; shift; ls $R/exp14_$st$1.csv >/dev/null 2>&1 && python3 merge_exp14.py "$st" "$@"; }
m14 tau_gamma _g100 _g105 _g110 _g120
m14 single _a _b
m14 ablation _1 _2 _3
m14 region_S2-30 _p1 _p2 _p3 _p4
echo "merge done"
