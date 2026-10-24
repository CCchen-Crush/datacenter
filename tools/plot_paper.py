#!/usr/bin/env python3
"""Figures of the Applied Energy manuscript (English, vector PDF/SVG + PNG preview) from matlab/results.

Usage: python3 tools/plot_paper.py [fig ...]      e.g.  python3 tools/plot_paper.py 5 9 S7
Fig. 1 system and recovery channel | 2 framework | 3 typical-day power balance | 4 backlogs and storage |
5 recovery-energy Sankey | 6 reliability curves | 7 two-event region | 8 coordination vs foresight | 9 sensitivity |
10 substitution curves | 11 distributionally robust commitment | 12 IES contribution | 13 capacity-service Pareto |
14 economics | 15 benefit versus the commitment | 16 event-call uncertainty and post-event rebound |
S1 perfect-information regions | S2 commitment methods | S3 Proposition 1 | S4 Proposition 2 | S5 channel price | GA graphical abstract (13 x 5 cm)
"""
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from paper_style import (rd, save, shade, panel, bottom_legend, load_capacity, capacity_table, share_band, c_rho, recovery_flows, COL, MK, LS,
                         ORDER, SCEN, EVENTS, SINGLE_COL, DOUBLE_COL)

CAP_TAGS = [("_S1", "S1"), ("_S2", "S2"), ("_S3", "S3")]


# ------------------------------------------------------------------ Fig. 6 reliability curves
def fig6_capacity():
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
    fig.subplots_adjust(top=0.95, bottom=0.17)
    fig.legend(hh, ll, loc="lower center", bbox_to_anchor=(0.5, 0.0), ncol=4, handlelength=2.6, columnspacing=1.6)
    save(fig, "Fig6_reliable_capacity")


# ------------------------------------------------------------------ cost components (Fig. 14)
# cost groups (columns summed) in stacking order; adjacent colours pass the colour-vision checks of the stacked charts
DCOST = [(("cost_energy", "cost_gas", "term_adj"), "Energy and end state", "#2a78d6"), (("cost_delay",), "Task delay", "#e87ba4"),
         (("cost_deg",), "Storage degradation", "#eda100"), (("pen_dev",), "Shortfall assessment", "#e34948"), (("dr_pay",), "DR revenue", "#008300")]


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


def figS2(rho=0.95):
    """Day-ahead commitment methods in the plane of out-of-sample full delivery and benefit (Table 6): physical
    capability (perfect-recourse MILP, single-event capability; Exp16) and the closed-loop back-test on the historical
    days (sample average, Wasserstein-robust, cost-optimal below the robust capacity; Exp18 with Exp12). Points are
    numbered; the key lists the strategy, the commitment and the methods that select it."""
    from paper_style import capability, dro_capacity, eps_sampling
    from matplotlib.lines import Line2D
    nd = rd("exp17_nodr.csv")
    if nd is None: return
    nd = nd.set_index("realisation")
    mk = {"sample average": "o", "robust": "s", "cost-optimal": "*"}
    fig, axs = plt.subplots(1, 2, figsize=(DOUBLE_COL, 3.0), sharey=True); fig.subplots_adjust(wspace=0.08, top=0.84)
    for j, (scen, tag) in enumerate([("S1", "_S1"), ("S2", "_S2")]):
        ax = axs[j]; t = load_capacity(tag); h = _history(scen)
        if t is None or h is None: continue
        grid = np.sort(h.C.unique()); groups = {}
        for n in ["JR-M", "JR-D"]:
            lb, step = capability(h, n); x = lb.values + step / 2
            c_saa = dro_capacity(x, rho, 0, grid); c_dro = dro_capacity(x, rho, eps_sampling(x), grid)
            N = h.day.nunique(); hn = h[h.name == n]; cnt = hn.groupby("C").day.nunique()
            J = hn.groupby("C").net_cost_adj.mean()[cnt == N]; cand = J[J.index <= (c_dro + 1e-9 if not np.isnan(c_dro) else -1)]
            c_opt = cand.idxmin() if len(cand) else np.nan
            for lab, c in [("sample average", c_saa), ("robust", c_dro), ("cost-optimal", c_opt)]:
                if np.isnan(c): continue
                if (n, c) not in groups:
                    q = t[(t.name == n) & np.isclose(t.C, c)].set_index("realisation")
                    groups[(n, c)] = [100 * q.all_full.mean(), (nd.net_cost_adj.reindex(q.index) - q.net_cost_adj).mean() / 1e3, []]
                groups[(n, c)][2].append(lab)
        items = []                                         # marker, size, face, edge, x, y, key text
        for (n, c), (f, bft, labs) in groups.items():
            lab = "cost-optimal" if "cost-optimal" in labs else ("robust" if "robust" in labs else "sample average")
            items.append((mk[lab], 80 if lab == "cost-optimal" else 36, COL[n], "black" if lab == "cost-optimal" else COL[n], f, bft,
                          f"{n}, {c:g} MW: {', '.join(labs)}"))
        e16 = rd(f"exp16_endogenous_{scen}.csv"); pk = rd(f"exp16_packages_{scen}.csv")
        if e16 is not None and pk is not None:
            e16["pkg"] = e16.package.map(dict(zip(pk["index"], pk["label"])))
            for labp, n, txt in [("RA|JR-D", "JR-D", "JR-D, 8.18/7.98 MW: perfect-recourse MILP"), ("SE|IR-O*", "IR-O*", "IR-O*, 8.18/7.98 MW: single-event capability"),
                                 ("SE|IR-P", "IR-P", "IR-P, 8.18/7.98 MW: single-event capability")]:
                q = e16[e16.pkg == labp]
                if not q.empty:
                    items.append(("D", 30, "white", COL[n], 100 * q.all_full.mean(), (q.nodr_net_cost_adj - q.net_cost_adj).mean() / 1e3, txt))
        seen = {}
        for k, (m, sz, fc, ec, f, bft, txt) in enumerate(items, 1):
            ax.scatter(f, bft, marker=m, s=sz, facecolor=fc, edgecolor=ec, lw=0.9 if m == "D" else 0.5, zorder=3)
            key = (round(f / 3), round(bft)); off = seen.get(key, 0); seen[key] = off + 1
            ax.annotate(str(k), (f, bft), xytext=(-9 - 8 * off, 4), textcoords="offset points", fontsize=6.4, ha="center", color=ec if m == "D" else fc)
        key = "\n".join(f"{k}  {it[6]}" for k, it in enumerate(items, 1)) + "\nIR-O*, IR-P: no commitment ≥ 1 MW from the back-test"
        ax.text(0.03, 0.4, key, transform=ax.transAxes, fontsize=5.6, va="center", color="#333333",
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#cccccc", alpha=0.9))
        ax.set_xlim(-5, 108); ax.set_ylim(-4, 52); ax.set_xlabel("Days with full delivery, out of sample (%)"); ax.set_title(SCEN[scen], fontsize=7.8)
        if j == 0: ax.set_ylabel("Daily benefit vs no DR (10$^3$ CNY)")
        panel(ax, "ab"[j], x=-0.12 if j == 0 else -0.04)
    hd = [Line2D([], [], marker=m, ls="", color="#555555", ms=6 if l != "cost-optimal" else 9, mec="black" if l == "cost-optimal" else "#555555", label=l)
          for l, m in mk.items()] + [Line2D([], [], marker="D", ls="", mfc="white", mec="#555555", ms=5, label="physical capability")]
    fig.legend(handles=hd, loc="upper center", bbox_to_anchor=(0.5, 1.0), ncol=4, fontsize=6.4)
    save(fig, "FigS2_commitment_methods")


def fig7_region(lo=1.0):
    """Two-event firm region in S2 (30-min interval): largest C2 delivered in full on >= 95 % of the test days for a fixed
    first-event commitment C1 (Exp20 'region', bisection), uniform firm capacities on the diagonal (Exp20 bess6) and the
    physical capability boundary with perfect information on the DR day (Exp13, tau = 0.5 h)."""
    from paper_style import exp20
    r = exp20("region"); b = exp20("bess"); p = rd("exp13_region.csv")
    if r is None: return
    r["C1"] = r.cfg.str.replace("C1_", "").astype(float)
    fig, ax = plt.subplots(figsize=(SINGLE_COL, 3.05))
    if p is not None:
        q = p[np.isclose(p.tau_h, 0.5) & np.isclose(p.DA_h, 1) & np.isclose(p.DB_h, 1)].sort_values("C1")
        if not q.empty:                                   # reduction -> commitment delivered in full (tolerance 2 %)
            ax.plot(q.C1, q.C2_JR / 0.98, color="black", lw=1.1, ls=(0, (5, 2)),
                    label="Physical capability, perfect information\n(same for joint, event-by-event and\nindependent recovery)")
    top = {}
    for n in ["JR-D", "JR-M"]:
        q = r[r.strategy == n][["C1", "C_rho"]].copy()
        if b is not None:
            u = b[(b.cfg == "bess6") & (b.strategy == n)]
            if not u.empty and not np.isnan(u.C_rho.iloc[0]): q = pd.concat([q, pd.DataFrame({"C1": [u.C_rho.iloc[0]], "C_rho": [u.C_rho.iloc[0]]})])
        q = q.sort_values("C1"); ok = ~q.C_rho.isna()
        ax.plot(q.C1[ok], q.C_rho[ok], color=COL[n], ls=LS[n], marker=MK[n], ms=4.2, mfc="white", mew=1.0, lw=1.5, label=f"{n}: firm region boundary")
        if n == "JR-D": ax.fill_between(q.C1[ok], 0, q.C_rho[ok], color=COL[n], alpha=0.09, lw=0)
        for c1 in q.C1[~ok]:
            ax.plot(c1, lo - 0.45, marker="x", ms=5, color=COL[n], mew=1.2)
        top[n] = q
    ax.plot([0, 9], [0, 9], color="#999999", lw=0.6, ls=":"); ax.text(8.55, 8.9, "$C_1=C_2$", fontsize=6.2, color="#777777", ha="right")
    ax.axhline(lo, color="#cccccc", lw=0.5, ls=":")
    if any(q.C_rho.isna().any() for q in top.values()):
        ax.text(0.25, lo - 0.45, r"×  no firm $C_2\geq$ 1 MW", fontsize=6.0, va="center", color="#666666")
    ax.text(0.25, 0.3, "IR-O*, IR-P: no firm pair, not even (1, 1) MW", fontsize=6.0, color="#333333")
    ax.set_xlim(0, 9); ax.set_ylim(0, 9.4)
    ax.set_xlabel("Commitment of event 1, $C_1$ (MW)"); ax.set_ylabel("Firm commitment of event 2, $C_2$ (MW)")
    ax.legend(loc="lower right", fontsize=6.0, bbox_to_anchor=(1.0, 0.1)); ax.set_title("S2, 30-min interval, reliability 95 %", fontsize=8)
    save(fig, "Fig7_two_event_region")
    return top


# ------------------------------------------------------------------ Fig. 1 system and recovery channel
def _box(ax, x, y, w, h, text, fc, ec="#333333", fs=7, bold=False, pad=0.012):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad={pad},rounding_size=0.015", fc=fc, ec=ec, lw=0.7))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, fontweight="bold" if bold else "normal")


def _arr(ax, p, q, color, ls="-", lw=1.1, style="-|>", rad=0.0):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=7, color=color, lw=lw, ls=ls,
                                 connectionstyle=f"arc3,rad={rad}", shrinkA=1, shrinkB=1))


