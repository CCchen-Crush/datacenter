#!/usr/bin/env python3
"""Render the paper figures from matlab/results/*.csv (alternative to matlab/src/plot_all.m).

Usage: python3 tools/plot_results.py [results_dir] [figure_dir]
"""
import os, sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

HERE = os.path.dirname(os.path.abspath(__file__))
RES = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "matlab", "results")
FIG = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "matlab", "figures")
os.makedirs(FIG, exist_ok=True)

# fonts: CJK if available
for f in ["Noto Sans CJK SC", "WenQuanYi Micro Hei", "SimHei", "Microsoft YaHei"]:
    if any(f in x.name for x in font_manager.fontManager.ttflist):
        plt.rcParams["font.sans-serif"] = [f, "DejaVu Sans"]
        break
plt.rcParams.update({"axes.unicode_minus": False, "font.size": 9, "axes.titlesize": 10,
                     "axes.edgecolor": "#c9c8c2", "axes.linewidth": 0.8, "axes.grid": True,
                     "grid.color": "#e6e5e0", "grid.linewidth": 0.6, "grid.linestyle": "-",
                     "xtick.color": "#52514e", "ytick.color": "#52514e", "axes.labelcolor": "#0b0b0b",
                     "legend.frameon": False, "figure.dpi": 150, "savefig.bbox": "tight", "axes.axisbelow": True})

# fixed categorical slots (reference palette, light mode); colour follows the entity
C = {"JR-S": "#2a78d6", "IR-O": "#eb6834", "IR-R": "#1baf7a", "JR-D": "#eda100", "JR-oracle": "#e87ba4",
     "IRJ": "#6250d6", "bound": "#8a8984", "base": "#52514e", "cap": "#e34948", "NoDR": "#8a8984"}
NAME = {"IR-R": "独立恢复-规则 (IR-R)", "IR-O": "独立恢复-优化 (IR-O)", "JR-D": "联合恢复-确定性MPC (JR-D)",
        "JR-S": "联合恢复-场景MPC (JR-S, 本文)", "JR-oracle": "联合恢复-完美信息 (JR-oracle)", "NoDR": "不参与DR"}
EV = [(17, 18), (19, 20), (21, 22)]


def rd(name):
    p = os.path.join(RES, name)
    return pd.read_csv(p) if os.path.exists(p) else None


def shade(ax, ev=EV):
    for a, b in ev:
        ax.axvspan(a, b, color="#2a78d6", alpha=0.07, lw=0)


def save(fig, name):
    fig.savefig(os.path.join(FIG, name)); plt.close(fig); print("wrote", name)


def fig_case():
    d = rd("case_profiles.csv")
    if d is None: return
    h = d.hour
    fig, ax = plt.subplots(2, 2, figsize=(9, 5.4), sharex=True)
    a = ax[0, 0]; shade(a)
    a.plot(h, d.baseline, color=C["base"], lw=2, label="DR基线（前5个典型工作日均值）")
    a.plot(h, d.pg_noDR, color=C["JR-S"], lw=1.5, label="DR日不响应时的并网功率")
    cap = pd.read_csv(os.path.join(RES, "ts_DAcommit_JRS.csv")).Pcap.iloc[0] if os.path.exists(os.path.join(RES, "ts_DAcommit_JRS.csv")) else None
    if cap: a.axhline(cap, color=C["cap"], lw=1, label="并网容量上限")
    a.set_ylabel("并网功率 / MW"); a.set_title("(a) 并网功率基线"); a.legend(fontsize=7, loc="lower left")
    a = ax[0, 1]
    st = [d.gpu_inf, d.gpu_flex0, d.gpu_c1, d.gpu_c2, d.gpu_c3]
    lab = ["在线推理 (Flex0)", "不可延迟训练 (Flex0)", "C1 短作业 (L=0.5h)", "C2 中作业 (L=1.5h)", "C3 长训练 (L=3h)"]
    col = ["#8a8984", "#c3c2b7", "#1baf7a", "#eb6834", "#2a78d6"]
    a.stackplot(h, *[s / 1000 for s in st], labels=lab, colors=col, lw=0)
    a.set_ylabel("忙碌GPU / 千卡"); a.set_title("(b) GPU负载构成（PAI/Azure 轨迹）"); a.legend(fontsize=6.5, loc="upper left", ncol=2)
    a = ax[1, 0]
    a.step(h, d.price / 1000, where="post", color=C["base"], lw=2)
    a.set_ylabel("分时电价 / (元/kWh)"); a.set_xlabel("时刻 / h"); a.set_title("(c) 江苏工商业分时电价（夏季）"); shade(a)
    a = ax[1, 1]
    a.plot(h, d.pv, color=C["JR-D"], lw=2, label="光伏出力 / MW")
    a.plot(h, d.cop, color=C["IR-O"], lw=2, label="冷机系统COP")
    a.set_xlabel("时刻 / h"); a.set_title("(d) 光伏出力与冷机COP（苏州吴江 2024-08-05）"); a.legend(fontsize=7)
    for x in ax.flat: x.set_xlim(0, 30); x.set_xticks(range(0, 31, 3))
    save(fig, "fig01_case_profiles.png")


