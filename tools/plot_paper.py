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
from paper_style import (rd, save, shade, panel, load_capacity, capacity_table, share_band, c_rho, COL, MK, LS,
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
            # reliable capacities at 95 %
            tab, _ = capacity_table(d, col, rhos=(0.95,), B=200)
            cj = tab["JR-D"][0][0.95]; ci = np.nanmax([tab[n][0][0.95] for n in ("IR-O*", "IR-P")])
            if not np.isnan(cj):
                ax.annotate("", xy=(cj, 95), xytext=(cj, 4), arrowprops=dict(arrowstyle="-", color=COL["JR-D"], lw=0.8, ls=":"))
            if not np.isnan(cj):
                base = ci if not np.isnan(ci) else C.min() - 0.5
                txt = f"$\\Delta C_{{0.95}}$ = {cj - base:+.1f} MW" if not np.isnan(ci) else f"$\\Delta C_{{0.95}}$ > {cj - C.min() + 0.5:.1f} MW"
                ax.text(cj + 0.12, 50, txt, ha="left", va="center", fontsize=7.2, color=COL["JR-D"],
                        bbox=dict(boxstyle="round,pad=0.2", fc="white", ec=COL["JR-D"], lw=0.5))
    axs[0, 0].legend(loc="lower left", ncol=2, handlelength=2.2, columnspacing=0.8)
    save(fig, "Fig3_reliable_capacity")


# ------------------------------------------------------------------ Fig. 5 strategy comparison
COST = [("cost_energy", "Electricity", "#8fb3d9"), ("cost_gas", "Natural gas", "#e8c48a"), ("cost_deg", "Storage degradation", "#b9b9b9"),
        ("cost_delay", "Task delay", "#c9a3c9"), ("pen_dev", "Shortfall penalty", "#e39a8f")]


def fig5():
    tabs = []
    for t, s in CAP_TAGS[:2]:
        d = load_capacity(t)
        if d is not None: tabs.append((d, s))
    if not tabs: return
    Cfix = [6.5, 7.5]
    fig, axs = plt.subplots(1, len(tabs), figsize=(DOUBLE_COL, 3.1), squeeze=False); fig.subplots_adjust(wspace=0.38)
    for j, (d, s) in enumerate(tabs):
        ax = axs[0, j]; ax2 = ax.twinx(); ax2.grid(False)
        x0 = 0; ticks = []; tl = []
        for C in Cfix:
            for n in ORDER:
                q = d[(d.name == n) & (np.isclose(d.C, C))]
                if q.empty: continue
                bottom = 0
                for k, (c, lab, colr) in enumerate(COST):
                    v = q[c].mean() / 1e4
                    ax.bar(x0, v, 0.72, bottom=bottom, color=colr, edgecolor="white", lw=0.4, label=lab if (x0 == 0) else None)
                    bottom += v
                pay = q.dr_pay.mean() / 1e4
                ax.bar(x0, -pay, 0.72, color="#7fbf7f", edgecolor="white", lw=0.4, label="DR revenue (−)" if x0 == 0 else None)
                ax.plot(x0, q.net_cost_adj.mean() / 1e4, marker="_", ms=13, mew=2, color="black", label="Net cost" if x0 == 0 else None)
                ax2.plot(x0, 100 * q.all_full.mean(), marker=MK[n], color=COL[n], ms=5, mec="black", mew=0.5, ls="none")
                ticks.append(x0); tl.append(n); x0 += 1
            x0 += 0.8
        ax.set_xticks(ticks); ax.set_xticklabels(tl, rotation=0, fontsize=6.8)
        for k, C in enumerate(Cfix):
            ax.text(k * 4.8 + 1.5, 1.02, f"C = {C:g} MW", transform=ax.get_xaxis_transform(), ha="center", fontsize=7.5)
        ax.axhline(0, color="black", lw=0.6)
        tops = [sum(d[(d.name == n) & np.isclose(d.C, C)][c].mean() for c, _, _ in COST) / 1e4 for C in Cfix for n in ORDER]
        cap = 1.25 * np.median(tops)
        for x, t in zip(ticks, tops):
            if t > cap: ax.text(x, cap * 0.97, f"{t:.0f}↑", ha="center", va="top", fontsize=6.5, color="#5b2a6b")
        ax.set_ylim(top=cap)
        ax.set_ylabel("Mean daily cost (10$^4$ CNY)"); ax2.set_ylabel("Days with full delivery (%)"); ax2.set_ylim(0, 105)
        ax.set_title(SCEN[s], fontsize=8.5, pad=14); panel(ax, "ab"[j], y=1.08)
    h, l = axs[0, 0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=7, bbox_to_anchor=(0.5, -0.06), fontsize=7)
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
    ax.set_xticks(ticks); ax.set_xticklabels(tl, fontsize=6.5); ax.set_ylabel(f"Daily cost difference JR-D − benchmark (10$^3$ CNY), C = {C0:g} MW")
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
def fig2():
    cases = [("short", "Short interval (30 min)"), ("long", "Long interval (3 h)")]
    S = [("IROs", "IR-O*"), ("JRM", "JR-M"), ("JRD", "JR-D")]
    D = {c: {n: rd(f"ts15_{c}_{f}.csv") for f, n in S} for c, _ in cases}
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
    save(fig, "Fig2_recovery_mechanism")


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
    _box(ax, 0.00, 0.83, 0.40, 0.13, "Day-ahead recovery-aware\ncommitment $C_k$ (chance-constrained)", "#eef3fa", fs=5.8)
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

if __name__ == "__main__":
    which = sys.argv[1:] or list(FIGS)
    for w in which:
        if w in FIGS: FIGS[w]()