def _frame(ax, x, y, w, h, title, color, fc, tx=0.5):
    """Subsystem frame with its name along the bottom edge (centred at the fraction tx of the width)."""
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.004,rounding_size=0.018", fc=fc, ec=color, lw=0.9))
    ax.text(x + tx * w, y + 0.012, title, ha="center", va="bottom", fontsize=6.2, fontweight="bold", color=color)


def _loop_mark(ax, x, y, k, fs=5.4):
    """Circled number k of the closed computing-energy-thermal loop, drawn on a flow path."""
    ax.text(x, y, f"{k}", fontsize=fs, ha="center", va="center", color="white", fontweight="bold", zorder=6,
            bbox=dict(boxstyle="circle,pad=0.14", fc="#333333", ec="white", lw=0.6))


def fig1():
    from fig_icons import icon
    fig = plt.figure(figsize=(DOUBLE_COL, 3.95))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.42, 1], wspace=0.13, left=0.005, right=0.99, top=0.93, bottom=0.11)
    ax = fig.add_subplot(gs[0, 0]); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    E, Hh, Cc, K, Dg, W = "#1f5fa8", "#c0392b", "#1b9fc4", "#6d6d6d", "#b8860b", "#7a5cb8"
    bx = dict(pad=0.006); lab = dict(fontsize=5.6, ha="center", va="top", linespacing=1.05)
    # dispatch layer: DR operator, day-ahead commitment, intraday controller (icon at the left of each box)
    _box(ax, 0.01, 0.885, 0.205, 0.105, "", "#fff6e0", ec=Dg, **bx)
    _box(ax, 0.275, 0.885, 0.33, 0.105, "", "#f4effb", ec=W, **bx)
    _box(ax, 0.665, 0.885, 0.325, 0.105, "", "#f4effb", ec=W, **bx)
    for x, kind in [(0.012, "monitor"), (0.278, "calendar"), (0.668, "cycle")]:
        icon(fig, ax, (x, 0.892, 0.06, 0.09), kind)
    ax.text(0.143, 0.938, "DR operator\n(Jiangsu rules)", fontsize=5.9, ha="center", va="center")
    ax.text(0.452, 0.938, "Day-ahead recovery-aware\ncommitment $C_k$ (closed-loop\ncapability, Wasserstein-robust)", fontsize=5.6, ha="center", va="center")
    ax.text(0.838, 0.938, "Intraday cross-event joint\nrecovery MPC (15-min step,\n18-h horizon)", fontsize=5.6, ha="center", va="center")
    _arr(ax, (0.268, 0.925), (0.222, 0.925), Dg, style="<|-|>"); ax.text(0.245, 0.945, "$C_k$", ha="center", va="bottom", fontsize=5.7, color="#8a6508")
    _arr(ax, (0.612, 0.925), (0.658, 0.925), W); ax.text(0.635, 0.945, "$C_k$", ha="center", va="bottom", fontsize=5.7, color=W)
    # AC bus
    yb = 0.845; ax.plot([0.015, 0.985], [yb, yb], color=E, lw=2.4, solid_capstyle="round", zorder=3)
    ax.text(0.30, yb + 0.008, "AC bus", ha="left", va="bottom", fontsize=5.6, color=E, fontweight="bold")
    # subsystems (frame name along the bottom edge) with flat icons
    _frame(ax, 0.010, 0.535, 0.335, 0.270, "Energy supply", "#8c6d1f", "#fffaf0")
    _frame(ax, 0.360, 0.535, 0.325, 0.270, "Conversion and storage", "#b4561c", "#fff5ef", tx=0.66)
    _frame(ax, 0.730, 0.355, 0.260, 0.450, "Computing (16 000 GPUs)", W, "#f8f4fc")
    _frame(ax, 0.360, 0.015, 0.630, 0.285, "Cooling supply", "#167f9e", "#f0f9fc")
    for x, kind, text in [(0.030, "grid", "Utility grid\n$P^{grid}_t\\leq P^{cap}$"), (0.190, "pv", "PV\n8 MWp"),
                          (0.380, "gas", "Gas engine\n3 MW (CCHP)"), (0.535, "bess", "BESS\n6 MW / 12 MWh")]:
        icon(fig, ax, (x, 0.645, 0.13, 0.125), kind); ax.text(x + 0.065, 0.638, text, **lab)
    icon(fig, ax, (0.742, 0.675, 0.07, 0.115), "rack", fc="#ececec", ec="#6d6d6d", led="#9a9a9a")
    ax.text(0.818, 0.732, "Inference +\nFlex 0 (fixed)", fontsize=5.6, ha="left", va="center", linespacing=1.05)
    for k, (cl, L, fc) in enumerate([("C1", "0.5", "#f4effb"), ("C2", "1.5", "#e6dcf5"), ("C3", "3", "#d6c6ee")]):
        x = 0.742 + 0.083 * k
        icon(fig, ax, (x, 0.545, 0.07, 0.115), "rack", fc=fc, ec=W)
        ax.text(x + 0.035, 0.548, f"{cl}\n{L} h", **lab)
    ax.text(0.86, 0.445, "backlog $B_{c,t}$:\ndeadline-bound debt", ha="center", va="center", fontsize=5.5, color=W, style="italic")
    for x, kind, text in [(0.385, "absorption", "Absorption\nchiller"), (0.590, "chiller", "Electric chillers\nCOP($T_t$)"),
                          (0.815, "tes", "Chilled-water\nTES 10 MWh$_{th}$")]:
        icon(fig, ax, (x, 0.13, 0.15, 0.135), kind); ax.text(x + 0.075, 0.123, text, **lab)
    # electricity: sources inject into the bus, the computing load and the electric chillers draw from it
    for x0 in (0.095, 0.255, 0.445):
        _arr(ax, (x0, 0.772), (x0, yb - 0.004), E, lw=1.0)
    _arr(ax, (0.600, 0.772), (0.600, yb - 0.004), E, lw=1.0, style="<|-|>")
    _arr(ax, (0.777, yb - 0.004), (0.777, 0.803), E, lw=1.0); ax.text(0.797, 0.812, "$P^{IT}_t$", fontsize=5.6, color=E, va="center")
    ax.plot([0.712, 0.712], [yb, 0.30], color=E, lw=1.0); _arr(ax, (0.712, 0.302), (0.712, 0.268), E, lw=1.0)
    ax.text(0.705, 0.445, "$Q^{EC}_t/\\mathrm{COP}_t$", fontsize=5.4, color=E, rotation=90, va="center", ha="right")
    # heat and cooling
    _arr(ax, (0.445, 0.578), (0.445, 0.268), Hh, lw=1.1); ax.text(0.452, 0.445, "recovered heat\n$k^hP^{GT}_t$", fontsize=5.4, color=Hh, va="center")
    _arr(ax, (0.965, 0.355), (0.965, 0.302), Hh, lw=1.1); ax.text(0.945, 0.328, "IT heat $\\theta P^{IT}_t$", fontsize=5.3, color=Hh, ha="right", va="center")
    ax.plot([0.46, 0.89], [0.282, 0.282], color=Cc, lw=1.0, ls=(0, (3, 1.6)))
    for x0 in (0.46, 0.665, 0.89):
        ax.plot([x0, x0], [0.268, 0.282], color=Cc, lw=1.0, ls=(0, (3, 1.6)))
    _arr(ax, (0.80, 0.282), (0.80, 0.355), Cc, ls=(0, (3, 1.6)), lw=1.0); ax.text(0.79, 0.328, "cooling", fontsize=5.3, color=Cc, ha="right", va="center")
    # control and settlement
    _arr(ax, (0.93, 0.879), (0.93, 0.783), K, ls=":", lw=0.9); _arr(ax, (0.69, 0.879), (0.632, 0.772), K, ls=":", lw=0.9)
    _arr(ax, (0.05, 0.879), (0.05, 0.772), Dg, lw=0.9, style="<|-|>")
    ax.text(0.062, 0.866, "metered $P^{grid}_t$", fontsize=5.1, color="#8a6508", va="center")
    # closed loop: circled numbers on the flow paths, with a compact key
    for x, y, k in [(0.777, 0.823, 1), (0.965, 0.330, 2), (0.712, 0.585, 3), (0.05, 0.80, 4)]:
        _loop_mark(ax, x, y, k)
    ax.text(0.015, 0.495, "Closed computing–energy–thermal loop", fontsize=5.9, fontweight="bold", color="#333333", va="top")
    steps = ["deferrable work sets the IT power $P^{IT}_t$", "IT heat $\\theta P^{IT}_t$ sets the cooling load",
             "chiller power and recovered heat\nreturn to the electric balance", "grid import within $P^{cap}$ is settled\nagainst the baseline $P^{base}_t$"]
    yy = 0.445
    for k, t in enumerate(steps, 1):
        _loop_mark(ax, 0.03, yy - 0.012, k)
        ax.text(0.055, yy + 0.004, t, fontsize=5.5, va="top", color="#333333", linespacing=1.05)
        yy -= 0.058 if "\n" not in t else 0.085
    for k, (c, lab_, ls_) in enumerate([(E, "electricity", "-"), (Hh, "heat", "-"), (Cc, "cooling", (0, (3, 1.6))), (K, "control", ":"), (Dg, "settlement", "-")]):
        y0 = 0.13 - 0.025 * k
        ax.plot([0.03, 0.08], [y0, y0], color=c, lw=1.2, ls=ls_); ax.text(0.09, y0, lab_, fontsize=5.5, va="center")
    panel(ax, "a", x=0.0, y=1.012)
    # (b) two consecutive events and the recovery channel between them
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
    ax.fill_between(tg, bg, mid, color="#c0392b", alpha=0.55, lw=0, label="Compute catch-up (backlog)")
    ax.fill_between(tg, mid, top, color="#1f5fa8", alpha=0.35, lw=0, label="Storage recharge (SOC deficit)")
    ax.annotate("one recovery channel,\ntwo heterogeneous debts", xy=(18.4, 13.3), xytext=(19.95, 13.0), fontsize=6.2, ha="left", va="center",
                arrowprops=dict(arrowstyle="-|>", lw=0.7, color="#333333"))
    yb2 = base[np.argmin(np.abs(t - 17.5))] - 6.0
    ax.text(17.5, yb2 + 0.45, "$R_1 \\geq C_1$", ha="center", fontsize=6.4); ax.text(19.25, yb2 + 0.45, "$R_2 \\geq C_2$ ?", ha="center", fontsize=6.4)
    ax.annotate("", xy=(18.0, 2.4), xytext=(18.75, 2.4), arrowprops=dict(arrowstyle="<|-|>", lw=0.7)); ax.text(18.37, 2.75, "τ", ha="center", fontsize=6.6)
    ax.set_xlim(16, 22); ax.set_ylim(1.5, 19.6); ax.set_yticks(range(2, 17, 2)); ax.set_xlabel("Hour of day"); ax.set_ylabel("Power (MW)")
    ax.set_title("Consecutive DR events and the recovery channel", fontsize=7.6)
    ax.legend(loc="upper center", fontsize=5.6, ncol=2, handlelength=1.6, columnspacing=0.9)
    panel(ax, "b", x=-0.15, y=1.0)
    save(fig, "Fig1_system_recovery_channel")


