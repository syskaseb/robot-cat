#!/usr/bin/env python3
"""Render every .scad part and check it is one watertight, printable solid.

Usage: python3 verify.py
Needs: openscad, and `pip install trimesh scipy`.
"""
import pathlib
import subprocess
import sys

import trimesh

HERE = pathlib.Path(__file__).parent
# Structural parts first, then the cosmetic skin. Order is the order you
# would print them in if you were building the cat from nothing.
PARTS = [
    "thigh_segment", "calf_segment", "hip_link", "trunk_frame",
    "pi_shelf", "paw_pad",
    "shell_back_front", "shell_back_rear",
    "shell_belly_front", "shell_belly_rear",
    "head_upper", "head_lower", "ear", "neck_collar",
    "joint_housing", "eye_lens", "thigh_fairing", "calf_fairing",
    "tail_segment",
]

# How many of each go into one cat, for the mass total.
COUNT = {
    "thigh_segment": 4, "calf_segment": 4, "hip_link": 4, "trunk_frame": 1,
    "pi_shelf": 1, "paw_pad": 4,
    "shell_back_front": 1, "shell_back_rear": 1,
    "shell_belly_front": 1, "shell_belly_rear": 1,
    "head_upper": 1, "head_lower": 1, "ear": 2, "neck_collar": 1,
    "joint_housing": 8, "eye_lens": 2, "thigh_fairing": 4, "calf_fairing": 4,
    "tail_segment": 11,
}

PETG_DENSITY = 1.27e-3   # g/mm3

# Seconds to allow one part. The structural parts render in seconds; a body
# panel is a CGAL boolean between two hulls of seven spheres and takes about
# five minutes, so a whole run is roughly an hour. Do not lower this without
# checking the slowest part still fits - a timeout here looks exactly like a
# broken part until you read the traceback.
RENDER_TIMEOUT = 900

def check(name):
    scad = HERE / f"{name}.scad"
    if not scad.exists():
        return None
    stl = HERE / f"_check_{name}.stl"
    try:
        r = subprocess.run(["openscad", "--render", "-o", str(stl), str(scad)],
                           capture_output=True, text=True,
                           timeout=RENDER_TIMEOUT)
    except subprocess.TimeoutExpired:
        return f"TIMED OUT after {RENDER_TIMEOUT}s - raise RENDER_TIMEOUT"
    if r.returncode != 0:
        return f"FAILED TO RENDER: {r.stderr.strip().splitlines()[-1] if r.stderr else 'unknown error'}"
    m = trimesh.load(str(stl))
    stl.unlink()
    ok = m.is_watertight and m.body_count == 1
    n = COUNT.get(name, 1)
    grams = m.volume * PETG_DENSITY
    return dict(
        ok=ok, n=n, grams=grams,
        line=(f"{'OK ' if ok else 'PROBLEM'}  watertight={m.is_watertight}  "
              f"bodies={m.body_count}  x{n}  {grams:5.1f}g each  "
              f"{grams * n:6.1f}g total  bbox={(m.bounds[1] - m.bounds[0]).round(1)}"))

if __name__ == "__main__":
    bad = False
    total = 0.0
    for name in PARTS:
        result = check(name)
        if result is None:
            continue
        if isinstance(result, str):          # render failure or timeout
            print(f"{name:18s} {result}")
            bad = True
            continue
        print(f"{name:18s} {result['line']}")
        total += result["grams"] * result["n"]
        bad = bad or not result["ok"]
    print()
    print(f"{'PETG for one cat':18s} {total:6.1f} g")
    sys.exit(1 if bad else 0)
