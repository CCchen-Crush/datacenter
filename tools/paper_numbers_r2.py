"""Numbers of the second review round (batch 8), appended to paper/numbers.md by tools/paper_numbers.py.

Stronger benchmarks (IR-PD, SR-D), low computing flexibility, MPC horizon, DR price x delay cost (with the shortfall
assessment kappa = 0), nominal versus actual recovery channel, 78 operating days and a July DR day.
"""
import numpy as np
import pandas as pd
from scipy.stats import beta
from paper_style import rd, load_capacity, load_capacity_all, capacity_table, c_rho, capability, dro_capacity, eps_sampling, cv_radius

B = 2000
SC = [("_S1", "S1"), ("_S2", "S2"), ("_S3", "S3")]
STRONG = ["IR-O*", "IR-P", "IR-PD", "SR-D", "JR-M", "JR-D"]


def h(t): print(f"\n## {t}\n")


def cp_lower(k, n, conf=0.95):
    """One-sided Clopper-Pearson lower bound of a success probability (k successes in n trials)."""
    return 0.0 if k <= 0 else float(beta.ppf(1 - conf, k, n - k + 1))


def history(tag):
    hh = rd(f"exp18_history{tag}.csv"); hs = rd(f"exp18_strategies{tag}.csv")
    if hh is None or hs is None: return None
    hh["name"] = hh.strategy.map(dict(zip(hs["index"], hs["label"])))
    return hh


def nodr_cost(c_jct=0.5, tag=""):
    """No-DR cost per test day at the delay price c_jct (its delay cost is linear in c_jct, no overdue work)."""
    nd = rd(f"exp17_nodr{tag}.csv")
    if nd is None: return None
    nd = nd.set_index("realisation")
    return nd.net_cost_adj + (c_jct - 0.5) * nd.delay_GPUh_h


def benchmark_section():
    h("Stronger independent benchmarks (Section 5.3.4): IR-PD (iterative two-way price) and SR-D (staged recovery)")
    print("Firm capacity C_0.95 on the 26 operating days (grid of each run; '<1' = not reached at 1 MW), share of days with full "
          "delivery at selected commitments, and mean fulfilment.\n")
    for tag, s in SC:
        d = load_capacity_all(tag)
        if d is None: continue
        names = [n for n in STRONG if n in set(d.name)]
        print(f"**{s}**\n")
        print("| strategy | grid (MW) | C_0.95 full | C_0.95 80 % rule | full % at 1 / 2 / 3 / 5 / 7 MW | fulfil % at 1 / 7 MW | min share over C <= 3 MW |")
        print("|---|---|---|---|---|---|---|")
        for n in names:
            q = d[d.name == n]; sh = q.groupby("C").all_full.mean(); sv = q.groupby("C").all_valid.mean(); fu = q.groupby("C").fulfil_rate_pct.mean()
            g = lambda x: "<%g" % sh.index.min() if np.isnan(x) else f"{x:g}"
            at = lambda ser, c: f"{100 * ser.get(c, np.nan):.0f}" if c in ser.index else "–"
            low = sh[sh.index <= 3]
            print(f"| {n} | {sh.index.min():g}–{sh.index.max():g} | {g(c_rho(sh, 0.95))} | {g(c_rho(sv, 0.95))} | "
                  f"{' / '.join(at(sh, c) for c in (1, 2, 3, 5, 7))} | {fu.get(1, np.nan):.1f} / {fu.get(7, np.nan):.1f} | {100 * low.min():.0f} |")
        print()
        # days on which IR-PD / SR-D fail at low commitments, and the baseline deviation of those days
        nd = rd("exp17_nodr.csv")
        for n in ("IR-PD", "SR-D"):
            q = d[(d.name == n) & (d.C <= 3)]
            if q.empty: continue
            bad = sorted(q[q.all_full < 0.5].realisation.unique())
            print(f"- {n}: days failing full delivery at some C <= 3 MW: {len(bad)} of {q.realisation.nunique()} ({bad})")
        # paired comparison of JR-D with SR-D and IR-PD at 7 MW
        for n in ("SR-D", "IR-PD"):
            a = d[(d.name == "JR-D") & np.isclose(d.C, 7)].set_index("realisation"); b = d[(d.name == n) & np.isclose(d.C, 7)].set_index("realisation")
            if a.empty or b.empty: continue
            j = a.index.intersection(b.index); dc = (b.net_cost_adj - a.net_cost_adj).loc[j] / 1e3
            print(f"- 7 MW, {n} minus JR-D daily cost: mean {dc.mean():.1f} k CNY (min {dc.min():.1f}, max {dc.max():.1f}); "
                  f"JR-D cheaper on {(dc > 0).sum()} of {len(j)} days; full delivery {100 * a.all_full.loc[j].mean():.0f} % vs {100 * b.all_full.loc[j].mean():.0f} %")
        for n in ("IR-PD", "SR-D"):
            q = d[d.name == n]
            if q.empty: continue
            print(f"- {n}: solver time per closed-loop day mean / median / max {q.solve_time_s.mean():.1f} / {q.solve_time_s.median():.1f} / "
                  f"{q.solve_time_s.max():.1f} s, fallback steps {int(q.fallbacks.sum())} in {len(q)} runs; overdue runs {int((q.lateness_GPUh_h > 1e-6).sum())}")
        print()


