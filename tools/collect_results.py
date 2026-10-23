#!/usr/bin/env python3
"""Collect the parts of the parallel experiment runs into one file per study (idempotent; parts are kept).

Usage: python3 tools/collect_results.py
Parts are read from the run copy (DCDR_RUN_RESULTS, default /home/user/dev/matlab/results) and the merged files
are written to matlab/results. Every experiment writes its CSV after each commitment or strategy, so parts that
are still being written are merged as they stand and the script can be re-run at any time.
  Exp12  exp12_capacity_<S>_<part>.csv         -> exp12_capacity_<S>.csv, exp12_strategies_<S>.csv
  Exp18  exp18_history_<S>_<part>.csv          -> exp18_history_<S>.csv, exp18_strategies_<S>.csv
  Exp20  exp20_<set>[_<part>][_evals].csv      -> exp20_<set>.csv, exp20_<set>_evals.csv
  Exp14  exp14_single_a[_cfg|_strategies].csv  -> exp14_single[_cfg|_strategies].csv
  other  exp19_hindsight_<S>.csv and the outputs of Exp1, 4, 5, 8, 11, 13 are copied when newer
"""
import os, re, shutil, time
import pandas as pd

RES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "matlab", "results")
RUN = os.environ.get("DCDR_RUN_RESULTS", "/home/user/dev/matlab/results")
SKIP = ("smoke",)


def parts(pattern):
    """{key: [file, ...]} of the run-copy files matching pattern (group 1 = key), parts in name order."""
    out = {}
    for f in sorted(os.listdir(RUN)):
        m = re.fullmatch(pattern, f)
        if m and not any(s in f for s in SKIP): out.setdefault(m.group(1), []).append(f)
    return out


def settled(f):
    """Path of a run-copy file once it has not been written for 2 s (the experiments rewrite their CSVs)."""
    p = os.path.join(RUN, f)
    while time.time() - os.path.getmtime(p) < 2: time.sleep(1)
    return p


def concat(files, keys):
    D = [pd.read_csv(settled(f)) for f in files]
    D = [d for d in D if len(d)]
    if not D: return None
    assert all(list(d.columns) == list(D[0].columns) for d in D), f"headers differ: {files}"
    d = pd.concat(D, ignore_index=True)
    return d.drop_duplicates(keys, keep="last").sort_values(keys).reset_index(drop=True)


def same_strategies(files):
    S = [pd.read_csv(settled(f)) for f in files]
    assert all(s.equals(S[0]) for s in S), f"strategy lists differ: {files}"
    return S[0]


def write(d, name):
    d.to_csv(os.path.join(RES, name), index=False, float_format="%.10g")


log = []
# Exp12 capacity sweeps and Exp18 historical back-test: parts per scenario
for exp, base, keys in (("exp12", "capacity", ["C", "realisation", "strategy"]), ("exp18", "history", ["C", "day", "strategy"])):
    for S, fs in parts(rf"{exp}_{base}_(S\d)_[a-z]+\.csv").items():
        d = concat(fs, keys)
        if d is None: continue
        write(d, f"{exp}_{base}_{S}.csv")
        same_strategies([f.replace(base, "strategies") for f in fs]).to_csv(os.path.join(RES, f"{exp}_strategies_{S}.csv"), index=False)
        log.append(f"{exp}_{base}_{S}: {len(fs)} parts, {len(d)} rows, C = {sorted(float(c) for c in d.C.unique())}")
# Exp20 firm capacities by bisection: one file per set (+ every evaluated commitment)
for st, fs in parts(r"exp20_([A-Za-z]+)(?:_[a-z]{1,2})?\.csv").items():
    d = concat(fs, ["label"])
    if d is None: continue
    write(d, f"exp20_{st}.csv")
    ev = [f[:-4] + "_evals.csv" for f in fs if os.path.exists(os.path.join(RUN, f[:-4] + "_evals.csv"))]
    if ev: write(pd.concat([pd.read_csv(settled(f)) for f in ev], ignore_index=True), f"exp20_{st}_evals.csv")
    log.append(f"exp20_{st}: " + ", ".join(f"{l} {c:g}" for l, c in zip(d.label, d.C_rho)))
# Exp14 lag-bound sweep (one part)
for suf in ("", "_cfg", "_strategies"):
    src = os.path.join(RUN, f"exp14_single_a{suf}.csv")
    if os.path.exists(src): shutil.copy2(settled(f"exp14_single_a{suf}.csv"), os.path.join(RES, f"exp14_single{suf}.csv"))
# whole-file outputs: copied when missing or newer
for f in sorted(os.listdir(RUN)):
    if any(s in f for s in SKIP) or not re.fullmatch(r"(exp19_hindsight_S\d|exp(1|4|5|8|11|13)_.*)\.csv", f): continue
    src, dst = os.path.join(RUN, f), os.path.join(RES, f)
    if not os.path.exists(dst) or os.path.getmtime(src) > os.path.getmtime(dst):
        shutil.copy2(settled(f), dst); log.append(f"copied {f}")
print("\n".join(log) if log else "nothing to collect")
