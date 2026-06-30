#!/usr/bin/env bash
# Fig. 11 - Seismic strain rate & seismicity, Western Anatolian Extensional Province.
# Catalog-derived Kostrov seismic strain rate over grey shaded relief, with
# epicentres (1970-2026, M>=4), active faults (flt4_2l) and graben axes.
# Reproduce the strain field from scratch:  python3 fig11_data/strain.py
# (re-writes strain.xyz + quakes_all.txt from the IEB CSV). Requires GMT 6.5.
set -e
cd "$(dirname "$0")/fig11_data"

R=26/31/36/40.5
J=M16c

# --- data prep: DEM + strain-rate grid (gridded, smoothed, low values masked) -
gmt grdconvert dem.tif dem.nc
gmt xyz2grd strain.xyz -Gstrain.nc -R26/31/36/40.48 -I0.04
gmt grdsample strain.nc -I0.01 -Gstrain_s.nc
gmt grdclip  strain_s.nc -Gstrain_m.nc -Sb-15.5/NaN

gmt begin fig11_strain_seismicity png,pdf
  gmt set FONT_TITLE 15p,Helvetica-Bold FONT_ANNOT_PRIMARY 10p FONT_LABEL 11p \
          MAP_FRAME_TYPE plain PS_CHAR_ENCODING ISOLatin1+ \
          MAP_GRID_PEN_PRIMARY 0.25p,white@55 MAP_TICK_LENGTH_PRIMARY 0.18c

  gmt makecpt -Cgray    -T-7000/4500 -H > gray.cpt
  gmt makecpt -Clajolla -T-15.5/-13.7 -H > strain.cpt

  gmt grdimage dem.nc -R$R -J$J -Cgray.cpt -I+a315+nt0.7 \
      -Bxa1f6mg1 -Bya1f6mg1 \
      -BWSne+t"Seismic strain rate & seismicity - Western Anatolian Extensional Province"

  gmt grdimage strain_m.nc -Cstrain.cpt -Q -t10          # strain field (NaN transparent)

  gmt coast -Wthin,black -N1/0.8p,gray30 -Df

  gmt plot faults_box.gmt -W2.6p,white@35
  gmt plot faults_box.gmt -W1.4p,magenta2
  gmt plot grabens_lines.gmt -W2.0p,purple
  gmt plot ibtz.txt -W2.0p,orange2,8_4:0p
  echo "27.05 39.28 64 Izmir-Balikesir TZ" | \
      gmt text -F+a+f9p,Helvetica-BoldOblique,orange4 -Gwhite@40 -C0.04c/0.04c

  gmt plot quakes_all.txt -i0,1,4 -Sc -Gblack@55 -W0.2p,white@50
  gmt plot quakes_big.txt -i0,1,3 -Sc -Gred3 -W1.1p,black
  echo "26.7838 37.8973 2020 M7.0" | \
      gmt text -F+f8.5p,Helvetica-Bold,black+jRB -Gwhite@25 -C0.04c/0.04c -D-0.30c/0.18c
  echo "29.5700 39.0980 1970 M7.2" | \
      gmt text -F+f8.5p,Helvetica-Bold,black+jCT -Gwhite@25 -C0.04c/0.04c -D0/-0.40c

  gmt text grabens_lab.txt -F+f9.5p,Helvetica-Oblique,purple4 -Gwhite@35 -C0.05c/0.05c

  gmt plot cities.txt -Ss0.24c -Gwhite -W0.9p,black
  gmt text cities.txt -F+f9p,Helvetica,black -D0/-0.40c -Gwhite@45 -C0.02c/0.02c

  gmt basemap -LjBL+w100k+f+l"km"+o0.8c/0.8c

  gmt colorbar -Cstrain.cpt -DJMR+o0.8c/0c+w7c/0.35c \
      -Bxa0.5f0.1+l"log@-10@- seismic strain rate" -By+l"s@+-1@+"

  echo "31 36 Data: IEB/IRIS seismicity 1970-2026 (M>=4); strain = Kostrov sum (crustal <=40 km, H@-s@-=15 km, @~m@~=33 GPa); faults flt4_2l; GEBCO_2026; GSHHG." | \
      gmt text -F+f7p,Helvetica,gray25+jBR -Gwhite@25 -D-0.15c/0.15c -C0.06c/0.06c -N

  gmt legend legend11.txt -DjTR+w4.9c+o0.25c/0.25c -F+gwhite@8+p0.9p,black+r \
      --FONT_ANNOT_PRIMARY=8.5p

  gmt inset begin -DjTL+w4.0c/2.21c+o0.25c/0.25c -F+gwhite+p0.9p,black
    gmt coast -R19/42/33/43 -JM4.0c -Ggray85 -Slightblue -Wfaint -N1/0.3p,gray60 -Bf
    gmt plot -W1.2p,red <<'BOX'
26 36
31 36
31 40.5
26 40.5
26 36
BOX
    echo "33.2 38.8 Turkiye" | gmt text -F+f7.5p,Helvetica,gray20
    echo "23.0 35.2 Aegean"  | gmt text -F+f7p,Helvetica-Oblique,gray30
  gmt inset end
gmt end

mv fig11_strain_seismicity.png fig11_strain_seismicity.pdf ..
echo "done -> fig11_strain_seismicity.png / .pdf"
