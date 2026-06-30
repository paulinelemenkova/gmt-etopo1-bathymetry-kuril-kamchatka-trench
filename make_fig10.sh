#!/usr/bin/env bash
# Fig. 10 - 3D perspective relief of the Western Anatolian Extensional Province.
# GEBCO_2026 DEM draped with a hillshaded turbo CPT, viewed obliquely (grdview).
# Reuses the DEM staged for fig01 (fig01_data/dem.tif). Requires GMT 6.5.
set -e
cd "$(dirname "$0")/fig01_data"

R=26/31/36/40.5
J=M16c
Z=2.5c
P=150/40                 # perspective azimuth/elevation (used everywhere)

gmt grdconvert dem.tif dem.nc                 # GeoTIFF -> netCDF
gmt grdgradient dem.nc -A315 -Ne0.8 -Gintens.nc   # hillshade intensity

gmt begin fig10_relief3d png,pdf
  gmt set FONT_TITLE 15p,Helvetica-Bold FONT_ANNOT_PRIMARY 9p FONT_LABEL 11p \
          MAP_FRAME_TYPE plain PS_CHAR_ENCODING ISOLatin1+

  gmt makecpt -Cturbo -T-4500/3000 -H > turbo.cpt

  gmt grdview dem.nc -R$R -J$J -JZ$Z -p$P -Cturbo.cpt -Iintens.nc -Qi300 \
      -N-4500+glightgray \
      -Bxa1f30m -Bya1f30m -Bza2000f1000+l"Elevation (m)" \
      -BwSEnZ+t"Western Anatolian Extensional Province - 3D relief"

  gmt colorbar -Cturbo.cpt -DJMR+o1.4c/0c+w7c/0.35c \
      -Bxa1000f500+l"Elevation" -By+l"m"

  gmt text -R0/10/0/10 -Jx1c -N -F+f9p,Helvetica-Oblique,gray25+jLB <<EOF
0.15 0.15 Perspective view azimuth/elevation: ${P}@.;  vertical exaggeration ~9x
EOF
  gmt text -R0/10/0/10 -Jx1c -N -F+f7.5p,Helvetica,gray35+jLB <<EOF
0.15 -0.30 Data: GEBCO_2026 sub-ice DEM (15 arc-sec).
EOF
gmt end

# move the rendered figure up next to the script
mv fig10_relief3d.png fig10_relief3d.pdf ..
echo "done -> fig10_relief3d.png / .pdf"