def exp20_parts(name, parts):
    out = []
    for p in parts:
        d = rd(f"exp20_{name}{p}.csv")
        if d is not None: out.append(d)
    if not out: return None
    d = pd.concat(out, ignore_index=True).drop_duplicates("label", keep="last")
    d[["cfg", "strategy"]] = d.label.str.split("|", expand=True)
    return d


FLEX = [("base", "base case"), ("fs50", "deferrable share 50 % (of 75 %)"), ("fs25", "deferrable share 25 %"),
        ("lag50", "lag bounds x 0.5"), ("idle40", "idle power 40 % of peak"), ("low", "all three: 50 %, x 0.5, 40 %")]


def flex_section():
    h("Low computing flexibility (Section 5.10.1): firm capacity C_0.95 by bisection (0.25 MW), connection kept")
    for s, parts in [("S1", ["_S1a", "_S1b"]), ("S2", ["_S2a", "_S2b"])]:
        d = exp20_parts("flex", parts)
        if d is None: continue
        p = d.pivot(index="cfg", columns="strategy", values="C_rho")
        cols = [c for c in ["IR-O*", "SR-D", "JR-M", "JR-D"] if c in p.columns]
        print(f"**{s}**\n")
        print("| configuration | " + " | ".join(cols) + " | JR-D − JR-M | JR-D − SR-D |")
        print("|---|" + "---|" * (len(cols) + 2))
        for k, lab in FLEX:
            if k not in p.index: continue
            r = p.loc[k]; f = lambda x: "<1" if pd.isna(x) else f"{x:g}"
            dm = r.get("JR-D", np.nan) - r.get("JR-M", np.nan); ds = r.get("JR-D", np.nan) - r.get("SR-D", np.nan)
            print(f"| {lab} | " + " | ".join(f(r[c]) for c in cols) + f" | {dm:+.2f} | {ds:+.2f} |")
        print()


def horizon_section():
    h("Prediction horizon of the MPC (Section 5.10.2): firm capacity of JR-D by bisection (0.25 MW)")
    for s, tag in [("S1", "_S1"), ("S2", "_S2")]:
        d = rd(f"exp20_horizon{tag}.csv")
        if d is None: continue
        d[["cfg", "strategy"]] = d.label.str.split("|", expand=True)
        print(f"- {s}: " + ", ".join(f"{c[2:]} h: {'<1' if pd.isna(v) else f'{v:g}'} MW" for c, v in zip(d.cfg, d.C_rho)))


PRICE = [("p1c05", 1000, 0.5), ("p1c1", 1000, 1), ("p1c2", 1000, 2), ("p2c05", 2000, 0.5), ("p2c1", 2000, 1), ("p2c2", 2000, 2),
         ("", 3000, 0.5), ("p3c1", 3000, 1), ("p3c2", 3000, 2), ("k0", 3000, 0.5)]


