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
PARTS = ["thigh_segment", "calf_segment", "hip_link", "trunk_frame",
         "pi_shelf", "paw_pad"]

def check(name):
    scad = HERE / f"{name}.scad"
    if not scad.exists():
        return None
    stl = HERE / f"_check_{name}.stl"
    r = subprocess.run(["openscad", "--render", "-o", str(stl), str(scad)],
                       capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        return f"FAILED TO RENDER: {r.stderr.strip().splitlines()[-1] if r.stderr else 'unknown error'}"
    m = trimesh.load(str(stl))
    stl.unlink()
    ok = m.is_watertight and m.body_count == 1
    verdict = "OK" if ok else "PROBLEM"
    return (f"{verdict}  watertight={m.is_watertight}  bodies={m.body_count}  "
            f"volume={m.volume:.0f}mm3  bbox={m.bounds[1]-m.bounds[0]}")

if __name__ == "__main__":
    bad = False
    for name in PARTS:
        result = check(name)
        if result is None:
            continue
        print(f"{name:16s} {result}")
        if "PROBLEM" in result or "FAILED" in result:
            bad = True
    sys.exit(1 if bad else 0)