# ------------------------------------------------------------------ supplementary figures
def figS3():
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
    axs[1].legend(loc="lower right", fontsize=5.6)
    a = axs[2]; a.tick_params(length=0)
    d = data[0][0]; taus = sorted(d.tau_h.unique()); gams = sorted(d.gamma.unique())
    Z = np.array([[float((d[(d.gamma == g) & (d.tau_h == t)].G_JR - d[(d.gamma == g) & (d.tau_h == t)].G_IR).iloc[0] / d[(d.gamma == g) & (d.tau_h == t)].G0.iloc[0]) for t in taus] for g in gams])
    a = axs[2]; a.grid(False); im = a.imshow(100 * Z, origin="lower", aspect="auto", cmap="Blues", vmin=0)
    for i in range(len(gams)):
        for k in range(len(taus)): a.text(k, i, f"{100 * Z[i, k]:.0f}", ha="center", va="center", fontsize=6, color="white" if Z[i, k] > 0.35 else "black")
    a.set_xticks(range(len(taus))); a.set_xticklabels([f"{x:g}" for x in taus]); a.set_yticks(range(len(gams))); a.set_yticklabels([f"{x:.2f}" for x in gams])
    a.set_xlabel("Event interval τ (h)"); a.set_ylabel("Connection margin γ"); a.set_title("Capability gain of joint recovery (% of $Γ_B^0$)", fontsize=7.8)
    panel(a, "c", x=-0.22)
    save(fig, "FigS3_mechanism_bound")


def figS4():
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
    fig.subplots_adjust(top=0.8)
    fig.text(0.99, 0.985, f"max |closed form − LP| = {err:.0e} MW over {len(d)} cases (rounding of the stored results)", ha="right", va="top", fontsize=6.5)
    save(fig, "FigS4_proposition2_check")


def figS1():
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
    save(fig, "FigS1_perfect_information_regions")


def figS5():
    d = rd("exp5_shadow.csv")
    if d is None: return
    fig, axs = plt.subplots(2, 1, figsize=(SINGLE_COL * 1.4, 3.6), sharex=True); fig.subplots_adjust(hspace=0.15)
    a = axs[0]; shade(a, EVENTS["S1"]); a.step(d.hour, d.price, where="post", color="black", lw=0.8, ls="--", label="TOU price")
    a.plot(d.hour, d.lambda_el, color=COL["JR-D"], lw=1.3, label="Recovery-channel price $\\lambda^{el}_t$ (electric balance dual)")
    a.set_ylabel("CNY/MWh"); a.legend(fontsize=6.3, loc="upper left"); a.set_ylim(0, max(2500, float(np.nanpercentile(d.lambda_el, 97)) * 1.1)); panel(a, "a", x=-0.12)
    a = axs[1]; shade(a, EVENTS["S1"])
    for k, c in zip([1, 2, 3], ["#9ecae1", "#4292c6", "#08519c"]): a.plot(d.hour, d[f"cost_B{k}"], color=c, lw=1.3, label=f"Backlog value C{k}")
    a.set_ylabel("CNY per GPU·h"); a.set_xlabel("Hour of day"); a.legend(fontsize=6.3); panel(a, "b", x=-0.12)
    for a in axs: a.set_xlim(12, 30)
    save(fig, "FigS5_shadow_prices")


FIGS = {"S1": figS1, "S2": figS2, "S3": figS3, "S4": figS4, "S5": figS5}



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
    fig.legend(*axs[0, 0].get_legend_handles_labels(), loc="lower center", bbox_to_anchor=(0.5, 0.0), ncol=5, fontsize=7)
    fig.subplots_adjust(top=0.95, bottom=0.14)
    save(fig, "Fig13_capacity_service_pareto")




# ------------------------------------------------------------------ Fig. 2 framework: day-ahead DRO commitment + intraday joint recovery
def eq_labels():
    """Equation numbers of the manuscript (paper/labels.json, written by tools/resolve_manuscript.py)."""
    import json, os
    return json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "paper", "labels.json")))["equations"]


def _mini(fig, rect):
    """Inset axes of a mini schematic at the figure rectangle rect, without ticks."""
    a = fig.add_axes(rect); a.set_xticks([]); a.set_yticks([]); a.grid(False); a.set_facecolor("white")
    for sp in a.spines.values(): sp.set_color("#a0a0a0"); sp.set_linewidth(0.5)
    return a


def _tiny(a, xlabel=None, ylabel=None):
    if xlabel: a.set_xlabel(xlabel, fontsize=5.0, labelpad=1.0)
    if ylabel: a.set_ylabel(ylabel, fontsize=5.0, labelpad=1.0)


