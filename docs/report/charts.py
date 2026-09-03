"""Speed chart for the actuator report. Every plotted point is measured."""

import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

INK, ACCENT, WARM, MUTED, GRID = "#16191d", "#0f4c5c", "#b3541e", "#5f6b73", "#dfe5e8"
GOOD = "#1c6b45"

plt.rcParams.update({
    # Bundled with matplotlib; a single family avoids broken fallback glyphs.
    "font.family": "DejaVu Sans",
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
        label="cykl 0,5 s")
ax.plot(fast_x, fast_y, "o-", color=ACCENT, lw=2, ms=6,
        label="cykl 0,3 s — obecne tempo")

ax.annotate("dłuższy krok,\nale WOLNIEJ", xy=(0.20, 0.034), xytext=(0.185, 0.24),
            color=WARM, fontsize=8.5, ha="center",
            arrowprops=dict(arrowstyle="->", color=WARM, lw=1.2))
ax.annotate("0,61 m/s", xy=(0.16, 0.609), xytext=(0.166, 0.60),
            color=ACCENT, fontsize=9.5, fontweight="bold", va="center")
ax.annotate("0,168 m/s", xy=(0.081, 0.168), xytext=(0.098, 0.30),
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


print("chart_speed written")
