#!/usr/bin/env python3
"""Fig. 5 - ML model architecture and feature set (schematic; no data plotted)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 8.2,
    "pdf.fonttype": 42, "ps.fonttype": 42,
})

FIG_W, FIG_H = 6.9, 3.7
fig = plt.figure(figsize=(FIG_W, FIG_H))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis("off")

# Colour-blind- and grayscale-safe palette (lightness-ordered).
C_IN   = dict(fill="#d4e6f4", edge="#2c5f8a")   # inputs  - blue
C_GBT  = dict(fill="#f7e2cb", edge="#b5651d")   # primary model - orange
C_BASE = dict(fill="#e7e7ea", edge="#6b6b73")   # baselines - grey
C_OUT  = dict(fill="#e4dcef", edge="#6a4a9c")   # outputs - purple
TXT = "#1a1a2e"

def box(x, y, w, h, c, text, fs=7.4, bold=False, ls="-", alpha=0.96, fc=None):
    p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=1.6",
                       linewidth=1.1, edgecolor=c["edge"], linestyle=ls,
                       facecolor=(fc if fc else "white"), alpha=alpha, zorder=2)
    ax.add_patch(p)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
            color=(c["edge"] if bold else TXT),
            fontweight=("bold" if bold else "normal"), zorder=3, linespacing=1.15)
    return (x, y, w, h)

def container(x, y, w, h, c, title):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                 boxstyle="round,pad=0.6,rounding_size=2.2",
                 linewidth=1.4, edgecolor=c["edge"], facecolor=c["fill"],
                 alpha=0.5, zorder=1))
    ax.text(x + w / 2, y + h - 4.0, title, ha="center", va="center",
            fontsize=8.6, fontweight="bold", color=c["edge"], zorder=3)

def arrow(p1, p2, color="#555555", lw=1.6, ls="-", rad=0.0, z=2, ms=10):
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle="-|>", mutation_scale=ms,
                 linewidth=lw, color=color, linestyle=ls,
                 connectionstyle=f"arc3,rad={rad}", zorder=z, shrinkA=0, shrinkB=0))

def right(b): x, y, w, h = b; return (x + w, y + h / 2)
def left(b):  x, y, w, h = b; return (x, y + h / 2)
def top(b):   x, y, w, h = b; return (x + w / 2, y + h)
def bot(b):   x, y, w, h = b; return (x + w / 2, y)

# ===================== Stage 1: input feature vector =====================
x1, w1 = 1.5, 20.0
container(x1, 4, w1, 92, C_IN, "Input features")
feats = [
    "Longitude, latitude",
    "$v_e$, $v_n$  velocity",
    "Focal depth",
    "log$_{10}$ elevation",
    "Gravity disturbance $\\delta g$",
][::-1]   # stacked bottom-up, so reverse to read position-first at the top
fy0, fh, fgap = 11, 11.6, 3.0
fboxes = []
for k, t in enumerate(feats):
    yy = fy0 + k * (fh + fgap)
    fboxes.append(box(x1 + 2.0, yy, w1 - 4.0, fh, C_IN, t, fs=7.0))
fmid = (x1 + w1, fy0 + (len(feats) * (fh + fgap) - fgap) / 2)  # right-edge mid point

# ===================== Stage 2: models =====================
x2, w2 = 31.0, 34.0
# --- primary: gradient-boosted ensemble (top) ---
container(x2, 40, w2, 56, C_GBT, "Gradient-boosted ensemble")
# sequential trees fitted to pseudo-residuals (left -> right)
tw, th = 5.8, 13.0
ty = 50
trees = []
labels = ["Tree 1", "Tree 2", r"$\cdots$", "Tree $M$"]
tx0 = x2 + 2.5
tgap = (w2 - 5.0 - 4 * tw) / 3.0
for k, lb in enumerate(labels):
    xx = tx0 + k * (tw + tgap)
    trees.append(box(xx, ty, tw, th, C_GBT, lb, fs=7.0))
# residual-passing arrows between successive trees
for k in range(3):
    arrow(right(trees[k]), left(trees[k + 1]), color="#b5651d", lw=1.3, ms=8)
# additive-update note under the trees (in empty space, no overlap)
ax.text(x2 + w2 / 2, 44.0,
        r"each tree fits pseudo-residuals; added with shrinkage $\eta$, $L_2$ reg. $\lambda$",
        ha="center", va="center", fontsize=6.7, style="italic", color="#7a4a12")
# summation node (additive combination of the trees) to the right of the ensemble
sx = x2 + w2 + 4.0
sy = ty + th / 2
ax.add_patch(plt.Circle((sx, sy), 2.6, facecolor="white",
             edgecolor=C_GBT["edge"], linewidth=1.3, zorder=3))
ax.text(sx, sy, r"$\Sigma$", ha="center", va="center", fontsize=11,
        color=C_GBT["edge"], zorder=4)
# single arrow from the last tree to the summation node
arrow(right(trees[-1]), (sx - 2.6, sy), color="#b5651d", lw=1.4, ms=9)

# --- baselines (bottom) ---
container(x2, 6, w2, 28, C_BASE, "Baseline regressors")
bw = (w2 - 4.0 - 4.0) / 2.0
rf = box(x2 + 2.0, 11, bw, 13, C_BASE, "Random forest", fs=7.3)
svr = box(x2 + 2.0 + bw + 4.0, 11, bw, 13, C_BASE, "Support-vector\nregressor", fs=7.3)

# inputs -> primary ensemble and -> baselines (shared feature vector)
arrow((fmid[0], fmid[1]), (x2, sy), color="#2c5f8a", lw=1.9, rad=0.04)
arrow((fmid[0], fmid[1]), (x2, 20), color="#2c5f8a", lw=1.5, ls="--", rad=-0.10)
ax.text(28.6, 34.5, "shared\nfeatures", ha="center", va="center",
        fontsize=6.6, color="#2c5f8a", style="italic")

# ===================== Stage 3: per-target outputs =====================
x3, w3 = 78.5, 20.0
container(x3, 4, w3, 92, C_OUT, "Target fields")
outs = [
    "Strain-rate\ninvariant $\\dot{\\varepsilon}_{\\mathrm{II}}$",
    "Gravity\ngradient",
    "Seismicity\ndensity",
][::-1]   # stacked bottom-up, so reverse to read strain-rate-first at the top
oy0, oh, ogap = 13, 21.0, 5.0
oboxes = []
for k, t in enumerate(outs):
    yy = oy0 + k * (oh + ogap)
    oboxes.append(box(x3 + 2.0, yy, w3 - 4.0, oh, C_OUT, t, fs=7.4))
omid = oy0 + (len(outs) * (oh + ogap) - ogap) / 2

# ensemble summation -> each target (one ensemble trained per target field)
for ob in oboxes:
    arrow((sx + 2.6, sy), left(ob), color="#6a4a9c", lw=1.4,
          rad=(left(ob)[1] - sy) / 200.0, ms=9)
# note: separate ensemble per target
ax.text((sx + 2.6 + x3) / 2, 90.5, "one ensemble\nper target field",
        ha="center", va="center", fontsize=6.6, style="italic", color="#6a4a9c")

fig.savefig("figures/fig05_ml_architecture.pdf", bbox_inches="tight", pad_inches=0.02)
fig.savefig("figures/fig05_ml_architecture.png", bbox_inches="tight",
            pad_inches=0.02, dpi=600)
print("saved figures/fig05_ml_architecture.pdf and .png")
