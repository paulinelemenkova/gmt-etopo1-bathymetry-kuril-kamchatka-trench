#!/usr/bin/env python3
"""
fig03_data_distribution -- distribution of the geodetic / gravimetric /
seismological sample of the WAEP. Four panels:
  (a) GNSS + InSAR coverage and seismicity across the province (spatial);
  (b) velocity-magnitude histogram (GNSS vs InSAR);
  (c) earthquake depth-magnitude bivariate histogram;
  (d) training-sample count per 0.5-deg spatial cross-validation block.
House style applied via mpl_style; overlap of every legend / tag verified
against the data in pixel space (must be zero hits).
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.text import Text
from matplotlib.ticker import AutoMinorLocator
from mpl_style import set_rc, apply_style, palette, legend_in_gap, finalize, HALO

set_rc()
C = palette(3)                       # tab10: 0 blue, 1 orange, 2 green
BLUE, ORANGE, GREEN = C[0], C[1], C[2]

gnss = pd.read_csv("gnss.csv")
insar = pd.read_csv("insar.csv")
eq = pd.read_csv("eq.csv")
per_block = pd.read_csv("per_block.csv")["n"].to_numpy()

LON0, LON1, LAT0, LAT1 = 26.0, 31.0, 36.0, 40.5

fig = plt.figure(figsize=(6.9, 5.5), constrained_layout=True)
gs = fig.add_gridspec(2, 2)
axA = fig.add_subplot(gs[0, 0])
axB = fig.add_subplot(gs[0, 1])
axC = fig.add_subplot(gs[1, 0])
axD = fig.add_subplot(gs[1, 1])

# ---------------------------------------------------------------- (a) coverage
# InSAR pixels (faint), GNSS sites (triangles), epicentres (circles).
axA.scatter(insar.lon, insar.lat, s=1.0, c="0.62", alpha=0.20,
            edgecolor="none", rasterized=True, label="InSAR pixels")
axA.scatter(eq.lon, eq.lat, s=4.0, color=GREEN, alpha=0.35,
            edgecolor="none", rasterized=True, label="earthquakes")
axA.scatter(gnss.lon, gnss.lat, s=20, marker="^", facecolor=ORANGE,
            edgecolor="0.15", linewidth=0.4, label="GNSS sites", zorder=5)
axA.set_xlim(LON0, LON1)
axA.set_ylim(LAT0, LAT1)
axA.set_aspect(1.0 / np.cos(np.deg2rad(0.5 * (LAT0 + LAT1))))
apply_style(axA, xlabel="Longitude (\u00b0E)", ylabel="Latitude (\u00b0N)")
legA = axA.legend(loc="lower right", bbox_to_anchor=(1.0, 1.01), ncol=1,
                  labelspacing=0.25, markerscale=1.3, handletextpad=0.3,
                  borderpad=0.3, frameon=False, fontsize=7.0)

# ------------------------------------------------------ (b) velocity-magnitude
vmax = 34
bins = np.linspace(0, vmax, 28)
axB.hist(insar.v_mag_mm_yr.clip(0, vmax), bins=bins, density=True,
         histtype="stepfilled", color=BLUE, alpha=0.40, label="InSAR")
axB.hist(insar.v_mag_mm_yr.clip(0, vmax), bins=bins, density=True,
         histtype="step", color=BLUE, lw=1.4, ls="-")
axB.hist(gnss.v_mag_mm_yr.clip(0, vmax), bins=bins, density=True,
         histtype="stepfilled", color=ORANGE, alpha=0.40, label="GNSS")
axB.hist(gnss.v_mag_mm_yr.clip(0, vmax), bins=bins, density=True,
         histtype="step", color=ORANGE, lw=1.4, ls="--")
axB.set_xlim(0, vmax)
apply_style(axB, xlabel="Velocity magnitude (mm yr$^{-1}$)",
            ylabel="Probability density")
legB = legend_in_gap(axB, labelspacing=0.25, handletextpad=0.5)

# ------------------------------------------------- (c) depth-magnitude 2D hist
hb = axC.hexbin(eq.depth_km, eq.mag, gridsize=24, cmap="viridis",
                mincnt=1, linewidths=0.15, edgecolors="0.85")
axC.set_xlim(0, 26)
axC.set_ylim(1.8, 7.2)
apply_style(axC, xlabel="Focal depth (km)", ylabel="Magnitude $M$")
cb = fig.colorbar(hb, ax=axC, fraction=0.046, pad=0.02)
cb.set_label("Earthquake count", labelpad=2)
cb.ax.tick_params(which="both", direction="in", length=3)
cb.ax.yaxis.set_minor_locator(AutoMinorLocator())

# ------------------------------------------------------- (d) samples per block
bmax = int(np.ceil(per_block.max() / 20) * 20)
axD.hist(per_block, bins=np.linspace(0, bmax, 18), color=GREEN, alpha=0.55,
         edgecolor="0.15", linewidth=0.5)
med = np.median(per_block)
axD.axvline(med, color="0.15", lw=1.1, ls=":")
axD.set_xlim(0, bmax)
apply_style(axD, xlabel="Samples per 0.5\u00b0 CV block",
            ylabel="Number of blocks")
# annotate median in blank upper area, arrow to the line
ymax = axD.get_ylim()[1]
axD.annotate(f"median = {med:.0f}", xy=(med, ymax * 0.55),
             xytext=(med + 0.30 * bmax, ymax * 0.78),
             arrowprops=dict(arrowstyle="->", lw=0.8, color="0.15"),
             fontsize=7.5, ha="left", va="center")

# ----------------------------------------------------------- panel tags (a-d)
# Placed just OUTSIDE each axes' top-left corner so they never cover data.
for ax, tag in [(axA, "(a)"), (axB, "(b)"), (axC, "(c)"), (axD, "(d)")]:
    ax.text(0.0, 1.02, tag, transform=ax.transAxes, fontsize=9.5,
            fontweight="bold", ha="left", va="bottom")

# ------------------------------------------------- overlap verification (rule 7)
fig.canvas.draw()
r = fig.canvas.get_renderer()


def _data_pts(ax):
    chunks = []
    for col in ax.collections:
        off = col.get_offsets()
        if len(off):
            chunks.append(ax.transData.transform(np.asarray(off)))
    for pch in ax.patches:
        vs = pch.get_path().transformed(pch.get_patch_transform()).vertices
        if len(vs):
            chunks.append(ax.transData.transform(vs))
    return np.vstack(chunks) if chunks else np.empty((0, 2))


def covers(bb, ax):
    P = _data_pts(ax)
    if len(P) == 0:
        return 0
    return int(((P[:, 0] >= bb.x0) & (P[:, 0] <= bb.x1) &
                (P[:, 1] >= bb.y0) & (P[:, 1] <= bb.y1)).sum())


report = []
for name, leg, ax in [("legA", legA, axA), ("legB", legB, axB)]:
    if leg is not None:
        report.append((name, covers(leg.get_window_extent(r), ax)))
# annotation text box in (d)
for t in axD.texts:
    if t.get_text().startswith("median"):
        report.append(("annD", covers(Text.get_window_extent(t, renderer=r), axD)))
print("overlap hit counts (must be 0):", report)

# verify the (a) panel tag does not overlap the coverage legend box
tagA = [t for t in axA.texts if t.get_text() == "(a)"][0]
tb = Text.get_window_extent(tagA, renderer=r)
lb = legA.get_window_extent(r)
sep = lb.x0 - tb.x1          # horizontal gap (px) between tag right and legend left
print(f"tag(a)->legend gap: {sep:.1f}px  (must be > 0)")

finalize(fig, "fig03_data_distribution", dpi=600, outdir="figures")
print("saved figures/fig03_data_distribution.{pdf,png}")
