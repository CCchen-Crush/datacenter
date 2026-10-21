#!/usr/bin/env python3
"""Print every number quoted in docs/论文主要思路.md from matlab/results/*.csv."""
import os, sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RES = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "matlab", "results")
pd.set_option("display.width", 200)


def rd(n):
    p = os.path.join(RES, n)
    return pd.read_csv(p) if os.path.exists(p) else None


def improve(a, b, name):
    """a = proposed row, b = benchmark row (pandas Series)."""
    return {"vs": name,
            "fulfil_pp": a.fulfil_rate_pct - b.fulfil_rate_pct,
            "rebound_pct": 100 * (a.max_rebound_MW - b.max_rebound_MW) / b.max_rebound_MW,
            "net_cost_pct": 100 * (a.net_cost - b.net_cost) / b.net_cost,
            "op_cost_pct": 100 * (a.cost_op - b.cost_op) / b.cost_op}


print("=== Exp2 main comparison ===")
for case in ["DAcommit", "uniform6"]:
    d = rd(f"exp2_{case}.csv")
    if d is None: continue
    d = d.set_index("label")
    print(f"--- {case}")
    print(d[["fulfil_rate_pct", "n_valid", "red_E1", "red_E2", "red_E3", "max_rebound_MW", "cost_op", "dr_pay",
             "pen_dev", "pen_rb", "net_cost", "lateness_GPUh_h"]].round(2).to_string())
    for b in ["IR-O", "IR-R"]:
        print({k: (round(v, 2) if isinstance(v, float) else v) for k, v in improve(d.loc["JR-S"], d.loc[b], b).items()})

print("\n=== Exp4 Monte Carlo (mean / std / min) ===")
d = rd("exp4_montecarlo.csv")
if d is not None:
    names = {1: "IR-R", 2: "IR-O", 3: "JR-D", 4: "JR-S"}
    g = d.groupby("strategy")
    tab = g.agg(fulfil_mean=("fulfil_pct", "mean"), fulfil_std=("fulfil_pct", "std"), fulfil_min=("fulfil_pct", "min"),
                valid_mean=("n_valid", "mean"), all_valid=("n_valid", lambda x: np.mean(x == 3)),
                rb_mean=("max_rebound", "mean"), net_mean=("net_cost", "mean"), op_mean=("cost_op", "mean"),
                late=("lateness", "max"), viol=("cap_violation", "max"))
    tab.index = [names[i] for i in tab.index]
    print(f"N = {d.realisation.nunique()} days"); print(tab.round(3).to_string())
    for b in ["IR-O", "IR-R", "JR-D"]:
        s, r = tab.loc["JR-S"], tab.loc[b]
        print(f"JR-S vs {b}: fulfil {s.fulfil_mean - r.fulfil_mean:+.2f} pp, max rebound {100*(s.rb_mean-r.rb_mean)/r.rb_mean:+.1f}%, "
              f"net cost {100*(s.net_mean-r.net_mean)/r.net_mean:+.1f}%, op cost {100*(s.op_mean-r.op_mean)/r.op_mean:+.2f}%")
    p = d.pivot(index="realisation", columns="strategy", values="fulfil_pct")
    print("days where JR-S >= IR-O:", int((p[4] >= p[2] - 1e-6).sum()), "/", len(p))
    print("days where JR-S > JR-D :", int((p[4] > p[3] + 1e-6).sum()), " JR-S < JR-D:", int((p[4] < p[3] - 1e-6).sum()))

print("\n=== Exp1 mechanism (ratio to single-event capability) ===")
for f in ["exp1_mechanism_CA6_DA2.csv", "exp1_mechanism_CA6_DA1_DB2.csv"]:
    d = rd(f)
    if d is None: continue
    for c in ["G_IR", "G_IRJ", "G_JR", "G_bound"]: d[c + "_r"] = d[c] / d.G0
    print("---", f, " bound valid (IRJ<=bound):", bool((d.G_IRJ <= d.G_bound + 1e-3).all()))
    print(d[["gamma", "tau_h", "G0", "G_IR_r", "G_IRJ_r", "G_JR_r", "G_bound_r", "Rcomp_MWh", "Rstor_MWh", "Headroom_MWh"]].round(2).to_string(index=False))

print("\n=== Exp3 sensitivity (strategy 1=IR-R, 2=IR-O, 3=JR) ===")
for f in ["exp3_duration.csv", "exp3_interval.csv", "exp3_gamma.csv", "exp3_commitment.csv"]:
    d = rd(f)
    if d is None: continue
    print("---", f); print(d.pivot(index="x", columns="strategy", values=["fulfil_pct", "max_rebound", "net_cost"]).round(1).to_string())

print("\n=== Exp5 shadow prices ===")
d = rd("exp5_shadow.csv")
if d is not None:
    for a, b, lab in [(17, 18, "E1"), (18, 19, "gap1"), (19, 20, "E2"), (20, 21, "gap2"), (21, 22, "E3"), (22, 30, "after")]:
        q = d[(d.hour >= a) & (d.hour < b)]
        print(f"{lab:6s} lambda_cap mean {q.lambda_cap.mean():8.0f}  value_E mean {q.value_E.mean():7.0f}  "
              f"value_S {q.value_S.mean():6.0f}  cost_B1/2/3 {q.cost_B1.mean():6.2f} {q.cost_B2.mean():6.2f} {q.cost_B3.mean():6.2f}")

print("\n=== Exp6 commitment ===")
d = rd("exp6_commitment.csv")
if d is not None: print(d.round(2).to_string(index=False))

print("\n=== Exp7 ablation ===")
d = rd("exp7_ablation.csv")
if d is not None: print(d.round(2).to_string(index=False))
d = rd("exp7_alpha.csv")
if d is not None: print(d.round(2).to_string(index=False))