def fig_mechanism():
    files = [("exp1_mechanism_CA6_DA2.csv", "前序 6 MW×2 h，后续 1 h"), ("exp1_mechanism_CA6_DA1_DB2.csv", "前序 6 MW×1 h，后续 2 h")]
    data = [(rd(f), t) for f, t in files]
    if any(x is None for x, _ in data): return
    fig, ax = plt.subplots(2, 2, figsize=(9.5, 7.4)); fig.subplots_adjust(hspace=0.42, wspace=0.32)
    for j, (d, t) in enumerate(data):
        a = ax[0, j]; g = d[np.isclose(d.gamma, 1.10)]
        for key, col, lab in [("G_IR", C["IR-O"], "独立恢复 IR"), ("G_IRJ", C["IRJ"], "IR后状态+联合恢复"), ("G_JR", C["JR-S"], "联合响应+联合恢复 JR")]:
            a.plot(g.tau_h, g[key] / g.G0, color=col, lw=2, marker="o", ms=4, label=lab)
        a.plot(g.tau_h, g.G_bound / g.G0, color=C["bound"], lw=1.2, ls="--", label="命题1 上界")
        a.set_ylim(0, 1.08); a.set_xlabel("事件间隔 τ / h"); a.set_ylabel("后续事件可交付能力 Γ_B/Γ_B⁰")
        a.set_title(f"({'ab'[j]}) {t}，γ=1.10"); a.legend(fontsize=7, loc="lower right")
    d = data[0][0]
    taus = sorted(d.tau_h.unique()); gams = sorted(d.gamma.unique())
    for j, (key, lab) in enumerate([("G_IR", "独立恢复"), ("G_JR", "联合恢复")]):
        Z = np.array([[float((d[(d.gamma == g) & (d.tau_h == t)][key] / d[(d.gamma == g) & (d.tau_h == t)].G0).iloc[0]) for t in taus] for g in gams])
        a = ax[1, j]; im = a.imshow(Z, origin="lower", aspect="auto", cmap="Blues", vmin=0.2, vmax=1.0)
        a.set_xticks(range(len(taus))); a.set_xticklabels([f"{t:g}" for t in taus]); a.set_yticks(range(len(gams))); a.set_yticklabels([f"{g:.2f}" for g in gams])
        for i in range(len(gams)):
            for k in range(len(taus)):
                a.text(k, i, f"{Z[i,k]:.2f}", ha="center", va="center", fontsize=6.5, color="white" if Z[i, k] > 0.65 else "#0b0b0b")
        a.set_xlabel("事件间隔 τ / h"); a.set_ylabel("并网容量裕度 γ"); a.set_title(f"({'cd'[j]}) {lab}：Γ_B/Γ_B⁰（前序 6 MW×2 h）"); a.grid(False)
    fig.colorbar(im, ax=ax[1, :], shrink=0.8, label="可交付能力比")
    save(fig, "fig02_mechanism.png")