def commit_point(hist, test, name, c_jct, rho=0.95, ntag=""):
    """DRO capacity and cost-optimal commitment from the back-test, and its performance on the test days."""
    q = hist[hist.name == name]; grid = np.sort(hist.C.unique()); N = q.day.nunique()
    lb, step = capability(q, name); x = lb.values + step / 2
    e = eps_sampling(x); c_dro = dro_capacity(x, rho, e, grid)
    cnt = q.groupby("C").day.nunique(); J = q.groupby("C").net_cost_adj.mean()[cnt == N]
    cand = J[J.index <= (c_dro + 1e-9 if not np.isnan(c_dro) else -1)]
    cs = cand.idxmin() if len(cand) else np.nan
    out = dict(c_dro=c_dro, eps=e, c_star=cs, cap_mean=x.mean(), cap_min=x.min())
    t = test[test.name == name]; nodr = nodr_cost(c_jct, ntag)
    if not np.isnan(cs) and nodr is not None:
        tt = t[np.isclose(t.C, cs)].set_index("realisation")
        if len(tt):
            nd = rd(f"exp17_nodr{ntag}.csv").set_index("realisation"); j = tt.index
            out.update(full=tt.all_full.mean(), n=len(tt), benefit=(nodr.reindex(j) - tt.net_cost_adj).mean() / 1e3,
                       revenue=tt.dr_pay.mean() / 1e3, delay=(tt.cost_delay - (c_jct / 0.5) * nd.cost_delay.reindex(j)).mean() / 1e3,
                       savings=(nd.cost_op.reindex(j) - tt.cost_op_adj).mean() / 1e3, short=tt.pen_dev.mean() / 1e3)
    # benefit-maximising commitment on the test days (ex post) for reference
    if nodr is not None and not t.empty:
        bt = t.groupby("C").apply(lambda g: (nodr.reindex(g.realisation).values - g.net_cost_adj.values).mean() / 1e3)
        out.update(c_expost=float(bt.idxmax()), b_expost=float(bt.max()))
        sh = t.groupby("C").all_full.mean(); out.update(c_firm=c_rho(sh, rho))
    return out


def price_section():
    h("DR price x delay price, and kappa = 0 (Section 5.10.3): JR-D, back-test on the 14 historical days -> C*, 26 test days")
    print("benefit = no-DR cost - cost (both at the same delay price); savings = no-DR operating cost - operating cost incl. end "
          "state; delay = extra delay cost over no DR; revenue = DR payment; short = shortfall assessment (k CNY/day).\n")
    print("| scenario | DR price (CNY/kWh) | delay price | kappa | capability mean / min | eps_N | C_DRO | C* | full % at C* (lower 95 % bound) | "
          "benefit | revenue | savings | delay | short | C firm (test) | benefit-max C (test) |")
    print("|---" * 16 + "|")
    for scen, base in [("S1", "_S1"), ("S2", "_S2")]:
        for k, p, cj in PRICE:
            tag = base + (f"_{k}" if k else "")
            hh = history(tag) if k else history(base); tt = load_capacity(tag) if k else load_capacity(base)
            if k and load_capacity(tag + "b") is not None: tt = pd.concat([tt, load_capacity(tag + "b")], ignore_index=True)
            if hh is None or tt is None: continue
            r = commit_point(hh, tt, "JR-D", cj)
            kap = 0 if k == "k0" else 1
            f = lambda v, fmt="{:.1f}": "–" if v is None or (isinstance(v, float) and np.isnan(v)) else fmt.format(v)
            full = f"{100 * r['full']:.0f} ({cp_lower(round(r['full'] * r['n']), r['n']):.2f})" if "full" in r else "–"
            print(f"| {scen} | {p / 1000:g} | {cj:g} | {kap} | {r['cap_mean']:.2f} / {r['cap_min']:.2f} | {r['eps']:.3f} | {f(r['c_dro'], '{:g}')} | "
                  f"{f(r['c_star'], '{:g}')} | {full} | {f(r.get('benefit'))} | {f(r.get('revenue'))} | {f(r.get('savings'))} | "
                  f"{f(r.get('delay'))} | {f(r.get('short'))} | {f(r.get('c_firm'), '{:g}')} | {f(r.get('c_expost'), '{:g}')} ({f(r.get('b_expost'))}) |")


