#!/usr/bin/env python3
"""Merge the CSV parts of an experiment that was split over parallel processes.

Usage: python3 tools/merge_parts.py <out_tag> <part_tag> [<part_tag> ...]
  e.g. python3 tools/merge_parts.py "" _p1 _p2 _p3          -> exp12_capacity.csv, exp12_strategies.csv
       python3 tools/merge_parts.py _oracle _o1 _o2 _o3 _o4 -> exp12_capacity_oracle.csv, ...
Rows of exp12_capacity<part>.csv are concatenated; the strategy lists of the parts must be identical.
The part files are removed after a successful merge.
"""
import os, sys
import pandas as pd

RES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "matlab", "results")
out, parts = sys.argv[1], sys.argv[2:]
cap = [os.path.join(RES, f"exp12_capacity{p}.csv") for p in parts]
stg = [os.path.join(RES, f"exp12_strategies{p}.csv") for p in parts]
S = [pd.read_csv(f) for f in stg]
assert all(s.equals(S[0]) for s in S), "strategy lists differ between parts"
d = pd.concat([pd.read_csv(f) for f in cap], ignore_index=True).sort_values(["C", "realisation", "strategy"])
assert not d.duplicated(["C", "realisation", "strategy"]).any(), "duplicate rows across parts"
d.to_csv(os.path.join(RES, f"exp12_capacity{out}.csv"), index=False, float_format="%.10g")
S[0].to_csv(os.path.join(RES, f"exp12_strategies{out}.csv"), index=False)
for f in cap + stg: os.remove(f)
print(f"merged {len(parts)} parts -> exp12_capacity{out}.csv ({len(d)} rows, C = {sorted(d.C.unique())})")