def fig_timeseries(case="DAcommit"):
    S = ["IR-R", "IR-O", "JR-S"]
    D = {s: rd(f"ts_{case}_{s.replace('-', '')}.csv") for s in S}
    if any(v is None for v in D.values()): return
    fig, ax = plt.subplots(3, 1, figsize=(8.5, 7.2), sharex=True)
    a = ax[0]; shade(a); b = D["JR-S"]
    a.plot(b.hour, b.base, color=C["base"], lw=1.5, ls="--", label="DR基线")
    a.axhline(b.Pcap.iloc[0], color=C["cap"], lw=1, label="并网容量")
    for s in S: a.plot(D[s].hour, D[s].pg, color=C[s], lw=1.8, label=NAME[s])
    a.set_ylabel("并网功率 / MW"); a.legend(fontsize=7, ncol=2, loc="lower left"); a.set_title("(a) 并网功率与基线（阴影为DR事件）")
    a = ax[1]; shade(a)
    for s in S: a.plot(D[s].hour, D[s].E, color=C[s], lw=1.8, label=NAME[s])
    a.set_ylabel("电储能电量 / MWh"); a.set_title("(b) 储能状态（储侧恢复状态）")
    a = ax[2]; shade(a)
    for s in S: a.plot(D[s].hour, (D[s].B1 + D[s].B2 + D[s].B3) / 1000, color=C[s], lw=1.8, label=NAME[s])
    a.set_ylabel("积压任务 / 千GPU·h"); a.set_xlabel("时刻 / h"); a.set_title("(c) 任务积压（算侧恢复状态）")
    for x in ax: x.set_xlim(12, 30); x.set_xticks(range(12, 31, 2))
    save(fig, f"fig03_timeseries_{case}.png")
    # backlog by class + IES dispatch for the proposed strategy
    fig, ax = plt.subplots(2, 1, figsize=(8.5, 5), sharex=True)
    j = D["JR-S"]; o = D["IR-O"]
    a = ax[0]; shade(a)
    for k, col in zip([1, 2, 3], ["#1baf7a", "#eb6834", "#2a78d6"]):
        a.plot(j.hour, j[f"B{k}"] / 1000, color=col, lw=2, label=f"JR-S C{k}")
        a.plot(o.hour, o[f"B{k}"] / 1000, color=col, lw=1, alpha=0.6, ls=":", label=f"IR-O C{k}")
    a.set_ylabel("积压 / 千GPU·h"); a.legend(fontsize=7, ncol=3); a.set_title("(a) 分类别积压：联合恢复跨事件“携带”长时限任务")
    a = ax[1]; shade(a)
    a.plot(j.hour, j.pdis - j.pch, color=C["JR-S"], lw=2, label="BESS 放电(+)/充电(-)")
    a.plot(j.hour, (j.qtd - j.qtc) / 4.5, color=C["IR-R"], lw=2, label="蓄冷 放冷(+)/蓄冷(-)（电当量）")
    a.plot(j.hour, j.pgt, color=C["JR-D"], lw=2, label="燃气内燃机出力")
    a.plot(j.hour, j.ppv, color=C["JR-oracle"], lw=2, label="光伏")
    a.set_ylabel("功率 / MW"); a.set_xlabel("时刻 / h"); a.legend(fontsize=7, ncol=2); a.set_title("(b) JR-S 综合能源设备出力")
    for x in ax: x.set_xlim(12, 30); x.set_xticks(range(12, 31, 2))
    save(fig, f"fig04_backlog_ies_{case}.png")


