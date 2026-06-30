# GNSS velocities — Western Anatolian Extensional Province

Station velocities extracted from open GNSS sources for the window
**26–31°E, 36–40.5°N** (and a padded 24–33°E / 34–42°N box for interpolation).

## Files
- `gnss_wanatolia_studybox.txt` — 50 stations inside the study window.
- `gnss_wanatolia_padbox.txt`   — 154 stations in the padded box (use these when
  gridding/interpolating, so the edges of the study box are constrained).
- `fig_gnss_velocity.png/.pdf`  — Eurasia-fixed velocity-vector map (validation figure).
- `extract_ngl_gnss.py`         — reproducible download + clip + frame-reduction script.

## Source
**Nevada Geodetic Laboratory (NGL), University of Nevada Reno** — global MIDAS
velocity solution, free / no login:
- velocities : https://geodesy.unr.edu/velocities/midas.IGS14.txt  (~5 MB, plain text)
- column doc : https://geodesy.unr.edu/velocities/midas.readme.txt
MIDAS is a robust (median-based) trend estimator, insensitive to steps/outliers
(Blewitt et al., 2016, *J. Geophys. Res.*).

Other open sources considered:
- **EarthScope / GAGE** velocity products (`*.vel`) — the formerly open archive
  URL now sits behind an EarthScope login, so it was not used here.
- **GEM GSRM v2.1** (Kreemer et al., 2014) — global compiled velocities + modeled
  strain grid; good ready-made alternative.
- Regional dense fields with open tables: **Kurt et al. (2023)** "Contemporary
  velocity field for Turkey" (836 sites), **Briole et al. (2021)** Aegean field.

## Columns
```
sta  lon  lat  Ve_igs14  Vn_igs14  Ve_eur  Vn_eur  sVe  sVn  Vu  sVu  span_yr  ngood  in_tightbox
```
- `Ve_igs14, Vn_igs14` : east/north velocity in **IGS14** (= ITRF2014-aligned), mm/yr.
- `Ve_eur,  Vn_eur`    : east/north velocity in **Eurasia-fixed** frame, mm/yr.
- `sVe, sVn`           : 1-sigma horizontal velocity uncertainties, mm/yr.
- `Vu, sVu`            : vertical velocity and uncertainty, mm/yr.
- `span_yr, ngood`     : time-series length and number of good daily epochs.

## Reference frames
- **IGS14** velocities are absolute (dominated by ~25 mm/yr NE Eurasian plate motion).
- **Eurasia-fixed** removes rigid Eurasia rotation using the ITRF2014 plate-motion
  model Eurasia pole (Altamimi et al., 2017; omega = -0.085, -0.531, 0.770 mas/yr).
  Validation: stable-Eurasia sites (e.g. ZONG, ANKR-north) reduce to ~0 mm/yr,
  while Anatolia shows the expected SW-increasing extension/extrusion.
- **For strain rate, the choice of frame does not matter** — the symmetric velocity
  gradient (strain rate) is invariant to a rigid-body rotation. Use either column.

## Next step (geodetic strain rate, companion to fig11)
Interpolate the velocity field and differentiate, e.g. with GMT `gpsgridder`:
```
gmt gpsgridder gnss_wanatolia_padbox.txt -R26/31/36/40.5 -I0.05 \
    -Gvel_%s.nc -Sv0.5 -Fd20 -W   # -> gridded Ve, Vn
# then second invariant / dilatation from the gradients of Ve, Vn (grdgradient).
```
Alternatives: VISR (Shen et al.), SSPX. The padded-box file feeds the interpolator
so the study-box edges are well constrained.
