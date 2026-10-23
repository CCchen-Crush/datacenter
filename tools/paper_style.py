"""Shared style, loaders and statistics for the Applied Energy figures (tools/plot_paper.py, tools/paper_numbers.py)."""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "matlab", "results")
FIG = os.path.join(HERE, "..", "paper", "figures")
os.makedirs(FIG, exist_ok=True)

plt.rcParams.update({
    "font.family": "serif", "font.serif": ["Liberation Serif", "Times New Roman", "DejaVu Serif"],
    "mathtext.fontset": "stix", "font.size": 8.5, "axes.titlesize": 9, "axes.labelsize": 8.5,
    "legend.fontsize": 7.5, "xtick.labelsize": 7.5, "ytick.labelsize": 7.5,
    "axes.linewidth": 0.6, "axes.edgecolor": "#3b3b3b", "axes.grid": True, "grid.color": "#e3e3e3",
    "grid.linewidth": 0.5, "grid.linestyle": "-", "axes.axisbelow": True, "legend.frameon": False,
    "xtick.direction": "in", "ytick.direction": "in", "xtick.major.width": 0.6, "ytick.major.width": 0.6,
    "figure.dpi": 150, "savefig.bbox": "tight", "savefig.pad_inches": 0.02, "pdf.fonttype": 42, "svg.fonttype": "none",
})
# fixed colour per strategy (muted, print- and colour-blind-safe pairs)
COL = {"JR-D": "#1f5fa8", "IR-O*": "#e07b2a", "IR-P": "#3a9a5b", "JR-M": "#c4508a", "JR-S": "#7a5cb8",
       "JR-oracle": "#5c5c5c", "NoDR": "#9a9a9a", "SE": "#b8860b", "RA": "#1f5fa8"}
MK = {"JR-D": "o", "IR-O*": "s", "IR-P": "^", "JR-M": "v", "JR-S": "D", "JR-oracle": "x"}
LS = {"JR-D": "-", "IR-O*": "--", "IR-P": "-.", "JR-M": ":"}
ORDER = ["IR-O*", "IR-P", "JR-M", "JR-D"]
SCEN = {"S1": "S1: two events, 1-h interval", "S2": "S2: two events, 30-min interval", "S3": "S3: three events (stress)"}
EVENTS = {"S1": [(17, 18), (19, 20)], "S2": [(17, 18), (18.5, 19.5)], "S3": [(17, 18), (19, 20), (21, 22)],
          "short": [(17, 18), (18.5, 19.5)], "long": [(17, 18), (21, 22)]}
SINGLE_COL, DOUBLE_COL = 3.54, 7.48          # Elsevier column widths (inch)
rng = np.random.default_rng(2024)


def rd(name):
    p = os.path.join(RES, name)
    return pd.read_csv(p) if os.path.exists(p) else None


def save(fig, name):
    for ext in ("pdf", "svg", "png"):
        fig.savefig(os.path.join(FIG, f"{name}.{ext}"), dpi=300 if ext == "png" else None)
    plt.close(fig)
    print("wrote", name)


def shade(ax, ev, color="#1f5fa8", alpha=0.08):
    for a, b in ev:
        ax.axvspan(a, b, color=color, alpha=alpha, lw=0)


def panel(ax, letter, x=-0.14, y=1.04):
    ax.text(x, y, f"({letter})", transform=ax.transAxes, fontsize=9, fontweight="bold", va="bottom")


def load_capacity(tag):
    """exp12_capacity<tag>.csv with strategy names."""
    d = rd(f"exp12_capacity{tag}.csv"); s = rd(f"exp12_strategies{tag}.csv")
    if d is None or s is None: return None
    d["name"] = d.strategy.map(dict(zip(s["index"], s["label"])))
    return d


def c_rho(share, rho):
    """Largest C of a sorted share-vs-C series such that share >= rho for C and all smaller C (NaN if none)."""
    sh = share.sort_index(); ok = (sh.values >= rho - 1e-9)
    if not ok[0]: return np.nan
    k = len(ok) if ok.all() else int(np.argmin(ok))
    return float(sh.index.values[k - 1])


def capacity_table(d, col="all_full", rhos=(0.90, 0.95), B=2000):
    """C_rho per strategy with a block bootstrap over test days (each realisation = one PAI weekday)."""
    days = np.sort(d.realisation.unique()); out = {}
    piv = {n: d[d.name == n].pivot(index="realisation", columns="C", values=col).loc[days] for n in d.name.unique()}
    Cs = next(iter(piv.values())).columns.values
    idx = rng.integers(0, len(days), (B, len(days)))
    for n, p in piv.items():
        pt = {r: c_rho(p.mean(axis=0), r) for r in rhos}
        bt = {r: np.array([c_rho(pd.Series(p.values[i].mean(axis=0), index=Cs), r) for i in idx]) for r in rhos}
        out[n] = (pt, bt)
    return out, idx


