#!/usr/bin/env python3
"""Figures of the Applied Energy manuscript (English, vector PDF/SVG + PNG preview) from matlab/results.

Usage: python3 tools/plot_paper.py [fig ...]      e.g.  python3 tools/plot_paper.py 3 5
Fig. 1 system and recovery channel | 2 typical-day recovery | 3 reliability curves | 4 two-event region |
5 strategy comparison | 6 sensitivity | 7 ablation | 8 multi-scenario statistics
"""
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from paper_style import (rd, save, shade, panel, load_capacity, capacity_table, share_band, c_rho, recovery_flows, COL, MK, LS,
                         ORDER, SCEN, EVENTS, SINGLE_COL, DOUBLE_COL)

CAP_TAGS = [("_S1", "S1"), ("_S2", "S2"), ("_S3", "S3")]


# ------------------------------------------------------------------ Fig. 3 reliability curves
def fig3():
    data = [(load_capacity(t), s) for t, s in CAP_TAGS]
    data = [(d, s) for d, s in data if d is not None]
    if not data: return
    fig, axs = plt.subplots(2, len(data), figsize=(DOUBLE_COL, 4.6), squeeze=False, sharey="row")
    fig.subplots_adjust(wspace=0.08, hspace=0.42)
    for j, (d, s) in enumerate(data):
        for i, (col, lab) in enumerate([("all_full", "Days with full delivery (%)"), ("all_valid", "Days all valid, 80 % rule (%)")]):
            ax = axs[i, j]
            for n in ORDER:
                C, m, lo, hi = share_band(d, n, col)
                if n in ("JR-D", "IR-O*"): ax.fill_between(C, 100 * lo, 100 * hi, color=COL[n], alpha=0.12, lw=0)
                ax.plot(C, 100 * m, color=COL[n], ls=LS[n], lw=1.4, marker=MK[n], ms=3.2, mfc="white", mew=0.9, label=n)
            ax.axhline(95, color="#555555", lw=0.7, ls=(0, (4, 3)))
            ax.set_ylim(-3, 104); ax.set_xlim(C.min() - 0.15, C.max() + 0.15)
            if j == 0: ax.set_ylabel(lab)
            if i == 1: ax.set_xlabel("Uniform commitment per event C (MW)")
            if i == 0: ax.set_title(SCEN[s], fontsize=8.5)
            panel(ax, "abcdef"[i * len(data) + j], x=-0.02, y=1.02)
            # firm capacities at 95 %: markers on the reliability line and the gain of JR-D over the best independent benchmark
            tab, _ = capacity_table(d, col, rhos=(0.95,), B=200)
            cr = {n: tab[n][0][0.95] for n in ORDER}
            cj = cr["JR-D"]; ci = np.nanmax([cr["IR-O*"], cr["IR-P"]]) if not np.all(np.isnan([cr["IR-O*"], cr["IR-P"]])) else np.nan
            for n in ORDER:
                if not np.isnan(cr[n]): ax.plot(cr[n], 95, marker="|", ms=9, mew=1.6, color=COL[n], zorder=4)
            if not np.isnan(cj) and i == 0:
                x0 = ci if not np.isnan(ci) else C.min()
                ya = 12
                ax.annotate("", xy=(cj, ya), xytext=(x0, ya), arrowprops=dict(arrowstyle="<|-|>", color=COL["JR-D"], lw=0.9, mutation_scale=7))
                txt = f"$\\Delta C_{{0.95}}$ = {cj - ci:+.1f} MW" if not np.isnan(ci) else f"$\\Delta C_{{0.95}}$ > {cj - C.min():.1f} MW"
                ax.text((x0 + cj) / 2, ya + 3, txt, ha="center", va="bottom", fontsize=6.8, color=COL["JR-D"],
                        bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85))
    hh, ll = axs[0, 0].get_legend_handles_labels()
    fig.subplots_adjust(top=0.9)
    fig.legend(hh, ll, loc="upper center", bbox_to_anchor=(0.5, 0.995), ncol=4, handlelength=2.6, columnspacing=1.6)
    save(fig, "Fig3_reliable_capacity")


# ------------------------------------------------------------------ Fig. 5 strategy comparison
DCOST = [("cost_energy", "Electricity", "#8fb3d9"), ("cost_gas", "Natural gas", "#e8c48a"), ("cost_deg", "Storage degradation", "#b9b9b9"),
         ("cost_delay", "Task delay", "#c9a3c9"), ("term_adj", "End-of-day state", "#a6d4c8"), ("pen_dev", "Shortfall assessment", "#e39a8f"),
         ("dr_pay", "DR revenue", "#7fbf7f")]


def endogenous_points(scen="S1", tag="_S1", rho=1.0):
    """(label, strategy, commitment text, full-delivery share %, benefit vs no DR in 10^3 CNY/day) of the endogenous protocol."""
    da = rd(f"exp16_dayahead_{scen}.csv"); en = rd(f"exp16_endogenous_{scen}.csv"); pk = rd(f"exp16_packages_{scen}.csv")
    cap = load_capacity(tag); nd = rd("exp17_nodr.csv")
    if da is None or en is None or cap is None: return []
    nodr = (nd.set_index("realisation").net_cost_adj if nd is not None else en.groupby("realisation").nodr_net_cost_adj.first())
    t = da.set_index("C"); pts = []
    for n in ORDER:
        ok = (t["full_" + n] >= rho - 1e-9).cummin().astype(bool)
        Cs = t[n][ok].idxmin(); q = cap[(cap.name == n) & np.isclose(cap.C, Cs)].set_index("realisation")
        pts.append((f"Back-test, {n}", n, f"{Cs:g}", 100 * q.all_full.mean(), (nodr.reindex(q.index) - q.net_cost_adj).mean() / 1e3, True))
    en["pkg"] = en.package.map(dict(zip(pk["index"], pk["label"])))
    for lab, n, txt in [("RA|JR-D", "JR-D", "Perfect-recourse MILP, JR-D"), ("SE|IR-O*", "IR-O*", "Single-event capability, IR-O*"),
                        ("SE|IR-P", "IR-P", "Single-event capability, IR-P")]:
        g = en[en.pkg == lab]
        if g.empty: continue
        Cv = "/".join(f"{x:.2f}" for x in g[["C1", "C2", "C3"]].iloc[0].dropna())
        pts.append((txt, n, Cv, 100 * g.all_full.mean(), (g.nodr_net_cost_adj - g.net_cost_adj).mean() / 1e3, False))
    return pts


def fig5(C0=7.0):
    nd = rd("exp17_nodr.csv")
    tabs = [(load_capacity(t), s) for t, s in CAP_TAGS]; tabs = [(d, s) for d, s in tabs if d is not None]
    if not tabs or nd is None: return
    nd = nd.set_index("realisation")
    fig = plt.figure(figsize=(DOUBLE_COL, 3.5)); gs = fig.add_gridspec(1, 2, width_ratios=[1.55, 1], wspace=0.3)
    ax = fig.add_subplot(gs[0, 0])
    x0 = 0; ticks = []; tl = []; groups = []
    for d, s in tabs:
        xs = x0
        for n in ORDER:
            q = d[(d.name == n) & np.isclose(d.C, C0)].set_index("realisation")
            if q.empty: continue
            ref = nd.reindex(q.index); up = 0; dn = 0
            for c, lab, colr in DCOST:
                v = (-q[c].mean() if c == "dr_pay" else (q[c] - ref[c]).mean()) / 1e3
                if v >= 0: ax.bar(x0, v, 0.7, bottom=up, color=colr, edgecolor="white", lw=0.3, label=lab if x0 == 0 else None); up += v
                else: ax.bar(x0, v, 0.7, bottom=dn, color=colr, edgecolor="white", lw=0.3, label=lab if x0 == 0 else None); dn += v
            net = (q.net_cost_adj - ref.net_cost_adj).mean() / 1e3
            ax.plot([x0 - 0.38, x0 + 0.38], [net, net], color="black", lw=1.8, solid_capstyle="butt", label="Net change (− benefit)" if x0 == 0 else None)
            ax.text(x0, up + 0.8, f"{100 * q.all_full.mean():.0f}%", ha="center", va="bottom", fontsize=6.4, color=COL[n], fontweight="bold")
            ticks.append(x0); tl.append(n); x0 += 1
        groups.append(((xs + x0 - 1) / 2, s)); x0 += 0.7
    ax.axhline(0, color="black", lw=0.6)
    ax.set_xticks(ticks); ax.set_xticklabels(tl, fontsize=6.5, rotation=90)
    for xm, s in groups: ax.text(xm, 1.01, s, transform=ax.get_xaxis_transform(), ha="center", va="bottom", fontsize=8)
    ax.set_ylabel("Daily cost change vs no DR (10$^3$ CNY)")
    ax.set_title(f"Fixed commitment, C = {C0:g} MW", fontsize=8, pad=13)
    ax.set_ylim(top=ax.get_ylim()[1] + 3)
    panel(ax, "a", x=-0.1, y=1.06)
    hh, ll = ax.get_legend_handles_labels()
    fig.legend(hh, ll, loc="lower center", ncol=8, bbox_to_anchor=(0.5, -0.1), fontsize=6.6, handlelength=1.4, columnspacing=0.9)
    # (b) endogenous protocol: reliability-benefit plane
    ax = fig.add_subplot(gs[0, 1]); pts = endogenous_points()
    place = {"Back-test, JR-D": (99, 49.5, "right"), "Perfect-recourse MILP, JR-D": (64, 46.5, "right"),
             "Back-test, IR-O*": (64, 41.0, "right"), "Back-test, JR-M": (97, 31.0, "center"),
             "Single-event capability, IR-O*": (4, 26.0, "left"), "Back-test, IR-P": (62, 22.0, "left"),
             "Single-event capability, IR-P": (5, 8.0, "left")}
    for lab, n, Cv, sh, ben, bt in pts:
        ax.scatter(sh, ben, s=46 if bt else 40, marker=MK[n], color=COL[n] if bt else "white", edgecolor=COL[n], lw=1.2, zorder=3)
        name = lab.split(", ")[0].replace("Single-event capability", "single-event").replace("Perfect-recourse MILP", "perfect-recourse MILP")
        txt = f"{n}, {name.lower() if name.startswith('Back') else name}\n({Cv} MW)"
        x, y, ha = place.get(lab, (sh + 4, ben + 3, "left"))
        ax.annotate(txt, (sh, ben), xytext=(x, y), textcoords="data", ha=ha, va="center", fontsize=5.9, color=COL[n],
                    arrowprops=dict(arrowstyle="-", color=COL[n], lw=0.5, shrinkA=0, shrinkB=3.5))
    ax.scatter([], [], marker="o", color="#555555", s=30, label="Back-test commitment, Eq. (15)")
    ax.scatter([], [], marker="o", color="white", edgecolor="#555555", s=30, label="Capability-based commitment")
    ax.legend(loc="lower right", fontsize=6.2, handletextpad=0.3, borderaxespad=0.3)
    ax.set_xlim(-8, 108); ax.set_ylim(-3, 55)
    ax.set_xlabel("Days with full delivery, out of sample (%)"); ax.set_ylabel("Daily benefit vs no DR (10$^3$ CNY)")
    ax.set_title("Endogenous commitment, S1", fontsize=8, pad=13); panel(ax, "b", x=-0.2, y=1.06)
    save(fig, "Fig5_strategy_comparison")


