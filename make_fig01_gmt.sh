#!/usr/bin/env bash
# Fig. 1 - Study area & geodynamic setting of the Western Anatolian Extensional
# Province. Shaded SRTM15 relief + grabens, schematic active normal faults,
# Izmir-Balikesir transfer zone, documented large earthquakes, locator inset.
set -e
cd /sandbox/output

R=26/31/36/40.5
J=M15c

# ---- overlay data (ASCII labels to avoid glyph issues) ----------------------
# schematic graben-bounding normal faults (REPLACE with real fault DB traces)
cat > faults.txt <<'EOF'
> Gediz
27.70 38.48
28.10 38.50
28.55 38.55
28.95 38.60
> BuyukMenderes
27.55 37.85
28.10 37.83
28.60 37.84
29.00 37.88
> KucukMenderes
27.05 38.10
27.55 38.12
28.00 38.14
> Simav
28.55 39.05
29.05 39.08
29.55 39.12
> Denizli
28.95 37.80
29.25 37.78
29.45 37.74
> Acigol
29.55 38.00
29.90 38.02
30.10 38.05
> Gokova
27.95 37.02
28.35 37.03
28.70 37.05
EOF

# Izmir-Balikesir transfer zone (schematic, transtensional)
cat > ibtz.txt <<'EOF'
26.85 37.75
27.25 38.45
27.70 39.10
28.00 39.60
EOF

# graben labels: lon lat label
cat > grabens.txt <<'EOF'
28.30 38.52 Gediz Graben
28.10 37.82 Buyuk Menderes Graben
27.55 38.12 K. Menderes Gr.
29.05 39.10 Simav Graben
29.10 37.70 Denizli B.
29.78 38.05 Acigol Gr.
28.30 37.02 Gokova Gulf
EOF

# documented large earthquakes: lon lat size(cm)  (size = 0.10*(Mw-3))
cat > quakes.txt <<'EOF'
26.79 37.92 0.40
28.60 38.55 0.39
29.30 37.43 0.27
29.62 37.90 0.28
27.73 38.72 0.21
EOF
# earthquake labels: lon lat label
cat > quakelab.txt <<'EOF'
26.79 38.05 2020 Mw7.0
28.60 38.68 1969 Mw6.9
29.30 37.56 2019 Mw5.7
29.62 38.03 2019 Mw5.8
27.73 38.85 2017 Mw5.1
EOF

# cities: lon lat name
cat > cities.txt <<'EOF'
27.14 38.42 Izmir
27.43 38.61 Manisa
29.09 37.78 Denizli
27.85 37.85 Aydin
28.36 37.21 Mugla
EOF

# ---- figure -----------------------------------------------------------------
gmt begin fig01_studyarea png,pdf
  gmt set FONT_TITLE 14p,Helvetica-Bold FONT_ANNOT_PRIMARY 9p FONT_LABEL 10p \
          MAP_FRAME_TYPE plain PS_CHAR_ENCODING ISOLatin1+

  gmt makecpt -Cgeo -T-5000/3000 -H > relief.cpt
  gmt grdimage @earth_relief_15s -R$R -J$J -Crelief.cpt -I+a315+nt0.8 \
      -Bxa1f0.5 -Bya1f0.5 -BWSne+t"Western Anatolian Extensional Province"
  gmt coast -Wthin,black -N1/0.8p,gray30 -Df

  # schematic active normal faults
  gmt plot faults.txt -W1.5p,red3

  # Izmir-Balikesir transfer zone (dashed)
  gmt plot ibtz.txt -W1.8p,orange2,-
  echo "27.05 39.35 64 Izmir-Balikesir TZ" | \
      gmt text -F+a+f8p,Helvetica-BoldOblique,orange4 -Gwhite@40 -C0.04c/0.04c

  # graben labels
  gmt text grabens.txt -F+f8.5p,Helvetica-Oblique,gray15 -Gwhite@40 -C0.04c/0.04c

  # GNSS sites if a gnss.txt (lon lat) is supplied
  if [ -f /sandbox/input/gnss.txt ]; then
      gmt plot /sandbox/input/gnss.txt -St0.28c -Gcyan -W0.6p,black
  fi

  # cities
  gmt plot cities.txt -Ss0.22c -Gwhite -W0.8p,black
  gmt text cities.txt -F+f8p,Helvetica,black -D0/-0.32c -Gwhite@50 -C0.02c/0.02c

  # earthquakes (yellow stars scaled by Mw)
  gmt plot quakes.txt -Sa -Gyellow -W0.8p,black
  gmt text quakelab.txt -F+f7.5p,Helvetica-Bold,black -Gwhite@30 -C0.03c/0.03c

  # furniture: scale bar + colour bar + credit
  gmt basemap -LjBL+w100k+f+l"km"+o0.7c/0.7c
  gmt colorbar -Crelief.cpt -Bxa1000+l"Elevation" -By+l"m" \
      -DJMR+o0.7c/0c+w7c/0.35c
  echo "31 36 Data: SRTM15; GSHHG; DCW.  Source: authors." | \
      gmt text -F+f6.5p,Helvetica,gray30+jBR -D-0.15c/0.15c -N

  # locator inset
  gmt inset begin -DjTR+w4.3c+o0.15c -F+gwhite+p0.8p,black
    gmt coast -R19/42/33/43 -JM4.3c -Ggray85 -Slightblue -Wfaint \
        -N1/0.3p,gray60 -Bf
    gmt plot -W1.1p,red <<'BOX'
26 36
31 36
31 40.5
26 40.5
26 36
BOX
    echo "33 39.2 Turkiye" | gmt text -F+f6.5p,Helvetica,gray20
    echo "23.5 35.0 Aegean" | gmt text -F+f6p,Helvetica-Oblique,gray30
  gmt inset end
gmt end

echo "=== outputs ==="
ls -la fig01_studyarea.*
