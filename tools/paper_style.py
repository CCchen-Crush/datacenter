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
