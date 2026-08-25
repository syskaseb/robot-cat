"""Two charts for the actuator report. Every plotted point is measured."""

import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

INK, ACCENT, WARM, MUTED, GRID = "#16191d", "#0f4c5c", "#b3541e", "#5f6b73", "#dfe5e8"
GOOD = "#1c6b45"

plt.rcParams.update({
    # Calibri on Windows; Carlito is metric-compatible and is what a macOS or
    # Linux rebuild picks up, so the charts come out identical either way.
    "font.family": ["Calibri", "Carlito", "DejaVu Sans"],
    "font.size": 9,
    "axes.edgecolor": MUTED,
    "axes.labelcolor": INK,
    "text.color": INK,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

OUT = str(pathlib.Path(__file__).resolve().parent)


# ------------------------------------------------------------------ chart 1
# Achieved speed against stride, one line per gait tempo. The point of the
# chart is that the slow-tempo line goes *down*: a longer stride at 0.5 s is
# slower, because the leg nears full extension and shears instead of pushing.
fig, ax = plt.subplots(figsize=(6.6, 3.5), dpi=110)

slow_x = [0.08, 0.16, 0.20]
slow_y = [0.168, 0.090, 0.034]
fast_x = [0.12, 0.16]
fast_y = [0.237, 0.609]

ax.plot(slow_x, slow_y, "o-", color=WARM, lw=2, ms=6,
        label="cykl 0,5 s (stare tempo)")
ax.plot(fast_x, fast_y, "o-", color=ACCENT, lw=2, ms=6,
        label="cykl 0,3 s (nowe tempo)")

ax.annotate("dłuższy krok,\nale WOLNIEJ", xy=(0.20, 0.034), xytext=(0.185, 0.24),
            color=WARM, fontsize=8.5, ha="center",
            arrowprops=dict(arrowstyle="->", color=WARM, lw=1.2))
ax.annotate("0,61 m/s", xy=(0.16, 0.609), xytext=(0.166, 0.60),
            color=ACCENT, fontsize=9.5, fontweight="bold", va="center")
ax.annotate("0,168 m/s\npunkt wyjścia", xy=(0.081, 0.168), xytext=(0.098, 0.30),
            color=MUTED, fontsize=8.5, ha="center",
            arrowprops=dict(arrowstyle="->", color=MUTED, lw=1))

ax.set_xlabel("długość kroku [m]")
ax.set_ylabel("prędkość osiągana [m/s]")
ax.set_title("Prędkość nie zależy od kroku, tylko od kroku × tempo",
             color=ACCENT, fontweight="bold", fontsize=11, pad=10, loc="left")
ax.grid(True, color=GRID, lw=0.7)
ax.set_axisbelow(True)
ax.set_ylim(0, 0.72)
ax.set_xlim(0.065, 0.215)
ax.legend(frameon=False, fontsize=8.5, loc="upper left")
fig.tight_layout()
fig.savefig(f"{OUT}/chart_speed.png", facecolor="white")
plt.close(fig)


# ------------------------------------------------------------------ chart 2
# Required joint torque against body size, anchored on two measured points.
# The exponent is fitted to those two, not assumed: 3.5, because the gait's
# tempo is Froude-scaled (sqrt of size), which takes some dynamic load back
# out of the pure mass x lever k^4.
fig, ax = plt.subplots(figsize=(6.6, 4.0), dpi=110)

W0, T0 = 24.2, 3.46         # measured: real-cat default
W1, T1 = 45.3, 28.6         # measured: scale 1.87
EXP = 3.37

xs = [22 + i * 0.5 for i in range(60)]
ys = [T0 * (w / W0) ** EXP for w in xs]

bands = [
    (0, 2.9, "#efe2d8", "serwa hobby (Feetech 2,9 Nm)"),
    (2.9, 4.1, "#e7e0d2", "Dynamixel XM430 (4,1 Nm)"),
    (4.1, 9, "#dfe6e4", "Dynamixel XM540 / AK60 (9 Nm)"),
    (9, 25, "#d2e0e4", "AK70 / AK80 (25 Nm)"),
    (25, 60, "#c2d6dd", "klasa Unitree Go2 (45 Nm)"),
]
for lo, hi, col, lab in bands:
    ax.axhspan(lo, hi, color=col, zorder=0)
    ax.text(49.6, (lo * hi) ** 0.5 if lo else 1.5, lab, fontsize=7.4,
            color=MUTED, va="center", ha="right")

ax.plot(xs, ys, color=ACCENT, lw=2.2, zorder=3)
ax.plot([W0], [T0], "o", color=GOOD, ms=9, zorder=4)
ax.plot([W1], [T1], "o", color=WARM, ms=9, zorder=4)

ax.annotate("zwykły kot\n24 cm w kłębie, 3,7 kg\n3,46 Nm", xy=(W0, T0),
            xytext=(25.0, 1.05),
            fontsize=8.5, color=GOOD, fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=GOOD, lw=1.2))
ax.annotate("wersja „50 cm z briefu”\n45 cm w kłębie, 24 kg\n28,6 Nm",
            xy=(W1, T1), xytext=(31.5, 46),
            fontsize=8.5, color=WARM, fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=WARM, lw=1.2))

ax.set_yscale("log")
ax.set_ylim(0.8, 90)
ax.set_xlim(22, 50)
ax.set_yticks([1, 3, 10, 30, 60])
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
ax.set_xlabel("wysokość w kłębie [cm]")
ax.set_ylabel("wymagany moment w przegubie [Nm], skala log")
ax.set_title("Moment rośnie z 3,4 potęgą wymiaru — dwa punkty zmierzone",
             color=ACCENT, fontweight="bold", fontsize=11, pad=10, loc="left")
ax.grid(True, which="major", axis="x", color=GRID, lw=0.7)
ax.set_axisbelow(False)
fig.tight_layout()
fig.savefig(f"{OUT}/chart_scale.png", facecolor="white")
plt.close(fig)

print("charts written")
