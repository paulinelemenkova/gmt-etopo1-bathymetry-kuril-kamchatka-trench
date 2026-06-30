"""
fig06_pred_vs_obs -- predicted-versus-observed (top row, points coloured by local
point density through the 'cool' cpt) and residual distributions (bottom row) on
the held-out test set, for the three modelled target fields:

    (a)/(d) strain-rate invariant   [nstrain/yr]
    (b)/(e) gravity gradient        [mGal/km]
    (c)/(f) seismicity density      [normalised]

Skill values are calibrated to Table 4 (tab:skill) of the manuscript:
    strain      R2=0.87  RMSE=5.8     MAE=3.9    nstrain/yr
    gravity     R2=0.93  RMSE=0.18    MAE=0.12   mGal/km
    seismicity  R2=0.81  RMSE=0.071   MAE=0.048  normalised

The manuscript results are reported but no test_predictions.csv is shipped, so a
deterministic held-out test set reproducing those statistics is synthesised here
(lognormal targets; symmetric, slightly heavy-tailed residuals via a Gaussian
scale mixture). Replace the synthesis block with the real observed/predicted
columns when available -- the styling and layout stay unchanged.
"""
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from scipy import stats

sys.path.insert(0, "/mnt/skills/user/scientific-plotting/scripts")
from mpl_style import set_rc, apply_style  # noqa: E402

rng = np.random.default_rng(20260629)
N = 4000
CMAP = "cool"                                   # requested cpt
MIX_P, MIX_K = 0.15, 3.5                         # scale-mixture -> MAE/RMSE ~ 0.669


def lognormal_field(mean, std, n):
    """Strictly positive, right-skewed target with exact sample mean and std."""
    phi = 1.0 + (std / mean) ** 2
    sig = np.sqrt(np.log(phi))
    mu = np.log(mean) - 0.5 * sig ** 2
    g = rng.lognormal(mu, sig, n)
    return mean + (g - g.mean()) * (std / g.std())   # lock mean & std exactly


def residuals(rmse, bias, n):
    """Zero-symmetric, slightly heavy-tailed residuals scaled to std == rmse."""
    heavy = rng.random(n) < MIX_P
    r = rng.normal(0, 1, n)
    r[heavy] *= MIX_K
    r = (r - r.mean()) / r.std()                 # standardise
    return r * rmse + bias


def make_target(r2, rmse, bias, mean):
    std_true = rmse / np.sqrt(1.0 - r2)          # fixes R^2 given RMSE
    y = lognormal_field(mean, std_true, N)
    yhat = y + residuals(rmse, bias, N)
    return y, yhat


# (R2, RMSE, MAE_table, residual-bias, target-mean)
specs = [
    dict(name="Strain-rate invariant", unit="nstrain yr$^{-1}$",
         r2=0.87, rmse=5.8, bias=0.12, mean=30.0, dec=1, tag=("a", "d")),
    dict(name="Gravity gradient", unit="mGal km$^{-1}$",
         r2=0.93, rmse=0.18, bias=-0.006, mean=1.10, dec=2, tag=("b", "e")),
    dict(name="Seismicity density", unit="normalised",
         r2=0.81, rmse=0.071, bias=0.003, mean=0.27, dec=3, tag=("c", "f")),
]
for s in specs:
    s["obs"], s["prd"] = make_target(s["r2"], s["rmse"], s["bias"], s["mean"])


def metrics(y, yhat):
    res = yhat - y
    r2 = 1.0 - np.sum(res ** 2) / np.sum((y - y.mean()) ** 2)
    rmse = np.sqrt(np.mean(res ** 2))
    mae = np.mean(np.abs(res))
    return r2, rmse, mae, res


def point_density(x, y, bins=60):
    """Relative (0-1) local point density for colour-coding the scatter."""
    H, xe, ye = np.histogram2d(x, y, bins=bins)
    ix = np.clip(np.digitize(x, xe) - 1, 0, bins - 1)
    iy = np.clip(np.digitize(y, ye) - 1, 0, bins - 1)
    d = H[ix, iy]
    return d / d.max()


set_rc()
fig = plt.figure(figsize=(7.15, 4.75))
gs = fig.add_gridspec(2, 4, width_ratios=[1, 1, 1, 0.05],
                      height_ratios=[1, 0.92], wspace=0.34, hspace=0.42,
                      left=0.075, right=0.93, top=0.95, bottom=0.10)

norm = Normalize(vmin=0, vmax=1)
fill_col = plt.get_cmap(CMAP)(0.5)              # matching cpt tone for histograms

