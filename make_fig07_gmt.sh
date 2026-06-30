#!/usr/bin/env bash
# ============================================================================
# fig07_velocity_field - GMT 6.6 (modern mode)
# Predicted horizontal velocity field of the Western Anatolian Extensional
# Province on the regular model grid, referenced to stable Eurasia, with
# active-fault traces overlaid. Region/projection match fig01/fig02
# (-R26/31/36/40.5 -JM15c).
#
# DATA HONESTY: the velocity field below is a REPRODUCIBLE ANALYTIC PLACEHOLDER
# carrying the published kinematics (vectors rotating WSW->SW from north to
# south; speed increasing toward the Hellenic front; ~12-34 mm/yr). The fault
# traces are schematic. >>> Replace field() / arrows.txt + speed.xyz with the
# real model-predicted v_e, v_n grid, and faults.txt with the vetted fault
# database (e.g. Emre et al. 2018), then rerun. Coast/borders are GMT GSHHG/DCW.
# ============================================================================
set -e

# ---- data (python, stdlib only) -------------------------------------------
python3 - <<'PY'
import math
R=[26,31,36,40.5]
def field(lon,lat):
    fs=(R[3]-lat)/(R[3]-R[2]); fw=(R[1]-lon)/(R[1]-R[0])
    sp=12.0+13.0*fs+9.0*fw           # ~12 (NE) .. 34 (SW) mm/yr
    az=250.0-28.0*fs                 # WSW (north) .. SW (south), deg CW from N
    return sp*math.sin(math.radians(az)), sp*math.cos(math.radians(az)), sp
def fr(a,b,s):
    n=int(round((b-a)/s)); return [a+i*s for i in range(n+1)]
with open("speed.xyz","w") as f:                      # smooth speed raster
    for lat in fr(R[2],R[3],0.05):
        for lon in fr(R[0],R[1],0.05):
            f.write(f"{lon:.4f} {lat:.4f} {field(lon,lat)[2]:.4f}\n")
with open("arrows.txt","w") as f:                     # psvelo: lon lat ve vn se sn corr
    lat=R[2]+0.25
    while lat<R[3]:
        lon=R[0]+0.25
        while lon<R[1]:
            ve,vn,sp=field(lon,lat); f.write(f"{lon:.3f} {lat:.3f} {ve:.3f} {vn:.3f} 0 0 0\n"); lon+=0.40
        lat+=0.40
open("ref.txt","w").write("26.55 36.33 -20 0 0 0 0\n")
open("refbox.txt","w").write("26.05 36.05 27.55 36.55\n")
open("studybox.txt","w").write("26 36 31 40.5\n")
F={"gediz":[(28.00,38.45),(28.55,38.55),(29.15,38.62)],
   "bmen":[(27.55,37.83),(28.30,37.86),(29.05,37.92)],
   "kmen":[(27.30,38.05),(27.70,38.10),(28.05,38.16)],
   "simav":[(28.45,39.02),(28.95,39.10),(29.35,39.16)],
   "deniz":[(29.00,37.75),(29.45,37.85),(29.90,37.98)],
   "gokova":[(27.65,37.05),(28.10,37.08),(28.55,37.10)]}
with open("faults.txt","w") as f:
    for pts in F.values():
        f.write(">\n")
        for lo,la in pts: f.write(f"{lo} {la}\n")
with open("transfer.txt","w") as f:
    for lo,la in [(26.85,38.28),(27.25,38.66),(27.75,39.08)]: f.write(f"{lo} {la}\n")
PY

# ---- grids / cpt -----------------------------------------------------------
gmt xyz2grd speed.xyz -Gspeed.nc -R26/31/36/40.5 -I0.05
gmt makecpt -Cviridis -T10/35/1 > speed.cpt

# ---- config ----------------------------------------------------------------
gmt set FONT_ANNOT_PRIMARY 9p,Helvetica,black FONT_LABEL 10p,Helvetica,black \
        MAP_FRAME_TYPE plain MAP_FRAME_PEN 0.8p,black \
        MAP_GRID_PEN_PRIMARY 0.2p,gray80 MAP_TICK_LENGTH_PRIMARY 3p FORMAT_GEO_MAP ddd:mm
R=-R26/31/36/40.5; J=-JM15c

# ---- render ----------------------------------------------------------------
gmt begin fig07_velocity_field pdf,png
  gmt grdimage speed.nc -Cspeed.cpt $R $J -t45
  gmt coast $R $J -W0.4p,gray35 -N1/0.5p,gray45 -Di -Bxa1f0.5g1 -Bya1f0.5g0.5 -BWSne
  gmt plot faults.txt $R $J -W1.4p,firebrick
  gmt plot faults.txt $R $J -Sf0.6c/0.10c+l+t -Gfirebrick -W0.8p,firebrick
  gmt plot transfer.txt $R $J -W1.6p,orange,-
  gmt velo arrows.txt $R $J -Se0.038/0.39/0 -A0.28c+e -Gnavy -W0.8p,navy
  gmt plot refbox.txt $R $J -Sr+s -Gwhite -W0.6p,black
  gmt velo ref.txt $R $J -Se0.038/0.39/0 -A0.28c+e -Gblack -W0.9p,black
  echo "27.05 36.22 20 mm yr@+-1@+" | gmt text $R $J -F+f8p,Helvetica,black+jCM
  gmt text $R $J -F+f8p,Helvetica-Oblique,gray25+jCM <<EOF
28.55 38.70 Gediz
28.35 37.74 B. Menderes
28.95 39.24 Simav
29.55 37.66 Denizli
EOF
  gmt colorbar -Cspeed.cpt -DJBC+w8c/0.35c+o0c/0.9c+h -Bxa5f1+l"Predicted speed" -By+l"mm yr@+-1@+"
  gmt basemap -LjBR+w50k+o0.5c/0.6c+f+l"km"+c38.25 -F+gwhite+p0.5p,black
  printf "Source: authors. Predicted velocity field schematic; fault traces schematic.\n" \
    | gmt text $R $J -N -F+cBL+jTL+f6p,Helvetica-Oblique,gray30 -D0.1c/-0.5c
  gmt inset begin -DjTR+w3.2c+o0.15c -F+p0.7p,black+gwhite
    gmt coast -R24/46/34/43 -JM3.2c -Ggray85 -Swhite -W0.2p,gray50 -N1/0.3p,gray60 -A5000
    gmt plot studybox.txt -R24/46/34/43 -JM3.2c -Sr+s -W1.0p,red
  gmt inset end
gmt end