# ------------------------------------------------------------------ Fig. 8 multi-scenario statistics
def fig8():
    data = [(load_capacity(t), s) for t, s in CAP_TAGS]
    data = [(d, s) for d, s in data if d is not None]
    if not data: return
    C0 = 7.0
    fig = plt.figure(figsize=(DOUBLE_COL, 3.3)); gs = fig.add_gridspec(1, 2, width_ratios=[1.25, 1], wspace=0.28)
    ax = fig.add_subplot(gs[0, 0])
    pos = 0; ticks = []; tl = []; D = []
    for d, s in data:
        P = d[(d.name == "JR-D") & np.isclose(d.C, C0)].set_index("realisation")
        for n in ["IR-O*", "IR-P", "JR-M"]:
            B = d[(d.name == n) & np.isclose(d.C, C0)].set_index("realisation")
            D.append((pos, n, ((P.net_cost_adj - B.net_cost_adj) / 1e3).dropna().values)); pos += 1
        pos += 0.6
    allv = np.concatenate([v for _, _, v in D]); lo = np.percentile(allv, 3); hi = max(np.percentile(allv, 99.5), 0); pad = 0.1 * (hi - lo)
    for pos, n, diff in D:
        if True:
            vc = np.clip(diff, lo - pad, None)
            vp = ax.violinplot(vc, [pos], widths=0.8, showextrema=False)
            for b in vp["bodies"]: b.set_facecolor(COL[n]); b.set_alpha(0.35); b.set_edgecolor(COL[n])
            ax.boxplot(vc, positions=[pos], widths=0.18, showfliers=False, patch_artist=True,
                       boxprops=dict(facecolor="white", lw=0.6), medianprops=dict(color=COL[n], lw=1.4), whiskerprops=dict(lw=0.6), capprops=dict(lw=0.6))
            nb = int((diff < lo - pad).sum())
            if nb: ax.text(pos, lo - pad * 0.6, f"{nb} day{'s' if nb > 1 else ''} ↓", ha="center", fontsize=6, color="#555555")
            ticks.append(pos); tl.append(f"{[s for _, s in data][int(pos // 3.6)]}\nvs {n}")
    ax.axhline(0, color="black", lw=0.6); ax.set_ylim(lo - pad, hi + pad)
    ax.set_xticks(ticks); ax.set_xticklabels(tl, fontsize=6.5); ax.set_ylabel("Daily cost, JR-D − benchmark (10$^3$ CNY)")
    ax.set_title(f"Paired daily cost differences, C = {C0:g} MW", fontsize=8)
    panel(ax, "a", x=-0.1)
    # ridgeline: worst-event delivery ratio across test days
    ax = fig.add_subplot(gs[0, 1]); d, s = data[min(1, len(data) - 1)]
    q = d[np.isclose(d.C, C0)].copy()
    q["ratio"] = q[["red_E1", "red_E2", "red_E3"]].min(axis=1) / C0
    grid = np.linspace(0.3, 1.25, 300)
    for k, n in enumerate(ORDER):
        v = q[q.name == n].ratio.dropna().values
        bw = 0.06; dens = np.exp(-0.5 * ((grid[:, None] - v[None, :]) / bw) ** 2).sum(axis=1); dens = dens / dens.max() * 0.85
        ax.fill_between(grid, k, k + dens, color=COL[n], alpha=0.55, lw=0); ax.plot(grid, k + dens, color=COL[n], lw=0.8)
        ax.text(0.31, k + 0.12, n, fontsize=7.5, color=COL[n])
    ax.axvline(0.98, color="black", lw=0.7, ls="--"); ax.axvline(0.8, color="#888888", lw=0.6, ls=":")
    ax.text(0.98, len(ORDER) + 0.05, "full", ha="center", fontsize=7); ax.text(0.8, len(ORDER) + 0.05, "valid", ha="center", fontsize=7)
    ax.set_yticks([]); ax.set_xlabel("Worst-event delivery ratio min$_k$ $R_k$/C"); ax.set_xlim(0.3, 1.25); ax.set_ylim(0, len(ORDER) + 0.4)
    ax.set_title(f"{SCEN[s]}, C = {C0:g} MW", fontsize=8); panel(ax, "b", x=-0.04)
    save(fig, "Fig8_multi_scenario")


# ------------------------------------------------------------------ Fig. 2 typical-day recovery mechanism
FIG2_CASE = ""          # suffix of the typical-day case of exp15 (e.g. "_r21"); set by the environment variable FIG2_CASE


def fig2():
    import os
    suf = os.environ.get("FIG2_CASE", FIG2_CASE)
    cases = [("short", "Short interval (30 min)"), ("long", "Long interval (3 h)")]
    S = [("IROs", "IR-O*"), ("JRM", "JR-M"), ("JRD", "JR-D")]
    D = {c: {n: rd(f"ts15_{c}{suf}_{f}.csv") for f, n in S} for c, _ in cases}
    if any(v is None for c in D for v in D[c].values()): return
    fig, axs = plt.subplots(4, 2, figsize=(DOUBLE_COL, 7.4), sharex="col"); fig.subplots_adjust(hspace=0.12, wspace=0.22)
    for j, (c, title) in enumerate(cases):
        ev = EVENTS[c]; J = D[c]["JR-D"]; I = D[c]["IR-O*"]; h = J.hour
        a = axs[0, j]; shade(a, ev)
        a.plot(h, J.base, color="black", lw=0.9, ls="--", label="DR baseline")
        a.axhline(J.Pcap.iloc[0], color="#b22222", lw=0.8, label="Connection limit")
        for n in ["IR-O*", "JR-M", "JR-D"]:
            a.plot(h, D[c][n].pg, color=COL[n], ls=LS[n], lw=1.3, label=n)
        a.set_ylabel("Grid import (MW)"); a.set_title(title, fontsize=9); panel(a, "ae"[j], x=-0.13)
        a = axs[1, j]; shade(a, ev)
        cl = ["#9ecae1", "#4292c6", "#08519c"]
        a.stackplot(h, J.B1 / 1e3, J.B2 / 1e3, J.B3 / 1e3, colors=cl, labels=["C1 (L = 0.5 h), JR-D", "C2 (L = 1.5 h), JR-D", "C3 (L = 3 h), JR-D"], alpha=0.9, lw=0)
        a.plot(h, (I.B1 + I.B2 + I.B3) / 1e3, color=COL["IR-O*"], ls="--", lw=1.2, label="Total backlog, IR-O*")
        a.set_ylabel("Backlog (10$^3$ GPU·h)"); panel(a, "bf"[j], x=-0.13)
        a = axs[2, j]; shade(a, ev)
        a.bar(h, J.pdis - J.pch, width=0.22, color=np.where(J.pdis - J.pch >= 0, "#1f5fa8", "#8fb3d9"), label="BESS discharge (+) / charge (−), JR-D")
        a2 = a.twinx(); a2.grid(False)
        for n in ["IR-O*", "JR-D"]:
            a2.plot(h, D[c][n].E, color=COL[n], ls=LS[n], lw=1.3, label=f"BESS energy, {n}")
        a.set_ylabel("BESS power (MW)"); a2.set_ylabel("BESS energy (MWh)"); panel(a, "cg"[j], x=-0.13)
        if j == 0:
            hh, ll = a.get_legend_handles_labels(); h2, l2 = a2.get_legend_handles_labels()
            a.legend(hh + h2, ll + l2, loc="lower left", fontsize=6.5)
        a = axs[3, j]; shade(a, ev)
        for k, (n, sgn) in enumerate([("JR-D", 1), ("IR-O*", -1)]):
            q = D[c][n]
            phi = 1.05 + 1.0 / q.cop
            pdyn = 8.4 / 8 / 1000 * 0.75
            catch = np.maximum((q.y1 + q.y2 + q.y3) - (q.a1 + q.a2 + q.a3), 0) * pdyn * phi
            rech = q.pch + q.qtc / q.cop
            out = np.ones(len(h), bool)
            for s0, e0 in ev: out &= ~((h >= s0) & (h < e0))
            a.fill_between(h, 0, sgn * catch * out, color="#e07b2a" if sgn > 0 else "#f3b98a", step="post", lw=0, label=f"Compute catch-up, {n}")
            a.fill_between(h, sgn * catch * out, sgn * (catch + rech) * out, color="#1f5fa8" if sgn > 0 else "#8fb3d9", step="post", lw=0, label=f"Storage recharge, {n}")
        a.axhline(0, color="black", lw=0.6)
        a.text(0.01, 0.93, "JR-D", transform=a.transAxes, fontsize=7.5, va="top"); a.text(0.01, 0.06, "IR-O*", transform=a.transAxes, fontsize=7.5)
        a.set_ylabel("Recovery power (MW)"); a.set_xlabel("Hour of day"); panel(a, "dh"[j], x=-0.13)
        if j == 0: a.legend(loc="upper right", fontsize=6.3, ncol=2)
        for a in axs[:, j]: a.set_xlim(15, 26)
    axs[0, 0].legend(loc="lower left", fontsize=6.5, ncol=2); axs[1, 0].legend(loc="upper right", fontsize=6.5)
    save(fig, "Fig2_recovery_mechanism" + (os.environ.get("FIG2_OUT", "") if suf else ""))


# ------------------------------------------------------------------ Fig. 4 two-event reliability region
def fig4(rho=0.9):
    sets = []
    for tag, lab in [("_S2-30", "S2: 30-min interval"), ("_S1", "S1: 1-h interval")]:
        d = rd(f"exp14_region{tag}.csv"); s = rd(f"exp14_region{tag}_strategies.csv")
        if d is not None: d["name"] = d.strategy.map(dict(zip(s["index"], s["label"]))); sets.append((d, lab))
    if not sets: return
    fig, axs = plt.subplots(1, len(sets), figsize=(SINGLE_COL * len(sets), 3.2), squeeze=False); fig.subplots_adjust(wspace=0.25)
    for j, (d, lab) in enumerate(sets):
        ax = axs[0, j]; g = d.groupby(["name", "C1", "C2"]).all_full.mean().reset_index()
        Cg = np.sort(g.C1.unique())
        for n in [x for x in ORDER if x in g.name.unique()]:
            q = g[g.name == n]
            bd = []
            for c1 in Cg:
                ok = q[(q.C1 == c1)].sort_values("C2"); v = ok.all_full.values >= rho - 1e-9
                k = len(v) if v.all() else int(np.argmin(v)); bd.append(ok.C2.values[k - 1] if k > 0 else np.nan)
            bd = np.array(bd)
            ax.step(Cg, bd, where="mid", color=COL[n], ls=LS[n], lw=1.6, label=n)
            if n == "JR-D": ax.fill_between(Cg, 0, np.nan_to_num(bd), step="mid", color=COL[n], alpha=0.08)
        ax.plot([Cg.min(), Cg.max()], [Cg.min(), Cg.max()], color="#888888", lw=0.6, ls=":")
        ax.set_xlabel("Commitment of event 1, $C_1$ (MW)"); ax.set_ylabel("Commitment of event 2, $C_2$ (MW)")
        ax.set_xlim(Cg.min() - 0.5, Cg.max() + 0.5); ax.set_ylim(Cg.min() - 0.5, Cg.max() + 0.5)
        ax.set_title(f"{lab}, reliability ≥ {100 * rho:.0f} %", fontsize=8.5); panel(ax, "ab"[j])
    axs[0, 0].legend(loc="lower left")
    save(fig, "Fig4_two_event_region")