def fig_sensitivity():
    files = [("exp3_duration.csv", "事件持续时间 / h"), ("exp3_interval.csv", "事件间隔 / h"),
             ("exp3_gamma.csv", "并网容量裕度 γ"), ("exp3_commitment.csv", "响应承诺 / MW")]
    data = [(rd(f), l) for f, l in files]
    if any(d is None for d, _ in data): return
    fig, ax = plt.subplots(2, 4, figsize=(12, 5.2))
    for j, (d, lab) in enumerate(data):
        for i, s in enumerate(["IR-R", "IR-O", "JR-S"]):
            q = d[d.strategy == i + 1]
            nm = {"JR-S": "联合恢复 JR"}.get(s, NAME[s])
            ax[0, j].plot(q.x, q.fulfil_pct, color=C[s], lw=2, marker="o", ms=4, label=nm)
            ax[1, j].plot(q.x, q.max_rebound, color=C[s], lw=2, marker="o", ms=4, label=nm)
        ax[0, j].set_ylim(0, 105); ax[0, j].set_title(f"({'abcd'[j]}) {lab}")
        ax[1, j].set_xlabel(lab); ax[1, j].set_ylim(bottom=0)
    ax[0, 0].set_ylabel("连续响应兑现率 / %"); ax[1, 0].set_ylabel("恢复阶段最大反弹 / MW")
    ax[0, 0].legend(fontsize=7, loc="lower left")
    save(fig, "fig05_sensitivity.png")


def fig_map():
    d = rd("exp3_map.csv")
    if d is None: return
    taus = sorted(d.x.unique()); gams = sorted(d.gamma.unique())
    def get(g, t, s, col):
        return float(d[(d.gamma == g) & (d.x == t) & (d.strategy == s)][col].iloc[0])
    Zf = np.array([[get(g, t, 3, "fulfil_pct") - get(g, t, 2, "fulfil_pct") for t in taus] for g in gams])
    Zr = np.array([[get(g, t, 2, "max_rebound") - get(g, t, 3, "max_rebound") for t in taus] for g in gams])
    fig, ax = plt.subplots(1, 2, figsize=(10.5, 3.6)); fig.subplots_adjust(wspace=0.55)
    for a, Z, title, unit in [(ax[0], Zf, "(a) 兑现率提升（JR − IR-O）", "百分点"), (ax[1], Zr, "(b) 最大反弹降低（IR-O − JR）", "MW")]:
        im = a.imshow(Z, origin="lower", aspect="auto", cmap="Blues", vmin=min(0, Z.min()))
        a.set_xticks(range(len(taus))); a.set_xticklabels([f"{t:g}" for t in taus]); a.set_yticks(range(len(gams))); a.set_yticklabels([f"{g:.2f}" for g in gams])
        for i in range(len(gams)):
            for k in range(len(taus)):
                a.text(k, i, f"{Z[i,k]:.1f}", ha="center", va="center", fontsize=7, color="white" if Z[i, k] > 0.6 * Z.max() else "#0b0b0b")
        a.set_xlabel("事件间隔 τ / h"); a.set_ylabel("并网容量裕度 γ"); a.set_title(title); a.grid(False)
        fig.colorbar(im, ax=a, label=unit)
    save(fig, "fig06_interval_capacity_map.png")


def fig_mc():
    d = rd("exp4_montecarlo.csv")
    if d is None: return
    S = ["IR-R", "IR-O", "JR-D", "JR-S"]
    fig, ax = plt.subplots(1, 3, figsize=(11, 3.6))
    for j, (col, lab) in enumerate([("fulfil_pct", "连续响应兑现率 / %"), ("max_rebound", "最大反弹功率 / MW"), ("net_cost", "综合运行成本 / 万元")]):
        a = ax[j]
        vals = [d[d.strategy == i + 1][col].values / (1e4 if col == "net_cost" else 1) for i in range(4)]
        bp = a.boxplot(vals, widths=0.45, patch_artist=True, showfliers=False)
        for k, b in enumerate(bp["boxes"]):
            b.set_facecolor(C[S[k]] + "33"); b.set_edgecolor(C[S[k]])
        for k, m in enumerate(bp["medians"]): m.set_color(C[S[k]]); m.set_linewidth(2)
        for k, v in enumerate(vals):
            a.scatter(np.full(len(v), k + 1) + np.linspace(-0.12, 0.12, len(v)), v, s=10, color=C[S[k]], zorder=3, edgecolor="white", linewidth=0.6)
        a.set_xticks(range(1, 5)); a.set_xticklabels(S); a.set_title(f"({'abc'[j]}) {lab}")
    save(fig, "fig07_montecarlo.png")


