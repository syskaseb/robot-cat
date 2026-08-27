#!/usr/bin/env python3
"""What the cosmetic skin costs in servo headroom.

The skin is 20% of the robot's mass, and at 0.10 m/s the load is dominated by
gravity rather than inertia, so joint torque tracks total mass close enough to
linearly for this to be the right first-order answer.

Volumes come from verify.py's own render, so this cannot drift from the parts:

    python3 verify.py > /tmp/v.txt && python3 measure/mass_check.py /tmp/v.txt

With no argument it uses the figures recorded below, which is what README.md
quotes.
"""
import re
import sys

# g, build mass without any skin - from napedy-v4.pdf. The printed
# structure is inside this figure already; SKIN below is what the
# cosmetic layer adds on top, and both come from verify.py.
BASE = 2000.0
# Nm, worst joint. 95th percentile at 0.10 m/s, and the standing case.
WORST, STAND = 1.87, 0.70
# Nm, what an ST3215 delivers at the start and end of a 3S discharge.
FRESH, EMPTY = 3.08, 2.57

# Parts that hang on a swinging leg rather than on the trunk. Their grams
# cost more than trunk grams, because they load swing inertia as well.
LEG_PARTS = {"joint_cap", "thigh_fairing", "calf_fairing"}

SKIN = {
    "shell_back_front": 72.9, "shell_back_rear": 71.9, "shell_belly_front": 70.7,
    "shell_belly_rear": 60.9, "head_upper": 28.8, "head_lower": 15.3,
    "ear": 6.4, "neck_collar": 4.8, "tail_segment": 23.3,
    "joint_cap": 13.0, "thigh_fairing": 30.9, "calf_fairing": 26.3,
}


def from_verify(path):
    """Pull 'total' grams per part out of a verify.py run."""
    out = {}
    for line in open(path, encoding="utf-8"):
        m = re.match(r"(\S+)\s+.*?([\d.]+)g total", line)
        if m and m.group(1) in SKIN:
            out[m.group(1)] = float(m.group(2))
    return out or SKIN


def main():
    skin = from_verify(sys.argv[1]) if len(sys.argv) > 1 else SKIN
    legs = sum(g for n, g in skin.items() if n in LEG_PARTS)
    trunk = sum(skin.values()) - legs
    total = trunk + legs
    k = (BASE + total) / BASE

    print(f"trunk, head and tail   {trunk:7.1f} g")
    print(f"legs                   {legs:7.1f} g   <- the expensive grams")
    print(f"skin total             {total:7.1f} g   (+{100 * (k - 1):.1f}%)")
    print(f"robot                  {BASE + total:7.0f} g")
    print()
    for label, t in (("walking, 0.10 m/s", WORST), ("standing", STAND)):
        print(f"  {label:20s} {t:.2f} -> {t * k:.2f} Nm")
    print()
    print("ST3215 headroom:")
    for label, cap in (("battery full", FRESH), ("battery flat", EMPTY)):
        print(f"  {label:16s} {100 * (cap / WORST - 1):5.1f}%"
              f"  ->  {100 * (cap / (WORST * k) - 1):5.1f}%")
    print()
    print("thinner skin, same shape:")
    for wall in (1.4, 1.2):
        t = total * wall / 1.8
        kk = (BASE + t) / BASE
        print(f"  {wall} mm: {t:5.0f} g, "
              f"{100 * (EMPTY / (WORST * kk) - 1):.1f}% left when flat")


if __name__ == "__main__":
    main()