def channel_section():
    h("Nominal versus actual recovery channel (Section 5.1.3, Eqs. (1)-(2)), 26 operating days")
    d = rd("exp21_channel.csv")
    if d is None: return
    names = {1: "S1 interval 18-19 h", 2: "S1 after the events 20-22 h", 3: "S2 interval 18-18.5 h", 4: "S2 after the events 19.5-21.5 h"}
    print("| window | H_nom mean (MWh) | H_act mean [min, max] | H_act - H_nom mean [min, max] | days H_act < H_nom | H_idle mean | mean (P_noDR - P_base) (MW) | corr(H_act - H_nom, dev) |")
    print("|---|---|---|---|---|---|---|---|")
    for w, g in d.groupby("window"):
        e = g.H_act_MWh - g.H_nom_MWh
        print(f"| {names[w]} | {g.H_nom_MWh.mean():.2f} | {g.H_act_MWh.mean():.2f} [{g.H_act_MWh.min():.2f}, {g.H_act_MWh.max():.2f}] | "
              f"{e.mean():+.2f} [{e.min():+.2f}, {e.max():+.2f}] | {(e < -1e-6).sum()} of {len(g)} | {g.H_idle_MWh.mean():.2f} | "
              f"{g.dev_mean_MW.mean():+.2f} | {np.corrcoef(e, g.dev_mean_MW)[0, 1]:+.2f} |")
    j = rd("exp21_channel_jrd.csv")
    if j is None: return
    print("\nJR-D at 7 MW: channel drawn in the interval, U = sum (P_grid - P_noDR) dt\n")
    for q, g in j.groupby("scenario"):
        s = "S1" if q == 1 else "S2"
        print(f"- {s}: U mean {g.U_MWh.mean():.2f} MWh [{g.U_MWh.min():.2f}, {g.U_MWh.max():.2f}]; U > H_nom on {(g.U_MWh > g.H_nom_MWh + 1e-6).sum()} days, "
              f"U > H_act on {(g.U_MWh > g.H_act_MWh + 1e-3).sum()} days; U / H_act mean {np.mean(g.U_MWh / g.H_act_MWh):.2f}; "
              f"peak import in the interval max {g.pg_max_MW.max():.2f} MW; full delivery {100 * g.all_full.mean():.0f} %")


def d78_section():
    h("78 operating days (Section 5.10.4): three weather / inference days per PAI weekday")
    print("| scenario | strategy | C (MW) | full % on 78 (lower 95 % bound) | full % on the first 26 | on realisations 27-78 |")
    print("|---|---|---|---|---|---|")
    for s in ("S1", "S2"):
        for t in (f"_{s}_d78", f"_{s}_d78m"):
            d = load_capacity(t)
            if d is None: continue
            for (n, C), g in d.groupby(["name", "C"]):
                k = int(g.all_full.sum()); n_ = len(g)
                a = g[g.realisation <= 26].all_full.mean(); b = g[g.realisation > 26].all_full.mean()
                print(f"| {s} | {n} | {C:g} | {100 * k / n_:.1f} ({cp_lower(k, n_):.3f}) | {100 * a:.0f} | {100 * b:.0f} |")


def july_section():
    h("July DR day (cross-month test, Section 5.10.4): DR day 22 July 2024, baseline and history from July")
    for s in ("S1", "S2"):
        t = load_capacity(f"_{s}_jul"); hh = history(f"_{s}_jul")
        if t is None: continue
        tab, _ = capacity_table(t, "all_full", rhos=(0.95,), B=200)
        print(f"- {s}: firm capacity on the 26 test days: " + ", ".join(f"{n} {'<1' if np.isnan(tab[n][0][0.95]) else tab[n][0][0.95]:}" for n in tab))
        if hh is not None:
            for n in ("JR-M", "JR-D"):
                if n in set(hh.name):
                    r = commit_point(hh, t, n, 0.5, ntag="_jul")
                    print(f"  {n}: capability mean / min {r['cap_mean']:.2f} / {r['cap_min']:.2f}, eps {r['eps']:.3f}, C_DRO {r['c_dro']}, C* {r['c_star']}, "
                          f"full at C* {100 * r.get('full', np.nan):.0f} %, benefit {r.get('benefit', np.nan):.1f} k CNY/day")


def all_sections():
    benchmark_section(); flex_section(); horizon_section(); price_section(); channel_section(); d78_section(); july_section()


if __name__ == "__main__":
    all_sections()
