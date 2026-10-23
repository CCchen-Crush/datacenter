#!/usr/bin/env python3
"""Decision experiment G1: reliable-capacity curve (Exp12) and two-event capacity region (Exp13).

Usage: python3 tools/g1_decision.py [results_dir] > matlab/results/g1_decision.txt

G1a  C_rho = largest uniform commitment C of the grid such that the share of days on which every
     event is delivered in full (>= 98 % of C) is >= rho for C and every smaller grid value
     (monotone, conservative). Also reported for the Jiangsu validity rule (all events >= 80 %).
     Confidence intervals: cluster bootstrap over the PAI days (each realisation is a different PAI
     weekday), B resamples, percentile intervals.
G1b  area of the region {(C1, C2): C2 <= C2_max(C1)} of each strategy (trapezoid over the C1 grid,
     a strategy contributes up to the largest C1 it can deliver).
Criteria (suggested values of the research plan):
  1. at rho = 95 %, JR-D commits >= 1 MW more than the stronger of IR-O* and IR-P
  2. JR-D - JR-M >= 0.5 MW, or a fulfilment gap >= 5 pp at commitments >= 7 MW
  3. for intervals <= 1 h, the JR region is >= 20 % larger than the IR-O* region
"""
import glob, os, sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RES = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "matlab", "results")
pd.set_option("display.width", 200); pd.set_option("display.max_columns", 30)
RHOS = [0.90, 0.95]
NBOOT = 2000
rng = np.random.default_rng(2024)


def load_exp12(tag=""):
    """exp12_capacity<tag>.csv (tag '' = deterministic MPC with forecasts, '_oracle' = perfect forecasts)."""
    f = os.path.join(RES, f"exp12_capacity{tag}.csv"); sf = os.path.join(RES, f"exp12_strategies{tag}.csv")
    if not os.path.exists(f) or not os.path.exists(sf): return None, None
    d = pd.read_csv(f); s = pd.read_csv(sf)
    d["name"] = d.strategy.map(dict(zip(s["index"], s["label"])))
    return d, list(s["label"])


def c_rho(share, rho):
    """share: Series indexed by sorted C. Largest C with share >= rho for it and all smaller C (NaN if none)."""
    ok = (share.sort_index() >= rho - 1e-9).values
    Cs = share.sort_index().index.values
    if not ok[0]: return np.nan
    k = np.argmin(ok) if not ok.all() else len(ok)
    return Cs[k - 1]


def caps(d, names, col):
    """C_rho per strategy and rho from day-level indicator col (0/1)."""
    out = {}
    for nm in names:
        sh = d[d.name == nm].groupby("C")[col].mean()
        out[nm] = {rho: c_rho(sh, rho) for rho in RHOS}
    return out


def boot_caps(d, names, col):
    """Cluster bootstrap over realisations (PAI days): array [NBOOT, strategy, rho]."""
    days = np.sort(d.realisation.unique())
    piv = {nm: d[d.name == nm].pivot(index="realisation", columns="C", values=col).loc[days] for nm in names}
    Cs = piv[names[0]].columns.values
    out = np.full((NBOOT, len(names), len(RHOS)), np.nan)
    for b in range(NBOOT):
        idx = rng.integers(0, len(days), len(days))
        for i, nm in enumerate(names):
            sh = pd.Series(piv[nm].values[idx].mean(axis=0), index=Cs)
            for j, rho in enumerate(RHOS):
                out[b, i, j] = c_rho(sh, rho)
    return out


def fmt_ci(x):
    x = x[~np.isnan(x)]
    if len(x) == 0: return "n/a"
    lo, hi = np.percentile(x, [2.5, 97.5])
    return f"[{lo:+.1f}, {hi:+.1f}]"


