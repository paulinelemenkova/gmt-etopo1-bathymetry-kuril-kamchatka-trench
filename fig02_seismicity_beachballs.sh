#!/usr/bin/env bash
# =============================================================================
# fig02_seismicity_beachballs.sh
#
# Western Anatolian Extensional Province (WAEP): regional instrumental
# seismicity scaled by magnitude and coloured by focal depth, over grey-scale
# shaded relief, with focal-mechanism beachballs for the principal
# normal-faulting events.
#
# Backend : GMT 6 (modern mode) + a small Python pre-processing step.
# Input   : IEB_Turkey_5000_events.csv  (cols: Year,Month,Day,Time,Lat,Lon,
#                                         Depth,Mag,Region,Timestamp)
# Output  : fig02_seismicity_beachballs.png (600 dpi) and .pdf
#
# NOTE ON THE BEACHBALLS
#   The IEB catalogue carries only lon/lat/depth/magnitude -- it has NO moment
#   tensors. The seismicity layer is therefore fully data-driven, but the seven
#   beachballs are anchored on the REAL hypocentres of the principal events and
#   given REPRESENTATIVE normal-faulting Aki angles (strike/dip/rake) consistent
#   with each event's documented faulting style. Replace the rows of meca.txt
#   with the exact GCMT moment tensors (psmeca -Sc / -Sm columns) before
#   submission; the rest of the pipeline is unchanged.
# =============================================================================
set -e

CSV="${1:-IEB_Turkey_5000_events.csv}"     # path to the catalogue
W=25.5; E=31.5; S=35.8; N=40.7             # study window
REGION="$W/$E/$S/$N"
PROJ="M15c"

# ---- 1. build the plotting tables from the catalogue ------------------------
python3 - "$CSV" "$W" "$E" "$S" "$N" <<'PYEOF'
import sys, numpy as np, pandas as pd
csv,W,E,S,N = sys.argv[1], *map(float, sys.argv[2:6])
df = pd.read_csv(csv)
df = df[(df.Lon.between(W,E)) & (df.Lat.between(S,N))].copy()
df.Depth = df.Depth.clip(lower=0)
df["size"] = 0.045 * 1.8**(df.Mag - 4.0)          # circle diameter (cm)
df = df.sort_values("Mag")                         # large events drawn last
with open("quakes.txt","w") as f:                  # lon lat depth size
    for _,r in df.iterrows():
        f.write(f"{r.Lon:.4f} {r.Lat:.4f} {r.Depth:.1f} {r['size']:.3f}\n")
print("events in window:", len(df))
PYEOF

# principal normal-faulting events: lon lat depth strike dip rake mag
cat > meca.txt <<'EOF'
29.570 39.098 25 290 45 -90  7.2
26.784 37.897 21 270 37 -95  7.0
30.134 38.063 33 130 45 -85  6.4
27.414 36.929  7 275 40 -90  6.6
29.784 37.585 22  45 50 -100 6.3
29.700 37.935 11 290 45 -90  5.9
29.531 37.408  8 300 50 -90  5.7
EOF

# event labels (lat offset upward so the text clears the ball)
cat > evlabels.txt <<'EOF'
29.570 39.268 1970 Gediz M7.2
26.784 38.067 2020 Samos M7.0
30.134 38.233 1995 Dinar M6.4
27.414 37.099 2017 Gokova M6.6
29.784 37.755 1971 Burdur M6.3
29.700 38.105 2019 Bozkurt M5.9
29.531 37.238 2019 Acipayam M5.7
EOF

# orientation cities
cat > cities.txt <<'EOF'
27.142 38.423
29.087 37.783
28.360 37.215
30.553 37.766
EOF
cat > citynames.txt <<'EOF'
27.212 38.423 Izmir
29.157 37.783 Denizli
28.430 37.215 Mugla
30.623 37.766 Isparta
EOF

# magnitude size legend (sizes match 0.045*1.8^(M-4))
cat > leg.txt <<'EOF'
G 0.05c
H 8p,Helvetica-Bold Magnitude
G 0.08c
S 0.30c c 0.081c white 0.4p,gray25 0.72c M 5
S 0.30c c 0.146c white 0.4p,gray25 0.72c M 6
S 0.30c c 0.262c white 0.4p,gray25 0.72c M 7
EOF

# ---- 2. relief, palettes, hillshade -----------------------------------------
# Needs GMT remote data. If auto-download is disabled, fetch the 90-deg tile
# manually and grdcut it, e.g.:
#   curl -sLo tile.jp2 \
#     https://oceania.generic-mapping-tools.org/server/earth/earth_relief/earth_relief_03m_p/N00E000.earth_relief_03m_p.jp2
#   gmt grdcut tile.jp2=gd -R$REGION -Grelief.nc
gmt grdcut @earth_relief_03m -R$REGION -Grelief.nc

gmt makecpt -Cgray   -T-1500/3200 > relief.cpt
gmt makecpt -Chawaii -T0/60/5 -I  > depth.cpt          # shallow=cyan, deep=magenta
gmt grdgradient relief.nc -A315 -Ne0.6 -Gint.nc

# ---- 3. render --------------------------------------------------------------
gmt set PROJ_LENGTH_UNIT cm FONT_ANNOT_PRIMARY 9p FONT_LABEL 10p \
        MAP_FRAME_TYPE plain MAP_FRAME_PEN 0.9p FORMAT_GEO_MAP ddd:mm

gmt begin fig02_seismicity_beachballs png,pdf E600
  gmt grdimage relief.nc -Crelief.cpt -Iint.nc -J$PROJ -R$REGION \
               -BWSne -Bxa1f0.5 -Bya1f0.5
  gmt coast  -W0.4p,gray35 -N1/0.4p,gray45,-- -Df
  gmt plot   quakes.txt -Sc -Cdepth.cpt -W0.2p,gray25 -t30
  gmt meca   meca.txt -Sa0.42c -Ggray15 -Ewhite -L0.6p,black
  gmt text   evlabels.txt  -F+f6.6p,Helvetica-Bold,black+jBC -Gwhite@25 \
             -W0.2p,gray -C0.04c/0.02c
  gmt plot   cities.txt -Ss0.16c -Gblack -W0.5p,white
  gmt text   citynames.txt -F+f7.5p,Helvetica,black+jLM -Gwhite@35 -C0.03c/0.03c
  gmt colorbar -Cdepth.cpt -DJBC+w8c/0.35c+h+o0c/0.9c \
               -Bxa10f5+l"Focal depth" -By+lkm
  gmt legend leg.txt -DjTR+w3.1c+o0.2c -F+gwhite@10+p0.6p,gray40
  gmt basemap -Ljbl+w100k+o0.6c/0.6c+f+u -F+gwhite@20+p0.5p,gray40
gmt end show
