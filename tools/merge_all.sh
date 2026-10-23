#!/bin/bash
# Collect the results of the parallel experiment parts (run copy -> matlab/results), see tools/collect_results.py.
# Parts are kept and the collection is idempotent, so it can be re-run while experiments are still writing.
# The merges of batches 1-4 (merge_parts.py for Exp12, merge_exp14.py for Exp14) were applied once; their merged
# files are in matlab/results and enter the collection as the parts exp12_capacity_<S>_ab.csv of the run copy.
cd "$(dirname "$0")" || exit 1
python3 collect_results.py
