"""Flat vector icons for the schematic figures (Fig. 1 and the graphical abstract), drawn with matplotlib patches.

icon(fig, ax, (x, y, w, h), kind) draws the icon `kind` into a square inset placed at the data rectangle (x, y, w, h) of `ax`
(centred, as large as fits). Every icon is drawn in the unit square of its own equal-aspect axes."""
import numpy as np
from matplotlib.patches import Circle, Ellipse, FancyBboxPatch, Polygon, Rectangle, Wedge

INK, GRID, BLUE, ORANGE, TEAL, PURPLE, RED, GOLD = "#3b3b3b", "#4a4a4a", "#1f5fa8", "#b4561c", "#167f9e", "#6a4fa3", "#c0392b", "#d9a400"


def _inset(fig, ax, rect):
    """Square axes centred in the data rectangle rect = (x, y, w, h) of ax."""
    x, y, w, h = rect
    (x0, y0), (x1, y1) = fig.transFigure.inverted().transform(ax.transData.transform([(x, y), (x + w, y + h)]))
    fw, fh = fig.get_size_inches(); s = min((x1 - x0) * fw, (y1 - y0) * fh)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    a = fig.add_axes([cx - s / fw / 2, cy - s / fh / 2, s / fw, s / fh])
    a.set_xlim(0, 1); a.set_ylim(0, 1); a.set_aspect("equal"); a.axis("off")
    return a


def _snow(a, x, y, r, color=TEAL, lw=0.9):
    for k in range(3):
        t = np.pi / 3 * k
        a.plot([x - r * np.cos(t), x + r * np.cos(t)], [y - r * np.sin(t), y + r * np.sin(t)], color=color, lw=lw, solid_capstyle="round")


def pylon(a):
    c = GRID
    a.plot([0.28, 0.45, 0.55, 0.72], [0.02, 0.86, 0.86, 0.02], color=c, lw=1.1)
    for y0, half in [(0.70, 0.33), (0.86, 0.24)]:
        a.plot([0.5 - half, 0.5 + half], [y0, y0], color=c, lw=1.1)
        for s in (-1, 1):
            a.plot([0.5 + s * half] * 2, [y0, y0 - 0.09], color=c, lw=0.8)
    xs = lambda y: (0.28 + (0.45 - 0.28) * y / 0.86, 0.72 - (0.72 - 0.55) * y / 0.86)
    for y0, y1 in [(0.02, 0.24), (0.24, 0.46), (0.46, 0.70)]:
        l0, r0 = xs(y0); l1, r1 = xs(y1)
        a.plot([l0, r1], [y0, y1], color=c, lw=0.6); a.plot([r0, l1], [y0, y1], color=c, lw=0.6)
        a.plot([l1, r1], [y1, y1], color=c, lw=0.6)
    a.plot([0.1, 0.9], [0.02, 0.02], color=c, lw=0.8)


def pv(a):
    a.add_patch(Circle((0.82, 0.83), 0.09, fc=GOLD, ec="none"))
    for k in range(8):
        t = np.pi / 4 * k
        a.plot([0.82 + 0.12 * np.cos(t), 0.82 + 0.17 * np.cos(t)], [0.83 + 0.12 * np.sin(t), 0.83 + 0.17 * np.sin(t)], color=GOLD, lw=0.8)
    p = np.array([(0.06, 0.18), (0.70, 0.18), (0.86, 0.60), (0.22, 0.60)])
    a.add_patch(Polygon(p, closed=True, fc="#2f5f9e", ec="#1d3d66", lw=0.8))
    for f in (1 / 3, 2 / 3):
        a.plot([p[0, 0] + f * (p[1, 0] - p[0, 0]), p[3, 0] + f * (p[2, 0] - p[3, 0])], [0.18, 0.60], color="#a9c4e8", lw=0.6)
    for f in (0.5,):
        a.plot([p[0, 0] + f * (p[3, 0] - p[0, 0]), p[1, 0] + f * (p[2, 0] - p[1, 0])], [0.18 + f * 0.42] * 2, color="#a9c4e8", lw=0.6)
    a.plot([0.46, 0.46], [0.18, 0.03], color=GRID, lw=1.0); a.plot([0.30, 0.62], [0.03, 0.03], color=GRID, lw=1.0)


