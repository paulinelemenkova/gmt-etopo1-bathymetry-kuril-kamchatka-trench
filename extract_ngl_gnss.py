#!/usr/bin/env python3
"""
extract_ngl_gnss.py
-------------------
Download NGL (Nevada Geodetic Laboratory, UNR) MIDAS GNSS station velocities,
clip them to the Western Anatolia window, and add Eurasia-fixed horizontal
velocities using the ITRF2014 plate-motion-model Eurasia pole.

Open source, no login required.  Source file (~5 MB, global, plain text):
    https://geodesy.unr.edu/velocities/midas.IGS14.txt
NGL MIDAS column doc:
    https://geodesy.unr.edu/velocities/midas.readme.txt

Usage:  python3 extract_ngl_gnss.py
Output: gnss_wanatolia_padbox.txt and gnss_wanatolia_studybox.txt
"""
import urllib.request, math

URL  = "https://geodesy.unr.edu/velocities/midas.IGS14.txt"
PAD  = (24.0, 33.0, 34.0, 42.0)   # W E S N  (padded box, for interpolation)
BOX  = (26.0, 31.0, 36.0, 40.5)   # study window

# ITRF2014-PMM Eurasia angular velocity (Altamimi et al., 2017, GJI 209, 1906),
# Cartesian components in mas/yr  (pole ~55.07N, 260.65E, 0.261 deg/Myr):
WX, WY, WZ = -0.085, -0.531, 0.770
MAS2RAD = 4.84813681e-9
Wx, Wy, Wz = WX*MAS2RAD, WY*MAS2RAD, WZ*MAS2RAD     # rad/yr
RE = 6378137.0                                       # m (spherical approx.)

def norm_lon(x):
    while x < -180: x += 360
    while x >  180: x -= 360
    return x

def eurasia_plate_enu(lon, lat):
    """Rigid Eurasia plate velocity (mm/yr, E,N) at lon/lat from Omega x r."""
    la, lo = math.radians(lat), math.radians(lon)
    x = RE*math.cos(la)*math.cos(lo); y = RE*math.cos(la)*math.sin(lo); z = RE*math.sin(la)
    vx, vy, vz = Wy*z - Wz*y, Wz*x - Wx*z, Wx*y - Wy*x          # m/yr
    E = (-math.sin(lo)*vx + math.cos(lo)*vy) * 1000.0
    N = (-math.sin(la)*math.cos(lo)*vx - math.sin(la)*math.sin(lo)*vy + math.cos(la)*vz) * 1000.0
    return E, N

def main():
    raw = urllib.request.urlopen(URL, timeout=120).read().decode().splitlines()
    rows = []
    for ln in raw:
        f = ln.split()
        if len(f) < 27:
            continue
        try:
            sta = f[0]
            Ve, Vn, Vu    = (float(f[8])*1000, float(f[9])*1000,  float(f[10])*1000)   # m->mm/yr
            sVe, sVn, sVu = (float(f[11])*1000, float(f[12])*1000, float(f[13])*1000)
            lat = float(f[24]); lon = norm_lon(float(f[25]))
            dt = float(f[4]);   ng = int(f[6])
        except ValueError:
            continue
        if PAD[0] <= lon <= PAD[1] and PAD[2] <= lat <= PAD[3]:
            Ep, Np = eurasia_plate_enu(lon, lat)
            tight = int(BOX[0] <= lon <= BOX[1] and BOX[2] <= lat <= BOX[3])
            rows.append((sta, lon, lat, Ve, Vn, Ve-Ep, Vn-Np, sVe, sVn, Vu, sVu, dt, ng, tight))
    rows.sort(key=lambda r: (r[2], r[1]))

    hdr = ("# GNSS velocities, Western Anatolia — extracted from NGL MIDAS (UNR)\n"
           "# source : https://geodesy.unr.edu/velocities/midas.IGS14.txt  (MIDAS5)\n"
           "# frames : IGS14 (=ITRF2014) and Eurasia-fixed (ITRF2014-PMM, Altamimi+2017)\n"
           "# units  : mm/yr ; Eurasia omega(mas/yr)=(-0.085,-0.531,0.770)\n"
           "# cols   : sta lon lat Ve_igs14 Vn_igs14 Ve_eur Vn_eur sVe sVn Vu sVu span_yr ngood in_tightbox\n")

    def write(path, keep):
        with open(path, "w") as o:
            o.write(hdr)
            for r in rows:
                if keep(r):
                    o.write("{:5s} {:9.4f} {:8.4f} {:7.2f} {:7.2f} {:7.2f} {:7.2f} "
                            "{:5.2f} {:5.2f} {:7.2f} {:5.2f} {:5.2f} {:6d} {}\n".format(*r))

    write("gnss_wanatolia_padbox.txt",   lambda r: True)
    write("gnss_wanatolia_studybox.txt", lambda r: r[13] == 1)
    print("padbox:", len(rows), " studybox:", sum(r[13] for r in rows))

if __name__ == "__main__":
    main()