def fig2_framework():
    L = eq_labels(); q = lambda *k: "(" + "–".join(L[x] for x in k) + ")"
    fig = plt.figure(figsize=(DOUBLE_COL, 4.4)); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    PU, BL, OR, GR, K, GY = "#6a4fa3", "#1f5fa8", "#d98200", "#2e8b57", "#333333", "#7a7a7a"

    def layer(y0, h, title, color, fc):
        ax.add_patch(FancyBboxPatch((0.005, y0), 0.99, h, boxstyle="round,pad=0.002,rounding_size=0.01", fc=fc, ec=color, lw=0.9))
        ax.add_patch(FancyBboxPatch((0.005, y0), 0.036, h, boxstyle="round,pad=0.002,rounding_size=0.01", fc=color, ec=color, lw=0.9))
        ax.text(0.023, y0 + h / 2, title, rotation=90, ha="center", va="center", fontsize=6.6, fontweight="bold", color="white", linespacing=1.15)

    def step(x, y, w, h, title, text, ec, fc, tag):
        """Step box: bold title, mini schematic (returned inset) and text with equation numbers; badge = lines of Algorithm 1."""
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.004,rounding_size=0.012", fc=fc, ec=ec, lw=0.9))
        ax.text(x + w / 2, y + h - 0.022, title, ha="center", va="center", fontsize=6.4, fontweight="bold", color="#222222")
        ax.text(x + w / 2, y + 0.012, text, ha="center", va="bottom", fontsize=5.7, color="#222222", linespacing=1.12)
        ax.text(x + w - 0.004, y + h + 0.003, tag, fontsize=5.0, ha="right", va="center", color="white", fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.18,rounding_size=0.25", fc=ec, ec="none"))
        return _mini(fig, [x + 0.014, y + 0.092, w - 0.028, h - 0.145])

    layer(0.525, 0.465, "Day-ahead layer\n(once per day, Section 4.1)", PU, "#faf8fd")
    layer(0.010, 0.465, "Intraday layer\n(every 15 min, Section 4.2)", BL, "#f7fafd")
    # ---------------- day-ahead layer: five steps
    w, gap, y, h = 0.164, 0.029, 0.552, 0.405
    X = [0.052 + k * (w + gap) for k in range(5)]
    a = step(X[0], y, w, h, "Historical days $\\Omega^{DA}$", "14 weekdays: computing,\ninference, weather", GY, "#f4f4f4", "input")
    t = np.linspace(0, 24, 97)
    for k in range(5):
        a.plot(t, 10 + 2.2 * np.sin((t - 9) / 24 * 2 * np.pi) + 0.5 * np.sin(t / 2.3 + k) + 0.7 * k, color=plt.cm.Greys(0.45 + 0.1 * k), lw=0.8)
    a.set_xlim(0, 24); _tiny(a, "hour", "load")
    a = step(X[1], y, w, h, "Closed-loop back-test", "intraday controller on every\nday, $C\\in\\mathcal{G}$ until first failure", PU, "#efeaf8", "lines 1–2")
    for i, f in enumerate([6, 8, 5, 7, 6, 8]):
        for j in range(8):
            if j < f: a.add_patch(plt.Rectangle((j - 0.38, i - 0.38), 0.76, 0.76, fc="#7fc49a", ec="none"))
            elif j == f: a.plot(j, i, marker="x", ms=4.2, mew=1.2, color="#c0392b")
            else: a.add_patch(plt.Rectangle((j - 0.2, i - 0.2), 0.4, 0.4, fc="#dddddd", ec="none"))
    a.set_xlim(-0.7, 7.7); a.set_ylim(-0.7, 5.7); _tiny(a, "commitment $C$ →", "day $d$")
    a = step(X[2], y, w, h, "Capability per day", f"capability $\\xi_d$ {q('eq:capability')};\n$\\hat P_N$, radius $\\varepsilon_N$ {q('eq:radius')}", PU, "#efeaf8", "line 3")
    xi = np.array([5.9, 6.6, 6.9, 7.2, 7.4, 7.6, 7.8, 8.0])
    a.step(np.r_[5.2, xi, 8.6], np.r_[0, np.arange(1, 9) / 8, 1], where="post", color=PU, lw=1.1)
    a.plot(xi, np.full(8, 0.06), "o", ms=2.6, color=PU, mfc="white", mew=0.8)
    a.annotate("", xy=(7.4, 0.5), xytext=(7.9, 0.5), arrowprops=dict(arrowstyle="<->", lw=0.7, color=OR))
    a.text(7.65, 0.56, "$\\varepsilon_N$", fontsize=5.6, color=OR, ha="center", va="bottom")
    a.set_xlim(5.2, 8.6); a.set_ylim(0, 1.12); _tiny(a, "capability $\\xi$", "$\\hat F_N$")
    a = step(X[3], y, w, h, "Sorted-margin certificate", f"knapsack {q('eq:knap')}, dual {q('eq:dual')}:\n$\\Phi_\\rho(C)\\geq\\varepsilon$ {q('eq:phi')} (Prop. 4)", PU, "#efeaf8", "line 4")
    d = np.array([0.18, 0.32, 0.5, 0.72, 0.95, 1.2, 1.5]); qf = 2.6
    for j, v in enumerate(d):
        a.bar(j + 1, v, 0.78, color="#e4dcf3", edgecolor=PU, lw=0.5)
        f = min(max(qf - j, 0), 1)
        if f > 0: a.bar(j + 1 - 0.39 * (1 - f), v, 0.78 * f, color=PU, edgecolor="none")
    a.text(2.0, 0.62, "$\\Phi_\\rho(C)$", fontsize=5.8, color=PU, ha="center", va="bottom")
    a.set_xlim(0.3, 7.7); a.set_ylim(0, 1.75); _tiny(a, "days sorted by margin", "$\\delta_{(j)}(C)$")
    a = step(X[4], y, w, h, "Cost-optimal commitment", f"$C^*$ {q('eq:commit')}: least back-tested\ncost below $C^{{DRO}}_\\rho(\\varepsilon)$ {q('eq:dro')}", OR, "#fdf1e3", "line 5")
    c = np.linspace(1, 9, 80); J = 0.9 * (c - 7) ** 2 / 4 - 4.5 + 0.9 * np.maximum(c - 7.6, 0) ** 2
    a.plot(c, J, color=OR, lw=1.2); a.axvspan(8.0, 9.2, color="#e6e6e6", lw=0)
    a.axvline(8.0, color=K, lw=0.7, ls="--"); a.text(8.08, 1.2, "$C^{DRO}$", fontsize=5.4, ha="left", va="center", color=K)
    a.plot(7.0, -4.5, marker="*", ms=7, color=OR, mec="white", mew=0.4); a.text(7.0, -3.6, "$C^*$", fontsize=5.8, ha="center", va="bottom", color="#9c5d00")
    a.set_xlim(1, 9.2); a.set_ylim(-5.4, 3.2); _tiny(a, "commitment $C$", "$\\bar J(C)$")
    for k in range(4):
        _arr(ax, (X[k] + w + 0.004, y + h / 2), (X[k + 1] - 0.004, y + h / 2), K)
    # ---------------- intraday layer: four steps
    ws, yb, hb = [0.185, 0.18, 0.31, 0.185], 0.08, 0.36
    gb = (0.936 - sum(ws)) / 3; XB = [0.052 + sum(ws[:k]) + k * gb for k in range(4)]
    a = step(XB[0], yb, ws[0], hb, "Measure state", "$\\hat{\\mathbf{x}}_t$: backlogs, stored energy\nand cold, gas engine, events", GY, "#f4f4f4", "line 8")
    v = [0.55, 0.35, 0.8, 0.62, 0.45]; cols = ["#d6c6ee", "#b49ddf", "#8e72c8", BL, "#1b9fc4"]
    a.bar(range(5), v, 0.62, color=cols)
    for j, lab in enumerate(["$B_1$", "$B_2$", "$B_3$", "$E$", "$S$"]):
        a.text(j, v[j] + 0.04, lab, fontsize=5.3, ha="center", va="bottom")
    a.set_xlim(-0.6, 4.6); a.set_ylim(0, 1.08)
    a = step(XB[1], yb, ws[1], hb, "Forecasts and scenarios", "error-corrected forecasts\n(JR-D) or a scenario tree (JR-S)", BL, "#e8f0fa", "line 9")
    tt = np.linspace(-4, 0, 30); tf = np.linspace(0, 8, 50); base = lambda x: 6 + 1.5 * np.sin(x / 2.2)
    a.plot(tt, base(tt) + 0.2 * np.sin(3 * tt), color=K, lw=1.0)
    a.fill_between(tf, base(tf) - 0.25 * tf ** 0.8, base(tf) + 0.25 * tf ** 0.8, color=BL, alpha=0.15, lw=0)
    a.plot(tf, base(tf), color=BL, lw=1.1, ls="--")
    for s_ in (-0.9, 0.9):
        a.plot(tf, base(tf) + s_ * 0.18 * tf ** 0.9, color="#7a5cb8", lw=0.6)
    a.axvline(0, color=GY, lw=0.6, ls=":"); a.text(0.2, 8.9, "now", fontsize=5.2, color=GY, va="top")
    a.set_xlim(-4, 8); a.set_ylim(2.5, 9.3); _tiny(a, "time", None)
    a = step(XB[2], yb, ws[2], hb, "Cross-event joint recovery MPC",
             f"MILP {q('eq:mpc')} over the 18-h horizon with all confirmed\nevents: which debt to repay first", GR, "#e7f4ec", "line 10")
    for e0, e1, lab in [(17, 18, "E1"), (18.5, 19.5, "E2")]:
        a.axvspan(e0, e1, color=BL, alpha=0.18, lw=0); a.text((e0 + e1) / 2, 0.16, lab, fontsize=5.4, ha="center", color=BL)
    a.fill_between([18, 18.5], 0.55, 0.78, color="#c0392b", alpha=0.45, lw=0); a.fill_between([18, 18.5], 0.32, 0.55, color=BL, alpha=0.45, lw=0)
    a.text(18.25, 0.84, "catch-up\n/ recharge", fontsize=4.8, ha="center", va="bottom", color="#333333", linespacing=1.0)
    for t0, ls_, yy in [(14.0, "-", 1.32), (14.25, "--", 1.12)]:
        a.annotate("", xy=(t0, yy), xytext=(t0 + 18, yy), arrowprops=dict(arrowstyle="|-|", lw=0.8, color=GR, ls=ls_, mutation_scale=2.5))
    a.text(23.0, 1.38, "horizon $[t,\\,t+T_H]$", fontsize=5.3, ha="center", va="bottom", color=GR)
    a.text(31.0, 1.0, "$t+\\Delta t$", fontsize=5.0, ha="right", va="top", color=GR)
    a.axvline(14.0, color=K, lw=0.6); a.text(14.15, 0.16, "$t$", fontsize=5.4)
    a.set_xlim(13, 33); a.set_ylim(0, 1.62); a.set_xticks([14, 18, 22, 26, 30]); a.tick_params(labelsize=4.8, length=1.5, pad=1)
    a.set_xticklabels(["14", "18", "22", "26", "30 h"])
    a = step(XB[3], yb, ws[3], hb, "Apply and settle", f"first step applied, plant replay,\nEDF execution; settlement {q('eq:rbar', 'eq:short')}", GY, "#f4f4f4", "lines 11–12")
    a.barh([0], [1.06], 0.42, color=BL, alpha=0.8); a.text(0.03, 0, "$\\bar r_k$", fontsize=5.6, color="white", va="center", fontweight="bold")
    for xv, lab in [(0.8, "$0.8C_k$"), (1.0, "$C_k$"), (1.2, "$1.2C_k$")]:
        a.axvline(xv, color=K, lw=0.6, ls="--"); a.text(xv, 0.42, lab, fontsize=5.0, ha="center", va="bottom")
    for xv, lab in [(0.8, "valid"), (1.0, "full"), (1.2, "cap")]:
        a.text(xv, -0.45, lab, fontsize=4.8, ha="center", va="center", color=GY)
    a.set_xlim(0, 1.32); a.set_ylim(-0.6, 0.75)
    for k in range(3):
        _arr(ax, (XB[k] + ws[k] + 0.004, yb + hb / 2), (XB[k + 1] - 0.004, yb + hb / 2), K)
    _arr(ax, (XB[3] + ws[3] / 2, yb - 0.006), (XB[0] + ws[0] / 2, yb - 0.006), "#555555", ls="--", rad=-0.08)
    ax.text(0.52, 0.041, "$t\\leftarrow t+\\Delta t$", fontsize=6.2, ha="center", va="bottom", color="#555555")
    # ---------------- between the layers
    _arr(ax, (X[4] + w / 2, y - 0.004), (XB[2] + 0.80 * ws[2], yb + hb + 0.006), OR, lw=1.3)
    ax.text(0.862, 0.495, "commitments $C_k$,\nterminal references", fontsize=6.0, ha="left", va="center", color="#9c5d00", linespacing=1.05)
    _arr(ax, (XB[2] + 0.25 * ws[2], yb + hb + 0.006), (X[1] + w / 2, y - 0.004), BL, ls=":", lw=1.1)
    ax.text(0.40, 0.49, "the same controller is back-tested", fontsize=6.0, ha="right", va="center", color=BL)
    save(fig, "Fig2_framework")


# ------------------------------------------------------------------ Fig. 5 recovery energy Sankey
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


def fig5_sankey(case="short_r21", gap=(18.0, 18.5), after=(19.5, 21.5)):
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
        ax.set_title(f"{n}: BESS recharge takes {share:.0f} % of the interval channel", fontsize=7.4, pad=8)
        panel(ax, "ab"[j], x=-0.02, y=1.06)
    save(fig, "Fig5_recovery_sankey")




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




# ------------------------------------------------------------------ Fig. 8 value of coordination and of cross-event foresight vs interval
def fig8_decomp():
    """Firm capacity versus the event interval (Exp20 'tau' + the 30-min base case of 'bess'): coordination value
    JR-M - IR-O* and cross-event foresight value JR-D - JR-M. A strategy below the search bracket (NaN) is drawn just under
    it and its value counts as a lower bound; a configuration that has not been run is left out."""
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
    R = pd.DataFrame(rows, columns=["tau", "name", "C"])
    T = R.pivot(index="tau", columns="name", values="C").sort_index()
    ran = R.assign(v=1).pivot(index="tau", columns="name", values="v").reindex(T.index).notna()
    lo = 1.0                                              # lower end of the search bracket
    Tv = T.where(~(T.isna() & ran), lo - 0.25)            # below the bracket: drawn just under it; not run: NaN
    full = T.index[ran.all(axis=1)] if set(["IR-O*", "JR-M", "JR-D"]) <= set(ran.columns) else T.index[:0]
    fig, axs = plt.subplots(1, 2, figsize=(DOUBLE_COL, 2.95), gridspec_kw=dict(width_ratios=[1.25, 1], wspace=0.3))
    ax = axs[0]; F = Tv.loc[full]
    if len(F):
        ax.fill_between(F.index, F["IR-O*"], F["JR-M"], color="#c4508a", alpha=0.12, lw=0, label="Coordination value")
        ax.fill_between(F.index, F["JR-M"], F["JR-D"], color="#1f5fa8", alpha=0.15, lw=0, label="Cross-event foresight value")
    for n in ["IR-O*", "JR-M", "JR-D"]:
        if n in Tv:
            v = Tv[n].dropna(); ax.plot(v.index, v.values, color=COL[n], ls=LS[n], marker=MK[n], ms=4, mfc="white", lw=1.4,
                                       label=n + (" (< 1 MW)" if T[n].isna().all() else ""))
    ax.axhline(7.98, color="#555555", lw=0.7, ls=(0, (4, 3))); ax.text(T.index.max(), 8.12, "≈ single-event capability (8 MW)", ha="right", fontsize=6.4, color="#555555")
    ax.axhline(lo, color="#aaaaaa", lw=0.5, ls=":")
    ax.set_xscale("log", base=2); ax.set_xticks(T.index); ax.set_xticklabels([f"{x:g}" for x in T.index])
    ax.set_xlabel("Event interval τ (h)"); ax.set_ylabel("Firm capacity $C^{firm}_{0.95}$ (MW)"); ax.set_ylim(0, 9)
    ax.legend(loc="center right", bbox_to_anchor=(1.0, 0.36), fontsize=6.2, ncol=1); panel(ax, "a", x=-0.12)
    ax = axs[1]; x = np.arange(len(full)); wb = 0.6
    if len(full):
        below = T.loc[full, "IR-O*"].isna().values
        coord = (T.loc[full, "JR-M"] - T.loc[full, "IR-O*"].fillna(lo)).values
        fore = (T.loc[full, "JR-D"] - T.loc[full, "JR-M"]).values
        for i in range(len(x)):
            ax.bar(x[i], coord[i], wb, color="#c4508a", alpha=0.45 if below[i] else 0.75, hatch="///" if below[i] else None, edgecolor="#c4508a",
                   lw=0.4, label="Coordination, JR-M − IR-O* (hatched: lower bound)" if i == 0 else None)
        ax.bar(x, fore, wb, bottom=np.maximum(coord, 0), color="#1f5fa8", alpha=0.85, label="Cross-event foresight, JR-D − JR-M")
        for i in range(len(x)):
            ax.text(x[i], max(coord[i], 0) + fore[i] + 0.12, f"+{fore[i]:.2f}", ha="center", fontsize=6.6, color="#1f5fa8")
            ax.text(x[i], coord[i] / 2, ("≥" if below[i] else "") + f"{coord[i]:.2f}", ha="center", va="center", fontsize=6.0, color="#6d1f4b")
        ax.set_ylim(0, max(coord + fore) + 2.4)
    ax.axhline(0, color="black", lw=0.6); ax.set_xticks(x); ax.set_xticklabels([f"{v:g}" for v in full])
    ax.set_xlabel("Event interval τ (h)"); ax.set_ylabel("Capacity gain (MW)"); ax.legend(loc="upper left", fontsize=6.0); panel(ax, "b", x=-0.14)
    save(fig, "Fig8_value_decomposition")


# ------------------------------------------------------------------ Fig. 10 substitution curves: battery energy and connection capacity
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
    b = exp20("bess"); bm = exp20("bessM"); g = exp20("gamma")
    if b is None: return None
    if bm is not None: b = pd.concat([b, bm], ignore_index=True)
    E = {}
    for n in ["JR-D", "JR-M", "IR-O*"]:
        q = b[b.strategy == n].copy()
        if q.empty: continue
        q["E"] = q.cfg.str.replace("bess", "").astype(float) * 2; E[n] = q.sort_values("E")[["E", "C_rho"]].values
    G = {}
    if g is not None:
        for n in ["JR-D", "IR-O*", "JR-M"]:
            q = g[g.strategy == n].copy(); q["gamma"] = q.cfg.str.replace("g", "").astype(float)
            base = b[(b.cfg == "bess6") & (b.strategy == n)]
            if not base.empty: q = pd.concat([q, pd.DataFrame({"gamma": [1.10], "C_rho": [float(base.C_rho.iloc[0])]})])
            if len(q): G[n] = q.sort_values("gamma")[["gamma", "C_rho"]].values
    return E, G


def _equiv(v_ref, v_new, x_base):
    """Resource the reference curve needs at x_base and the (smaller) resource at which the new curve reaches the same
    firm capacity: returns (C_ref(x_base), x_new) along the rising part of the new curve."""
    xr, yr = v_ref[:, 0], np.nan_to_num(v_ref[:, 1], nan=0.0); xn, yn = v_new[:, 0], np.nan_to_num(v_new[:, 1], nan=0.0)
    c = float(np.interp(x_base, xr, yr))
    k = int(np.argmax(yn)); return c, _inv(xn[:k + 1], yn[:k + 1], c)


def _need(v, target):
    """Smallest resource (first column of v) at which the rising part of the firm-capacity curve reaches target."""
    x, y = v[:, 0], np.nan_to_num(v[:, 1], nan=0.0); k = int(np.argmax(y))
    return _inv(x[:k + 1], y[:k + 1], target)


def fig10_substitution(lo=1.0):
    T = substitution_table()
    if T is None: return
    E, G = T; res = {}
    fig = plt.figure(figsize=(DOUBLE_COL, 3.0))
    gs = fig.add_gridspec(2, 3, width_ratios=[1.12, 1, 0.82], wspace=0.42, hspace=0.18, left=0.065, right=0.99, top=0.9, bottom=0.15)
    axs = [fig.add_subplot(gs[:, 0]), fig.add_subplot(gs[:, 1])]
    for k, (D, xl, base, conv, unit, title) in enumerate([(E, "BESS energy (MWh, 2-h rating)", 12.0, lambda x: x, "MWh", "S2, BESS swept (connection fixed)"),
                                                         (G, "Connection limit $P^{cap}$ (MW)", 1.10, lambda x: x * P_TYP, "MW", "S2, connection margin swept")]):
        ax = axs[k]; ax.set_title(title, fontsize=7.6)
        if not D: ax.text(0.5, 0.5, "pending", transform=ax.transAxes, ha="center"); panel(ax, "ab"[k], x=-0.18); continue
        for n, v in D.items():
            x = conv(v[:, 0]); y = np.where(np.isnan(v[:, 1]), lo - 0.35, v[:, 1])
            ax.plot(x, y, color=COL[n], ls=LS.get(n, "-"), marker=MK[n], ms=4, mfc="white", lw=1.4, label=n + (" (< 1 MW)" if np.all(np.isnan(v[:, 1])) else ""))
        ax.axhline(lo, color="#bbbbbb", lw=0.5, ls=":")
        ax.axvline(conv(base), color="#888888", lw=0.6, ls=":")
        if "JR-D" in D and "JR-M" in D:
            c, xn = _equiv(D["JR-M"], D["JR-D"], base)
            if not np.isnan(xn):
                bound = np.isclose(xn, D["JR-D"][:, 0].min())        # JR-D exceeds c already at the smallest resource tested
                ax.annotate("", xy=(conv(xn), c), xytext=(conv(base), c), arrowprops=dict(arrowstyle="-|>", color=COL["JR-D"], lw=1.0, mutation_scale=8))
                ax.text((conv(xn) + conv(base)) / 2, c + 0.18, ("≥ " if bound else "") + f"−{conv(base) - conv(xn):.{2 if unit == 'MW' else 1}f} {unit}", ha="center", va="bottom",
                        fontsize=6.6, color=COL["JR-D"], bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.85))
                res[unit] = (conv(base), c, conv(xn), bound)
        ax.set_xlabel(xl); ax.set_ylabel("Firm capacity $C^{firm}_{0.95}$ (MW)" if k == 0 else ""); ax.set_ylim(0, 9)
        ax.legend(loc="lower right", bbox_to_anchor=(1.0, 0.12) if k == 0 else (1.0, 0.16), fontsize=6.0); panel(ax, "ab"[k], x=-0.18)
    if "MWh" in res:
        axs[0].text(19.0, 7.9, "baseline erosion:\nlarger BESS lowers\nthe evening baseline", fontsize=5.8, ha="center", va="bottom", color="#555555")
    if G and "JR-M" in G and "JR-D" in G:
        gm, gd = G["JR-M"], G["JR-D"]; top = gm[np.argmax(gm[:, 0])]
        axs[1].text(0.03, 0.735, f"JR-M at γ = {top[0]:.2f}: {top[1]:.2f} MW\n< JR-D at γ = {gd[0, 0]:.2f}: {gd[0, 1]:.2f} MW", transform=axs[1].transAxes,
                    fontsize=5.8, va="top", color="#555555", bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.85))
    # (c, d) resource saved by cross-event foresight for every firm capacity that JR-M reaches
    targets = np.arange(4.0, 5.26, 0.25)
    ac, ad = fig.add_subplot(gs[0, 2]), fig.add_subplot(gs[1, 2])
    if "JR-M" in E and "JR-D" in E:
        sv = np.array([_need(E["JR-M"], c) - _need(E["JR-D"], c) for c in targets])
        ac.bar(targets, sv, 0.17, color=COL["JR-D"], alpha=0.85)
        for c, v in zip(targets, sv):
            ac.text(c, v + 0.4, f"{v:.1f}", ha="center", va="bottom", fontsize=5.6)
        k = int(np.argmin(np.abs(targets - 4.75)))
        ac.text(0.03, 0.95, f"{sv[k]:.1f} MWh ≈ {sv[k] * BESS_COST:.1f} M CNY\nat the base 12 MWh of JR-M", transform=ac.transAxes, fontsize=5.6, va="top", color="#333333")
        ac.set_ylim(0, 19); res["targets_MWh"] = dict(zip(np.round(targets, 2), np.round(sv, 2)))
    ac.set_ylabel("Battery saved\n(MWh)", fontsize=6.8); ac.tick_params(labelbottom=False); ac.set_xlim(3.8, 5.45)
    ac.set_title("Saved by cross-event foresight", fontsize=7.4); panel(ac, "c", x=-0.36, y=1.0)
    if "JR-M" in G and "JR-D" in G:
        for c in targets:
            gm_, gd_ = _need(G["JR-M"], c), _need(G["JR-D"], c)
            if np.isnan(gm_):
                ad.text(c, 0.15, "not\nreached", ha="center", va="bottom", fontsize=5.0, color="#777777"); continue
            v = (gm_ - gd_) * P_TYP
            ad.bar(c, max(v, 0.04), 0.17, color="#e07b2a", alpha=0.45, hatch="///", edgecolor="#e07b2a", lw=0.5)
            ad.text(c, max(v, 0.04) + 0.12, f"≥ {v:.2f}" if v > 0.005 else "0", ha="center", va="bottom", fontsize=5.6)
            res.setdefault("targets_MW", {})[round(float(c), 2)] = round(float(v), 2)
    ad.set_ylim(0, 3.9); ad.set_xlim(3.8, 5.45); ad.set_ylabel("Connection saved\n(MW)", fontsize=6.8)
    ad.set_xlabel("Target firm capacity (MW)"); panel(ad, "d", x=-0.36, y=1.0)
    save(fig, "Fig10_substitution")
    return res


