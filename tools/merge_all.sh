#!/bin/bash
# Merge the parallel parts of all sweeps into one file per study. Exp12 merges incrementally: finished parts are
# appended to an existing merged file, so the script can be re-run while other parts are still running.
# Exp14 sets are merged once all of their parts exist.
cd "$(dirname "$0")" || exit 1
R=../matlab/results
m12() {
    out=$1; shift; parts=()
    for p in "$@"; do [ -f "$R/exp12_capacity$p.csv" ] && parts+=("$p"); done
    [ ${#parts[@]} -eq 0 ] && return
    if [ -f "$R/exp12_capacity$out.csv" ]; then
        mv "$R/exp12_capacity$out.csv" "$R/exp12_capacity${out}_prev.csv"
        mv "$R/exp12_strategies$out.csv" "$R/exp12_strategies${out}_prev.csv"
        parts=("${out}_prev" "${parts[@]}")
    fi
    python3 merge_parts.py "$out" "${parts[@]}"
}
m12 _S1 _S1_a _S1_b _S1_c
m12 _S2 _S2_a _S2_b _S2_c
m12 _S3 _S3_a _S3_b _S3_c _S3_d _S3_e
m14() {
    st=$1; shift
    for p in "$@"; do [ -f "$R/exp14_$st$p.csv" ] || { echo "exp14 $st: part $p missing, not merged"; return; }; done
    python3 merge_exp14.py "$st" "$@"
}
m14 tau_gamma _g100 _g105 _g110 _g120
m14 single _a
m14 region_S2-30 _p1 _p2 _p3 _p4
# Exp18 (historical back-test) and Exp20 (firm capacity by bisection): parts are concatenated
mc() { out=$1; shift; python3 merge_concat.py "$out" "$@"; }
[ -f $R/exp18_history_S1_a.csv ] && [ -f $R/exp18_history_S1_b.csv ] && { mc exp18_history_S1.csv exp18_history_S1_a.csv exp18_history_S1_b.csv; \
    cp $R/exp18_strategies_S1_a.csv $R/exp18_strategies_S1.csv; rm -f $R/exp18_strategies_S1_a.csv $R/exp18_strategies_S1_b.csv; }
for st in bess bessM tau gamma; do
    mc exp20_$st.csv exp20_${st}_a.csv exp20_${st}_b.csv exp20_${st}_c.csv
    mc exp20_${st}_evals.csv exp20_${st}_a_evals.csv exp20_${st}_b_evals.csv exp20_${st}_c_evals.csv
done
echo "merge done"
