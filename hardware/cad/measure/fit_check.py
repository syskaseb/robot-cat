#!/usr/bin/env python3
"""Check the seam tabs land on the wall of the skin that actually exists.

The skin is a lofted mesh built by skin/loft.py, and loft.py already asserts
that it fits inside the box the torque budget was computed on. What it cannot
know is where shell_lib puts the seam tabs, which are placed at fixed x and
have to reach the wall wherever the loft leaves it.

This used to check `body_stations` in shell_params.scad. That table drove a
hull of spheres and is gone - the loft replaced it. A check that validates a
table nothing reads is worse than no check, because it passes while the real
surface drifts, so it now reads the loft's own sections.

Usage, from hardware/cad:

    python3 measure/fit_check.py
"""

import pathlib
import re
import sys

import numpy as np
from scipy.interpolate import PchipInterpolator

HERE = pathlib.Path(__file__).resolve().parent
CAD = HERE.parent
sys.path.insert(0, str(CAD / "skin"))


def scalars(text, *names):
    out = {}
    for n in names:
        m = re.search(rf"^\s*{n}\s*=\s*([-0-9.]+)\s*;", text, re.M)
        if m:
            out[n] = float(m.group(1))
    return out


def wall_at(x, z=0.0):
    """Half-width of the lofted skin at (x, z), from the loft's own table."""
    import loft

    a = np.array(loft.SECTIONS, dtype=float)
    xs = a[:, 0]
    hw, top, bot, n = (PchipInterpolator(xs, a[:, i])(x) for i in (1, 2, 3, 4))
    zc = (top + bot) / 2.0
    half_h = (top - zc) if z >= zc else (zc - bot)
    if half_h <= 0:
        return 0.0
    # invert the superellipse: given z, how far out does the section reach
    s = min(abs((z - zc) / half_h), 1.0) ** (n / 2.0)
    c = max(0.0, 1.0 - s ** 2) ** 0.5 if s <= 1.0 else 0.0
    return float(hw * c ** (2.0 / n) if c > 0 else 0.0)


def main():
    lib = (CAD / "shell_lib.scad").read_text(encoding="utf-8")
    params = (CAD / "params.scad").read_text(encoding="utf-8")

    tabs = [float(v) for v in re.findall(
        r"-?[0-9.]+",
        re.search(r"seam_tab_x[ =]+\[([^\]]*)\]", lib).group(1))]
    g = scalars(lib, "tab_min_hw", "tab_screw_y", "tab_y_in")
    hip_x = scalars(params, "hip_x")["hip_x"]
    relief = 18.0 + 6.0          # hip_relief_d / 2, plus the tab's own width

    seam = scalars(lib, "flank_seam_z").get("flank_seam_z", 0.0)
    print(f"seam tabs at z = {seam:.0f}, need the wall at "
          f"{g['tab_min_hw']:.0f}mm or more and no hip relief:")
    bad = False
    for x in tabs:
        hw = wall_at(x, seam)
        in_hip = abs(abs(x) - hip_x) < relief
        ok = hw >= g["tab_min_hw"] and not in_hip
        bad = bad or not ok
        note = "  <- inside the hip relief" if in_hip else ""
        print(f"  {'OK ' if ok else 'BAD'} x = {x:+7.1f}   wall at {hw:5.1f}, "
              f"rib runs {g['tab_y_in']:.0f}..wall, screw at "
              f"{g['tab_screw_y']:.0f}{note}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