# ------------------------------------------------------------------ Fig. 11 distributionally robust commitment: calibration
def _history(scen):
    h = rd(f"exp18_history_{scen}.csv"); hs = rd(f"exp18_strategies_{scen}.csv")
    if h is None or hs is None: return None
    h["name"] = h.strategy.map(dict(zip(hs["index"], hs["label"]))); return h


def fig11_calibration(rho=0.95):
    """Distributionally robust commitment: (a) capability per day on the historical and the test days, (b) robust firm
    capacity versus the Wasserstein radius, (c) predicted versus realised full-delivery probability; one row per scenario."""
    from paper_style import capability, worst_case_prob, dro_capacity, eps_sampling
    rows = [(s, tag, _history(s), load_capacity(tag)) for s, tag in [("S1", "_S1"), ("S2", "_S2")]]
    rows = [r for r in rows if r[2] is not None and r[3] is not None]
    if not rows: return
    fig, axs = plt.subplots(len(rows), 3, figsize=(DOUBLE_COL, 2.75 * len(rows) + 0.2), squeeze=False,
                            gridspec_kw=dict(wspace=0.36, hspace=0.55))
    sel = {}
    for i, (s, tag, h, t) in enumerate(rows):
        grid = np.sort(h.C.unique()); names = [n for n in ORDER if n in set(h.name)]
        ax = axs[i, 0]
        for k, n in enumerate(names):
            lb, step = capability(h, n); xh = lb.values + step / 2
            tl, st2 = capability(t[t.C.isin(grid)], n); xt = tl.values + st2 / 2
            ax.scatter(xh, k + 0.14 + 0.16 * (np.random.default_rng(1).random(len(xh)) - 0.5), s=9, color=COL[n], alpha=0.85,
                       label="historical days" if k == 0 else None)
            ax.scatter(xt, k - 0.2 + 0.16 * (np.random.default_rng(2).random(len(xt)) - 0.5), s=9, facecolor="white", edgecolor=COL[n], lw=0.7,
                       label="test days" if k == 0 else None)
        ax.set_yticks(range(len(names))); ax.set_yticklabels(names); ax.set_xlabel("Capability $\\xi$ (MW)")
        ax.set_xlim(grid.min() - 0.6, grid.max() + 0.4); ax.legend(loc="lower left", fontsize=6.0)
        ax.set_title(SCEN[s], fontsize=7.8, loc="left"); panel(ax, "adg"[i] if len(rows) > 1 else "a", x=-0.28)
        ax = axs[i, 1]; emax = 0.25; eps = np.round(np.arange(0, emax + 1e-9, 0.0025), 4); off = []
        for n in names:
            lb, step = capability(h, n); x = lb.values + step / 2
            Cd = [dro_capacity(x, rho, e, grid) for e in eps]
            e_n = eps_sampling(x); c_n = dro_capacity(x, rho, e_n, grid); sel[(s, n)] = (e_n, c_n, dro_capacity(x, rho, 0, grid))
            if np.all(np.isnan(Cd)): off.append(f"{n}: none ≥ {grid.min():g} MW ($\\varepsilon_N$ = {e_n:.2f})"); continue
            ax.plot(eps, np.where(np.isnan(Cd), np.nan, Cd), color=COL[n], ls=LS[n], lw=1.3, label=n, drawstyle="steps-post")
            if e_n <= emax and not np.isnan(c_n): ax.plot(e_n, c_n, marker="*", ms=9, color=COL[n], mec="black", mew=0.4, zorder=4)
            elif np.isnan(c_n): off.append(f"{n}: none ≥ {grid.min():g} MW at $\\varepsilon_N$ = {e_n:.2f}")
        if off: ax.text(0.97, 0.04, "\n".join(off), transform=ax.transAxes, ha="right", va="bottom", fontsize=5.8, color="#555555")
        ax.set_xlim(0, emax); ax.axhline(grid.min(), color="#cccccc", lw=0.5, ls=":")
        ax.set_xlabel("Wasserstein radius ε (MW); $\\star$ = $\\varepsilon_N$"); ax.set_ylabel(f"$C^{{DRO}}_{{{rho}}}(\\varepsilon)$ (MW)")
        ax.set_ylim(grid.min() - 0.8, grid.max() + 0.3); ax.legend(loc="upper right", fontsize=6.0)
        panel(ax, "beh"[i] if len(rows) > 1 else "b", x=-0.2)
        ax = axs[i, 2]
        for n in names:
            lb, step = capability(h, n); x = lb.values + step / 2
            real = t[t.name == n].groupby("C").all_full.mean(); e_n = sel[(s, n)][0]
            for C in grid:
                if C not in real.index: continue
                ax.scatter(worst_case_prob(x, C, 0), real[C], s=12, marker="o", facecolor="white", edgecolor=COL[n], lw=0.7)
                ax.scatter(worst_case_prob(x, C, e_n), real[C], s=12, marker=MK[n], color=COL[n])
        ax.fill_between([0, 1], [0, 1], [0, 0], color="#d9534f", alpha=0.06, lw=0)
        ax.text(0.97, 0.06, "over-confident", ha="right", fontsize=5.8, color="#b03a36", transform=ax.transAxes)
        ax.text(0.03, 0.62, "conservative", ha="left", fontsize=5.8, color="#2f6b2f", transform=ax.transAxes)
        ax.plot([0, 1], [0, 1], color="#555555", lw=0.6, ls="--"); ax.axhline(rho, color="#bbbbbb", lw=0.5, ls=":")
        ax.set_xlim(-0.03, 1.03); ax.set_ylim(-0.03, 1.03)
        ax.set_xlabel("Predicted full-delivery probability"); ax.set_ylabel("Realised share on test days")
        ax.text(0.03, 0.95, "hollow: sample average (ε = 0)\nfilled: distributionally robust ($\\varepsilon_N$)", transform=ax.transAxes, fontsize=5.8, va="top")
        panel(ax, "cfi"[i] if len(rows) > 1 else "c", x=-0.2)
    save(fig, "Fig11_dro_calibration")
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
    order = [("noGT", "w/o gas engine", "#e07b2a"), ("noAC", "w/o absorption chiller", "#f2b880"), ("noTES", "w/o cold storage", "#2aa7c9"),
             ("noIES", "w/o all three", "#b5651d"), ("compute_BESS", "compute + BESS (no cold storage)", "#8c8c8c"),
             ("compute_only", "compute flexibility only", "#8c8c8c"), ("BESS_only", "BESS only", "#8c8c8c")]
    D = pd.concat([d for d in (ies, rs) if d is not None], ignore_index=True) if (ies is not None or rs is not None) else None
    if D is not None:
        for cfg, l, c in order:
            q = D[D.cfg == cfg]
            if not q.empty: bars.append((l, float(q.C_rho.iloc[0]), c))
    if bars:
        y = np.arange(len(bars))[::-1].astype(float); base = bars[0][1] if bars[0][0] == "Full AIDC-IES" else np.nanmax([v for _, v, _ in bars])
        y[[i for i, b_ in enumerate(bars) if b_[2] == "#8c8c8c"]] -= 0.5           # gap before the resource ablation
        for yy, (l, v, c) in zip(y, bars):
            vv = lo - 0.25 if np.isnan(v) else v
            ax.barh(yy, vv, 0.6, color=c, alpha=0.9)
            ax.text(vv + 0.1, yy, ("< %g MW" % lo) if np.isnan(v) else (f"{v:.2f} MW" + ("" if l == "Full AIDC-IES" else f"  ({v - base:+.2f})")), va="center", fontsize=6.5)
        ax.set_yticks(y); ax.set_yticklabels([l for l, _, _ in bars], fontsize=6.8); ax.set_xlim(0, base + 3)
        ax.axvline(base, color=COL["JR-D"], lw=0.6, ls=":")
    ax.set_xlabel("Firm capacity of JR-D, $C^{firm}_{0.95}$ (MW), S2"); panel(ax, "a", x=-0.42)
    # (b) composition of the evening recovery channel in the no-DR operation of the typical day
    ax = axs[1]; R = rd(f"ts15_{case}_NoDR.csv")
    if R is not None:
        h = R.hour.values; m = (h >= 18) & (h < 22.5); cop = R.cop.values         # recovery windows (connection margin >= 0)
        comp = [("Gas engine", R.pgt.values, "#e07b2a"), ("Absorption chiller", R.qac.values / cop, "#f2b880"), ("PV", R.ppv.values, "#e8c84a"),
                ("Cold storage", (R.qtd.values - R.qtc.values) / cop, "#2aa7c9"),
                ("BESS (no-DR peak shaving)", R.pdis.values - R.pch.values, "#7f9fbf"),
                ("Connection margin", R.Pcap.values - R.pg.values - R.pgt.values - R.ppv.values - (R.qac.values + R.qtd.values - R.qtc.values) / cop - (R.pdis.values - R.pch.values), "#c4c4c4")]
        ax.stackplot(h[m], *[np.maximum(v[m], 0) for _, v, _ in comp], colors=[c for _, _, c in comp], labels=[l for l, _, _ in comp], lw=0, alpha=0.9)
        ax.plot(h[m], (R.Pcap - R.pg).values[m], color="black", lw=0.9, label="Channel $P^{cap}-P^{grid}_{noDR}$")
        shade(ax, EVENTS["short"]); ax.set_xlim(18, 22.5); ax.set_ylim(0, 9.4); ax.set_xlabel("Hour of day"); ax.set_ylabel("Recovery channel (MW)")
        ax.set_title("Who keeps the no-DR import below $P^{cap}$ (S2 typical day)", fontsize=7.4)
        ax.legend(loc="upper center", fontsize=5.3, ncol=3, columnspacing=0.5, handlelength=1.1, handletextpad=0.4, borderpad=0.35)
    panel(ax, "b", x=-0.14)
    save(fig, "Fig12_ies_contribution")




