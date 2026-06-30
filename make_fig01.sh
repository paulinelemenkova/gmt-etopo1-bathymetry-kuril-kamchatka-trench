#!/usr/bin/env bash
# Fig. 1 (updated) - Study area & geodynamic setting of the Western Anatolian
# Extensional Province. GEBCO_2026 shaded relief + active faults (flt4_2l),
# graben axes, Izmir-Balikesir transfer zone, IEB instrumental seismicity
# (1970-2026, M>=4) coloured by focal depth & scaled by magnitude, locator inset
# and full explanation legend.
set -e
cd "$(dirname "$0")/fig01_data"

R=26/31/36/40.5
J=M16c

gmt grdconvert dem.tif dem.nc

cat > grabens_lab.txt <<'EOF'
28.30 38.55 Gediz Graben
28.45 37.66 Buyuk Menderes Graben
27.45 38.18 K. Menderes Gr.
29.02 39.16 Simav Graben
29.58 37.64 Denizli Basin
29.82 38.10 Acigol Gr.
28.32 36.97 Gokova Gulf
EOF

cat > legend.txt <<'EOF'
H 11p,Helvetica-Bold Explanation
D 0.06c 0.8p,black
S 0.26c - 0.60c - 1.6p,magenta2 0.74c Active fault (flt4_2l)
S 0.26c - 0.60c - 2.0p,purple 0.74c Graben / basin axis
S 0.26c - 0.60c - 2.0p,orange2,8_4:0p 0.74c Izmir-Balikesir TZ
S 0.26c s 0.17c white 0.8p,black 0.74c City
D 0.06c 0.5p,black
L 9.5p,Helvetica-Bold L Earthquake magnitude (M@-w@-)
N 4
S 0.05c c 0.08c gray80 0.4p,gray20 0.22c 4
S 0.07c c 0.128c gray80 0.4p,gray20 0.26c 5
S 0.11c c 0.205c gray80 0.4p,gray20 0.32c 6
S 0.16c c 0.328c gray80 0.4p,gray20 0.44c 7
N 1
G 0.18c
B depth.cpt 0.15c 0.32c -Bxa40f20+l"Focal depth (km)"
G 0.05c
EOF

gmt begin fig01_studyarea png,pdf
  gmt set FONT_TITLE 15p,Helvetica-Bold FONT_ANNOT_PRIMARY 10p FONT_LABEL 11p \
          MAP_FRAME_TYPE plain PS_CHAR_ENCODING ISOLatin1+ \
          MAP_GRID_PEN_PRIMARY 0.25p,white@55 MAP_TICK_LENGTH_PRIMARY 0.18c

  gmt makecpt -Cgeo -T-5000/3000 -H > relief.cpt
  gmt makecpt -Cviridis -T0/160 -H > depth.cpt

  gmt grdimage dem.nc -R$R -J$J -Crelief.cpt -I+a315+nt0.8 \
      -Bxa1f6mg1 -Bya1f6mg1 -BWSne+t"Western Anatolian Extensional Province"
  gmt coast -Wthin,black -N1/0.8p,gray30 -Df

  gmt plot faults_box.gmt -W1.4p,magenta2
  gmt plot grabens_lines.gmt -W2.0p,purple

  gmt plot ibtz.txt -W2.0p,orange2,8_4:0p
  echo "27.05 39.28 64 Izmir-Balikesir TZ" | \
      gmt text -F+a+f9p,Helvetica-BoldOblique,orange4 -Gwhite@40 -C0.04c/0.04c

  gmt plot quakes.xyz -Sc -Cdepth.cpt -W0.2p,gray20 -t10
  gmt plot quakes_big.txt -Sc -Cdepth.cpt -W1.0p,black
  echo "26.7838 37.8973 2020 M7.0" | \
      gmt text -F+f8.5p,Helvetica-Bold,black+jRB -Gwhite@25 -C0.04c/0.04c -D-0.30c/0.18c
  echo "29.5700 39.0980 1970 M7.2" | \
      gmt text -F+f8.5p,Helvetica-Bold,black+jCT -Gwhite@25 -C0.04c/0.04c -D0/-0.40c

  gmt text grabens_lab.txt -F+f9.5p,Helvetica-Oblique,purple4 -Gwhite@35 -C0.05c/0.05c

  gmt plot cities.txt -Ss0.24c -Gwhite -W0.9p,black
  gmt text cities.txt -F+f9p,Helvetica,black -D0/-0.40c -Gwhite@45 -C0.02c/0.02c

  gmt basemap -LjBL+w100k+f+l"km"+o0.8c/0.8c
  gmt colorbar -Crelief.cpt -Bxa1000f500+l"Elevation" -By+l"m" \
      -DJMR+o0.8c/0c+w7c/0.35c

  echo "31 36 Data: GEBCO_2026; IEB / IRIS seismicity 1970-2026 (M>=4); active faults (flt4_2l); GSHHG." | \
      gmt text -F+f7.5p,Helvetica,gray25+jBR -Gwhite@25 -D-0.15c/0.15c -C0.06c/0.06c -N

  gmt legend legend.txt -DjTR+w4.9c+o0.25c/0.25c -F+gwhite@8+p0.9p,black+r \
      --FONT_ANNOT_PRIMARY=8.5p

  gmt inset begin -DjTL+w4.0c/2.21c+o0.25c/0.25c -F+gwhite+p0.9p,black
    gmt coast -R19/42/33/43 -JM4.0c -Ggray85 -Slightblue -Wfaint \
        -N1/0.3p,gray60 -Bf
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

echo "=== outputs ==="
ls -la fig01_studyarea.*