def g1a(tag="", title="closed-loop deterministic MPC (forecasts)"):
    d, names = load_exp12(tag)
    if d is None:
        print(f"G1a{tag}: no exp12 results"); return {}
    print("=" * 100); print(f"G1a{tag}  reliable capacity, uniform commitment, {title}, c_rb = 0"); print("=" * 100)
    N = d.realisation.nunique()
    print(f"realisations (distinct PAI weekdays): {N}; commitment grid: {sorted(d.C.unique())} MW")
    g = d.groupby(["C", "name"]).agg(fulfil=("fulfil_rate_pct", "mean"), all_valid=("all_valid", "mean"),
                                     all_full=("all_full", "mean"), net_adj=("net_cost_adj", "mean"),
                                     dr_pay=("dr_pay", "mean"), delay_h=("mean_delay_h", "mean"),
                                     sla=("sla_use_pct", "mean"), c3carry=("c3_carry_GPUh", "mean"),
                                     cap_viol=("cap_violation_MW", "max"), late=("lateness_GPUh_h", "max"),
                                     fb=("fallbacks", "sum"))
    for col, lab, sc in [("all_full", "share of days with every event delivered in full (>= 98 %)", 100),
                         ("all_valid", "share of days with every event valid (Jiangsu >= 80 %)", 100),
                         ("fulfil", "mean fulfilment (%)", 1), ("net_adj", "mean comprehensive cost (kCNY)", 1e-3),
                         ("delay_h", "mean extra completion time per deferred GPU-h (h)", 1),
                         ("sla", "share of the SLA slack used by deferred work (%)", 1)]:
        print(f"\n--- {lab}")
        print((g[col].unstack(1)[names] * sc).round(1 if sc != 100 else 0).to_string())
    print(f"\nsimulator checks: max connection overrun {g.cap_viol.max() * 1000:.1f} kW, max lateness {g.late.max():.3g} GPU-h*h, solver fallbacks {int(g.fb.sum())}")
    res = {}
    cmin = float(d.C.min())
    for col, lab in [("all_full", "full delivery (>= 98 % in every event)"), ("all_valid", "Jiangsu validity (>= 80 % in every event)")]:
        cp = caps(d, names, col); bt = boot_caps(d, names, col)
        print(f"\n--- reliable capacity C_rho by {lab} (MW per event; NaN = below the smallest grid value {cmin:g} MW)")
        print(pd.DataFrame(cp).T.rename(columns=lambda r: f"rho={r:.0%}").to_string())
        ib = [names.index(x) for x in ("IR-O*", "IR-P") if x in names]
        jd = names.index("JR-D"); jm = names.index("JR-M") if "JR-M" in names else None
        # a benchmark that misses rho already at the smallest commitment has C_rho < cmin: the difference
        # is then computed with cmin and is a strict lower bound (marked ">")
        lb = lambda v: cmin if np.isnan(v) else v
        for j, rho in enumerate(RHOS):
            irv = [cp[names[i]][rho] for i in ib]
            best_ir = max(lb(v) for v in irv); low_ir = all(np.isnan(v) for v in irv)
            d_ir = cp["JR-D"][rho] - best_ir
            bt_ir = bt[:, jd, j] - np.max(np.where(np.isnan(bt[:, ib, j]), cmin, bt[:, ib, j]), axis=1)
            line = (f"  rho={rho:.0%}: dC(JR-D - best of IR-O*/IR-P) {'>' if low_ir else '='} {d_ir:+.1f} MW, bootstrap 95% CI {fmt_ci(bt_ir)}"
                    f"{' (lower bounds)' if low_ir else ''}, P(dC >= 1 MW) = {np.nanmean(bt_ir >= 1 - 1e-9):.2f}")
            d_m = np.nan
            if jm is not None:
                low_m = np.isnan(cp["JR-M"][rho])
                d_m = cp["JR-D"][rho] - lb(cp["JR-M"][rho])
                bt_m = bt[:, jd, j] - np.where(np.isnan(bt[:, jm, j]), cmin, bt[:, jm, j])
                line += f" | dC(JR-D - JR-M) {'>' if low_m else '='} {d_m:+.1f} MW, CI {fmt_ci(bt_m)}, P(dC >= 0.5) = {np.nanmean(bt_m >= 0.5 - 1e-9):.2f}"
            print(line)
            res[(col, rho)] = (d_ir, d_m)
    # paired fulfilment gap JR-D - JR-M at C >= 7
    if "JR-M" in names:
        print("\n--- paired fulfilment gap JR-D - JR-M (pp), mean [95% bootstrap CI over days]")
        gaps = {}
        for C in sorted(d.C.unique()):
            a = d[(d.name == "JR-D") & (d.C == C)].set_index("realisation").fulfil_rate_pct
            b = d[(d.name == "JR-M") & (d.C == C)].set_index("realisation").fulfil_rate_pct
            x = (a - b).dropna().values
            bs = [x[rng.integers(0, len(x), len(x))].mean() for _ in range(NBOOT)]
            gaps[C] = x.mean()
            print(f"  C={C:4.1f}: {x.mean():+6.2f} [{np.percentile(bs, 2.5):+.2f}, {np.percentile(bs, 97.5):+.2f}]")
        res["gap_ge7"] = min(v for C, v in gaps.items() if C >= 7) if any(C >= 7 for C in gaps) else np.nan
    return res