# ------------------------------------------------------------------ Fig. 9 sensitivity: interval x connection margin, lag bounds
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


def fig9_sensitivity():
    d = _exp14("tau_gamma", ["_g100", "_g105", "_g110", "_g120"])
    if d is None: return
    d["gap"] = d.cfgname.map(lambda x: float(x.split("_")[0][3:])); d["gamma"] = d.cfgname.map(lambda x: float(x.split("_")[1][1:]))
    g = d.groupby(["gap", "gamma", "name"]).all_full.mean().unstack("name") * 100
    Z = [(g["JR-D"], "JR-D: full delivery (%)", "Blues", 0, 100), (g["JR-D"] - g[["IR-O*", "IR-P"]].max(axis=1), "JR-D − best IR (pp)", "Oranges", 0, 100),
         (g["JR-D"] - g["JR-M"], "JR-D − JR-M (pp)", "Purples", 0, 100)]
    fig = plt.figure(figsize=(DOUBLE_COL, 2.75)); gs = fig.add_gridspec(1, 4, width_ratios=[1, 1, 1, 1.05], wspace=0.42)
    for k, (v, title, cm, vmin, vmax) in enumerate(Z):
        ax = fig.add_subplot(gs[0, k]); M = v.unstack("gap"); ax.grid(False); ax.tick_params(length=0)
        ax.imshow(M.values, origin="lower", aspect="auto", cmap=cm, vmin=vmin, vmax=vmax)
        for i in range(M.shape[0]):
            for jj in range(M.shape[1]):
                val = M.values[i, jj]
                if np.isnan(val): continue
                ax.text(jj, i, f"{val:.0f}", ha="center", va="center", fontsize=6.6, color="white" if val > 0.6 * vmax else "black")
        ax.set_xticks(range(M.shape[1])); ax.set_xticklabels([f"{x:g}" for x in M.columns]); ax.set_yticks(range(M.shape[0]))
        ax.set_yticklabels([f"{x:.2f}" for x in M.index]); ax.set_xlabel("Event interval τ (h)")
        if k == 0: ax.set_ylabel("Connection margin γ")
        ax.set_title(title, fontsize=7.4); panel(ax, "abc"[k], x=-0.32 if k == 0 else -0.26, y=1.08)
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
        ax.legend(loc="center right", bbox_to_anchor=(1.0, 0.45), fontsize=6.2)
    panel(ax, "d", x=-0.28)
    save(fig, "Fig9_sensitivity")