def share_band(d, name, col="all_full", B=2000):
    """Mean share vs C and 95 % block-bootstrap band."""
    p = d[d.name == name].pivot(index="realisation", columns="C", values=col)
    idx = rng.integers(0, p.shape[0], (B, p.shape[0]))
    bs = np.array([p.values[i].mean(axis=0) for i in idx])
    return p.columns.values, p.values.mean(axis=0), np.percentile(bs, 2.5, axis=0), np.percentile(bs, 97.5, axis=0)


# ------------------------------------------------------------------ distributionally robust firm capacity (Proposition 3)
def capability(d, name, col="all_full"):
    """Capability xi of one strategy per day: largest commitment C of the grid with full delivery at C and at every
    smaller C of the grid (monotone definition, as Eq. 13). Returns (lower bound on the grid, grid step); a day that
    fails at the smallest commitment gets the lower bound grid_min - step."""
    p = d[d.name == name].pivot_table(index=d.columns[1] if "day" not in d.columns else "day", columns="C", values=col)
    Cs = p.columns.values.astype(float); step = np.min(np.diff(Cs)) if len(Cs) > 1 else 0.5
    ok = (p.values > 0.5).cumprod(axis=1).astype(bool)
    k = ok.sum(axis=1)
    lb = np.where(k > 0, Cs[np.maximum(k - 1, 0)], Cs[0] - step)
    return pd.Series(lb, index=p.index), step


def worst_case_prob(xi, C, eps):
    """inf of Q(xi >= C) over the 1-Wasserstein ball of radius eps (MW) around the empirical distribution of xi:
    the adversary moves probability mass from the samples closest above C to just below C (cost = distance x mass)."""
    xi = np.asarray(xi, float); N = len(xi)
    dist = np.sort(xi[xi >= C - 1e-12] - C)
    if eps <= 0: return len(dist) / N
    budget = N * eps; m = 0.0
    for dd in dist:
        if dd <= 1e-12: m += 1; continue
        if budget >= dd: budget -= dd; m += 1
        else: m += budget / dd; break
    return max(len(dist) - m, 0.0) / N


def dro_capacity(xi, rho, eps, grid):
    """Largest commitment of the grid whose worst-case full-delivery probability is at least rho (NaN if none);
    eps = 0 gives the sample-average (order-statistic) capacity."""
    best = np.nan
    for c in sorted(grid):
        if worst_case_prob(xi, c, eps) >= rho - 1e-9: best = c
        else: break
    return best


def cv_radius(xi_mid, xi_lb, rho, grid, eps_grid=None):
    """Leave-one-out choice of the radius: the smallest eps for which the commitment computed without day d is
    delivered on day d (xi_lb[d] >= C_-d) on at least a share rho of the days."""
    if eps_grid is None: eps_grid = np.round(np.arange(0, 0.501, 0.005), 3)
    xi_mid = np.asarray(xi_mid, float); xi_lb = np.asarray(xi_lb, float); N = len(xi_mid)
    for e in eps_grid:
        hit = []
        for j in range(N):
            c = dro_capacity(np.delete(xi_mid, j), rho, e, grid)
            hit.append(True if np.isnan(c) else xi_lb[j] >= c - 1e-9)
        if np.mean(hit) >= rho - 1e-9: return float(e)
    return float(eps_grid[-1])


# ------------------------------------------------------------------ recovery energy sources and uses (Sankey, Fig. 11)
PDYN = 8.4 / 8 / 1000 * 0.75          # MW per busy GPU (dynamic part), Table A1
def recovery_flows(q, ref, windows, theta=1.0, ups=0.05):
    """Energy (MWh) supplied to and used by recovery in the given hour windows, relative to the no-DR operation of the
    same day. Electric and cooling balances combined: d(grid) + d(PV) + d(gas engine) + d(absorption cooling)/COP +
    d(TES discharge)/COP = d(compute facility energy) + d(BESS net charge) + d(TES charge)/COP."""
    h = q.hour.values; dt = h[1] - h[0]
    w = np.zeros(len(h), bool)
    for a, b in windows: w |= (h >= a - 1e-9) & (h < b - 1e-9)
    d = lambda c: (q[c].values - ref[c].values)[w]
    cop = q.cop.values[w]
    src = {"Grid headroom": d("pg"), "PV": d("ppv"), "Gas engine": d("pgt"), "Absorption chiller": d("qac") / cop,
           "TES discharge": d("qtd") / cop}
    use = {"Compute catch-up": (1 + ups + theta / cop) * d("pit"), "BESS recharge": d("pch") - d("pdis"), "TES recharge": d("qtc") / cop}
    S = {k: float(np.sum(v) * dt) for k, v in src.items()}; U = {k: float(np.sum(v) * dt) for k, v in use.items()}
    # a negative source is a use and vice versa (e.g. less gas than without DR)
    for k in list(S):
        if S[k] < 0: U[k + " (reduced)"] = -S.pop(k)
    for k in list(U):
        if U[k] < 0 and not k.endswith("(reduced)"): S[k.replace("recharge", "discharge").replace("catch-up", "carried over")] = -U.pop(k)
    return S, U
