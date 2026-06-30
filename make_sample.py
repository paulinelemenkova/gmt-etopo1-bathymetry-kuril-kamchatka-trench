#!/usr/bin/env python3
"""
make_sample.py -- build a REPRESENTATIVE, reproducible geodetic / gravimetric /
seismological sample for the Western Anatolian Extensional Province (WAEP),
used only to render the data-distribution diagnostic (fig03_data_distribution).

The spatial domain, motion sense (broadly N-S extension, ~20 mm/yr, increasing
toward the SW Aegean), crustal-earthquake depth range (<~25 km) and magnitude
range (up to ~7) follow the setting described in the paper. The numeric values
are ILLUSTRATIVE placeholders, not a real solution: swap in the real GNSS
velocity file, LiCSAR/LiCSBAS InSAR products and instrumental catalogue and
rerun. Everything is seeded for reproducibility.
"""
import numpy as np
import pandas as pd

RNG = np.random.default_rng(20260629)

# WAEP domain (deg) -- matches fig01/fig02 study area.
LON0, LON1, LAT0, LAT1 = 26.0, 31.0, 36.0, 40.5

# Principal grabens / fault corridors (approx. centre lon, lat, half-length deg,
# strike deg from E, relative seismic productivity). E-W normal-fault grabens
# plus the NE-trending Izmir-Balikesir transfer zone.
CORRIDORS = [
    ("Gediz (Alasehir)",      28.55, 38.55, 0.75,   5, 1.00),
    ("Buyuk Menderes",        28.30, 37.85, 0.85,  -2, 0.95),
    ("Kucuk Menderes",        27.70, 38.10, 0.45,   3, 0.55),
    ("Simav",                 28.95, 39.10, 0.60,  10, 0.70),
    ("Denizli/Acigol",        29.55, 37.85, 0.55, -10, 0.65),
    ("Izmir-Balikesir TZ",    27.40, 38.70, 0.70,  55, 0.80),  # NE-trending
    ("Gokova",                28.10, 37.05, 0.40,   0, 0.50),
]

# --- Built-up basin floors (Global-Human-Settlement-style mask) where InSAR is
#     discarded -> these become coverage GAPS in the sample. (lon, lat, radius). 
BUILT = [(28.52, 38.62, 0.10),   # Salihli/Alasehir basin floor (Gediz)
         (28.35, 37.86, 0.10),   # Aydin/Nazilli (B. Menderes)
         (27.14, 38.42, 0.13),   # Izmir metro
         (29.09, 37.78, 0.09)]   # Denizli


def _in_built(lon, lat):
    m = np.zeros(lon.shape, bool)
    for bx, by, br in BUILT:
        m |= ((lon - bx) ** 2 + (lat - by) ** 2) < br ** 2
    return m


def _in_sea_sw(lon, lat):
    # Deep SW Aegean-Sea corner: no land-based geodesy or shallow crustal
    # seismicity here, so the sample naturally thins toward it.
    return (lon < 26.95) & (lat < 37.6)


# ----------------------------------------------------------------------------
# 1) GNSS sites: sparse, stable-Eurasia frame. Broadly SSW motion, magnitude
#    growing toward the SW (Hellenic roll-back), 5-30 mm/yr.
# ----------------------------------------------------------------------------
n_gnss = 88
glon = RNG.uniform(LON0 + 0.1, LON1 - 0.1, n_gnss)
glat = RNG.uniform(LAT0 + 0.1, LAT1 - 0.1, n_gnss)
_land = ~_in_sea_sw(glon, glat)
glon, glat = glon[_land], glat[_land]
n_gnss = glon.size
# velocity magnitude increases to the SW; azimuth ~ SSW
f_sw = (LON1 - glon) / (LON1 - LON0) * 0.5 + (LAT1 - glat) / (LAT1 - LAT0) * 0.5
gv_mag = 6 + 22 * f_sw + RNG.normal(0, 1.6, n_gnss)
gv_mag = np.clip(gv_mag, 3, 32)
gaz = np.deg2rad(205 + RNG.normal(0, 12, n_gnss))   # ~SSW
gv_e = gv_mag * np.sin(gaz)
gv_n = gv_mag * np.cos(gaz)
gnss = pd.DataFrame(dict(lon=glon, lat=glat, v_east_mm_yr=gv_e,
                         v_north_mm_yr=gv_n, v_mag_mm_yr=gv_mag, kind="GNSS"))