# ------------------------------------------------------------------ Fig. 14 economics and multi-day statistics
def _cost_decomp(ax, tabs, nd, C0):
    x0 = 0; ticks = []; tl = []; groups = []
    for d, s in tabs:
        xs = x0
        for n in ORDER:
            q = d[(d.name == n) & np.isclose(d.C, C0)].set_index("realisation")
            if q.empty: continue
            ref = nd.reindex(q.index); up = 0; dn = 0
            for cs, lab, colr in DCOST:
                v = (-q[cs[0]].mean() if cs[0] == "dr_pay" else sum((q[c] - ref[c]).mean() for c in cs)) / 1e3
                if v >= 0: ax.bar(x0, v, 0.62, bottom=up, color=colr, alpha=0.85, edgecolor="white", lw=0.6, label=lab if x0 == 0 else None); up += v
                else: ax.bar(x0, v, 0.62, bottom=dn, color=colr, alpha=0.85, edgecolor="white", lw=0.6, label=lab if x0 == 0 else None); dn += v
            net = (q.net_cost_adj - ref.net_cost_adj).mean() / 1e3
            ax.plot([x0 - 0.36, x0 + 0.36], [net, net], color="black", lw=1.8, solid_capstyle="butt", label="Net change (− benefit)" if x0 == 0 else None)
            ax.text(x0, up + 0.8, f"{100 * q.all_full.mean():.0f}%", ha="center", va="bottom", fontsize=6.2, color="#333333", fontweight="bold")
            ticks.append(x0); tl.append(n); x0 += 1
        groups.append(((xs + x0 - 1) / 2, s)); x0 += 0.7
    ax.axhline(0, color="black", lw=0.6); ax.set_xticks(ticks); ax.set_xticklabels(tl, fontsize=6.4)
    for xm, s in groups: ax.text(xm, 1.01, SCEN[s], transform=ax.get_xaxis_transform(), ha="center", va="bottom", fontsize=7.2)
    ax.set_ylabel("Daily cost change vs no DR (10$^3$ CNY)"); ax.set_ylim(top=ax.get_ylim()[1] + 3)


def fig14_economics(C0=7.0):
    nd = rd("exp17_nodr.csv")
    tabs = [(load_capacity(t), s) for t, s in CAP_TAGS[:2]]; tabs = [(d, s) for d, s in tabs if d is not None]   # S3: medians in the text
    if not tabs or nd is None: return
    nd = nd.set_index("realisation")
    fig = plt.figure(figsize=(DOUBLE_COL, 6.0)); gs = fig.add_gridspec(2, 2, height_ratios=[1.05, 1], width_ratios=[1.25, 1], hspace=0.62, wspace=0.26)
    ax = fig.add_subplot(gs[0, :]); _cost_decomp(ax, tabs, nd, C0)
    ax.set_title(f"Fixed commitment C = {C0:g} MW: cost components relative to no DR (labels: days with full delivery)", fontsize=7.8, pad=14)
    panel(ax, "a", x=-0.06, y=1.08)
    hh, ll = ax.get_legend_handles_labels(); ax.legend(hh, ll, loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=8, fontsize=6.0, handlelength=1.2, columnspacing=0.7)
    ax = fig.add_subplot(gs[1, 0]); pos = 0; ticks = []; tl = []; D = []
    for d, s in tabs:
        P = d[(d.name == "JR-D") & np.isclose(d.C, C0)].set_index("realisation")
        for n in ["IR-O*", "IR-P", "JR-M"]:
            B = d[(d.name == n) & np.isclose(d.C, C0)].set_index("realisation")
            D.append((pos, n, s, ((P.net_cost_adj - B.net_cost_adj) / 1e3).dropna().values)); pos += 1
        pos += 0.6
    allv = np.concatenate([v for *_, v in D]); lo = np.percentile(allv, 3); hi = max(np.percentile(allv, 99.5), 0); pad = 0.1 * (hi - lo)
    for pos, n, s, diff in D:
        vc = np.clip(diff, lo - pad, None)
        vp = ax.violinplot(vc, [pos], widths=0.8, showextrema=False)
        for b in vp["bodies"]: b.set_facecolor(COL[n]); b.set_alpha(0.35); b.set_edgecolor(COL[n])
        ax.boxplot(vc, positions=[pos], widths=0.18, showfliers=False, patch_artist=True, boxprops=dict(facecolor="white", lw=0.6),
                   medianprops=dict(color=COL[n], lw=1.4), whiskerprops=dict(lw=0.6), capprops=dict(lw=0.6))
        nb = int((diff < lo - pad).sum())
        if nb: ax.text(pos, lo - pad * 0.6, f"{nb}↓", ha="center", fontsize=6, color="#555555")
        ticks.append(pos); tl.append(f"{s}\n{n}")
    ax.axhline(0, color="black", lw=0.6); ax.set_ylim(lo - pad, hi + pad); ax.set_xticks(ticks); ax.set_xticklabels(tl, fontsize=6.0)
    ax.set_ylabel("JR-D − benchmark (10$^3$ CNY/day)"); ax.set_title("Paired daily differences over 26 days", fontsize=7.8)
    panel(ax, "b", x=-0.16, y=1.06)
    ax = fig.add_subplot(gs[1, 1]); d, s = tabs[min(1, len(tabs) - 1)]
    q = d[np.isclose(d.C, C0)].copy(); q["ratio"] = q[["red_E1", "red_E2", "red_E3"]].min(axis=1) / C0
    grid = np.linspace(0.3, 1.25, 300)
    for k, n in enumerate(ORDER):
        v = q[q.name == n].ratio.dropna().values
        dens = np.exp(-0.5 * ((grid[:, None] - v[None, :]) / 0.06) ** 2).sum(axis=1); dens = dens / dens.max() * 0.85
        ax.fill_between(grid, k, k + dens, color=COL[n], alpha=0.55, lw=0); ax.plot(grid, k + dens, color=COL[n], lw=0.8)
        ax.text(0.31, k + 0.12, n, fontsize=7.2, color="#333333")
    ax.axvline(0.98, color="black", lw=0.7, ls="--"); ax.axvline(0.8, color="#888888", lw=0.6, ls=":")
    ax.text(0.98, len(ORDER) + 0.05, "full", ha="center", fontsize=6.6); ax.text(0.8, len(ORDER) + 0.05, "valid", ha="center", fontsize=6.6)
    ax.set_yticks([]); ax.set_xlabel("Worst-event delivery ratio min$_k$ $\\bar r_k$/C"); ax.set_xlim(0.3, 1.25); ax.set_ylim(0, len(ORDER) + 0.4)
    ax.set_title(f"{SCEN[s]}, C = {C0:g} MW", fontsize=7.8); panel(ax, "c", x=-0.04)
    save(fig, "Fig14_economics")




