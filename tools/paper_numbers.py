#!/usr/bin/env python3
"""Every number quoted in the Applied Energy manuscript, computed from matlab/results.

Usage: python3 tools/paper_numbers.py > paper/numbers.md
Statistics: the 26 test realisations use 26 different PAI weekdays; confidence intervals are block
bootstrap intervals over these days (2000 resamples, percentile method).
"""
import numpy as np
import pandas as pd
from paper_style import (rd, load_capacity, capacity_table, c_rho, ORDER, SCEN, capability, worst_case_prob, dro_capacity,
                         cv_radius, eps_sampling, exp20)

B = 2000
rng = np.random.default_rng(7)


def ci(x, stat=np.mean):
    x = np.asarray(x, float); x = x[~np.isnan(x)]
    if len(x) < 2: return np.nan, np.nan
    bs = [stat(x[rng.integers(0, len(x), len(x))]) for _ in range(B)]
    return np.percentile(bs, 2.5), np.percentile(bs, 97.5)


def h(t): print(f"\n## {t}\n")


h_ = h


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
            nd = rd("exp17_nodr.csv")
            if nd is not None:
                nd = nd.set_index("realisation")
                comp = [("cost_energy", "electricity"), ("cost_gas", "gas"), ("cost_deg", "degradation"), ("cost_delay", "delay"),
                        ("term_adj", "end state"), ("pen_dev", "shortfall"), ("dr_pay", "DR revenue (-)"), ("net_cost_adj", "net change")]
                print("\nCost change vs no DR (k CNY/day, mean over days):\n")
                print("| strategy | " + " | ".join(c[1] for c in comp) + " | E_start E2 (MWh) | backlog into E2 (GPU·h) |"); print("|---" * (len(comp) + 3) + "|")
                for n in ORDER:
                    r = q[q.name == n].set_index("realisation"); ref = nd.reindex(r.index)
                    v = [(-r[c].mean() if c == "dr_pay" else (r[c] - ref[c]).mean()) / 1e3 for c, _ in comp]
                    print(f"| {n} | " + " | ".join(f"{x:+.1f}" for x in v) + f" | {r.E_start_E2.mean():.2f} | {r.B_start_E2.mean():.0f} |")
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


def history(scen="S1"):
    """Exp18 back-test on the 14 historical days (strategy names attached); None if not available."""
    h = rd(f"exp18_history_{scen}.csv"); hs = rd(f"exp18_strategies_{scen}.csv")
    if h is None or hs is None: return None
    h["name"] = h.strategy.map(dict(zip(hs["index"], hs["label"])))
    return h