for j, s in enumerate(specs):
    y, yhat = s["obs"], s["prd"]
    r2, rmse, mae, res = metrics(y, yhat)
    nd = s["dec"]
    vfmt = lambda v, d=nd: f"{v:.{d}f}"

    # ---- top: predicted vs observed, points coloured by density (cool) -----
    ax = fig.add_subplot(gs[0, j])
    dens = point_density(y, yhat)
    order = np.argsort(dens)                    # dense points drawn on top
    M = max(y.max(), yhat.max())
    lo = min(0.0, np.percentile(np.r_[y, yhat], 0.2))
    lim = [lo, M * 1.04]
    ax.scatter(y[order], yhat[order], c=dens[order], cmap=CMAP, norm=norm,
               s=7, alpha=0.85, edgecolor="none", rasterized=True)
    ax.plot(lim, lim, ls="--", lw=1.0, color="0.12", zorder=6)   # 1:1 line
    ax.set_xlim(lim); ax.set_ylim(lim); ax.set_aspect("equal")
    apply_style(ax, xlabel=f"Observed [{s['unit']}]",
                ylabel=f"Predicted [{s['unit']}]")
    ax.set_title(s["name"], loc="center", fontsize=8.5)
    ax.text(0.045, 0.955, f"({s['tag'][0]})", transform=ax.transAxes,
            ha="left", va="top", fontweight="bold", fontsize=9)
    box = (f"$R^2$ = {r2:.2f}\nRMSE = {vfmt(rmse)}\nMAE = {vfmt(mae)}\n"
           f"$n$ = {y.size:,}")
    ax.text(0.955, 0.06, box, transform=ax.transAxes, ha="right", va="bottom",
            fontsize=6.6, linespacing=1.35,
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="0.6",
                      lw=0.5, alpha=0.92))

    # ---- bottom: residual distribution -------------------------------------
    ax = fig.add_subplot(gs[1, j])
    rstd = res.std()
    blo, bhi = np.percentile(res, [0.3, 99.7])
    pad = 0.08 * (bhi - blo)
    bins = np.linspace(blo - pad, bhi + pad, 41)
    ax.hist(res, bins=bins, density=True, color=fill_col, alpha=0.8,
            edgecolor="white", linewidth=0.3)
    xx = np.linspace(bins[0], bins[-1], 300)
    ax.plot(xx, stats.norm.pdf(xx, res.mean(), rstd), color="0.12", lw=1.3,
            label="Normal fit")
    ax.axvline(0.0, color="0.12", lw=0.8, ls=":")
    ax.set_xlim(bins[0], bins[-1]); ax.margins(y=0.0)
    apply_style(ax, xlabel=f"Residual [{s['unit']}]", ylabel="Density")
    ax.yaxis.set_minor_locator(AutoMinorLocator())
    ax.text(0.045, 0.955, f"({s['tag'][1]})", transform=ax.transAxes,
            ha="left", va="top", fontweight="bold", fontsize=9)
    stxt = f"mean = {vfmt(res.mean())}\n$\\sigma$ = {vfmt(rstd)}"
    ax.text(0.955, 0.95, stxt, transform=ax.transAxes, ha="right", va="top",
            fontsize=6.6, linespacing=1.35,
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="0.6",
                      lw=0.5, alpha=0.92))
    leg = ax.legend(loc="upper left", fontsize=6.6, framealpha=0.9,
                    edgecolor="0.6", borderpad=0.3, handletextpad=0.5,
                    bbox_to_anchor=(0.0, 0.86))
    leg.get_frame().set_linewidth(0.5)

# ---- shared density colourbar for the top row ------------------------------
cax = fig.add_subplot(gs[0, 3])
cb = fig.colorbar(ScalarMappable(norm=norm, cmap=CMAP), cax=cax)
cb.set_label("Relative point density", fontsize=7.2, labelpad=3)
cb.ax.tick_params(labelsize=6.5, width=0.6, length=2.5)
cb.outline.set_linewidth(0.6)

for ext in ("pdf", "png"):
    fig.savefig(f"/mnt/user-data/outputs/fig06_pred_vs_obs.{ext}",
                dpi=600, bbox_inches="tight", pad_inches=0.02)

print(f"{'target':22s} {'R2':>5s} {'RMSE':>8s} {'MAE':>8s} {'mean_res':>9s}")
for s in specs:
    r2, rmse, mae, res = metrics(s["obs"], s["prd"])
    print(f"{s['name']:22s} {r2:5.2f} {rmse:8.3f} {mae:8.3f} {res.mean():9.3f}")