# ------------------------------------------------------------------ Fig. 6 sensitivity
def fig6():
    d = rd("exp14_tau_gamma.csv"); s = rd("exp14_tau_gamma_strategies.csv"); cfg = rd("exp14_tau_gamma_cfg.csv")
    if d is None: return
    d["name"] = d.strategy.map(dict(zip(s["index"], s["label"]))); lab = dict(zip(cfg["cfg"], cfg["label"]))
    d["gap"] = d.cfg.map(lambda i: float(lab[i].split("_")[0][3:])); d["gamma"] = d.cfg.map(lambda i: float(lab[i].split("_")[1][1:]))
    g = d.groupby(["gap", "gamma", "name"]).all_full.mean().unstack("name")
    gain_ir = 100 * (g["JR-D"] - g[["IR-O*", "IR-P"]].max(axis=1)); gain_m = 100 * (g["JR-D"] - g["JR-M"])
    sd = rd("exp14_single.csv"); ss = rd("exp14_single_strategies.csv"); sc = rd("exp14_single_cfg.csv")
    fig = plt.figure(figsize=(DOUBLE_COL, 3.0)); gsp = fig.add_gridspec(1, 4, width_ratios=[1, 1, 0.8, 0.8], wspace=0.45)
    for k, (Z, title) in enumerate([(gain_ir, "JR-D − best independent (pp)"), (gain_m, "JR-D − JR-M (pp)")]):
        ax = fig.add_subplot(gsp[0, k]); M = Z.unstack("gap"); ax.grid(False)
        im = ax.imshow(M.values, origin="lower", aspect="auto", cmap="Blues", vmin=0, vmax=max(5, np.nanmax(M.values)))
        for i in range(M.shape[0]):
            for jj in range(M.shape[1]):
                v = M.values[i, jj]; ax.text(jj, i, f"{v:.0f}", ha="center", va="center", fontsize=7, color="white" if v > 0.6 * np.nanmax(M.values) else "black")
        ax.set_xticks(range(M.shape[1])); ax.set_xticklabels([f"{x:g}" for x in M.columns]); ax.set_yticks(range(M.shape[0])); ax.set_yticklabels([f"{x:.2f}" for x in M.index])
        ax.set_xlabel("Event interval τ (h)"); ax.set_ylabel("Connection margin γ" if k == 0 else ""); ax.set_title(title, fontsize=8); panel(ax, "ab"[k], x=-0.25)
    if sd is not None:
        sd["name"] = sd.strategy.map(dict(zip(ss["index"], ss["label"]))); lab2 = dict(zip(sc["cfg"], sc["label"]))
        sd["cfgname"] = sd.cfg.map(lab2)
        for k, (key, xlab, conv, b0) in enumerate([("lag", "Lag-bound scale of $L_c$", lambda x: float(x[3:]), 1.0), ("bess", "BESS power (MW)", lambda x: float(x[4:]), 6.0)]):
            ax = fig.add_subplot(gsp[0, 2 + k]); q = sd[sd.cfgname.str.startswith(key)].copy(); q["x"] = q.cfgname.map(conv)
            gb = q.groupby(["x", "name"]).all_full.mean().unstack("name") * 100
            b = d[(d.gap == 1.0) & np.isclose(d.gamma, 1.10)].groupby("name").all_full.mean() * 100
            gb.loc[b0] = b; gb = gb.sort_index()
            for n in ORDER:
                if n in gb: ax.plot(gb.index, gb[n], color=COL[n], ls=LS[n], marker=MK[n], ms=3.5, mfc="white", lw=1.3, label=n)
            ax.set_xlabel(xlab); ax.set_ylabel("Full delivery (%)" if k == 0 else ""); ax.set_ylim(-3, 104); panel(ax, "cd"[k], x=-0.3)
        fig.axes[-2].legend(loc="lower right", fontsize=6.5)
    save(fig, "Fig6_sensitivity")


# ------------------------------------------------------------------ Fig. 7 ablation
def fig7(rho=0.95):
    a = rd("exp14_ablation.csv"); s1 = load_capacity("_S1")
    if a is None or s1 is None: return
    cfg = rd("exp14_ablation_cfg.csv"); names = dict(zip(cfg["cfg"], cfg["label"])); a["config"] = a.cfg.map(names)
    a["C"] = a.C1
    cap = {}
    for c in a.config.unique():
        sh = a[a.config == c].groupby("C").all_full.mean(); cap[c] = c_rho(sh, rho)
    for n in ORDER:
        cap[n] = c_rho(s1[s1.name == n].groupby("C").all_full.mean(), rho)
    steps = [("BESS only", cap.get("BESS_only")), ("Compute only", cap.get("compute_only")), ("Compute + BESS", cap.get("compute_BESS")),
             ("+ TES, independent (best IR)", np.nanmax([cap["IR-O*"], cap["IR-P"]])), ("+ joint, event-by-event (JR-M)", cap["JR-M"]),
             ("+ cross-event foresight (JR-D)", cap["JR-D"])]
    fig, ax = plt.subplots(figsize=(DOUBLE_COL * 0.62, 2.9))
    prev = 0
    for k, (lab, v) in enumerate(steps):
        v = 0 if v is None or np.isnan(v) else v
        colr = "#8fb3d9" if k < 3 else ("#e07b2a" if k == 3 else ("#c4508a" if k == 4 else "#1f5fa8"))
        if k < 3:
            ax.bar(k, v, 0.6, color=colr, edgecolor="black", lw=0.4)
        else:
            ax.bar(k, v - prev, 0.6, bottom=prev, color=colr, edgecolor="black", lw=0.4)
            ax.plot([k - 1.3, k + 0.3], [prev, prev], color="#555555", lw=0.6, ls=":")
        ax.text(k, v + 0.12, f"{v:.1f}", ha="center", fontsize=7.5)
        if k >= 2: prev = v
    ax.set_xticks(range(len(steps))); ax.set_xticklabels([s for s, _ in steps], rotation=18, ha="right", fontsize=7)
    ax.set_ylabel(f"Firm capacity $C_{{{rho}}}^{{firm}}$ (MW)"); ax.set_title("S1, full delivery of every event", fontsize=8.5)
    save(fig, "Fig7_ablation")


# ------------------------------------------------------------------ Fig. 1 system and recovery channel
def _box(ax, x, y, w, h, text, fc, ec="#333333", fs=7, bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012,rounding_size=0.015", fc=fc, ec=ec, lw=0.7))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, fontweight="bold" if bold else "normal")


def _arr(ax, p, q, color, ls="-", lw=1.1, style="-|>", rad=0.0):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=7, color=color, lw=lw, ls=ls,
                                 connectionstyle=f"arc3,rad={rad}", shrinkA=1, shrinkB=1))


def fig1():
    fig = plt.figure(figsize=(DOUBLE_COL, 3.6)); gs = fig.add_gridspec(1, 2, width_ratios=[1.15, 1], wspace=0.2)
    ax = fig.add_subplot(gs[0, 0]); ax.set_xlim(-0.03, 1.03); ax.set_ylim(-0.06, 1.0); ax.axis("off")
    E, Cc, Hh, W = "#1f5fa8", "#2aa7c9", "#c0392b", "#7a5cb8"
    _box(ax, 0.00, 0.83, 0.40, 0.13, "Day-ahead recovery-aware\ncommitment $C_k$: closed-loop\nback-test at reliability $\\rho$", "#eef3fa", fs=5.6)
    _box(ax, 0.44, 0.83, 0.56, 0.13, "Intraday cross-event joint recovery MPC\n$y_{c,t}$, BESS, TES, gas engine", "#eef3fa", fs=5.9)
    _box(ax, 0.00, 0.53, 0.17, 0.15, "Utility grid\n$P^{grid}_t \\leq P^{cap}$", "#f2f2f2", fs=6.0)
    _box(ax, 0.00, 0.30, 0.17, 0.12, "DR operator\n(Jiangsu rules)", "#fff7e6", fs=6.0)
    _box(ax, 0.23, 0.58, 0.14, 0.09, "PV", "#fff3cc", fs=6.2)
    _box(ax, 0.23, 0.40, 0.14, 0.12, "Gas engine\n(CCHP)", "#fde3d6", fs=6.0)
    _box(ax, 0.23, 0.18, 0.14, 0.12, "BESS\nSOC $E_t$", "#dce9f7", fs=6.0)
    _box(ax, 0.43, 0.04, 0.17, 0.11, "Absorption\nchiller", "#e3f4f8", fs=6.0)
    _box(ax, 0.43, 0.20, 0.17, 0.11, "Electric chiller\nCOP($T_t$)", "#e3f4f8", fs=6.0)
    _box(ax, 0.66, 0.04, 0.14, 0.11, "TES\n$S_t$", "#e3f4f8", fs=6.0)
    ax.add_patch(FancyBboxPatch((0.43, 0.38), 0.57, 0.36, boxstyle="round,pad=0.012,rounding_size=0.02", fc="#f6f1fb", ec=W, lw=0.8))
    ax.text(0.715, 0.70, "GPU cluster (16 000 GPUs)", ha="center", fontsize=6.4, fontweight="bold", color=W)
    _box(ax, 0.445, 0.53, 0.125, 0.12, "Inference\n+ Flex-0\n(fixed)", "white", ec=W, fs=5.4)
    for k, (lab, L) in enumerate([("C1", "0.5 h"), ("C2", "1.5 h"), ("C3", "3 h")]):
        _box(ax, 0.585 + 0.137 * k, 0.53, 0.125, 0.12, f"{lab} queue\n$L_c$ = {L}", "white", ec=W, fs=5.4)
    ax.text(0.715, 0.435, "backlog $B_{c,t}$: deadline-bound debt", ha="center", fontsize=5.8, color=W, style="italic")
    _arr(ax, (0.17, 0.61), (0.43, 0.61), E); _arr(ax, (0.37, 0.625), (0.43, 0.625), E)
    _arr(ax, (0.37, 0.46), (0.43, 0.46), E); _arr(ax, (0.37, 0.24), (0.43, 0.40), E, rad=-0.15)
    _arr(ax, (0.17, 0.56), (0.23, 0.27), E, rad=-0.25)
    _arr(ax, (0.30, 0.40), (0.47, 0.15), Hh, rad=0.2)
    _arr(ax, (0.60, 0.09), (0.66, 0.09), Cc, ls="--"); _arr(ax, (0.56, 0.31), (0.62, 0.38), Cc, ls="--"); _arr(ax, (0.74, 0.15), (0.78, 0.38), Cc, ls="--")
    _arr(ax, (0.085, 0.42), (0.085, 0.53), "#b8860b", style="<|-|>")
    _arr(ax, (0.12, 0.83), (0.085, 0.68), "#555555", ls=":"); _arr(ax, (0.72, 0.83), (0.72, 0.74), "#555555", ls=":")
    for k, (c, l, ls_) in enumerate([(E, "electricity", "-"), (Cc, "cooling", "--"), (Hh, "heat", "-"), (W, "computing", "-")]):
        ax.plot([0.02 + 0.25 * k, 0.07 + 0.25 * k], [-0.01, -0.01], color=c, ls=ls_, lw=1.2); ax.text(0.08 + 0.25 * k, -0.01, l, fontsize=5.8, va="center")
    panel(ax, "a", x=0.0, y=0.98)
    ax = fig.add_subplot(gs[0, 1]); t = np.linspace(16, 22, 600)
    base = 9.6 + 0.25 * np.sin((t - 16) / 1.7)
    ev = [(17, 18), (18.75, 19.75)]
    pg = base.copy()
    for a0, b0 in ev: pg = np.where((t >= a0) & (t < b0), base - 6.0, pg)
    gap = (t >= 18) & (t < 18.75); after = t >= 19.75
    cap = 14.9
    pg = np.where(gap, base + (cap - 0.15 - base) * (1 - np.exp(-(t - 18) * 14)), pg)
    pg = np.where(after, base + 3.0 * np.exp(-(t - 19.75) * 1.4), pg)
    ax.plot(t, base, color="black", lw=0.9, ls="--", label="DR baseline $P^{base}_t$")
    ax.axhline(cap, color="#b22222", lw=0.9, label="Connection limit $P^{cap}$")
    ax.plot(t, pg, color=COL["JR-D"], lw=1.6, label="Grid import $P^{grid}_t$")
    for a0, b0 in ev: ax.axvspan(a0, b0, color="#1f5fa8", alpha=0.08, lw=0)
    tg = t[gap]; bg = base[gap]; top = pg[gap]; mid = bg + 0.55 * (top - bg)
    ax.fill_between(tg, bg, mid, color="#e07b2a", alpha=0.55, lw=0, label="Compute catch-up (backlog)")
    ax.fill_between(tg, mid, top, color="#1f5fa8", alpha=0.35, lw=0, label="Storage recharge (SOC deficit)")
    ax.annotate("one recovery channel,\ntwo heterogeneous debts", xy=(18.4, 13.3), xytext=(19.95, 13.0), fontsize=6.2, ha="left", va="center",
                arrowprops=dict(arrowstyle="-|>", lw=0.7, color="#333333"))
    yb = base[np.argmin(np.abs(t - 17.5))] - 6.0
    ax.text(17.5, yb + 0.45, "$R_1 \\geq C_1$", ha="center", fontsize=6.4); ax.text(19.25, yb + 0.45, "$R_2 \\geq C_2$ ?", ha="center", fontsize=6.4)
    ax.annotate("", xy=(18.0, 2.4), xytext=(18.75, 2.4), arrowprops=dict(arrowstyle="<|-|>", lw=0.7)); ax.text(18.37, 2.75, "τ", ha="center", fontsize=6.6)
    ax.set_xlim(16, 22); ax.set_ylim(1.5, 16.2); ax.set_xlabel("Hour of day"); ax.set_ylabel("Power (MW)")
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), fontsize=5.8, ncol=2, columnspacing=0.8, handlelength=1.8)
    panel(ax, "b", x=-0.16, y=1.0)
    save(fig, "Fig1_system_recovery_channel")


