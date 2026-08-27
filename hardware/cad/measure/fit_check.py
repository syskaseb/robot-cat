#!/usr/bin/env python3
"""Check the cosmetic skin fits its box, and that the seam tabs land on it.

Two things drift silently when body_stations is edited:

  - The stations are sphere CENTRES, so a station of radius r at x puts skin
    out at x +/- r. Sizing them as if they were points on the surface grows a
    300mm body to 356mm without anything complaining.
  - The seam tabs are placed at fixed x. Reshaping the body moves the wall
    they are supposed to reach, and a tab whose screw boss ends up outside
    the skin is not obvious until something is printed.

Usage: python3 measure/fit_check.py
"""
import math
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
CAD = HERE.parent


def scalars(text, *names):
    out = {}
    for n in names:
        m = re.search(rf"^\s*{n}\s*=\s*([-0-9.]+)\s*;", text, re.M)
        if m:
            out[n] = float(m.group(1))
    return out


def half_width(stations, z_scale, x, z=0.0):
    """Half-width of the hull of spheres at (x, z).

    The hull's outline is the convex hull of each sphere's cross-section at
    this z. Taking the max over single circles and over every external
    tangent slightly OVERSTATES it where three or more circles overlap, which
    is the safe direction here: a tab sized against this reaches the wall.
    """
    circ = []
    for cx, r, lift in stations:
        rr = r * r - ((z - lift) / z_scale) ** 2
        if rr > 0:
            circ.append((cx, math.sqrt(rr)))
    best = 0.0
    for cx, r in circ:
        if abs(x - cx) < r:
            best = max(best, math.sqrt(r * r - (x - cx) ** 2))
    for i, (x1, r1) in enumerate(circ):
        for x2, r2 in circ[i + 1:]:
            d, dr = x2 - x1, r2 - r1
            if d * d <= dr * dr or not x1 <= x <= x2:
                continue
            best = max(best, (r1 * d + dr * (x - x1)) / math.sqrt(d * d - dr * dr))
    return best


def main():
    params = (CAD / "params.scad").read_text(encoding="utf-8")
    shell = (CAD / "shell_params.scad").read_text(encoding="utf-8")
    box = scalars(params, "body_length", "body_width", "body_height")
    block = re.search(r"body_stations\s*=\s*\[(.*?)\];", shell, re.S).group(1)
    rows = [[float(v) for v in re.findall(r"-?[0-9.]+", line)]
            for line in block.splitlines() if re.search(r"\[.*\]", line)]

    hw = box["body_width"] / 2
    z_scale = (box["body_height"] / 2) / hw

    lo_x = min(x - r for x, r, _ in rows)
    hi_x = max(x + r for x, r, _ in rows)
    hi_y = max(r for _, r, _ in rows)
    lo_z = min(lift - r * z_scale for _, r, lift in rows)
    hi_z = max(lift + r * z_scale for _, r, lift in rows)

    checks = [
        ("length", hi_x - lo_x, box["body_length"]),
        ("width", 2 * hi_y, box["body_width"]),
        ("height", hi_z - lo_z, box["body_height"]),
    ]
    print(f"{len(rows)} stations, vertical scale {z_scale:.3f}")
    print(f"  skin spans x {lo_x:+.1f} .. {hi_x:+.1f}, "
          f"y +/-{hi_y:.1f}, z {lo_z:+.1f} .. {hi_z:+.1f}")
    bad = False
    for name, got, limit in checks:
        slack = limit - got
        flag = "OK " if slack >= -1e-6 else "OVER"
        if slack < 0:
            bad = True
        print(f"  {flag} {name:7s} {got:7.1f} of {limit:6.1f}  "
              f"({slack:+.1f} mm spare)")

    lib = (CAD / "shell_lib.scad").read_text(encoding="utf-8")
    tabs = [float(v) for v in re.findall(
        r"-?[0-9.]+",
        re.search(r"seam_tab_x[ =]+\[([^\]]*)\]", lib).group(1))]
    min_hw = scalars(lib, "tab_min_hw")["tab_min_hw"]
    screw_y = scalars(lib, "tab_screw_y")["tab_screw_y"]
    hip_x = scalars(params, "hip_x")["hip_x"]
    relief = 18.0          # hip_relief_d / 2, rounded up

    print()
    print(f"seam tabs (need half-width >= {min_hw:.0f} and no hip relief):")
    for x in tabs:
        hw = half_width(rows, z_scale, x)
        in_hip = abs(abs(x) - hip_x) < relief + 6
        ok = hw >= min_hw and not in_hip
        bad = bad or not ok
        note = "in the hip relief" if in_hip else ""
        print(f"  {'OK ' if ok else 'BAD'} x = {x:+7.1f}   wall at "
              f"{hw:5.1f}, screw at {screw_y:.0f}  {note}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