def dro_section(rhos=(0.90, 0.95)):
    nd = rd("exp17_nodr.csv"); nodr = nd.set_index("realisation").net_cost_adj if nd is not None else None
    for scen, tag in [("S1", "_S1"), ("S2", "_S2")]:
        h = history(scen); t = load_capacity(tag)
        if h is None or t is None: continue
        N = h.day.nunique()
        h_(f"Distributionally robust commitment (Section 4.1, Proposition 3), {scen}: {N} historical days -> 26 test days")
        print("Back-test cost J(C) is averaged over the days that delivered every smaller commitment (all days for C <= the smallest "
              "capability); C* is chosen among commitments with all days available.\n")
        grid = np.sort(h.C.unique())
        print("| rho | strategy | capability on historical days: mean / min (MW) | SAA C | eps_N (MW, Eq. 18a) | DRO C | eps LOO (MW) | DRO C (LOO) | "
              "margin Phi at DRO C (MW) | C* (Eq. 18) | test: full % at C* | test: full % at SAA C | benefit at C* (k CNY/day) |")
        print("|---" * 13 + "|")
        for rho in rhos:
            for n in ORDER:
                if n not in set(h.name): continue
                lb, step = capability(h, n); x = lb.values + step / 2
                c_saa = dro_capacity(x, rho, 0, grid); e = eps_sampling(x); c_dro = dro_capacity(x, rho, e, grid)
                e_cv = cv_radius(x, lb.values, rho, grid); c_cv = dro_capacity(x, rho, e_cv, grid)
                phi = np.nan
                if not np.isnan(c_dro):
                    m = np.sort(x[x >= c_dro - 1e-12] - c_dro); r = len(m) - rho * len(x); k = int(np.floor(r + 1e-12))
                    phi = (m[:k].sum() + (r - k) * (m[k] if k < len(m) else 0)) / len(x)
                hn = h[h.name == n]; cnt = hn.groupby("C").day.nunique(); J = hn.groupby("C").net_cost_adj.mean()[cnt == N]
                cand = J[J.index <= (c_dro + 1e-9 if not np.isnan(c_dro) else -1)]
                cs = cand.idxmin() if len(cand) else np.nan
                real = t[t.name == n].groupby("C").all_full.mean()
                f = lambda c: f"{100 * real.get(c, np.nan):.0f}" if not np.isnan(c) else "–"
                ben = "–"
                if not np.isnan(cs) and nodr is not None:
                    q = t[(t.name == n) & np.isclose(t.C, cs)].set_index("realisation"); ben = f"{(nodr.reindex(q.index) - q.net_cost_adj).mean() / 1e3:.1f}"
                g = lambda c: "<%g" % grid.min() if np.isnan(c) else f"{c:g}"
                print(f"| {rho:.2f} | {n} | {x.mean():.2f} / {x.min():.2f} | {g(c_saa)} | {e:.3f} | {g(c_dro)} | {e_cv:.3f} | {g(c_cv)} | {phi:.3f} | {g(cs)} | {f(cs)} | {f(c_saa)} | {ben} |")


def exp20_section():
    for name, title in [("bess", "BESS size (S2, connection fixed)"), ("bessM", "BESS size, JR-M (S2, connection fixed)"),
                        ("gamma", "Connection margin (S2)"), ("tau", "Event interval"),
                        ("ies", "IES devices (S2, JR-D, connection fixed)"), ("resources", "Resource ablation (S2, JR-D, connection fixed)"),
                        ("overhead", "Pause/resume overhead (S2, connection fixed)"),
                        ("region", "Two-event firm region (S2): firm C2 for a fixed first-event commitment C1")]:
        d = exp20(name)
        if d is None: continue
        h_(f"Firm capacity C_0.95 by bisection (tolerance 0.25 MW): {title}")
        print(d.pivot(index="cfg", columns="strategy", values="C_rho").to_markdown())
    b = exp20("bess")
    if b is not None:
        print("\nBase configuration (bess6 = 6 MW / 12 MWh, gamma 1.10) is the reference of the gamma, ies, resources and overhead sets.")


def hindsight_section():
    for s, tag in [("S1", "_S1"), ("S2", "_S2")]:
        d = rd(f"exp19_hindsight{tag}.csv")
        if d is None: continue
        h_(f"Static-split independent recovery with the best split in hindsight (upper bound), {s}")
        best = d.groupby(["C", "realisation"]).all_full.max().groupby("C").mean() * 100
        cap = load_capacity(tag if s == "S1" else "_S2")
        rows = []
        for C, v in best.items():
            iro = cap[(cap.name == "IR-O*") & np.isclose(cap.C, C)].all_full.mean() * 100 if cap is not None else np.nan
            jrd = cap[(cap.name == "JR-D") & np.isclose(cap.C, C)].all_full.mean() * 100 if cap is not None else np.nan
            rows.append((C, v, iro, jrd))
        print("| C (MW) | best split in hindsight: full % | IR-O* (split tuned day-ahead): full % | JR-D: full % |\n|---|---|---|---|")
        for C, v, i, j in rows: print(f"| {C:g} | {v:.0f} | {i:.0f} | {j:.0f} |")


if __name__ == "__main__":
    print("# Numbers for the manuscript (generated by tools/paper_numbers.py)")
    capacity_section(); fixed_section(); endogenous_section(); dro_section(); sweep_section(); exp20_section(); hindsight_section()