# ------------------------------------------------------------------ supplementary figures
def figS1():
    files = [("exp1_mechanism_CA6_DA2.csv", "Event A: 6 MW × 2 h, event B: 1 h"), ("exp1_mechanism_CA6_DA1_DB2.csv", "Event A: 6 MW × 1 h, event B: 2 h")]
    data = [(rd(f), t) for f, t in files]
    if any(x is None for x, _ in data): return
    fig, axs = plt.subplots(1, 3, figsize=(DOUBLE_COL, 2.7), gridspec_kw=dict(width_ratios=[1, 1, 1.15])); fig.subplots_adjust(wspace=0.32)
    for j, (d, t) in enumerate(data):
        a = axs[j]; g = d[np.isclose(d.gamma, 1.10)]
        a.plot(g.tau_h, g.G_JR / g.G0, color=COL["JR-D"], lw=1.4, marker="o", ms=3, label="Joint response + joint recovery")
        a.plot(g.tau_h, g.G_IR / g.G0, color=COL["IR-O*"], lw=1.4, marker="s", ms=3, ls="--", label="Independent recovery (rule)")
        a.plot(g.tau_h, g.G_IRJ / g.G0, color=COL["IR-P"], lw=1.4, marker="^", ms=3, ls="-.", label="IR post-event state + joint recovery")
        a.plot(g.tau_h, g.G_bound / g.G0, color=COL["IR-P"], lw=0.9, ls=":", label="Proposition 1 bound (IR post-event state)")
        a.fill_between(g.tau_h, g.G_IRJ / g.G0, g.G_bound / g.G0, color=COL["IR-P"], alpha=0.12, lw=0)
        a.set_ylim(0, 1.08); a.set_xlabel("Event interval τ (h)"); a.set_ylabel("Deliverable capability $Γ_B/Γ_B^0$" if j == 0 else "")
        a.set_title(t, fontsize=7.8); panel(a, "ab"[j], x=-0.18)
    axs[0].legend(loc="lower right", fontsize=5.8)
    d = data[0][0]; taus = sorted(d.tau_h.unique()); gams = sorted(d.gamma.unique())
    Z = np.array([[float((d[(d.gamma == g) & (d.tau_h == t)].G_JR - d[(d.gamma == g) & (d.tau_h == t)].G_IR).iloc[0] / d[(d.gamma == g) & (d.tau_h == t)].G0.iloc[0]) for t in taus] for g in gams])
    a = axs[2]; a.grid(False); im = a.imshow(100 * Z, origin="lower", aspect="auto", cmap="Blues", vmin=0)
    for i in range(len(gams)):
        for k in range(len(taus)): a.text(k, i, f"{100 * Z[i, k]:.0f}", ha="center", va="center", fontsize=6, color="white" if Z[i, k] > 0.35 else "black")
    a.set_xticks(range(len(taus))); a.set_xticklabels([f"{x:g}" for x in taus]); a.set_yticks(range(len(gams))); a.set_yticklabels([f"{x:.2f}" for x in gams])
    a.set_xlabel("Event interval τ (h)"); a.set_ylabel("Connection margin γ"); a.set_title("Capability gain of joint recovery (% of $Γ_B^0$)", fontsize=7.8)
    panel(a, "c", x=-0.22)
    save(fig, "FigS1_mechanism_bound")


def figS2():
    d = rd("exp11_stylized.csv")
    if d is None: return
    Ls = sorted(d.L_h.unique())
    fig, axs = plt.subplots(1, len(Ls), figsize=(DOUBLE_COL, 2.3), sharey=True); fig.subplots_adjust(wspace=0.08)
    for a, L in zip(np.atleast_1d(axs), Ls):
        q = d[d.L_h == L]
        a.plot(q.tau_h, q.G_JR_closed, color=COL["JR-D"], lw=1.4, label="JR, closed form"); a.plot(q.tau_h, q.G_IR_closed, color=COL["IR-O*"], lw=1.4, ls="--", label="IR, closed form")
        a.scatter(q.tau_h, q.G_JR_lp, s=10, color=COL["JR-D"], marker="o", facecolor="white", zorder=3, label="JR, LP"); a.scatter(q.tau_h, q.G_IR_lp, s=10, color=COL["IR-O*"], marker="s", facecolor="white", zorder=3, label="IR, LP")
        a.set_title(f"Lag bound L = {L:g} h", fontsize=7.8); a.set_xlabel("Event interval τ (h)")
    np.atleast_1d(axs)[0].set_ylabel("Deliverable reduction of event B (MW)"); np.atleast_1d(axs)[0].legend(fontsize=5.8, loc="lower right")
    err = max((d.G_JR_closed - d.G_JR_lp).abs().max(), (d.G_IR_closed - d.G_IR_lp).abs().max())
    fig.text(0.99, 0.01, f"max |closed form − LP| = {err:.1e} MW over {len(d)} cases", ha="right", fontsize=6.5)
    save(fig, "FigS2_proposition2_check")


def figS3():
    files = [("", "A 1 h, B 1 h"), ("_DA2", "A 2 h, B 1 h"), ("_DB2", "A 1 h, B 2 h"), ("_K3", "Three events: E1 = E2 = $C_1$, max E3")]
    panels = []
    for tag, lab in files:
        d = rd(f"exp13_region{tag}.csv")
        if d is None: continue
        for tau, q in d.groupby("tau_h"): panels.append((f"{lab}, τ = {tau:g} h", q.sort_values("C1")))
    if not panels: return
    n = len(panels); nc = 4; nr = int(np.ceil(n / nc))
    fig, axs = plt.subplots(nr, nc, figsize=(DOUBLE_COL, 2.0 * nr), sharex=True, sharey=True, squeeze=False); fig.subplots_adjust(wspace=0.08, hspace=0.35)
    for k in range(n, nr * nc): axs.flat[k].set_visible(False)
    for k, (t, q) in enumerate(panels):
        a = axs.flat[k]
        for col, n_, ls in [("C2_JR", "JR-D", "-"), ("C2_JRM", "JR-M", ":"), ("C2_IRO", "IR-O*", "--")]:
            a.plot(q.C1, q[col], color=COL[n_], ls=ls, lw=1.3, label={"JR-D": "JR", "JR-M": "JR-M", "IR-O*": "IR-O* (best split)"}[n_])
        a.plot(q.C1, q.C2_IRJ, color=COL["IR-P"], ls="-.", lw=1.1, label="IR state + joint recovery")
        a.set_title(t, fontsize=6.8); a.set_ylim(0, 8.8)
    for a in axs[-1, :]: a.set_xlabel("$C_1$ (MW)")
    for a in axs[:, 0]: a.set_ylabel("max $C_2$ (MW)")
    axs.flat[0].legend(fontsize=5.6, loc="lower left")
    save(fig, "FigS3_perfect_information_regions")


def figS4():
    d = rd("exp4_e3uncertain.csv"); s = rd("exp4_e3uncertain_strategies.csv")
    if d is None or s is None: return
    d["name"] = d.strategy.map(dict(zip(s["index"], s["label"])))
    names = list(s["label"]); fig, axs = plt.subplots(1, 2, figsize=(DOUBLE_COL, 2.7)); fig.subplots_adjust(wspace=0.3)
    for j, (col, lab, sc) in enumerate([("net_cost_adj", "Mean daily cost (10$^3$ CNY)", 1e-3), ("fulfil_rate_pct", "Mean fulfilment (%)", 1)]):
        a = axs[j]; w = 0.38
        for k, called in enumerate([1, 0]):
            v = [d[(d.name == n) & (d.called_E3 == called)][col].mean() * sc for n in names]
            a.bar(np.arange(len(names)) + (k - 0.5) * w, v, w, color=["#1f5fa8", "#8fb3d9"][k], edgecolor="white", label=["E3 called", "E3 cancelled"][k])
        a.set_xticks(range(len(names))); a.set_xticklabels(names, fontsize=6.8); a.set_ylabel(lab); panel(a, "ab"[j])
        if j == 1: a.set_ylim(60, 102)
    axs[0].legend(fontsize=6.5); fig.suptitle("S3 with call uncertainty of the rapid peak-shaving event E3 (p = 0.6, 1 h notice), C = 6 MW", fontsize=8, y=1.02)
    save(fig, "FigS4_call_uncertainty")


