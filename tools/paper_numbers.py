#!/usr/bin/env python3
"""Every number quoted in the Applied Energy manuscript, computed from matlab/results.

Usage: python3 tools/paper_numbers.py > paper/numbers.md
Statistics: the 26 test realisations use 26 different PAI weekdays; confidence intervals are block
bootstrap intervals over these days (2000 resamples, percentile method).
"""
import numpy as np
import pandas as pd
from paper_style import rd, load_capacity, capacity_table, c_rho, ORDER, SCEN

B = 2000
rng = np.random.default_rng(7)


def ci(x, stat=np.mean):
    x = np.asarray(x, float); x = x[~np.isnan(x)]
    if len(x) < 2: return np.nan, np.nan
    bs = [stat(x[rng.integers(0, len(x), len(x))]) for _ in range(B)]
    return np.percentile(bs, 2.5), np.percentile(bs, 97.5)


def h(t): print(f"\n## {t}\n")


def capacity_section():
    h("Firm consecutive DR capacity (module 2)")
    print("C_rho = largest C with full-delivery share >= rho for all C' <= C (Eq. 13); '<x' = below the lowest commitment "
          "of the grid; CIs: block bootstrap over the 26 test days.\n")
    print("| Scenario | rule | rho | IR-O* | IR-P | JR-M | JR-D | dC vs best IR [95% CI] | I_rho | dC vs JR-M [95% CI] |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for tag, s in [("_S1", "S1"), ("_S2", "S2"), ("_S3", "S3")]:
        d = load_capacity(tag)
        if d is None: continue
        cmin = d.C.min()
        f = lambda x: "<%g" % cmin if np.isnan(x) else f"{x:g}"
        for col, rule in [("all_full", "full"), ("all_valid", "80 %")]:
            tab, _ = capacity_table(d, col, rhos=(0.90, 0.95), B=B)
            for rho in (0.90, 0.95):
                v = {n: tab[n][0][rho] for n in ORDER}
                ir = np.nanmax([v["IR-O*"], v["IR-P"]]) if not np.all(np.isnan([v["IR-O*"], v["IR-P"]])) else np.nan
                bj = tab["JR-D"][1][rho]; bi = np.fmax(tab["IR-O*"][1][rho], tab["IR-P"][1][rho]); bm = tab["JR-M"][1][rho]
                if np.isnan(ir):
                    dC = f"> {v['JR-D'] - cmin:+.1f}"; I = f"> {100 * (v['JR-D'] - cmin) / cmin:.0f} %"
                else:
                    lo, hi = np.nanpercentile(bj - bi, [2.5, 97.5])
                    dC = f"{v['JR-D'] - ir:+.1f} [{lo:+.1f}, {hi:+.1f}]"; I = f"{100 * (v['JR-D'] - ir) / ir:.0f} %"
                if np.isnan(v["JR-M"]):
                    dM = f"> {v['JR-D'] - cmin:+.1f}"
                else:
                    lo2, hi2 = np.nanpercentile(bj - bm, [2.5, 97.5]); dM = f"{v['JR-D'] - v['JR-M']:+.1f} [{lo2:+.1f}, {hi2:+.1f}]"
                print(f"| {s} | {rule} | {rho:.0%} | {f(v['IR-O*'])} | {f(v['IR-P'])} | {f(v['JR-M'])} | {f(v['JR-D'])} | {dC} | {I} | {dM} |")
    h("Full-delivery share by commitment (%, 26 test days)")
    for tag, s in [("_S1", "S1"), ("_S2", "S2"), ("_S3", "S3")]:
        d = load_capacity(tag)
        if d is None: continue
        g = (100 * d.groupby(["name", "C"]).all_full.mean()).unstack("C").reindex(ORDER).round(0)
        print(f"\n**{SCEN[s]}**\n"); print(g.to_markdown())


def fixed_section(Cs=(6.0, 7.0, 7.5)):
    h("Fixed-commitment comparison (module 1, protocol 1; means over 26 test days)")
    cols = [("fulfil_rate_pct", "fulfil %", 1), ("all_full", "all full %", 100), ("all_valid", "all valid %", 100),
            ("net_cost_adj", "cost (k CNY)", 1e-3), ("dr_pay", "DR pay (k)", 1e-3), ("max_rebound_MW", "peak rebound (MW)", 1),
            ("mean_delay_h", "extra delay (h)", 1), ("sla_use_pct", "SLA slack used %", 1), ("c3_carry_GPUh", "C3 carried (GPU·h)", 1)]
    for tag, s in [("_S1", "S1"), ("_S2", "S2"), ("_S3", "S3")]:
        d = load_capacity(tag)
        if d is None: continue
        for C in Cs:
            q = d[np.isclose(d.C, C)]
            if q.empty: continue
            print(f"\n**{SCEN[s]}, C = {C:g} MW**\n")
            print("| strategy | " + " | ".join(c[1] for c in cols) + " |"); print("|---" * (len(cols) + 1) + "|")
            for n in ORDER:
                r = q[q.name == n]
                print(f"| {n} | " + " | ".join(f"{r[c].mean() * sc:.1f}" for c, _, sc in cols) + " |")
            P = q[q.name == "JR-D"].set_index("realisation")
            for n in ["IR-O*", "IR-P", "JR-M"]:
                Bq = q[q.name == n].set_index("realisation"); dd = (P.net_cost_adj - Bq.net_cost_adj).dropna() / 1e3
                lo, hi = ci(dd.values); md = dd.median()
                print(f"- JR-D − {n}: cost {dd.mean():+.1f} k CNY/day [95% CI {lo:+.1f}, {hi:+.1f}], median {md:+.1f}; cheaper on {int((dd < 0).sum())}/{len(dd)} days")


def endogenous_section(rhos=(0.0, 0.8, 1.0)):
    for s, tag in [("S1", "_S1"), ("S2-30", "_S2"), ("S3", "_S3")]:
        d = rd(f"exp16_endogenous_{s}.csv"); p = rd(f"exp16_packages_{s}.csv"); da = rd(f"exp16_dayahead_{s}.csv")
        cap = load_capacity(tag)
        if d is None or da is None: continue
        h(f"Endogenous commitment (module 1, protocol 2), {s}")
        names = dict(zip(p["index"], p["label"])); d["pkg"] = d.package.map(names)
        nodr = d.groupby("realisation").nodr_net_cost_adj.first()
        t = da.set_index("C"); show = t[ORDER] / 1e3
        show = pd.concat([show.round(1), t[["full_" + n for n in ORDER]]], axis=1)
        print("Day-ahead back-test on the day-ahead scenarios: expected cost (k CNY) and full-delivery share by uniform commitment:\n")
        print(show.to_markdown() + "\n")
        print("Reliability-constrained back-test commitment (Eq. 15) and out-of-sample operation on the 26 test days:\n")
        print("| rho | strategy | C* (MW) | day-ahead cost (k) | day-ahead full share | all full % | fulfil % | net cost (k) | benefit vs no-DR (k) |")
        print("|---|---|---|---|---|---|---|---|---|")
        for rho in rhos:
            for n in ORDER:
                ok = (t["full_" + n] >= rho - 1e-9).cummin()
                if not ok.any(): print(f"| {rho:g} | {n} | – | | | | | | |"); continue
                Cs = t[n][ok.astype(bool)].idxmin()
                if cap is None: continue
                q = cap[(cap.name == n) & np.isclose(cap.C, Cs)].set_index("realisation")
                if q.empty: continue
                ben = (nodr.reindex(q.index) - q.net_cost_adj).mean() / 1e3
                print(f"| {rho:g} | {n} | {Cs:g} | {t.loc[Cs, n] / 1e3:.1f} | {t.loc[Cs, 'full_' + n]:.1f} | {100 * q.all_full.mean():.0f} | "
                      f"{q.fulfil_rate_pct.mean():.1f} | {q.net_cost_adj.mean() / 1e3:.1f} | {ben:.1f} |")
        print("\nModel-based commitments (RA: perfect-recourse two-stage MILP, Eq. 16; SE: single-event capability) and back-test "
              "packages as run in exp16:\n")
        print("| package | commitment (MW) | all full % | fulfil % | net cost (k) | benefit vs no-DR (k) |"); print("|---|---|---|---|---|---|")
        for k, g in d.groupby("pkg", sort=False):
            Cv = "/".join(f"{x:.2f}" for x in g[["C1", "C2", "C3"]].iloc[0].dropna())
            print(f"| {k} | {Cv} | {100 * g.all_full.mean():.0f} | {g.fulfil_rate_pct.mean():.1f} | {g.net_cost_adj.mean() / 1e3:.1f} | {(g.nodr_net_cost_adj - g.net_cost_adj).mean() / 1e3:.1f} |")


def sweep_section():
    d = rd("exp14_tau_gamma.csv")
    if d is not None:
        h("Sensitivity: interval x connection margin (share of days with full delivery, %)")
        s = rd("exp14_tau_gamma_strategies.csv"); cfg = rd("exp14_tau_gamma_cfg.csv")
        d["name"] = d.strategy.map(dict(zip(s["index"], s["label"]))); d["cfgname"] = d.cfg.map(dict(zip(cfg["cfg"], cfg["label"])))
        g = (100 * d.groupby(["cfgname", "name"]).all_full.mean()).unstack("name").round(0)
        print(g.to_markdown())
    d = rd("exp14_single.csv")
    if d is not None:
        h("Sensitivity: lag bounds and BESS power (share of days with full delivery, %)")
        s = rd("exp14_single_strategies.csv"); cfg = rd("exp14_single_cfg.csv")
        d["name"] = d.strategy.map(dict(zip(s["index"], s["label"]))); d["cfgname"] = d.cfg.map(dict(zip(cfg["cfg"], cfg["label"])))
        print((100 * d.groupby(["cfgname", "name"]).all_full.mean()).unstack("name").round(0).to_markdown())
    d = rd("exp14_ablation.csv")
    if d is not None:
        h("Ablation (JR-D controller, S1): firm capacity")
        cfg = rd("exp14_ablation_cfg.csv"); d["cfgname"] = d.cfg.map(dict(zip(cfg["cfg"], cfg["label"])))
        for k, g in d.groupby("cfgname"):
            sh = g.groupby("C1").all_full.mean()
            print(f"- {k}: C_0.90 = {c_rho(sh, 0.90)} MW, C_0.95 = {c_rho(sh, 0.95)} MW")


if __name__ == "__main__":
    print("# Numbers for the manuscript (generated by tools/paper_numbers.py)")
    capacity_section(); fixed_section(); endogenous_section(); sweep_section()
