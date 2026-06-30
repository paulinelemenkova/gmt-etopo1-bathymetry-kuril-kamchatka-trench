"""fig02_seismicity_beachballs (GEBCO version)
WAEP seismicity over GEBCO grey shaded relief, with 21 focal-mechanism
beachballs coloured by focal depth (rainbow CPT) and sized by magnitude.
Backend: rasterio + matplotlib + obspy (local). Mercator y so beachballs stay round.

Seismicity layer is fully data-driven (IEB catalogue). Beachball hypocentres are
real; strike/dip/rake are representative orientations -> replace with GCMT tensors.
"""
import numpy as np, pandas as pd, rasterio
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource, Normalize
from matplotlib.cm import ScalarMappable
from matplotlib.ticker import AutoMinorLocator, FixedLocator
from matplotlib.lines import Line2D
from obspy.imaging.beachball import beach

W,E,S,N = 25.5,31.5,35.8,40.7
CMAP = plt.cm.rainbow                      # requested rainbow cpt (depth)
DMIN,DMAX = 0,60
norm = Normalize(DMIN,DMAX)

def merc(lat):                             # spherical Mercator y (degree units)
    return np.degrees(np.log(np.tan(np.pi/4 + np.radians(lat)/2)))

# ---------- relief ----------
src = rasterio.open("/mnt/user-data/uploads/gebco_2026_n40_7_s35_8_w25_5_e31_5_geotiff.tif")
z = src.read(1).astype(float)
nx, ny = src.width, src.height
lon = np.linspace(W+src.res[0]/2, E-src.res[0]/2, nx)
lat = np.linspace(N-src.res[1]/2, S+src.res[1]/2, ny)     # descending (row0=N)
mY  = merc(lat)
ls = LightSource(azdeg=315, altdeg=30)
inten = ls.hillshade(z, vert_exag=2.0, dx=365, dy=463)
grey = 0.55 + 0.45*inten
rgb = np.dstack([grey,grey,grey])

# ---------- seismicity ----------
df = pd.read_csv("/mnt/user-data/uploads/IEB_Turkey_5000_events.csv")
df = df[(df.Lon.between(W,E)) & (df.Lat.between(S,N))].copy()
df.Depth = df.Depth.clip(lower=0)
df = df.sort_values("Mag")
df["my"] = merc(df.Lat.values)
df["s"]  = (2.2*1.62**(df.Mag-4.0))**2                      # marker area (pts^2)

# ---------- beachballs (21) ----------
M = np.loadtxt("/mnt/user-data/outputs/meca.txt")           # lon lat dep str dip rake mag
names = ["Gediz","Samos","Dinar","Gokova","Burdur","Bozkurt","Acipayam",
         "Gokceada","Biga","Seferihisar","Karaburun","Simav","Demirci",
         "Bigadic","Sindirgi","Sultandagi","Cay","Kuyucak","Marmaris",
         "Nisyros","Dodecanese"]
years = ["1970","2020","1995","2017","1971","2019","2019","1975","1983","1992",
         "1979","2011","1970","2025","2025","2002","2002","1986","1989","2021","1996"]

# ---------- figure ----------
fig, ax = plt.subplots(figsize=(8.0,7.4))
ax.imshow(rgb, extent=[W,E,merc(S),merc(N)], origin="upper", zorder=0,
          interpolation="bilinear")
ax.contour(lon, mY, z, levels=[0], colors="0.25", linewidths=0.4, zorder=1)  # coastline

sc = ax.scatter(df.Lon, df.my, s=df.s, c=df.Depth, cmap=CMAP, norm=norm,
                linewidths=0.2, edgecolors="0.25", alpha=0.75, zorder=3)

for (lo,la,dep,st,di,ra,mg),nm,yr in zip(M, names, years):
    w = 0.10*1.5**(mg-5.0)
    b = beach([st,di,ra], xy=(lo, merc(la)), width=w, linewidth=0.5,
              facecolor=CMAP(norm(dep)), edgecolor="black", zorder=5)
    ax.add_collection(b)
    if mg >= 6.4:
        ax.text(lo, merc(la)+0.55*w+0.05, f"{yr} {nm} M{mg:.1f}",
                ha="center", va="bottom", fontsize=6.6, fontweight="bold",
                zorder=6, bbox=dict(boxstyle="round,pad=0.15", fc="white",
                ec="0.6", lw=0.3, alpha=0.8))

# ---------- cities ----------
cities=[(27.142,38.423,"Izmir"),(29.087,37.783,"Denizli"),
        (28.360,37.215,"Mugla"),(30.553,37.766,"Isparta")]
for lo,la,nm in cities:
    ax.plot(lo, merc(la), "s", ms=4, mfc="black", mec="white", mew=0.5, zorder=6)
    ax.text(lo+0.07, merc(la), nm, fontsize=7.5, va="center", zorder=6,
            bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.7))

# ---------- frame / graticule ----------
ax.set_xlim(W,E); ax.set_ylim(merc(S),merc(N)); ax.set_aspect("equal")
ax.xaxis.set_major_locator(FixedLocator([26,27,28,29,30,31]))
ax.set_xticklabels([f"{v}\u00b0E" for v in [26,27,28,29,30,31]])
yt=[36,37,38,39,40]
ax.yaxis.set_major_locator(FixedLocator([merc(v) for v in yt]))
ax.set_yticklabels([f"{v}\u00b0N" for v in yt])
ax.xaxis.set_minor_locator(AutoMinorLocator(2))
ax.tick_params(which="both", direction="out", labelsize=9, top=True, right=True)
for s in ax.spines.values(): s.set_linewidth(0.9)

# ---------- scale bar (100 km) ----------
kmdeg = 111.320*np.cos(np.radians(38.25)); L=100/kmdeg
x0=W+0.35; y0=merc(S)+0.18
ax.plot([x0,x0+L],[y0,y0],"k-",lw=2.5,solid_capstyle="butt",zorder=7)
ax.plot([x0,x0+L/2],[y0,y0],"w-",lw=1.2,solid_capstyle="butt",zorder=8)
ax.text(x0+L/2,y0+0.06,"100 km",ha="center",va="bottom",fontsize=7.5,zorder=8,
        bbox=dict(boxstyle="round,pad=0.15",fc="white",ec="0.6",lw=0.3,alpha=0.85))

# ---------- magnitude legend ----------
handles=[Line2D([0],[0],marker="o",ls="",mfc="0.7",mec="0.25",mew=0.3,
                ms=np.sqrt((2.2*1.62**(m-4.0))**2),label=f"M {m:.0f}") for m in (5,6,7)]
leg=ax.legend(handles=handles,title="Magnitude",loc="upper right",fontsize=7.5,
              title_fontsize=8,framealpha=0.9,edgecolor="0.6",labelspacing=1.1,
              borderpad=0.7,handletextpad=1.0)
leg.get_frame().set_linewidth(0.5)

# ---------- depth colourbar ----------
cb=fig.colorbar(ScalarMappable(norm=norm,cmap=CMAP),ax=ax,orientation="horizontal",
                fraction=0.05,pad=0.09,aspect=38)
cb.set_label("Focal depth (km)",fontsize=9)
cb.ax.tick_params(labelsize=8,width=0.6); cb.outline.set_linewidth(0.6)

fig.subplots_adjust(left=0.07,right=0.985,top=0.99,bottom=0.04)
for ext in ("png","pdf"):
    fig.savefig(f"/mnt/user-data/outputs/fig02_seismicity_beachballs.{ext}",
                dpi=600, bbox_inches="tight", pad_inches=0.02)
print("events:",len(df),"| beachballs:",len(M))