def figS5():
    d = rd("exp8_rebound.csv"); s = rd("exp8_strategies.csv")
    if d is None or s is None: return
    d["name"] = d.strategy.map(dict(zip(s["index"], s["label"])))
    fig, axs = plt.subplots(1, 2, figsize=(DOUBLE_COL, 2.6)); fig.subplots_adjust(wspace=0.3)
    for n in ORDER:
        q = d[d.name == n].sort_values("c_rb")
        if q.empty: continue
        axs[0].plot(q.max_rebound_MW, q.net_cost_excl_rb / 1e3, color=COL[n], ls=LS[n], marker=MK[n], ms=3.5, mfc="white", lw=1.2, label=n)
        axs[1].plot(q.c_rb / 1e3, q.max_rebound_MW, color=COL[n], ls=LS[n], marker=MK[n], ms=3.5, mfc="white", lw=1.2, label=n)
    axs[0].set_xlabel("Peak post-event rebound (MW)"); axs[0].set_ylabel("Cost under Jiangsu rules (10$^3$ CNY)"); panel(axs[0], "a")
    axs[1].set_xlabel("Rebound assessment price $c^{rb}$ (CNY/kW per event)"); axs[1].set_ylabel("Peak post-event rebound (MW)"); panel(axs[1], "b")
    axs[0].legend(fontsize=6.5)
    save(fig, "FigS5_rebound_policy")


def figS6():
    d = rd("exp5_shadow.csv")
    if d is None: return
    fig, axs = plt.subplots(2, 1, figsize=(SINGLE_COL * 1.4, 3.6), sharex=True); fig.subplots_adjust(hspace=0.15)
    a = axs[0]; shade(a, EVENTS["S1"]); a.step(d.hour, d.price, where="post", color="black", lw=0.8, ls="--", label="TOU price")
    a.plot(d.hour, d.lambda_el, color=COL["JR-D"], lw=1.3, label="Recovery-channel price λ (electric balance dual)")
    a.set_ylabel("CNY/MWh"); a.legend(fontsize=6.3, loc="upper left"); a.set_ylim(0, max(2500, float(np.nanpercentile(d.lambda_el, 97)) * 1.1)); panel(a, "a", x=-0.12)
    a = axs[1]; shade(a, EVENTS["S1"])
    for k, c in zip([1, 2, 3], ["#9ecae1", "#4292c6", "#08519c"]): a.plot(d.hour, d[f"cost_B{k}"], color=c, lw=1.3, label=f"Backlog value C{k}")
    a.set_ylabel("CNY per GPU·h"); a.set_xlabel("Hour of day"); a.legend(fontsize=6.3); panel(a, "b", x=-0.12)
    for a in axs: a.set_xlim(12, 30)
    save(fig, "FigS6_shadow_prices")


FIGS = {"1": fig1, "2": fig2, "3": fig3, "4": fig4, "5": fig5, "6": fig6, "7": fig7, "8": fig8, "S1": figS1, "S2": figS2, "S3": figS3, "S4": figS4, "S5": figS5, "S6": figS6}



# ------------------------------------------------------------------ Fig. 13 firm capacity vs computing service quality
def fig13(rho=0.95):
    data = [(load_capacity(t), s) for t, s in CAP_TAGS[:2]]
    data = [(d, s) for d, s in data if d is not None]
    if not data: return
    fig, axs = plt.subplots(2, len(data), figsize=(DOUBLE_COL, 5.0), squeeze=False); fig.subplots_adjust(wspace=0.22, hspace=0.38)
    for j, (d, s) in enumerate(data):
        g = d.groupby(["name", "C"]).agg(delay=("mean_delay_h", "mean"), sla=("sla_use_pct", "mean"), full=("all_full", "mean")).reset_index()
        for i, (col, xl) in enumerate([("delay", "Mean extra completion time of deferred work (h)"), ("sla", "SLA slack used (%)")]):
            ax = axs[i, j]
            for n in ORDER:
                q = g[g.name == n].sort_values("C")
                ax.plot(q[col], q.C, color=COL[n], ls=LS[n], lw=1.1, alpha=0.8)
                firm = q.full >= rho - 1e-9
                ax.scatter(q[col][firm], q.C[firm], marker=MK[n], s=24, color=COL[n], zorder=3, label=n if (i == 0 and j == 0) else None)
                ax.scatter(q[col][~firm], q.C[~firm], marker=MK[n], s=20, facecolor="white", edgecolor=COL[n], lw=0.9, zorder=3)
            # Pareto front of firm operating points (largest commitment for a given service-quality cost)
            f = g[g.full >= rho - 1e-9].sort_values(col); best = -np.inf; fx, fy = [], []
            for _, r in f.iterrows():
                if r.C > best + 1e-9: best = r.C; fx.append(r[col]); fy.append(r.C)
            if fx:
                ax.step(fx + [ax.get_xlim()[1]], fy + [fy[-1]], where="post", color="#555555", lw=0.8, ls=(0, (3, 2)), zorder=1,
                        label="Front of firm points" if (i == 0 and j == 0) else None)
            ax.set_xlabel(xl); ax.set_ylabel("Uniform commitment C (MW)" if j == 0 else "")
            if i == 0: ax.set_title(SCEN[s], fontsize=8.5)
            panel(ax, "abcd"[i * len(data) + j], x=-0.14 if j == 0 else -0.08)
    fig.legend(*axs[0, 0].get_legend_handles_labels(), loc="upper center", bbox_to_anchor=(0.5, 1.0), ncol=5, fontsize=7)
    fig.subplots_adjust(top=0.9)
    save(fig, "Fig13_capacity_service_pareto")


FIGS["13"] = fig13


# ------------------------------------------------------------------ Fig. 2 framework: day-ahead DRO commitment + intraday joint recovery
def fig2_framework():
    fig, ax = plt.subplots(figsize=(DOUBLE_COL, 3.7)); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    B, O, G, P, K = "#eef3fa", "#fdf0e6", "#eaf5ec", "#f3eefa", "#333333"
    for y0, h, lab in [(0.53, 0.44, "Day-ahead layer (once per day)"), (0.03, 0.46, "Intraday layer (every 15 min)")]:
        ax.add_patch(FancyBboxPatch((0.005, y0), 0.99, h, boxstyle="round,pad=0.004,rounding_size=0.01", fc="#fafafa", ec="#bbbbbb", lw=0.6, ls="--"))
        ax.text(0.015, y0 + h - 0.03, lab, fontsize=7.2, fontweight="bold", va="top", color="#444444")
    _box(ax, 0.02, 0.6, 0.15, 0.22, "Historical days\n$\\Omega^{DA}$ (20 weekdays):\nloads, weather,\ninference", "#f2f2f2", fs=6.0)
    _box(ax, 0.21, 0.6, 0.17, 0.22, "Closed-loop back-test\nof the intraday controller\nfor every $C\\in\\mathcal{G}$", B, fs=6.0)
    _box(ax, 0.42, 0.6, 0.15, 0.22, "Capability per day\n$\\xi_d$ = largest $C$\nfully delivered\n(empirical $\\hat P_N$)", B, fs=6.0)
    _box(ax, 0.61, 0.6, 0.17, 0.22, "Wasserstein ball\n$\\mathcal{B}_\\varepsilon(\\hat P_N)$:\n$\\inf_Q Q(\\xi\\geq C)\\geq\\rho$\n(Proposition 3)", P, fs=6.0)
    _box(ax, 0.82, 0.6, 0.155, 0.22, "Commitment\n$C^*=C^{DRO}_{\\rho}(\\varepsilon)$\nsubmitted to the\nDR operator", O, fs=6.1)
    for x0, x1 in [(0.17, 0.21), (0.38, 0.42), (0.57, 0.61), (0.78, 0.82)]:
        _arr(ax, (x0, 0.71), (x1, 0.71), K)
    ax.text(0.695, 0.585, "radius $\\varepsilon$: leave-one-out\nvalidation on $\\Omega^{DA}$", fontsize=5.6, ha="center", va="top", color="#5b3c8c")
    _box(ax, 0.03, 0.12, 0.17, 0.22, "Measure state $\\mathbf{x}_t$:\nbacklogs $B_{1..3}$, SOC $E_t$,\ncold $S_t$, gas engine,\nevent confirmations", "#f2f2f2", fs=6.0)
    _box(ax, 0.25, 0.12, 0.2, 0.22, "Forecasts corrected by\nthe latest errors (JR-D)\nor scenario tree (JR-S)", B, fs=6.0)
    _box(ax, 0.5, 0.12, 0.22, 0.22, "Cross-event joint recovery\nMILP (2)-(11), 18-h horizon,\nall confirmed events:\nwhich debt to repay first", G, fs=6.0)
    _box(ax, 0.77, 0.12, 0.2, 0.22, "Apply first step; plant\nreplay (storage, TES,\ncompute throttling, EDF);\nsettlement records", "#f2f2f2", fs=6.0)
    for x0, x1 in [(0.2, 0.25), (0.45, 0.5), (0.72, 0.77)]:
        _arr(ax, (x0, 0.23), (x1, 0.23), K)
    _arr(ax, (0.87, 0.115), (0.115, 0.115), "#555555", ls="--", rad=-0.12)
    ax.text(0.49, 0.045, "$t\\leftarrow t+\\Delta t$", fontsize=6.4, ha="center", color="#555555")
    _arr(ax, (0.9, 0.6), (0.7, 0.34), "#e07b2a", lw=1.2)
    ax.text(0.845, 0.455, "commitments $C_k$,\nterminal SOC\nreferences", fontsize=5.8, ha="left", va="center", color="#b35a1a")
    _arr(ax, (0.56, 0.34), (0.3, 0.6), "#1f5fa8", ls=":", lw=1.0)
    ax.text(0.37, 0.455, "the same controller\nis back-tested", fontsize=5.8, ha="right", va="center", color="#1f5fa8")
    save(fig, "Fig2_framework")


FIGS["2f"] = fig2_framework


# ------------------------------------------------------------------ Fig. 11 recovery energy Sankey
def _sankey(ax, S, U, scol, ucol, total_h=0.86, gap=0.025, x0=0.27, x1=0.69, w=0.035):
    from matplotlib.path import Path
    from matplotlib.patches import PathPatch, Rectangle
    tot = sum(S.values()); hs = (total_h - gap * (len(S) - 1)) / tot; hu = (total_h - gap * (len(U) - 1)) / tot
    def stack(D, h):
        y = 0.07 + total_h; pos = {}
        for k, v in D.items():
            pos[k] = (y - v * h, y); y -= v * h + gap
        return pos
    ps, pu = stack(S, hs), stack(U, hu)
    cs = {k: ps[k][1] for k in S}; cu = {k: pu[k][1] for k in U}
    for i, (ks, vs) in enumerate(S.items()):
        for ku, vu in U.items():
            f = vs * vu / tot
            if f <= 1e-9: continue
            a1, a0 = cs[ks], cs[ks] - f * hs; b1, b0 = cu[ku], cu[ku] - f * hu
            cs[ks] = a0; cu[ku] = b0
            xm = (x0 + w + x1) / 2
            verts = [(x0 + w, a1), (xm, a1), (xm, b1), (x1, b1), (x1, b0), (xm, b0), (xm, a0), (x0 + w, a0), (x0 + w, a1)]
            codes = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4, Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4, Path.CLOSEPOLY]
            ax.add_patch(PathPatch(Path(verts, codes), fc=scol[ks], ec="none", alpha=0.42))
    def labels(pos, D, x, ha, col):
        ys = {k: (y0 + y1) / 2 for k, (y0, y1) in pos.items()}; keys = sorted(ys, key=lambda k: -ys[k]); last = None
        for k in keys:                                        # keep labels at least 0.075 apart (top to bottom)
            if last is not None and last - ys[k] < 0.085: ys[k] = last - 0.085
            last = ys[k]
        for k in keys:
            ax.add_patch(Rectangle((x if ha == "left" else x - w, pos[k][0]), w, pos[k][1] - pos[k][0], fc=col[k], ec="none"))
            ax.text(x + (w + 0.01 if ha == "left" else -w - 0.01), ys[k], f"{k}\n{D[k]:.1f} MWh", ha=ha, va="center", fontsize=5.9, linespacing=1.0)
    labels(ps, S, x0 + w, "right", scol); labels(pu, U, x1, "left", ucol)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")


