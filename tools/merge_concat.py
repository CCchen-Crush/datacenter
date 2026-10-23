#!/usr/bin/env python3
"""Concatenate the CSV parts of an experiment that writes self-describing rows (Exp18, Exp20).

Usage: python3 tools/merge_concat.py <out.csv> <part.csv> [<part.csv> ...]   (file names relative to matlab/results)
The headers of the parts must be identical; parts that do not exist are skipped; merged parts are removed;
an existing <out.csv> is kept and extended (incremental merge).
"""
import os, sys
import pandas as pd

RES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "matlab", "results")
out, parts = sys.argv[1], [p for p in sys.argv[2:] if os.path.exists(os.path.join(RES, p))]
if not parts: sys.exit(0)
if os.path.exists(os.path.join(RES, out)) and out not in parts: parts = [out] + parts     # incremental merge
D = [pd.read_csv(os.path.join(RES, p)) for p in parts]
assert all(list(d.columns) == list(D[0].columns) for d in D), "headers differ between parts"
pd.concat(D, ignore_index=True).to_csv(os.path.join(RES, out), index=False, float_format="%.10g")
for p in parts:
    if p != out: os.remove(os.path.join(RES, p))
print(f"merged {len(parts)} parts -> {out}")
