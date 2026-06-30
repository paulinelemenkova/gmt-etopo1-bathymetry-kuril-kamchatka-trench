#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fig08_strainrate_field.py
=========================
Predicted strain-rate field (second invariant of the strain-rate tensor) over the
Western Anatolian Extensional Province (WAEP), with the graben-bounding active
faults and GNSS sites overlaid. Warm `lajolla` colours denote elevated extension.

The model-predicted field is synthesised to honour the magnitudes stated in the
paper -- 70-90 nstrain/yr along the Buyuk Menderes and Gediz grabens, <15-20 on
the intervening horst blocks -- then scattered, block-averaged and re-gridded with
`pygmt.surface` exactly as in Listing lst:pygmt. Replace the synthetic `field`
block (sections 2-3) with your real model predictions before submission.

Backend  : PyGMT 0.18.0 (GMT 6.6.0)
Colormap : scientific colour map `lajolla` (reversed: pale = low, deep warm = high)
Outputs  : fig08_strainrate_field.pdf  (vector, for LaTeX)
           fig08_strainrate_field.png  (600 dpi preview)

Note on the runtime: GMT/PyGMT need the GMT C library. In a minimal container the
bare `libgmt.so` symlink may be missing even though `libgmt.so.6` is present; the
small block below creates the symlink and points PyGMT at it. On a normal GMT
install (e.g. conda-forge `pygmt`) that block is harmless and can be removed.
"""

import os
import subprocess
import sys

# --- make sure the GMT shared library is discoverable (see module docstring) ----
try:
    import pygmt  # noqa: F401
except Exception:
    subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", "pygmt"],
                   check=False)
for _libdir in ("/usr/lib64", "/usr/lib/x86_64-linux-gnu", "/usr/lib"):
    _so6 = os.path.join(_libdir, "libgmt.so.6")
    if os.path.exists(_so6):
        if not os.path.exists(os.path.join(_libdir, "libgmt.so")):
            subprocess.run(["ln", "-sf", _so6, os.path.join(_libdir, "libgmt.so")],
                           check=False)
        os.environ.setdefault("GMT_LIBRARY_PATH", _libdir)
        break

import numpy as np
import pandas as pd
import pygmt

rng = np.random.default_rng(42)              # reproducible synthetic field
REGION = [26.0, 31.0, 36.0, 40.5]            # WAEP bounding box (degrees)

# ===========================================================================
# 1. Graben axes (lon, lat poly-lines) -- realistic Western Anatolian geometry
# ===========================================================================
gediz   = np.array([(27.40, 38.62), (27.85, 38.55), (28.14, 38.48),
                    (28.52, 38.36), (28.75, 38.27), (29.00, 38.20)])
bmend   = np.array([(27.25, 37.72), (27.60, 37.78), (27.95, 37.84),
                    (28.32, 37.88), (28.70, 37.86), (29.05, 37.82),
                    (29.25, 37.78)])
kmend   = np.array([(27.25, 38.02), (27.65, 38.06), (28.00, 38.10),
                    (28.30, 38.12)])
simav   = np.array([(28.55, 39.18), (28.95, 39.12), (29.35, 39.06),
                    (29.75, 39.00)])
denizli = np.array([(28.95, 37.80), (29.20, 37.74), (29.45, 37.69)])
acigol  = np.array([(29.62, 37.94), (29.92, 37.89)])
civril  = np.array([(29.50, 38.26), (29.80, 38.31)])

# (axis, peak strain [nstrain/yr], cross-graben half-width [deg])
GRABENS = [(gediz, 88., 0.110), (bmend, 90., 0.110), (kmend, 46., 0.090),
           (simav, 52., 0.100), (denizli, 50., 0.085), (acigol, 42., 0.075),
           (civril, 38., 0.075)]


def dist_to_polyline(lon, lat, poly):
    """Vectorised planar (deg, lon scaled by cos lat) distance to a poly-line."""
    P = np.stack([lon.ravel(), lat.ravel()], axis=1)
    best = np.full(P.shape[0], np.inf)
    coslat = np.cos(np.deg2rad(P[:, 1]))
    sx = np.column_stack([coslat, np.ones_like(coslat)])
    cm = coslat.mean()
    for a, b in zip(poly[:-1], poly[1:]):
        a = np.asarray(a, float)
        b = np.asarray(b, float)
        ab = b - a
        ap = P - a
        denom = ((ab * np.array([cm, 1.0])) ** 2).sum() + 1e-12
        t = np.clip(((ap * sx) @ (ab * np.array([cm, 1.0]))) / denom, 0, 1)
        proj = a + t[:, None] * ab
        d = np.sqrt(((P - proj) * sx) ** 2 @ np.ones(2))
        best = np.minimum(best, d)
    return best.reshape(lon.shape)


# ===========================================================================
# 2. Analytic strain-rate field on a fine grid (replace with real predictions)
# ===========================================================================
gx = np.arange(REGION[0], REGION[1] + 1e-9, 0.04)
gy = np.arange(REGION[2], REGION[3] + 1e-9, 0.04)
LON, LAT = np.meshgrid(gx, gy)

# south-west-increasing regional background (toward the Hellenic front)
sw = ((31.0 - LON) / 5.0 + (40.5 - LAT) / 4.5) / 2.0
field = 5.0 + 8.0 * sw

# smooth long-wavelength undulation for a natural, model-like texture
for _ in range(6):
    kx, ky = rng.uniform(0.6, 1.8, 2)
    px, py = rng.uniform(0, 2 * np.pi, 2)
    field += 2.2 * np.cos(kx * (LON - 28) + px) * np.cos(ky * (LAT - 38) + py)

# graben strain ridges
for poly, peak, w in GRABENS:
    field += peak * np.exp(-(dist_to_polyline(LON, LAT, poly) / w) ** 2)

field = np.clip(field, 3.0, 96.0)

# ===========================================================================
# 3. Scatter model "predictions", block-average, then re-grid (lst:pygmt)
# ===========================================================================
n = 1600
slon = rng.uniform(REGION[0], REGION[1], n)
slat = rng.uniform(REGION[2], REGION[3], n)
ix = np.clip(((slon - REGION[0]) / 0.04).astype(int), 0, len(gx) - 1)
iy = np.clip(((slat - REGION[2]) / 0.04).astype(int), 0, len(gy) - 1)
sval = np.clip(field[iy, ix] + rng.normal(0, 2.0, n), 1.0, None)

tbl = pygmt.blockmean(data=pd.DataFrame({"x": slon, "y": slat, "z": sval}),
                      region=REGION, spacing=0.06)
grid = pygmt.surface(data=tbl, region=REGION, spacing=0.02, tension=0.40)

# ===========================================================================
# 4. Active graben-bounding normal faults (offset to each graben margin)
# ===========================================================================
def margin(poly, dlat):
    p = poly.copy().astype(float)
    p[:, 1] += dlat
    return p


faults = []
for poly in (gediz, bmend, kmend, simav):
    faults.append(margin(poly, +0.075))   # northern (antithetic) margin
    faults.append(margin(poly, -0.075))   # southern (main) bounding fault
faults.append(margin(denizli, -0.05))
faults.append(margin(acigol, -0.04))
# Izmir-Balikesir transfer zone (NE-trending, right-lateral) in the NW
faults.append(np.array([(26.95, 38.45), (27.25, 38.75),
                        (27.55, 39.05), (27.80, 39.35)]))

# ===========================================================================
# 5. GNSS sites (denser over the deforming grabens)
# ===========================================================================
bg_lon = rng.uniform(REGION[0] + 0.2, REGION[1] - 0.2, 26)
bg_lat = rng.uniform(REGION[2] + 0.2, REGION[3] - 0.2, 26)
near_lon, near_lat = [], []
for poly, *_ in GRABENS[:4]:
    k = 6
    idx = rng.integers(0, len(poly) - 1, k)
    t = rng.uniform(0, 1, k)
    seg = poly[idx] + (poly[idx + 1] - poly[idx]) * t[:, None]
    near_lon += list(seg[:, 0] + rng.normal(0, 0.05, k))
    near_lat += list(seg[:, 1] + rng.normal(0, 0.08, k))
gnss_lon = np.concatenate([bg_lon, near_lon])
gnss_lat = np.concatenate([bg_lat, near_lat])
m = ((gnss_lon > REGION[0] + 0.1) & (gnss_lon < REGION[1] - 0.1) &
     (gnss_lat > REGION[2] + 0.1) & (gnss_lat < REGION[3] - 0.1))
gnss_lon, gnss_lat = gnss_lon[m], gnss_lat[m]

# ===========================================================================
# 6. Render
# ===========================================================================
pygmt.config(FONT_ANNOT_PRIMARY="9p,Helvetica,black",
             FONT_LABEL="10p,Helvetica,black",
             MAP_FRAME_TYPE="plain", MAP_FRAME_PEN="0.8p",
             MAP_TICK_LENGTH_PRIMARY="3p",
             MAP_GRID_PEN_PRIMARY="0.2p,gray70,.")

fig = pygmt.Figure()

# warm scientific colour map; reversed so low = pale, elevated = deep warm
pygmt.makecpt(cmap="lajolla", series=[0, 95, 1], continuous=True, reverse=True)

fig.grdimage(grid=grid, region=REGION, projection="M14c",
             frame=["xa1f0.5", "ya1f0.5", "WSne"])
# light graticule (major+minor reference)
fig.basemap(region=REGION, projection="M14c", frame=["xa1f0.5g1", "ya1f0.5g1"])

# 40 nstrain/yr reference contour (referenced in Section sec:relation)
fig.grdcontour(grid=grid, levels=[40], pen="0.8p,gray20,--")

fig.coast(shorelines="1/0.6p,black", borders="1/0.7p,gray30,-",
          water="159/206/233", resolution="h")

# cased faults: white casing first, black core on top -> visible on pale AND dark
for fl in faults:
    fig.plot(x=fl[:, 0], y=fl[:, 1], pen="2.2p,white")
for fl in faults:
    fig.plot(x=fl[:, 0], y=fl[:, 1], pen="1.0p,black")

# GNSS sites: white inverted triangles with black edge
fig.plot(x=gnss_lon, y=gnss_lat, style="i0.22c", fill="white", pen="0.6p,black")

# graben labels (white halo so they read over the warm field); \374 = u-umlaut
labels = [(28.05, 38.50, "Gediz graben", 0),
          (28.20, 37.66, "B\\374y\\374k Menderes graben", 0),
          (27.48, 38.18, "K. Menderes", 0),
          (29.05, 39.22, "Simav graben", 0),
          (29.32, 37.62, "Denizli", 0),
          (26.98, 39.18, "Izmir-Balikesir TZ", 58)]
for lo, la, tx, ang in labels:
    fig.text(x=lo, y=la, text=tx, font="8.5p,Helvetica-Bold,black",
             angle=ang, fill="white@20", clearance="8%/26%+tO")

# annotate the 40 nstrain/yr contour in a low-strain area
fig.text(x=26.52, y=36.92, text="40 nstrain yr@+-1@+ contour",
         font="7.5p,Helvetica-Oblique,gray20", fill="white@20",
         clearance="8%/26%+tO", justify="LM")

# legend (GNSS / fault) in the empty SE low-strain corner
fig.plot(x=[30.28], y=[36.32], style="i0.22c", fill="white", pen="0.6p,black")
fig.text(x=30.40, y=36.32, text="GNSS site", font="8p,Helvetica,black",
         justify="LM", fill="white@20", clearance="8%/26%+tO")
fig.plot(x=[30.14, 30.40], y=[36.15, 36.15], pen="2.2p,white")
fig.plot(x=[30.14, 30.40], y=[36.15, 36.15], pen="1.0p,black")
fig.text(x=30.44, y=36.15, text="active fault", font="8p,Helvetica,black",
         justify="LM", fill="white@20", clearance="8%/26%+tO")

# scale bar (at the map's own latitude) + compass rose, in empty sea corners
fig.basemap(map_scale="jBL+w50k+o0.5c/0.6c+c38.2+f+lkm",
            box="+gwhite@30+p0.4p,gray40")
fig.basemap(rose="jTL+w0.9c+o0.5c/0.5c+f2+l,,,N")

fig.colorbar(cmap=True,
             frame=["xa20f10+lPredicted strain rate "
                    "@~e@~@-II@- (nstrain yr@+-1@+)"],
             position="JBC+w11c/0.35c+o0c/0.9c+h")

fig.savefig("fig08_strainrate_field.pdf")
fig.savefig("fig08_strainrate_field.png", dpi=600)
print("saved fig08_strainrate_field.{pdf,png} | grid range nstrain/yr:",
      round(float(np.nanmin(grid.values)), 1),
      round(float(np.nanmax(grid.values)), 1),
      "| n GNSS:", gnss_lon.size)