def fig11(case="short_r21", gap=(18.0, 18.5), after=(19.5, 21.5)):
    import os
    case = os.environ.get("FIG11_CASE", case)
    ref = rd(f"ts15_{case}_NoDR.csv")
    if ref is None: return
    scol = {"Connection margin": "#9a9a9a", "Gas engine": "#e07b2a", "Absorption chiller": "#f2b880", "PV": "#e8c84a",
            "Cold storage": "#2aa7c9", "BESS discharge": "#1f5fa8", "Compute deferred": "#c4508a"}
    ucol = {"Catch-up in the interval": "#c0392b", "Recharge in the interval": "#1f5fa8", "Catch-up after the events": "#e8a093",
            "Recharge after the events": "#8fb3d9", "TES recharge": "#2aa7c9"}
    fig, axs = plt.subplots(1, 2, figsize=(DOUBLE_COL, 3.3)); fig.subplots_adjust(wspace=0.12)
    for j, (f, n) in enumerate([("IROs", "IR-O*"), ("JRD", "JR-D")]):
        q = rd(f"ts15_{case}_{f}.csv")
        S1, U1 = recovery_flows(q, ref, [gap]); S2, U2 = recovery_flows(q, ref, [after])
        S = {}
        for D in (S1, S2):
            for k, v in D.items(): S[k] = S.get(k, 0) + v
        U = {"Catch-up in the interval": U1.get("Compute catch-up", 0), "Recharge in the interval": U1.get("BESS recharge", 0),
             "Catch-up after the events": U2.get("Compute catch-up", 0), "Recharge after the events": U2.get("BESS recharge", 0),
             "TES recharge": U1.get("TES recharge", 0) + U2.get("TES recharge", 0)}
        # balance the small remainder (reduced on-site supply, import reduction) into the uses it belongs to
        rest = sum(S.values()) - sum(U.values())
        if abs(rest) > 1e-6: U["TES recharge"] += rest
        U = {k: v for k, v in U.items() if v > 1e-6}
        S["Cold storage"] = S.pop("TES (no-DR discharge)", 0) + S.pop("TES discharge", 0)
        order = ["Gas engine", "Absorption chiller", "Connection margin", "Cold storage", "PV", "BESS discharge", "Compute deferred"]
        S = {k: S[k] for k in order if k in S and S[k] > 0.05}
        ax = axs[j]; _sankey(ax, S, U, scol, ucol)
        g = U.get("Catch-up in the interval", 0) + U.get("Recharge in the interval", 0)
        share = 100 * U.get("Recharge in the interval", 0) / max(g, 1e-9)
        ax.set_title(f"{n}: BESS recharge takes {share:.0f} % of the interval channel", fontsize=7.8)
        panel(ax, "ab"[j], x=0.0, y=0.98)
    save(fig, "Fig11_recovery_sankey")


FIGS["11"] = fig11


# ------------------------------------------------------------------ Fig. 3 typical-day power balance and recovery channel
PDYN_GPU, A_AUX = 0.00105 * 0.75, 0.05            # MW per busy GPU (dynamic), UPS/distribution share