def gas_engine(a):
    a.add_patch(Rectangle((0.44, 0.58), 0.10, 0.32, fc="#8a8a8a", ec=GRID, lw=0.7))
    for k, y in enumerate((0.93, 0.98)):
        a.add_patch(Circle((0.49 + 0.05 * k, y), 0.035 + 0.01 * k, fc="#d0d0d0", ec="none"))
    a.add_patch(FancyBboxPatch((0.06, 0.16), 0.52, 0.42, boxstyle="round,pad=0.0,rounding_size=0.05", fc="#f3d2bf", ec=ORANGE, lw=0.9))
    for x in (0.16, 0.30, 0.44):
        a.add_patch(Rectangle((x, 0.48), 0.08, 0.16, fc=ORANGE, ec="none"))
    a.add_patch(Polygon([(0.24, 0.24), (0.32, 0.40), (0.40, 0.24)], closed=True, fc="#e8833a", ec="none"))
    a.plot([0.58, 0.66], [0.37, 0.37], color=GRID, lw=1.2)
    a.add_patch(Circle((0.80, 0.37), 0.15, fc="white", ec=BLUE, lw=1.0))
    t = np.linspace(-1, 1, 40); a.plot(0.80 + 0.09 * t, 0.37 + 0.05 * np.sin(np.pi * t), color=BLUE, lw=0.9)
    a.plot([0.06, 0.94], [0.12, 0.12], color=GRID, lw=0.8)


def battery(a):
    a.add_patch(FancyBboxPatch((0.08, 0.20), 0.74, 0.52, boxstyle="round,pad=0.0,rounding_size=0.06", fc="white", ec=BLUE, lw=1.2))
    a.add_patch(Rectangle((0.82, 0.36), 0.07, 0.20, fc=BLUE, ec="none"))
    for k, c in enumerate(("#2e8b57", "#2e8b57", "#7fc49a")):
        a.add_patch(Rectangle((0.14 + 0.215 * k, 0.27), 0.18, 0.38, fc=c, ec="none"))
    a.text(0.45, 0.80, "+  −", ha="center", va="bottom", fontsize=5.5, color=BLUE, fontweight="bold")


def absorption(a):
    a.add_patch(FancyBboxPatch((0.06, 0.24), 0.88, 0.46, boxstyle="round,pad=0.0,rounding_size=0.22", fc="#dff1f7", ec=TEAL, lw=1.0))
    a.plot([0.5, 0.5], [0.26, 0.68], color=TEAL, lw=0.6, ls=(0, (2, 1.5)))
    t = np.linspace(0, 1, 50)
    for k in range(3):
        a.plot(0.16 + 0.08 * k + 0.025 * np.sin(2 * np.pi * 2 * t), 0.32 + 0.30 * t, color=RED, lw=0.9)
    _snow(a, 0.72, 0.47, 0.13)
    a.plot([0.2, 0.2], [0.24, 0.10], color=GRID, lw=0.9); a.plot([0.8, 0.8], [0.24, 0.10], color=GRID, lw=0.9)
    a.plot([0.1, 0.9], [0.10, 0.10], color=GRID, lw=0.9)


def chiller(a):
    a.add_patch(FancyBboxPatch((0.06, 0.14), 0.88, 0.66, boxstyle="round,pad=0.0,rounding_size=0.05", fc="#dff1f7", ec=TEAL, lw=1.0))
    a.add_patch(Circle((0.33, 0.47), 0.20, fc="white", ec=TEAL, lw=0.9))
    for k in range(3):
        a.add_patch(Wedge((0.33, 0.47), 0.17, 120 * k + 10, 120 * k + 60, fc=TEAL, ec="none", alpha=0.85))
    a.add_patch(Circle((0.33, 0.47), 0.03, fc=INK, ec="none"))
    _snow(a, 0.73, 0.47, 0.13)
    for y in (0.24, 0.70):
        a.plot([0.60, 0.88], [y, y], color=TEAL, lw=0.5)