# ------------------------------------------------------------------ Fig. 15 benefit of joint recovery versus the commitment
def fig15_commitment(rho=0.95, c_opt=7.0):
    """Daily benefit relative to no DR versus the uniform commitment on the 26 test days. (a, b) JR-D: contributions of the
    cost groups (DR revenue minus the cost changes, stacked above and below zero) and the net benefit, with the cost-optimal
    day-ahead commitment (Table 6) and the firm capacity; (c, d) net benefit of every controller, filled where the controller
    delivers in full on at least rho of the days at that commitment."""
    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D
    nd = rd("exp17_nodr.csv"); tabs = [(load_capacity(t), s) for t, s in CAP_TAGS[:2]]; tabs = [(d, s) for d, s in tabs if d is not None]
    if not tabs or nd is None: return
    nd = nd.set_index("realisation"); colors = {l: c for _, l, c in DCOST}
    order = ["DR revenue", "Energy and end state", "Task delay", "Storage degradation", "Shortfall assessment"]
    fig, axs = plt.subplots(2, len(tabs), figsize=(DOUBLE_COL, 5.2), sharex=True, sharey="row", squeeze=False,
                            gridspec_kw=dict(height_ratios=[1.3, 1], hspace=0.13, wspace=0.06))
    fig.subplots_adjust(left=0.075, right=0.99, top=0.94, bottom=0.165)
    res = {}
    for j, (d, s) in enumerate(tabs):
        d = d.copy(); ref = nd.reindex(d.realisation.values)
        for cs, lab, _ in DCOST:
            d[lab] = (d[cs[0]].values if cs[0] == "dr_pay" else -sum(d[c].values - ref[c].values for c in cs)) / 1e3
        d["benefit"] = (ref.net_cost_adj.values - d.net_cost_adj.values) / 1e3
        g = d.groupby(["name", "C"])[order + ["benefit", "all_full"]].mean()
        q = g.loc["JR-D"]; C = q.index.values; cf = c_rho(q.all_full, rho)
        ax = axs[0, j]; ax.axvspan(C.min() - 0.25, cf + 0.25, color=COL["JR-D"], alpha=0.06, lw=0)
        up = np.zeros(len(C)); dn = np.zeros(len(C))
        for lab in order:
            v = q[lab].values; pos, neg = np.maximum(v, 0), np.minimum(v, 0)
            if pos.max() > 1e-6: ax.fill_between(C, up, up + pos, color=colors[lab], alpha=0.75, lw=0.6, edgecolor="white"); up = up + pos
            if neg.min() < -1e-6: ax.fill_between(C, dn, dn + neg, color=colors[lab], alpha=0.75, lw=0.6, edgecolor="white"); dn = dn + neg
        ax.plot(C, q.benefit.values, color="black", lw=1.5, marker="o", ms=3.4, mfc="white", mew=0.9, zorder=4)
        ax.axhline(0, color="black", lw=0.6)
        bmax = q.benefit.max(); at = C[q.benefit.values >= bmax - 0.05]
        res[s] = dict(peak=bmax, at=at, cf=cf, rev=q["DR revenue"].values, C=C)
        ax.annotate(f"peak {bmax:.1f} k CNY/day\nat {at.min():g}" + (f"–{at.max():g}" if at.max() > at.min() else "") + " MW",
                    xy=(at.max(), bmax), xytext=(4.2, bmax + 3.2), fontsize=6.3, ha="center", va="bottom",
                    arrowprops=dict(arrowstyle="-|>", lw=0.6, color="#333333", mutation_scale=6),
                    bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#bdbdbd", lw=0.4))
        ax.text(3.0, 9.0, "DR revenue", fontsize=6.6, color="white", fontweight="bold", ha="center")
        for x0, txt, ha, ls_ in [(c_opt, f"$C^*$ = {c_opt:g} MW", "right", (0, (4, 2))), (cf, f"$C^{{firm}}_{{0.95}}$ = {cf:g} MW", "left", "-.")]:
            for a in axs[:, j]: a.axvline(x0, color="#444444", lw=0.8, ls=ls_, zorder=3)
            ax.text(x0 + (0.08 if ha == "left" else -0.08), 55.5, txt, fontsize=6.1, ha=ha, va="top", color="#333333")
        ax.set_title(SCEN[s], fontsize=7.8); ax.set_ylim(-14, 58)
        if j == 0: ax.set_ylabel("Benefit vs no DR, JR-D\n(10$^3$ CNY/day)")
        panel(ax, "ab"[j], x=-0.11 if j == 0 else -0.03, y=1.02)
        ax = axs[1, j]
        for n in ORDER:
            p_ = g.loc[n]; firm = p_.all_full.values >= rho - 1e-9
            ax.plot(p_.index, p_.benefit, color=COL[n], ls=LS[n], lw=1.2)
            ax.scatter(p_.index[firm], p_.benefit[firm], marker=MK[n], s=17, color=COL[n], zorder=3)
            ax.scatter(p_.index[~firm], p_.benefit[~firm], marker=MK[n], s=15, facecolor="white", edgecolor=COL[n], lw=0.8, zorder=3)
        ax.axhline(0, color="black", lw=0.6); ax.set_ylim(-14, 50); ax.set_xlim(C.min() - 0.25, C.max() + 0.25)
        ax.set_xlabel("Uniform commitment per event C (MW)")
        if j == 0: ax.set_ylabel("Benefit vs no DR\n(10$^3$ CNY/day)")
        panel(ax, "cd"[j], x=-0.11 if j == 0 else -0.03, y=1.02)
    hd = [Patch(color=colors[l], alpha=0.75, label=l) for l in order]
    hd += [Line2D([], [], color="black", lw=1.5, marker="o", ms=3.4, mfc="white", label="Net benefit, JR-D")]
    hd += [Line2D([], [], color=COL[n], ls=LS[n], marker=MK[n], ms=4, lw=1.2, label=n) for n in ORDER]
    hd += [Line2D([], [], color="#666666", marker="o", ms=4, ls="", label=f"filled: full delivery on ≥ {rho:.0%} of days")]
    fig.legend(handles=hd, loc="lower center", bbox_to_anchor=(0.53, 0.0), ncol=6, fontsize=6.3, handlelength=1.6, columnspacing=1.0)
    save(fig, "Fig15_commitment_benefit")
    return res


# ------------------------------------------------------------------ graphical abstract (Elsevier: 13 x 5 cm, readable at that size)
def graphical_abstract():
    fig = plt.figure(figsize=(13 / 2.54, 5 / 2.54))
    # problem: the debts of the first event compete for one recovery channel before the second
    ax = fig.add_axes([0.02, 0.05, 0.31, 0.72]); t = np.linspace(16.6, 21.4, 500)
    base = 9.6 + 0.2 * np.sin((t - 16) / 1.7); ev = [(17, 18), (18.75, 19.75)]; cap = 14.9
    pg = base.copy()
    for a, b in ev: pg = np.where((t >= a) & (t < b), base - 6.0, pg)
    gap = (t >= 18) & (t < 18.75)
    pg = np.where(gap, base + (cap - 0.15 - base) * (1 - np.exp(-(t - 18) * 14)), pg)
    pg = np.where(t >= 19.75, base + 3.0 * np.exp(-(t - 19.75) * 1.4), pg)
    for a, b in ev: ax.axvspan(a, b, color=COL["JR-D"], alpha=0.09, lw=0)
    ax.plot(t, base, color="black", lw=0.6, ls="--"); ax.axhline(cap, color="#b22222", lw=0.8); ax.plot(t, pg, color=COL["JR-D"], lw=1.1)
    tg, bg, top = t[gap], base[gap], pg[gap]; mid = bg + 0.55 * (top - bg)
    ax.fill_between(tg, bg, mid, color="#e07b2a", alpha=0.7, lw=0); ax.fill_between(tg, mid, top, color=COL["JR-D"], alpha=0.45, lw=0)
    ax.text(17.5, 2.9, "event 1", ha="center", fontsize=6.2); ax.text(19.25, 2.9, "event 2", ha="center", fontsize=6.2)
    ax.text(16.7, cap + 0.45, "connection limit", ha="left", fontsize=6, color="#b22222")
    ax.text(21.35, 7.6, "baseline", ha="right", fontsize=6)
    ax.annotate("backlog\n+ battery", xy=(18.5, 12.2), xytext=(20.2, 13.1), fontsize=6.2, va="center",
                arrowprops=dict(arrowstyle="-|>", lw=0.6, color="#333333", mutation_scale=6))
    ax.set_xlim(16.6, 21.4); ax.set_ylim(2.0, 16.6); ax.axis("off")
    fig.text(0.175, 0.93, "Two debts, one recovery channel", ha="center", va="center", fontsize=7, fontweight="bold")
    # method: day-ahead robust commitment from the closed-loop capability + intraday cross-event joint recovery
    ax = fig.add_axes([0.345, 0.03, 0.265, 0.80]); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    _box(ax, 0.03, 0.56, 0.94, 0.38, "Day ahead: closed-loop capability\n→ Wasserstein-robust\ncommitment", "#f3eefa", ec="#7a5cb8", fs=6.1)
    _box(ax, 0.03, 0.06, 0.94, 0.33, "Intraday: cross-event\njoint recovery MPC", "#eef3fa", ec=COL["JR-D"], fs=6.1)
    _arr(ax, (0.36, 0.56), (0.36, 0.39), "#e07b2a", lw=1.0); ax.text(0.30, 0.475, "$C_k$", ha="right", va="center", fontsize=6.4, color="#b35a14")
    _arr(ax, (0.66, 0.39), (0.66, 0.56), COL["JR-D"], lw=0.9, ls="--"); ax.text(0.71, 0.475, "back-test", ha="left", va="center", fontsize=5.9, color=COL["JR-D"])
    fig.text(0.478, 0.93, "Recovery-aware scheduling", ha="center", va="center", fontsize=7, fontweight="bold")
    # result: firm consecutive DR capacity (exp12, 26 operating days, reliability 95 %)
    ax = fig.add_axes([0.675, 0.15, 0.315, 0.60]); names, x, wd = ["IR-O*", "JR-M", "JR-D"], np.arange(3), 0.26
    for k, n in enumerate(names):
        vals = []
        for tag, _ in CAP_TAGS:
            d = load_capacity(tag); vals.append(c_rho(d[d.name == n].groupby("C").all_full.mean(), 0.95) if d is not None else np.nan)
        for i, v in enumerate(vals):
            xx = x[i] + (k - 1) * wd
            if np.isnan(v):
                ax.bar(xx, 0.5, wd * 0.92, color=COL[n], alpha=0.35, hatch="////", edgecolor=COL[n], lw=0.4)
                ax.text(xx, 0.75, "<1", ha="center", va="bottom", fontsize=5.6, color="#333333")
            else:
                ax.bar(xx, v, wd * 0.92, color=COL[n], alpha=0.9, lw=0)
                ax.text(xx, v + 0.2, f"{v:g}", ha="center", va="bottom", fontsize=5.8, color="#222222", fontweight="bold" if n == "JR-D" else "normal")
    ax.set_xticks(x); ax.set_xticklabels(["S1", "S2", "S3"], fontsize=6.2); ax.set_ylim(0, 9.4); ax.set_yticks([0, 4, 8])
    ax.tick_params(labelsize=6, length=2); ax.set_ylabel("MW", fontsize=6.2, labelpad=1)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    hs = [plt.Rectangle((0, 0), 1, 1, color=COL[n], alpha=0.9) for n in names]
    fig.legend(hs, ["Independent", "Event-by-event", "Cross-event"], fontsize=5.6, loc="center", bbox_to_anchor=(0.832, 0.825),
               ncol=3, frameon=False, handlelength=0.8, handletextpad=0.3, columnspacing=0.8)
    fig.text(0.832, 0.93, "Firm consecutive DR capacity", ha="center", va="center", fontsize=7, fontweight="bold")
    fig.text(0.832, 0.025, "full delivery on 95 % of 26 operating days", ha="center", va="bottom", fontsize=5.4, color="#555555")
    with plt.rc_context({"savefig.bbox": "standard"}): save(fig, "GraphicalAbstract", dpi=600)      # exactly 13 x 5 cm



# ------------------------------------------------------------------ Fig. 16 event-call uncertainty and post-event rebound
def fig16_uncertainty_rebound():
    d = rd("exp4_e3uncertain.csv"); s = rd("exp4_e3uncertain_strategies.csv")
    r = rd("exp8_rebound.csv"); rs = rd("exp8_strategies.csv")
    if d is None or s is None or r is None or rs is None: return
    d["name"] = d.strategy.map(dict(zip(s["index"], s["label"]))); r["name"] = r.strategy.map(dict(zip(rs["index"], rs["label"])))
    fig, axs = plt.subplots(2, 2, figsize=(DOUBLE_COL, 4.5)); fig.subplots_adjust(wspace=0.26, hspace=0.66, left=0.075, right=0.99, top=0.93, bottom=0.17)
    names = list(s["label"]); w = 0.38
    for j, (col, lab, sc) in enumerate([("net_cost_adj", "Mean daily cost (10$^3$ CNY)", 1e-3), ("fulfil_rate_pct", "Mean fulfilment (%)", 1)]):
        a = axs[0, j]
        for k, called in enumerate([1, 0]):
            v = [d[(d.name == n) & (d.called_E3 == called)][col].mean() * sc for n in names]
            a.bar(np.arange(len(names)) + (k - 0.5) * w, v, w, color=["#1f5fa8", "#8fb3d9"][k], edgecolor="white", label=["third event called", "third event cancelled"][k])
        a.set_xticks(range(len(names))); a.set_xticklabels(names, fontsize=6.8); a.set_ylabel(lab); panel(a, "ab"[j], x=-0.16)
        a.set_ylim(*((60, 104) if j else (0, 300)))
        a.set_title("Event-call uncertainty (S4-U, 6 MW)", fontsize=7.6)
    axs[0, 0].legend(fontsize=6.3, loc="upper center", ncol=2)
    for n in ORDER:
        q = r[r.name == n].sort_values("c_rb")
        if q.empty: continue
        axs[1, 0].plot(q.max_rebound_MW, q.net_cost_excl_rb / 1e3, color=COL[n], ls=LS[n], marker=MK[n], ms=3.5, mfc="white", lw=1.2, label=n)
        axs[1, 1].plot(q.c_rb / 1e3, q.max_rebound_MW, color=COL[n], ls=LS[n], marker=MK[n], ms=3.5, mfc="white", lw=1.2, label=n)
    axs[1, 0].set_xlabel("Peak post-event rebound (MW)"); axs[1, 0].set_ylabel("Daily cost (10$^3$ CNY)"); panel(axs[1, 0], "c", x=-0.16)
    axs[1, 1].set_xlabel("Rebound assessment price $c^{rb}$ (CNY/kW per event)"); axs[1, 1].set_ylabel("Peak rebound (MW)"); panel(axs[1, 1], "d", x=-0.16)
    axs[1, 0].set_title("Cost under the Jiangsu rules (S1, 6 MW)", fontsize=7.6)
    axs[1, 1].set_title("Rebound versus assessment price (S1, 6 MW)", fontsize=7.6)
    h, l = axs[1, 0].get_legend_handles_labels(); bottom_legend(fig, h, l, ncol=4, y=0.065)
    save(fig, "Fig16_uncertainty_rebound")


FIGS.update({"1": fig1, "2": fig2_framework, "3": fig3_typical, "4": fig4_states, "5": fig5_sankey, "6": fig6_capacity, "7": fig7_region,
             "8": fig8_decomp, "9": fig9_sensitivity, "10": fig10_substitution, "11": fig11_calibration, "12": fig12_ies, "13": fig13,
             "14": fig14_economics, "15": fig15_commitment, "16": fig16_uncertainty_rebound,
             "GA": graphical_abstract})


if __name__ == "__main__":
    which = sys.argv[1:] or list(FIGS)
    for w in which:
        if w in FIGS: FIGS[w]()