def area(c1, c2):
    m = ~np.isnan(c2)
    if m.sum() < 2: return 0.0
    x, y = c1[m], c2[m]
    return float(np.sum((x[1:] - x[:-1]) * (y[1:] + y[:-1]) / 2))


def g1b():
    print("\n" + "=" * 100); print("G1b  two-event capacity region (perfect information, deadlines met, connection limit hard)"); print("=" * 100)
    out = {}
    for f in sorted(glob.glob(os.path.join(RES, "exp13_region*.csv"))):
        d = pd.read_csv(f); tag = os.path.basename(f)[len("exp13_region"):-4] or "(A 1 h, B 1 h)"
        if tag == "_K3": tag = "_K3 (main-case timing 17/19/21 h: E1 = E2 = C1, C2 = max E3; diagnostic)"
        for tau, q in d.groupby("tau_h"):
            q = q.sort_values("C1"); c1 = q.C1.values
            A = {k: area(c1, q[f"C2_{k}"].values) for k in ["JR", "IRJ", "JRM", "IRO", "IR"]}
            fixed = {c: area(c1, q[c].values) for c in q.columns if c.startswith("C2_IRO_a")}
            if fixed:
                cbest = max(fixed, key=fixed.get); A["IRO_fixed"] = fixed[cbest]
            print(f"\n--- {tag}, tau = {tau:g} h: G0A = {q.G0A.iloc[0]:.2f} MW, G0B = {q.G0B.iloc[0]:.2f} MW")
            print("  region area (MW^2): " + ", ".join(f"{k} {v:.2f}" for k, v in A.items()) +
                  (f"  (IRO_fixed: best single alpha = {int(cbest[-3:]) / 100:.1f})" if fixed else ""))
            if A["IRO"] > 0:
                print(f"  JR / IR-O*(alpha per C1) = {A['JR'] / A['IRO']:.3f}" +
                      (f", JR / IR-O*(one alpha) = {A['JR'] / A['IRO_fixed']:.3f}" if fixed else "") +
                      f", JR / JR-M = {A['JR'] / A['JRM']:.3f}, JR / IRJ = {A['JR'] / A['IRJ']:.3f}")
            print(q[["C1", "C2_JR", "C2_IRJ", "C2_JRM", "C2_IRO", "alpha_IRO", "C2_IR"]].round(2).to_string(index=False))
            out[(tag, tau)] = A
    return out


if __name__ == "__main__":
    a = g1a(); g1a("_oracle", "same controllers with perfect forecasts (information diagnostic)"); b = g1b()
    print("\n" + "=" * 100); print("Criteria"); print("=" * 100)
    if a:
        d_ir, d_m = a.get(("all_full", 0.95), (np.nan, np.nan))
        print(f"1. rho=95 % (full delivery): JR-D - best independent = {d_ir:+.1f} MW  -> {'PASS' if d_ir >= 1 else 'FAIL'} (>= 1 MW)")
        gap = a.get("gap_ge7", np.nan)
        ok2 = (d_m >= 0.5) or (gap >= 5)
        print(f"2. JR-D - JR-M = {d_m:+.1f} MW, smallest fulfilment gap at C >= 7 MW = {gap:+.1f} pp -> {'PASS' if ok2 else 'FAIL'} (>= 0.5 MW or >= 5 pp)")
    for (tag, tau), A in b.items():
        if tau <= 1 and A["IRO"] > 0:
            r = A["JR"] / A["IRO"]; rf = A["JR"] / A["IRO_fixed"] if A.get("IRO_fixed", 0) > 0 else np.nan
            main = tag == "(A 1 h, B 1 h)"
            print(f"3. {tag}, tau = {tau:g} h: area JR / IR-O* = {r:.3f} (alpha per C1), {rf:.3f} (one alpha) -> "
                  f"{'PASS' if r >= 1.2 else 'FAIL'} (>= 1.20){'' if main else '  [sensitivity / diagnostic, not the pre-set criterion]'}")