def tes(a):
    a.add_patch(Rectangle((0.28, 0.12), 0.44, 0.72, fc="white", ec="none"))
    a.add_patch(Rectangle((0.28, 0.12), 0.44, 0.42, fc="#9fd3e6", ec="none"))
    a.add_patch(Ellipse((0.5, 0.12), 0.44, 0.12, fc="#9fd3e6", ec=TEAL, lw=1.0))
    a.add_patch(Ellipse((0.5, 0.54), 0.44, 0.10, fc="#c5e6f1", ec=TEAL, lw=0.5))
    a.plot([0.28, 0.28], [0.12, 0.84], color=TEAL, lw=1.0); a.plot([0.72, 0.72], [0.12, 0.84], color=TEAL, lw=1.0)
    a.add_patch(Ellipse((0.5, 0.84), 0.44, 0.12, fc="#eef8fb", ec=TEAL, lw=1.0))
    _snow(a, 0.5, 0.33, 0.10, color="white", lw=1.1)


def rack(a, fc="#efeaf8", ec=PURPLE, led="#2e8b57", n=5):
    a.add_patch(FancyBboxPatch((0.24, 0.04), 0.52, 0.92, boxstyle="round,pad=0.0,rounding_size=0.04", fc=fc, ec=ec, lw=1.0))
    h = 0.84 / n
    for k in range(n):
        y = 0.08 + k * h
        a.add_patch(Rectangle((0.30, y + 0.02), 0.40, h - 0.05, fc="white", ec=ec, lw=0.5))
        a.add_patch(Circle((0.36, y + h / 2 - 0.005), 0.018, fc=led, ec="none"))
        a.plot([0.42, 0.64], [y + h / 2 - 0.005] * 2, color=ec, lw=0.5)


def monitor(a, color=GOLD):
    a.add_patch(FancyBboxPatch((0.08, 0.30), 0.84, 0.58, boxstyle="round,pad=0.0,rounding_size=0.04", fc="white", ec=INK, lw=1.0))
    x = np.linspace(0.16, 0.84, 30); y = 0.62 + 0.10 * np.sin(5 * x) - 0.12 * ((x > 0.42) & (x < 0.62))
    a.plot(x, y, color=color, lw=1.1)
    a.plot([0.5, 0.5], [0.30, 0.16], color=INK, lw=1.0); a.plot([0.30, 0.70], [0.14, 0.14], color=INK, lw=1.2)


def calendar(a, color=PURPLE):
    a.add_patch(FancyBboxPatch((0.10, 0.08), 0.80, 0.76, boxstyle="round,pad=0.0,rounding_size=0.05", fc="white", ec=color, lw=1.0))
    a.add_patch(Rectangle((0.10, 0.66), 0.80, 0.18, fc=color, ec="none"))
    for x in (0.30, 0.70):
        a.plot([x, x], [0.78, 0.94], color=INK, lw=1.4, solid_capstyle="round")
    for i in range(3):
        for j in range(4):
            on = (i, j) in ((1, 2), (2, 1))
            a.add_patch(Rectangle((0.18 + 0.17 * j, 0.16 + 0.15 * i), 0.11, 0.10, fc=color if on else "#d9d0ec", ec="none"))


def cycle(a, color=PURPLE):
    t = np.linspace(0.25 * np.pi, 1.95 * np.pi, 60)
    a.plot(0.5 + 0.36 * np.cos(t), 0.5 + 0.36 * np.sin(t), color=color, lw=1.4)
    e = t[-1]; tip = (0.5 + 0.36 * np.cos(e), 0.5 + 0.36 * np.sin(e))
    a.add_patch(Polygon([(tip[0] - 0.10, tip[1] - 0.02), (tip[0] + 0.06, tip[1] + 0.10), (tip[0] + 0.07, tip[1] - 0.10)], closed=True, fc=color, ec="none"))
    a.plot([0.5, 0.5], [0.5, 0.74], color=INK, lw=1.1); a.plot([0.5, 0.66], [0.5, 0.42], color=INK, lw=1.1)
    a.add_patch(Circle((0.5, 0.5), 0.03, fc=INK, ec="none"))


KINDS = {"grid": pylon, "pv": pv, "gas": gas_engine, "bess": battery, "absorption": absorption, "chiller": chiller, "tes": tes,
         "rack": rack, "monitor": monitor, "calendar": calendar, "cycle": cycle}


def icon(fig, ax, rect, kind, **kw):
    a = _inset(fig, ax, rect)
    KINDS[kind](a, **kw)
    return a