# ----------------------------------------------------------------------------
# 2) InSAR pixels: dense LiCSAR/LiCSBAS-style sampling on ~0.04 deg grid, with
#    decomposed vertical + E-W velocities; built-up basin floors masked out.
# ----------------------------------------------------------------------------
step = 0.04
ilon, ilat = np.meshgrid(np.arange(LON0, LON1, step), np.arange(LAT0, LAT1, step))
ilon, ilat = ilon.ravel(), ilat.ravel()
# Drop ~30% at random (decorrelation / water / orbit edges) + built-up mask.
keep = (RNG.random(ilon.size) > 0.30) & ~_in_built(ilon, ilat)
# also drop the Aegean Sea SW corner (no land coverage)
keep &= ~_in_sea_sw(ilon, ilat)
ilon, ilat = ilon[keep], ilat[keep]
# LOS-derived magnitude: small far-field, localized highs along graben corridors
iv = np.full(ilon.shape, 0.0)
for _, cx, cy, hl, strike, prod in CORRIDORS:
    th = np.deg2rad(strike)
    dx, dy = ilon - cx, ilat - cy
    along = dx * np.cos(th) + dy * np.sin(th)
    across = -dx * np.sin(th) + dy * np.cos(th)
    band = np.exp(-(across / 0.10) ** 2) * np.exp(-(along / hl) ** 2)
    iv += prod * 9.0 * band
iv += np.abs(RNG.normal(0, 1.1, ilon.size)) + 1.0
insar = pd.DataFrame(dict(lon=ilon, lat=ilat, v_mag_mm_yr=iv, kind="InSAR"))

# ----------------------------------------------------------------------------
# 3) Earthquakes: instrumental catalogue, M2-7, crustal depths 3-25 km,
#    clustered on the graben corridors; Gutenberg-Richter-like magnitudes.
# ----------------------------------------------------------------------------
quakes = []
n_total = 1400
for _, cx, cy, hl, strike, prod in CORRIDORS:
    n = int(n_total * prod / sum(c[5] for c in CORRIDORS))
    th = np.deg2rad(strike)
    along = RNG.uniform(-hl, hl, n)
    across = RNG.normal(0, 0.05, n)
    qlon = cx + along * np.cos(th) - across * np.sin(th)
    qlat = cy + along * np.sin(th) + across * np.cos(th)
    # GR magnitudes: M = Mmin - log10(U)/b
    b = 1.0
    mag = 2.0 - np.log10(RNG.random(n)) / b
    mag = np.clip(mag, 2.0, 7.0)
    # shallow crustal extension: depth 3-22 km, deeper events slightly larger
    depth = np.clip(RNG.normal(9, 4, n) + (mag - 4) * 0.8, 2.5, 25)
    quakes.append(pd.DataFrame(dict(lon=qlon, lat=qlat, mag=mag,
                                    depth_km=depth)))
# add a few named large events (real, cited in the paper)
named = pd.DataFrame(dict(
    lon=[26.79, 29.62, 29.55, 28.50, 27.80],
    lat=[37.92, 37.92, 38.10, 38.55, 39.05],
    mag=[7.0,  5.8,  5.7,  6.9,  5.1],
    depth_km=[12, 9, 7, 10, 8]))
quakes.append(named)
eq = pd.concat(quakes, ignore_index=True)
eq = eq[(eq.lon.between(LON0, LON1)) & (eq.lat.between(LAT0, LAT1))]
eq = eq[~_in_sea_sw(eq.lon.to_numpy(), eq.lat.to_numpy())].reset_index(drop=True)

# ----------------------------------------------------------------------------
# 4) Per-0.5-deg spatial CV blocks: count valid training samples per block
#    (GNSS + InSAR + EQ), the basis of the GroupKFold split. Empty/low blocks
#    are the coverage gaps (sea, masked basins).
# ----------------------------------------------------------------------------
allpts = pd.concat([
    gnss[["lon", "lat"]], insar[["lon", "lat"]], eq[["lon", "lat"]]
], ignore_index=True)
bx = ((allpts.lon - LON0) // 0.5).astype(int)
by = ((allpts.lat - LAT0) // 0.5).astype(int)
allpts["block_id"] = bx * 100 + by
# samples per block, but only land blocks (>=1 sample) enter CV
per_block = allpts.groupby("block_id").size()

gnss.to_csv("gnss.csv", index=False)
insar.to_csv("insar.csv", index=False)
eq.to_csv("eq.csv", index=False)
per_block.to_frame("n").to_csv("per_block.csv")

print(f"GNSS sites      : {len(gnss)}")
print(f"InSAR pixels    : {len(insar)} (thinned for plotting downstream)")
print(f"Earthquakes     : {len(eq)}  (M {eq.mag.min():.1f}-{eq.mag.max():.1f}, "
      f"depth {eq.depth_km.min():.0f}-{eq.depth_km.max():.0f} km)")
print(f"CV blocks (0.5d): {per_block.size}  "
      f"(samples/block {per_block.min()}-{per_block.max()})")