def fig_shadow():
    d = rd("exp5_shadow.csv"); t = rd("exp5_shadow_gamma100.csv")
    if d is None: return
    fig, ax = plt.subplots(3, 1, figsize=(8.5, 6.6), sharex=True)
    for a in ax: shade(a)
    ax[0].plot(d.hour, d.lambda_headroom, color=C["JR-S"], lw=2, label="γ=1.10：恢复通道总影子价格（并网约束+反弹考核）")
    ax[0].plot(d.hour, d.lambda_cap, color=C["cap"], lw=1.5, label="γ=1.10：其中并网容量约束")
    if t is not None:
        ax[0].plot(t.hour, t.lambda_cap, color=C["IR-O"], lw=1.5, label="γ=1.00：并网容量约束")
    ax[0].axhline(1010, color=C["base"], lw=1, ls="--", label="峰时电价 1010 元/MWh")
    ax[0].set_ylabel("元/MWh"); ax[0].legend(fontsize=7, loc="upper right"); ax[0].set_title("(a) 事件间隔内“恢复通道”的边际价值")
    ax[1].plot(d.hour, d.value_E, color=C["JR-S"], lw=2, label="电储能电量")
    ax[1].plot(d.hour, d.value_S, color=C["IR-R"], lw=2, label="蓄冷量")
    ax[1].set_ylabel("元/MWh"); ax[1].legend(fontsize=7); ax[1].set_title("(b) 储侧状态的边际价值")
    for k, col in zip([1, 2, 3], ["#1baf7a", "#eb6834", "#2a78d6"]):
        ax[2].plot(d.hour, d[f"cost_B{k}"], color=col, lw=2, label=f"C{k} 积压（L={[0.5,1.5,3][k-1]} h）")
    ax[2].set_ylabel("元/(GPU·h)"); ax[2].set_xlabel("时刻 / h"); ax[2].legend(fontsize=7); ax[2].set_title("(c) 算侧积压状态的边际成本")
    for a in ax: a.set_xlim(12, 30); a.set_xticks(range(12, 31, 2))
    save(fig, "fig08_shadow_prices.png")


def fig_commit():
    d = rd("exp6_commitment.csv")
    if d is None: return
    fig, ax = plt.subplots(1, 2, figsize=(9.5, 3.4))
    x = np.arange(3); w = 0.32
    cpl = d[d.assessment == 1].iloc[0]; sgl = d[d.assessment == 2].iloc[0]
    ax[0].bar(x - w / 2 - 0.01, [cpl.C1, cpl.C2, cpl.C3], w, color=C["JR-S"], label="耦合评估（本文）")
    ax[0].bar(x + w / 2 + 0.01, [sgl.C1, sgl.C2, sgl.C3], w, color=C["IR-O"], label="单事件独立评估")
    ax[0].set_xticks(x); ax[0].set_xticklabels(["E1", "E2", "E3"]); ax[0].set_ylabel("日前响应承诺 / MW"); ax[0].legend(fontsize=7); ax[0].set_title("(a) 日前承诺")
    labs = d.label.tolist(); v = d.fulfil_pct.values
    cols = [C["JR-S"] if l.startswith("coupled") else C["IR-O"] for l in labs]
    ax[1].bar(range(len(v)), v, 0.6, color=cols)
    ax[1].set_xticks(range(len(v))); ax[1].set_xticklabels([l.split("|")[1] for l in labs], fontsize=7)
    for i, t in enumerate(v): ax[1].text(i, t + 1, f"{t:.0f}", ha="center", fontsize=7)
    ax[1].set_ylabel("实际兑现率 / %"); ax[1].set_ylim(0, 110); ax[1].set_title("(b) 实际兑现率（蓝=耦合承诺，橙=单事件承诺）")
    save(fig, "fig09_commitment.png")


if __name__ == "__main__":
    fig_case(); fig_mechanism(); fig_timeseries("DAcommit"); fig_timeseries("uniform6")
    fig_sensitivity(); fig_map(); fig_mc(); fig_shadow(); fig_commit()
