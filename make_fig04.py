#!/usr/bin/env python3
"""Fig. 4 - methodological workflow (schematic; no data plotted)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 8.2,
    "pdf.fonttype": 42, "ps.fonttype": 42,
})

# Double-column width ~17.5 cm.
FIG_W, FIG_H = 6.9, 3.55
fig = plt.figure(figsize=(FIG_W, FIG_H))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis("off")

# Colour-blind- and grayscale-safe stage palette (ordered by lightness).
STAGES = {
    "in":   dict(fill="#d4e6f4", edge="#2c5f8a"),   # inputs  - light blue
    "pre":  dict(fill="#d2ece5", edge="#2a7d6f"),   # preproc - light teal
    "ml":   dict(fill="#f7e2cb", edge="#b5651d"),   # ML      - light orange
    "out":  dict(fill="#e4dcef", edge="#6a4a9c"),   # output  - light purple
}
TXT = "#1a1a2e"

def container(x, y, w, h, key, title):
    c = STAGES[key]
    box = FancyBboxPatch((x, y), w, h,
                         boxstyle="round,pad=0.6,rounding_size=2.2",
                         linewidth=1.4, edgecolor=c["edge"],
                         facecolor=c["fill"], alpha=0.55, zorder=1)
    ax.add_patch(box)
    ax.text(x + w / 2, y + h - 4.2, title, ha="center", va="center",
            fontsize=8.8, fontweight="bold", color=c["edge"], zorder=3)
    return box

def item(x, y, w, h, key, text, fs=7.4, ls="-"):
    c = STAGES[key]
    box = FancyBboxPatch((x, y), w, h,
                         boxstyle="round,pad=0.4,rounding_size=1.4",
                         linewidth=1.0, edgecolor=c["edge"], linestyle=ls,
                         facecolor="white", alpha=0.96, zorder=2)
    ax.add_patch(box)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fs, color=TXT, zorder=3, linespacing=1.15)
    return (x, y, w, h)

def arrow(p1, p2, color="#444444", lw=1.7, ls="-", rad=0.0, zorder=2):
    a = FancyArrowPatch(p1, p2, arrowstyle="-|>", mutation_scale=11,
                        linewidth=lw, color=color, linestyle=ls,
                        connectionstyle=f"arc3,rad={rad}", zorder=zorder,
                        shrinkA=0, shrinkB=0)
    ax.add_patch(a)

# ---------------- Stage 1 : open-access data ----------------
x1, w1 = 1.5, 20.0
container(x1, 6, w1, 88, "in", "Open-access data")
inputs = [
    "GNSS velocities\n(stable Eurasia)",
    "Sentinel-1 InSAR\n(LiCSAR / LiCSBAS)",
    "EGM2008\ngravity field",
    "Earthquake catalogue\n+ GCMT tensors",
    "SRTM / GEBCO /\nALOS terrain",
]
iy0, ih, igap = 12, 12.6, 3.4
in_boxes = []
for k, t in enumerate(inputs):
    yy = iy0 + k * (ih + igap)
    in_boxes.append(item(x1 + 2.0, yy, w1 - 4.0, ih, "in", t, fs=7.0))

# ---------------- Stage 2 : preprocessing & features ----------------
x2, w2 = 27.0, 20.5
container(x2, 6, w2, 88, "pre", "Preprocessing & features")
pre = [
    "Merge & co-register\non 0.02$\\degree$ grid",
    "Quality control &\nGHS built-up masking",
    "Feature engineering\n(predictors + targets)",
]
py0, ph, pgap = 14, 18.5, 6.0
pre_boxes = []
for k, t in enumerate(reversed(pre)):
    yy = py0 + k * (ph + pgap)
    pre_boxes.append(item(x2 + 2.0, yy, w2 - 4.0, ph, "pre", t, fs=7.3))
pre_boxes = pre_boxes[::-1]   # top-to-bottom order

# ---------------- Stage 3 : machine learning ----------------
x3, w3 = 52.5, 21.0
container(x3, 6, w3, 88, "ml", "Machine learning")
ml = [
    "Spatially grouped split\n+ standardise",
    "Gradient-boosted ensemble\n(RF / SVR baselines)",
    "10-fold grouped\nCV tuning",
]
my0, mh, mgap = 14, 18.5, 6.0
ml_boxes = []
for k, t in enumerate(reversed(ml)):
    yy = my0 + k * (mh + mgap)
    ls = "--" if ml[::-1][k].startswith("10-fold") else "-"
    ml_boxes.append(item(x3 + 2.0, yy, w3 - 4.0, mh, "ml", t, fs=7.3, ls=ls))
ml_boxes = ml_boxes[::-1]   # [split, ensemble, cv]

# ---------------- Stage 4 : mapping & validation ----------------
x4, w4 = 78.5, 20.0
container(x4, 6, w4, 88, "out", "Mapping & validation")
out = [
    "Grid prediction\n(0.02$\\degree$ grid)",
    "GMT / PyGMT maps:\nstrain rate, gravity\ngradient, seismicity",
    "Validation:\n$R^2$, RMSE, MAE\n+ residuals",
]
oy0, oh, ogap = 13, 19.0, 5.5
out_boxes = []
for k, t in enumerate(reversed(out)):
    yy = oy0 + k * (oh + ogap)
    out_boxes.append(item(x4 + 2.0, yy, w4 - 4.0, oh, "out", t, fs=7.1))
out_boxes = out_boxes[::-1]

# ---------------- connectors ----------------
def right(b): x, y, w, h = b; return (x + w, y + h / 2)
def left(b):  x, y, w, h = b; return (x, y + h / 2)
def top(b):   x, y, w, h = b; return (x + w / 2, y + h)
def bot(b):   x, y, w, h = b; return (x + w / 2, y)

# inputs -> first preprocessing box (converge)
tgt = left(pre_boxes[0])
for b in in_boxes:
    p = right(b)
    arrow((p[0], p[1]), (tgt[0] - 0.3, tgt[1]), color="#2c5f8a", lw=1.0,
          rad=(tgt[1] - p[1]) / 240.0, zorder=1)

# preprocessing internal chain (top -> bottom)
arrow(bot(pre_boxes[0]), top(pre_boxes[1]), color="#2a7d6f", lw=1.4)
arrow(bot(pre_boxes[1]), top(pre_boxes[2]), color="#2a7d6f", lw=1.4)

# preprocessing -> ML (smooth curve from last box up to first box of next stage)
arrow(right(pre_boxes[2]), left(ml_boxes[0]), color="#555555", lw=1.9, rad=-0.18)

# ML internal chain
arrow(bot(ml_boxes[0]), top(ml_boxes[1]), color="#b5651d", lw=1.4)
# dashed CV feedback loop between ensemble (mid) and CV box (bottom)
arrow(bot(ml_boxes[1]), top(ml_boxes[2]), color="#b5651d", lw=1.3, ls="--")
arrow((right(ml_boxes[2])[0] - 1.5, ml_boxes[2][1] + ml_boxes[2][3] / 2),
      (right(ml_boxes[1])[0] - 1.5, ml_boxes[1][1] + 1.5),
      color="#b5651d", lw=1.3, ls="--", rad=-0.55)

# ML -> output (smooth curve)
arrow(right(ml_boxes[1]), left(out_boxes[0]), color="#555555", lw=1.9, rad=-0.18)

# output internal chain
arrow(bot(out_boxes[0]), top(out_boxes[1]), color="#6a4a9c", lw=1.4)
arrow(bot(out_boxes[1]), top(out_boxes[2]), color="#6a4a9c", lw=1.4)

# dashed-loop legend note (in empty space, bottom centre, over no boxes)
ax.text(63.0, 2.4, "dashed loop: cross-validated hyper-parameter tuning",
        ha="center", va="center", fontsize=6.8, style="italic", color="#444444")

fig.savefig("figures/fig04_workflow.pdf", bbox_inches="tight", pad_inches=0.02)
fig.savefig("figures/fig04_workflow.png", bbox_inches="tight", pad_inches=0.02, dpi=600)
print("saved figures/fig04_workflow.pdf and .png")
