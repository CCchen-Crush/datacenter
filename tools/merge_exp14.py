#!/usr/bin/env python3
"""Merge the parallel parts of an exp14 sweep: exp14_<set><part>.csv (+ _cfg, _strategies) -> exp14_<set>.csv.

Usage: python3 tools/merge_exp14.py <set> <part> [<part> ...]   e.g.  merge_exp14.py tau_gamma _g100 _g105 _g110 _g120
Configuration indices are renumbered across parts; the strategy lists must be identical. Part files are removed.
"""
import os, sys
import pandas as pd

RES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "matlab", "results")
st, parts = sys.argv[1], sys.argv[2:]
rows, cfgs, strat, off = [], [], None, 0
for p in parts:
    d = pd.read_csv(os.path.join(RES, f"exp14_{st}{p}.csv")); c = pd.read_csv(os.path.join(RES, f"exp14_{st}{p}_cfg.csv"))
    s = pd.read_csv(os.path.join(RES, f"exp14_{st}{p}_strategies.csv"))
    assert strat is None or s.equals(strat), "strategy lists differ"; strat = s
    d["cfg"] += off; c["cfg"] += off; off += len(c); rows.append(d); cfgs.append(c)
pd.concat(rows).to_csv(os.path.join(RES, f"exp14_{st}.csv"), index=False, float_format="%.10g")
pd.concat(cfgs).to_csv(os.path.join(RES, f"exp14_{st}_cfg.csv"), index=False)
strat.to_csv(os.path.join(RES, f"exp14_{st}_strategies.csv"), index=False)
for p in parts:
    for suf in ["", "_cfg", "_strategies"]: os.remove(os.path.join(RES, f"exp14_{st}{p}{suf}.csv"))
print(f"merged {len(parts)} parts -> exp14_{st}.csv ({off} configurations)")