def fig3_typical(case="short_r21"):
    import os
    case = os.environ.get("FIG3_CASE", case)
    S = [("IROs", "IR-O*"), ("JRD", "JR-D")]
    D = {n: rd(f"ts15_{case}_{f}.csv") for f, n in S}
    if any(v is None for v in D.values()): return
    ev = EVENTS["short"] if case.startswith("short") else EVENTS["long"]
    fig, axs = plt.subplots(2, 2, figsize=(DOUBLE_COL, 5.0), sharex=True, sharey="row", gridspec_kw=dict(height_ratios=[1.7, 1], hspace=0.08, wspace=0.06))
    for j, (f, n) in enumerate(S):
        q = D[n]; h = q.hour.values; m = (h >= 15) & (h < 24); x = h[m] + 0.125; wd = 0.23
        defer = (1 + A_AUX) * PDYN_GPU * (q.y1 + q.y2 + q.y3).values
        itn = (1 + A_AUX) * q.pit.values - defer
        chill = (q.qec / q.cop).values
        aux = (q.pg + q.ppv + q.pgt + q.pdis - q.pch).values - (1 + A_AUX) * q.pit.values - chill
        sup = [("Grid import", q.pg.values, "#8c8c8c"), ("PV", q.ppv.values, "#e8c84a"), ("Gas engine", q.pgt.values, "#e07b2a"),
               ("BESS discharge", q.pdis.values, "#1f5fa8")]
        dem = [("Non-deferrable IT", itn, "#c9c9c9"), ("Deferrable compute", defer, "#c4508a"), ("Electric chiller", chill, "#2aa7c9"),
               ("BESS charge", q.pch.values, "#8fb3d9"), ("Auxiliaries", aux, "#e6e6e6")]
        ax = axs[0, j]; shade(ax, ev); b = np.zeros(m.sum())
        for lab, v, c in sup:
            ax.bar(x, v[m], wd, bottom=b, color=c, lw=0, label=lab if j == 0 else None); b += v[m]
        b = np.zeros(m.sum())
        for lab, v, c in dem:
            ax.bar(x, -v[m], wd, bottom=-b, color=c, lw=0, label=lab if j == 0 else None); b += v[m]
        ax.step(h[m], q.base.values[m], where="post", color="black", ls="--", lw=0.9, label="DR baseline" if j == 0 else None)
        ax.axhline(q.Pcap.iloc[0], color="#b22222", lw=0.8, label="Connection limit" if j == 0 else None)
        ax.axhline(0, color="black", lw=0.5)
        ax.set_title(f"{n}", fontsize=9); panel(ax, "ab"[j], x=-0.1 if j == 0 else -0.04)
        if j == 0: ax.set_ylabel("Supply (+) / demand (−) (MW)")
        # recovery channel: width P^cap - baseline and its use by compute catch-up and storage recharge
        ax = axs[1, j]; shade(ax, ev)
        arr = (q.a1 + q.a2 + q.a3).values; yy = (q.y1 + q.y2 + q.y3).values
        catch = np.maximum(yy - arr, 0) * PDYN_GPU * (1 + A_AUX + 1.0 / q.cop.values)
        rech = q.pch.values + (q.qtc / q.cop).values
        out = np.ones(len(h), bool)
        for s0, e0 in ev: out &= ~((h >= s0) & (h < e0))
        ax.bar(x, (catch * out)[m], wd, color="#c0392b", lw=0, label="Compute catch-up" if j == 0 else None)
        ax.bar(x, (rech * out)[m], wd, bottom=(catch * out)[m], color="#1f5fa8", lw=0, label="Storage recharge" if j == 0 else None)
        ax.step(h[m], (q.Pcap.iloc[0] - q.base.values)[m], where="post", color="black", lw=0.9, label="Channel width $P^{cap}-P^{base}$" if j == 0 else None)
        g = (h >= ev[0][1]) & (h < ev[1][0]); cg, rg = catch[g].sum() * 0.25, rech[g].sum() * 0.25
        ax.text(0.98, 0.93, f"interval: catch-up {cg:.1f} MWh, recharge {rg:.1f} MWh", transform=ax.transAxes, ha="right", va="top", fontsize=6.6,
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#999999", lw=0.4))
        ax.set_xlabel("Hour of day"); ax.set_xlim(15, 24)
        if j == 0: ax.set_ylabel("Recovery power (MW)")
        panel(ax, "cd"[j], x=-0.1 if j == 0 else -0.04)
    h1, l1 = axs[0, 0].get_legend_handles_labels(); h2, l2 = axs[1, 0].get_legend_handles_labels()
    fig.legend(h1 + h2, l1 + l2, loc="lower center", bbox_to_anchor=(0.5, -0.02), ncol=7, fontsize=6.4, handlelength=1.4, columnspacing=0.8)
    fig.subplots_adjust(bottom=0.14)
    save(fig, "Fig3_power_balance")


# ------------------------------------------------------------------ Fig. 4 class backlogs and storage states (short vs long interval)
def fig4_states(suf="_r21"):
    import os
    suf = os.environ.get("FIG4_CASE", suf)
    cases = [("short" + suf, "Short interval (30 min)", EVENTS["short"]), ("long" + suf, "Long interval (3 h)", EVENTS["long"])]
    S = [("IROs", "IR-O*"), ("JRM", "JR-M"), ("JRD", "JR-D")]
    D = {c: {n: rd(f"ts15_{c}_{f}.csv") for f, n in S} for c, _, _ in cases}
    if any(v is None for c in D for v in D[c].values()): return
    fig, axs = plt.subplots(2, 2, figsize=(DOUBLE_COL, 4.6), sharex=True, sharey="row", gridspec_kw=dict(hspace=0.16, wspace=0.06))
    for j, (c, title, ev) in enumerate(cases):
        J = D[c]["JR-D"]; h = J.hour.values
        ax = axs[0, j]; shade(ax, ev)
        ax.stackplot(h, J.B1 / 1e3, J.B2 / 1e3, J.B3 / 1e3, colors=["#c6dbef", "#6baed6", "#08519c"],
                     labels=["C1 (L = 0.5 h), JR-D", "C2 (L = 1.5 h), JR-D", "C3 (L = 3 h), JR-D"], lw=0, alpha=0.95)
        for n in ["IR-O*", "JR-M"]:
            q = D[c][n]; ax.plot(h, (q.B1 + q.B2 + q.B3) / 1e3, color=COL[n], ls=LS[n], lw=1.3, label=f"Total backlog, {n}")
        ax.set_title(title, fontsize=9); panel(ax, "ab"[j], x=-0.1 if j == 0 else -0.04)
        if j == 0: ax.set_ylabel("Backlog (10$^3$ GPU·h)"); ax.legend(loc="upper right", fontsize=6.3)
        ax = axs[1, j]; shade(ax, ev)
        for n in ["IR-O*", "JR-M", "JR-D"]:
            q = D[c][n]; ax.plot(h, q.E, color=COL[n], ls=LS[n], lw=1.4, label=f"BESS, {n}")
        ax.plot(h, J.S, color="#2aa7c9", lw=1.1, ls=(0, (5, 2)), label="Cold storage, JR-D")
        ax.plot(h, D[c]["IR-O*"].S, color="#7fd0e3", lw=1.0, ls=(0, (1, 1.5)), label="Cold storage, IR-O*")
        ax.set_xlabel("Hour of day"); ax.set_xlim(15, 26)
        if j == 0: ax.set_ylabel("Stored energy (MWh, MWh$_{th}$)"); ax.legend(loc="upper right", fontsize=6.3, ncol=1)
        panel(ax, "cd"[j], x=-0.1 if j == 0 else -0.04)
    save(fig, "Fig4_backlog_storage")


FIGS["3t"] = fig3_typical
FIGS["4s"] = fig4_states


# ------------------------------------------------------------------ Fig. 7 value of coordination and of cross-event foresight vs interval
def fig7_decomp():
    from paper_style import exp20
    t = exp20("tau"); b = exp20("bess")
    if t is None and b is None: return
    rows = []
    for d, cfgmap in [(t, {"tau15": 0.25, "tau60": 1.0, "tau120": 2.0, "tau180": 3.0}), (b, {"bess6": 0.5})]:
        if d is None: continue
        for cfg, tau in cfgmap.items():
            for n in ["IR-O*", "JR-M", "JR-D"]:
                q = d[(d.cfg == cfg) & (d.strategy == n)]
                if not q.empty: rows.append((tau, n, float(q.C_rho.iloc[0])))
    if not rows: return
    T = pd.DataFrame(rows, columns=["tau", "name", "C"]).pivot(index="tau", columns="name", values="C").sort_index()
    lo = 1.0                                              # lower end of the search bracket
    Tv = T.fillna(lo - 0.25)                              # below the bracket: plotted just under it
    fig, axs = plt.subplots(1, 2, figsize=(DOUBLE_COL, 2.9), gridspec_kw=dict(width_ratios=[1.25, 1], wspace=0.3))
    ax = axs[0]
    if {"IR-O*", "JR-M"} <= set(T.columns): ax.fill_between(T.index, Tv["IR-O*"], Tv["JR-M"], color="#c4508a", alpha=0.12, lw=0, label="Coordination value")
    if {"JR-M", "JR-D"} <= set(T.columns): ax.fill_between(T.index, Tv["JR-M"], Tv["JR-D"], color="#1f5fa8", alpha=0.15, lw=0, label="Cross-event foresight value")
    for n in ["IR-O*", "JR-M", "JR-D"]:
        if n in T: ax.plot(T.index, Tv[n], color=COL[n], ls=LS[n], marker=MK[n], ms=4, mfc="white", lw=1.4, label=n)
    ax.axhline(7.98, color="#555555", lw=0.7, ls=(0, (4, 3))); ax.text(T.index.max(), 8.05, "single-event capability of event 2", ha="right", fontsize=6.4, color="#555555")
    ax.axhline(lo, color="#aaaaaa", lw=0.5, ls=":"); ax.text(T.index.min(), lo - 0.5, "below search range", fontsize=6.2, color="#888888")
    ax.set_xscale("log", base=2); ax.set_xticks(T.index); ax.set_xticklabels([f"{x:g}" for x in T.index])
    ax.set_xlabel("Event interval τ (h)"); ax.set_ylabel("Firm capacity $C^{firm}_{0.95}$ (MW)"); ax.set_ylim(0, 9)
    ax.legend(loc="lower right", fontsize=6.4, ncol=2); panel(ax, "a", x=-0.12)
    ax = axs[1]; x = np.arange(len(T.index)); wb = 0.6
    coord = (Tv["JR-M"] - Tv["IR-O*"]).values if "IR-O*" in T else np.zeros(len(x))
    fore = (Tv["JR-D"] - Tv["JR-M"]).values
    ax.bar(x, coord, wb, color="#c4508a", alpha=0.75, label="Coordination (JR-M − IR-O*)")
    ax.bar(x, fore, wb, bottom=np.maximum(coord, 0), color="#1f5fa8", alpha=0.85, label="Foresight (JR-D − JR-M)")
    for i in range(len(x)): ax.text(x[i], max(coord[i], 0) + fore[i] + 0.12, f"+{fore[i]:.2f}", ha="center", fontsize=6.6, color="#1f5fa8")
    ax.axhline(0, color="black", lw=0.6); ax.set_xticks(x); ax.set_xticklabels([f"{v:g}" for v in T.index])
    ax.set_xlabel("Event interval τ (h)"); ax.set_ylabel("Capacity gain (MW)"); ax.legend(loc="upper right", fontsize=6.4); panel(ax, "b", x=-0.14)
    save(fig, "Fig7_value_decomposition")


FIGS["7d"] = fig7_decomp


# ------------------------------------------------------------------ Fig. 9 substitution curves: battery energy and connection capacity
BESS_COST = 0.6          # million CNY per MWh (0.6 CNY/Wh system cost, Table A1)
P_TYP = 14.573           # typical-day peak import (MW); P^cap = gamma * P_TYP


def _inv(xs, ys, target):
    """Smallest x of a piecewise-linear, non-decreasing curve (xs, ys) with y >= target (NaN if never reached)."""
    xs, ys = np.asarray(xs, float), np.asarray(ys, float)
    for i in range(len(xs)):
        if ys[i] >= target - 1e-9:
            if i == 0: return xs[0]
            return xs[i - 1] + (target - ys[i - 1]) * (xs[i] - xs[i - 1]) / max(ys[i] - ys[i - 1], 1e-9)
    return np.nan


def substitution_table():
    from paper_style import exp20
    b = exp20("bess"); g = exp20("gamma")
    if b is None: return None
    E = {}
    for n in ["JR-D", "IR-O*", "JR-M"]:
        q = b[b.strategy == n].copy()
        if q.empty: continue
        q["E"] = q.cfg.str.replace("bess", "").astype(float) * 2; E[n] = q.sort_values("E")[["E", "C_rho"]].values
    G = {}
    if g is not None:
        for n in ["JR-D", "IR-O*"]:
            q = g[g.strategy == n].copy(); q["gamma"] = q.cfg.str.replace("g", "").astype(float)
            base = b[(b.cfg == "bess6") & (b.strategy == n)]
            if not base.empty: q = pd.concat([q, pd.DataFrame({"gamma": [1.10], "C_rho": [float(base.C_rho.iloc[0])]})])
            G[n] = q.sort_values("gamma")[["gamma", "C_rho"]].values
    return E, G


def fig9_substitution(lo=1.0):
    T = substitution_table()
    if T is None: return
    E, G = T
    fig, axs = plt.subplots(1, 3, figsize=(DOUBLE_COL, 2.9), gridspec_kw=dict(width_ratios=[1, 1, 0.8], wspace=0.38))
    res = {}
    for k, (D, xl, base, conv, unit) in enumerate([(E, "BESS energy (MWh, 2-h rating)", 12.0, lambda x: x, "MWh"),
                                                   (G, "Connection limit $P^{cap}$ (MW)", 1.10, lambda x: x * P_TYP, "MW")]):
        ax = axs[k]
        if not D: ax.axis("off"); continue
        for n, v in D.items():
            x = conv(v[:, 0]); y = np.where(np.isnan(v[:, 1]), lo - 0.25, v[:, 1])
            ax.plot(x, y, color=COL[n], ls=LS.get(n, "-"), marker=MK[n], ms=4, mfc="white", lw=1.4, label=n)
        if "JR-D" in D and "IR-O*" in D:
            vj, vi = D["JR-D"], D["IR-O*"]
            cj = np.interp(base, vj[:, 0], np.nan_to_num(vj[:, 1], nan=lo - 0.25))
            ci = np.interp(base, vi[:, 0], np.nan_to_num(vi[:, 1], nan=lo - 0.25))
            xi = _inv(vi[:, 0], np.nan_to_num(vi[:, 1], nan=0), cj)       # benchmark needs this much to reach JR-D
            xj = _inv(vj[:, 0], np.nan_to_num(vj[:, 1], nan=0), ci)       # JR-D needs only this much to reach the benchmark
            res[unit] = (conv(base), cj, ci, conv(xi) if not np.isnan(xi) else np.nan, conv(xj) if not np.isnan(xj) else np.nan)
            ax.axvline(conv(base), color="#888888", lw=0.6, ls=":")
            ax.annotate("", xy=(conv(base), cj), xytext=(conv(base), max(ci, lo - 0.25)), arrowprops=dict(arrowstyle="<|-|>", color=COL["JR-D"], lw=0.9, mutation_scale=7))
            if not np.isnan(xj):
                ax.annotate("", xy=(conv(xj), ci), xytext=(conv(base), ci), arrowprops=dict(arrowstyle="-|>", color="#555555", lw=0.8, mutation_scale=7, ls="--"))
        ax.axhline(lo, color="#bbbbbb", lw=0.5, ls=":")
        ax.set_xlabel(xl); ax.set_ylabel("Firm capacity $C^{firm}_{0.95}$ (MW)" if k == 0 else ""); ax.set_ylim(0, None)
        ax.legend(loc="upper left", fontsize=6.4); panel(ax, "ab"[k], x=-0.16)
        ax.set_title("S2, BESS swept (connection fixed)" if k == 0 else "S2, connection margin swept", fontsize=7.8)
    # (c) mirrored bars: equivalent battery energy (up) and connection capacity (down) of joint recovery
    ax = axs[2]
    up = res.get("MWh"); dn = res.get("MW")
    items = []
    if up: items.append(("Battery saved by\nJR-D at equal $C^{firm}$", up[0] - up[4] if not np.isnan(up[4]) else np.nan, "MWh", COL["JR-D"]))
    if dn: items.append(("Connection saved by\nJR-D at equal $C^{firm}$", -(dn[0] - dn[4]) if not np.isnan(dn[4]) else np.nan, "MW", "#e07b2a"))
    for i, (lab, v, u, c) in enumerate(items):
        if np.isnan(v): continue
        ax.bar(0, v, 0.55, color=c, alpha=0.85)
        txt = f"{abs(v):.1f} {u}" + (f"\n≈ {abs(v) * BESS_COST:.1f} M CNY" if u == "MWh" else "")
        ax.text(0.33, v / 2, f"{lab}\n{txt}", ha="left", va="center", fontsize=6.3)
    ax.axhline(0, color="black", lw=0.6); ax.set_xlim(-0.5, 2.2); ax.set_xticks([])
    ax.set_ylabel("Battery energy (MWh, +) / connection (MW, −)"); panel(ax, "c", x=-0.3)
    save(fig, "Fig9_substitution")
    return res


# ------------------------------------------------------------------ Fig. 10 distributionally robust commitment: calibration
def fig10_calibration(rho=0.95):
    from paper_style import capability, worst_case_prob, dro_capacity, cv_radius
    h = rd("exp18_history_S1.csv"); hs = rd("exp18_strategies_S1.csv")
    if h is None:
        parts = [rd("exp18_history_S1_a.csv"), rd("exp18_history_S1_b.csv")]
        if any(p is None for p in parts): return
        h = pd.concat(parts, ignore_index=True); hs = rd("exp18_strategies_S1_a.csv")
    h["name"] = h.strategy.map(dict(zip(hs["index"], hs["label"])))
    t = load_capacity("_S1")
    grid = np.sort(h.C.unique())
    fig, axs = plt.subplots(1, 3, figsize=(DOUBLE_COL, 2.9), gridspec_kw=dict(wspace=0.36))
    ax = axs[0]
    for k, n in enumerate(ORDER):
        lb, step = capability(h, n); xh = lb.values + step / 2
        tl, st2 = capability(t[t.C.isin(grid)], n); xt = tl.values + st2 / 2
        ax.scatter(xh, k + 0.12 + 0.18 * (np.random.default_rng(1).random(len(xh)) - 0.5), s=9, color=COL[n], alpha=0.8, label="historical days" if k == 0 else None)
        ax.scatter(xt, k - 0.22 + 0.18 * (np.random.default_rng(2).random(len(xt)) - 0.5), s=9, facecolor="white", edgecolor=COL[n], lw=0.7, label="test days" if k == 0 else None)
    ax.set_yticks(range(len(ORDER))); ax.set_yticklabels(ORDER); ax.set_xlabel("Capability $\\xi$ (MW)"); ax.legend(loc="lower left", fontsize=6.2)
    panel(ax, "a", x=-0.28)
    ax = axs[1]; eps = np.round(np.arange(0, 0.201, 0.005), 3)
    sel = {}
    for n in ORDER:
        lb, step = capability(h, n); x = lb.values + step / 2
        Cd = [dro_capacity(x, rho, e, grid) for e in eps]
        ax.plot(eps, np.nan_to_num(Cd, nan=grid.min() - 0.5), color=COL[n], ls=LS[n], lw=1.3, label=n)
        e_cv = cv_radius(x, lb.values, rho, grid); c_cv = dro_capacity(x, rho, e_cv, grid); sel[n] = (e_cv, c_cv, dro_capacity(x, rho, 0, grid))
        ax.plot(e_cv, np.nan_to_num(c_cv, nan=grid.min() - 0.5), marker="*", ms=8, color=COL[n], mec="black", mew=0.4)
    ax.set_xlabel("Wasserstein radius ε (MW)"); ax.set_ylabel(f"$C^{{DRO}}_{{{rho}}}(\\varepsilon)$ (MW)"); ax.legend(loc="upper right", fontsize=6.2)
    panel(ax, "b", x=-0.2)
    ax = axs[2]
    for n in ORDER:
        lb, step = capability(h, n); x = lb.values + step / 2
        real = t[t.name == n].groupby("C").all_full.mean()
        e_cv = sel[n][0]
        for C in grid:
            if C not in real.index: continue
            ax.scatter(worst_case_prob(x, C, 0), real[C], s=12, marker="o", facecolor="white", edgecolor=COL[n], lw=0.7)
            ax.scatter(worst_case_prob(x, C, e_cv), real[C], s=12, marker=MK[n], color=COL[n])
    ax.plot([0, 1], [0, 1], color="#555555", lw=0.6, ls="--"); ax.set_xlim(-0.03, 1.03); ax.set_ylim(-0.03, 1.03)
    ax.set_xlabel("Predicted full-delivery probability"); ax.set_ylabel("Realised share on test days")
    ax.text(0.03, 0.95, "hollow: sample average (ε = 0)\nfilled: distributionally robust", transform=ax.transAxes, fontsize=6.0, va="top")
    panel(ax, "c", x=-0.2)
    save(fig, "Fig10_dro_calibration")
    return sel


# ------------------------------------------------------------------ Fig. 12 contribution of the IES devices and of the resources
def fig12_ies(case="short_r21", lo=1.0):
    from paper_style import exp20
    b = exp20("bess"); ies = exp20("ies"); rs = exp20("resources")
    fig, axs = plt.subplots(1, 2, figsize=(DOUBLE_COL, 2.9), gridspec_kw=dict(width_ratios=[1.05, 1], wspace=0.3))
    ax = axs[0]; bars = []
    if b is not None:
        q = b[(b.cfg == "bess6") & (b.strategy == "JR-D")]
        if not q.empty: bars.append(("Full AIDC-IES", float(q.C_rho.iloc[0]), COL["JR-D"]))
    lab = {"noGT": "w/o gas engine", "noTES": "w/o cold storage", "noAC": "w/o absorption chiller", "noIES": "w/o all three",
           "compute_BESS": "compute + BESS only", "compute_only": "compute only", "BESS_only": "BESS only"}
    for d in (ies, rs):
        if d is None: continue
        for _, r in d.iterrows(): bars.append((lab.get(r.cfg, r.cfg), r.C_rho, "#e07b2a" if r.cfg in ("noGT", "noAC", "noIES") else ("#2aa7c9" if r.cfg == "noTES" else "#8c8c8c")))
    if bars:
        y = np.arange(len(bars))[::-1]; base = bars[0][1]
        for yy, (l, v, c) in zip(y, bars):
            vv = lo - 0.25 if np.isnan(v) else v
            ax.barh(yy, vv, 0.6, color=c, alpha=0.85)
            ax.text(vv + 0.1, yy, ("< %g MW" % lo) if np.isnan(v) else (f"{v:.2f} MW" + ("" if l == "Full AIDC-IES" else f"  ({v - base:+.2f})")), va="center", fontsize=6.5)
        ax.set_yticks(y); ax.set_yticklabels([l for l, _, _ in bars], fontsize=6.8); ax.set_xlim(0, base + 3)
    ax.set_xlabel("Firm capacity of JR-D, $C^{firm}_{0.95}$ (MW), S2"); panel(ax, "a", x=-0.42)
    # (b) composition of the evening recovery channel in the no-DR operation of the typical day
    ax = axs[1]; R = rd(f"ts15_{case}_NoDR.csv")
    if R is not None:
        h = R.hour.values; m = (h >= 18) & (h < 22.5); cop = R.cop.values         # recovery windows (connection margin >= 0)
        comp = [("Gas engine", R.pgt.values, "#e07b2a"), ("Absorption chiller", R.qac.values / cop, "#f2b880"), ("PV", R.ppv.values, "#e8c84a"),
                ("Cold storage", (R.qtd.values - R.qtc.values) / cop, "#2aa7c9"),
                ("Connection margin", R.Pcap.values - R.pg.values - R.pgt.values - R.ppv.values - (R.qac.values + R.qtd.values - R.qtc.values) / cop - (R.pdis.values - R.pch.values), "#9a9a9a")]
        ax.stackplot(h[m], *[np.maximum(v[m], 0) for _, v, _ in comp], colors=[c for _, _, c in comp], labels=[l for l, _, _ in comp], lw=0, alpha=0.9)
        ax.plot(h[m], (R.Pcap - R.pg).values[m], color="black", lw=0.9, label="Channel $P^{cap}-P^{grid}_{noDR}$")
        shade(ax, EVENTS["short"]); ax.set_xlim(18, 22.5); ax.set_xlabel("Hour of day"); ax.set_ylabel("Recovery channel (MW)")
        ax.legend(loc="upper left", fontsize=6.0, ncol=2)
    panel(ax, "b", x=-0.14)
    save(fig, "Fig12_ies_contribution")


FIGS["9s"] = fig9_substitution
FIGS["10c"] = fig10_calibration
FIGS["12i"] = fig12_ies


# ------------------------------------------------------------------ Fig. 8 sensitivity: interval x connection margin, lag bounds
def _exp14(st, parts):
    d = rd(f"exp14_{st}.csv")
    if d is not None:
        s = rd(f"exp14_{st}_strategies.csv"); c = rd(f"exp14_{st}_cfg.csv")
        d["name"] = d.strategy.map(dict(zip(s["index"], s["label"]))); d["cfgname"] = d.cfg.map(dict(zip(c["cfg"], c["label"]))); return d
    out = []
    for p in parts:
        d = rd(f"exp14_{st}{p}.csv")
        if d is None: continue
        s = rd(f"exp14_{st}{p}_strategies.csv"); c = rd(f"exp14_{st}{p}_cfg.csv")
        d["name"] = d.strategy.map(dict(zip(s["index"], s["label"]))); d["cfgname"] = d.cfg.map(dict(zip(c["cfg"], c["label"]))); out.append(d)
    return pd.concat(out, ignore_index=True) if out else None


def fig8_sensitivity():
    d = _exp14("tau_gamma", ["_g100", "_g105", "_g110", "_g120"])
    if d is None: return
    d["gap"] = d.cfgname.map(lambda x: float(x.split("_")[0][3:])); d["gamma"] = d.cfgname.map(lambda x: float(x.split("_")[1][1:]))
    g = d.groupby(["gap", "gamma", "name"]).all_full.mean().unstack("name") * 100
    Z = [(g["JR-D"], "Full delivery, JR-D (%)", "Blues", 0, 100), (g["JR-D"] - g[["IR-O*", "IR-P"]].max(axis=1), "JR-D − best independent (pp)", "Oranges", 0, 100),
         (g["JR-D"] - g["JR-M"], "JR-D − JR-M (pp)", "Purples", 0, 100)]
    fig = plt.figure(figsize=(DOUBLE_COL, 2.75)); gs = fig.add_gridspec(1, 4, width_ratios=[1, 1, 1, 1.05], wspace=0.42)
    for k, (v, title, cm, vmin, vmax) in enumerate(Z):
        ax = fig.add_subplot(gs[0, k]); M = v.unstack("gap"); ax.grid(False)
        ax.imshow(M.values, origin="lower", aspect="auto", cmap=cm, vmin=vmin, vmax=vmax)
        for i in range(M.shape[0]):
            for jj in range(M.shape[1]):
                val = M.values[i, jj]
                if np.isnan(val): continue
                ax.text(jj, i, f"{val:.0f}", ha="center", va="center", fontsize=6.6, color="white" if val > 0.6 * vmax else "black")
        ax.set_xticks(range(M.shape[1])); ax.set_xticklabels([f"{x:g}" for x in M.columns]); ax.set_yticks(range(M.shape[0]))
        ax.set_yticklabels([f"{x:.2f}" for x in M.index]); ax.set_xlabel("Event interval τ (h)")
        if k == 0: ax.set_ylabel("Connection margin γ")
        ax.set_title(title, fontsize=7.4); panel(ax, "abc"[k], x=-0.3 if k == 0 else -0.2)
    sd = _exp14("single", ["_a"])
    ax = fig.add_subplot(gs[0, 3])
    if sd is not None:
        q = sd[sd.cfgname.str.startswith("lag")].copy(); q["x"] = q.cfgname.map(lambda x: float(x[3:]))
        gb = q.groupby(["x", "name"]).all_full.mean().unstack("name") * 100
        s1 = load_capacity("_S1")
        if s1 is not None: gb.loc[1.0] = s1[np.isclose(s1.C, 7.0)].groupby("name").all_full.mean() * 100
        gb = gb.sort_index()
        for n in ORDER:
            if n in gb: ax.plot(gb.index, gb[n], color=COL[n], ls=LS[n], marker=MK[n], ms=3.5, mfc="white", lw=1.3, label=n)
        ax.set_xlabel("Scale of lag bounds $L_c$"); ax.set_ylabel("Full delivery (%), S1, 7 MW"); ax.set_ylim(-3, 104)
        ax.legend(loc="lower right", fontsize=6.2)
    panel(ax, "d", x=-0.28)
    save(fig, "Fig8_sensitivity")


FIGS["8s"] = fig8_sensitivity


if __name__ == "__main__":
    which = sys.argv[1:] or list(FIGS)
    for w in which:
        if w in FIGS: FIGS[w]()
