"""Decision chart: earlier simulation requirement against estimated servo
stall torque as the battery drains. Curves use catalogue torque values."""

import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

INK, ACCENT, WARM, MUTED, GRID = "#16191d", "#0f4c5c", "#b3541e", "#5f6b73", "#dfe5e8"
GOOD = "#1c6b45"

plt.rcParams.update({
    # See charts.py - use matplotlib's bundled font consistently.
    "font.family": "DejaVu Sans", "font.size": 9,
    "axes.edgecolor": MUTED, "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.spines.top": False, "axes.spines.right": False,
})

OUT = str(pathlib.Path(__file__).resolve().parent)

fig, ax = plt.subplots(figsize=(6.6, 3.8), dpi=110)

# Servo stall torque falls with supply voltage - for a brushed DC motor stall
# current is V/R and torque follows it. Estimate anchored ONLY at 30 kg.cm
# at 12 V. The 19.5 kg.cm / 7.4 V product is a different winding, not a
# second calibration point. Stall does NOT establish continuous capability.
volts = [12.6, 12.2, 11.8, 11.4, 11.1, 10.8, 10.5]
st3215 = [30.0 * min(v,12.0) / 12.0 * 0.0980665 for v in volts]

ax.plot(volts, st3215, "-o", color=ACCENT, lw=2.4, ms=5, label="ST3215 12 V — szacunek stall")

ax.axhline(1.93, color=MUTED, lw=1.5, ls="--")

ax.text(12.55, 2.08, "stary model ROS: 1,93 Nm, nie obecny CAD", color=MUTED,
        fontsize=9, fontweight="bold", va="bottom")

ax.annotate("brak potwierdzonego\nmomentu ciągłego", xy=(10.5, 2.57), xytext=(10.85, 1.15),
            fontsize=8.4, color=ACCENT, ha="center",
            arrowprops=dict(arrowstyle="->", color=ACCENT, lw=1.2))

ax.set_xlabel("napięcie pakietu 3S LiPo [V]  —  od pełnego do rozładowanego")
ax.set_ylabel("moment [Nm]")
ax.set_title("Moment zatrzymania nie zatwierdza napędu",
             color=ACCENT, fontweight="bold", fontsize=11, pad=10, loc="left")
ax.invert_xaxis()
ax.set_ylim(0.8, 4.4)
ax.grid(True, color=GRID, lw=0.7)
ax.set_axisbelow(True)
ax.legend(frameon=False, fontsize=8.5, loc="upper right")
fig.tight_layout()
fig.savefig(f"{OUT}/chart_decision.png", facecolor="white")
print("chart_decision written")
