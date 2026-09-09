"""Offscreen previews of the mechanical prototype.

Gazebo sensors and the FreeCAD GUI both need a render window, which is exactly
what this machine (and CI) does not have, so the parts are tessellated and
rasterised here with a plain z-buffer.  The images are for judging proportion
and for reviewing a diff; they are not renders of print-ready geometry.

Run headless::

    freecadcmd tools/freecad/wavego_cat_render.py
"""

import math
from pathlib import Path

import numpy as np
from PIL import Image

import FreeCAD as App

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "hardware/wavego/mechanics"
DOCUMENT = ROOT / "hardware/wavego/WAVEGO_cat_mechanical.FCStd"

SHELL = (0.36, 0.39, 0.43)
ACCENT = (0.86, 0.83, 0.74)
MOUNT = (0.55, 0.58, 0.62)
TAIL = (0.30, 0.55, 0.62)
SOURCE = (0.22, 0.23, 0.25)

COLOURS = {
    "CAT_Base_Chassis_Tray": SHELL,
    "CAT_Spine_Front": (0.42, 0.45, 0.49),
    "CAT_Spine_Rear": (0.32, 0.35, 0.39),
    "CAT_Head_Shell": SHELL,
    "CAT_Face_Mask": ACCENT,
    "CAT_Camera_Carrier": MOUNT,
    "CAT_Neck_Load_Frame": MOUNT,
    "CAT_Tail_Mount": MOUNT,
}

VIEWS = {
    "preview-side": dict(eye=(0.0, -1.0, 0.12), up=(0, 0, 1), size=(1400, 760)),
    "preview-iso": dict(eye=(-0.72, -0.62, 0.31), up=(0, 0, 1), size=(1400, 900)),
    "preview-head": dict(eye=(-0.78, -0.52, 0.34), up=(0, 0, 1), size=(1100, 900),
                         focus=(-150.0, 0.0, 185.0), span=170.0),
    "preview-tail": dict(eye=(-0.10, -0.55, 0.83), up=(0, 0, 1), size=(1200, 800),
                         focus=(215.0, 0.0, 105.0), span=190.0),
}


def triangles(doc):
    out = []
    for obj in doc.Objects:
        if obj.TypeId != "Part::Feature" or obj.Shape.isNull():
            continue
        if obj.Name.startswith(("Axis_", "CameraFOV", "CameraMountPattern",
                                "StudyMountingAxes", "_0", "_1", "_2")):
            continue
        if obj.Label in ("TopCover", "Part9", "Part001"):
            continue
        colour = COLOURS.get(obj.Name)
        if colour is None:
            colour = TAIL if obj.Name.startswith("CAT_Tail_Seg") else None
        if colour is None and obj.Name.startswith("CAT_"):
            colour = SHELL
        if colour is None:
            colour = SOURCE
        shape = obj.Shape.copy()
        shape.Placement = obj.getGlobalPlacement()
        points, facets = shape.tessellate(1.2)
        verts = np.array([[p.x, p.y, p.z] for p in points], dtype=float)
        if not len(facets):
            continue
        out.append((verts, np.array(facets, dtype=int), colour))
    return out


def render(meshes, eye, up, size, focus=None, span=None, path=None):
    forward = np.array(eye, dtype=float)
    forward /= np.linalg.norm(forward)
    right = np.cross(np.array(up, dtype=float), forward)
    right /= np.linalg.norm(right)
    upv = np.cross(forward, right)

    allv = np.vstack([m[0] for m in meshes])
    centre = np.array(focus) if focus else (allv.min(0) + allv.max(0)) / 2.0
    width, height = size
    if span is None:
        projected = (allv - centre) @ np.stack([right, upv], axis=1)
        span = 2.2 * max(projected[:, 0].max(), -projected[:, 0].min(),
                         (projected[:, 1].max() - projected[:, 1].min()))
    scale = width / span

    colour_buf = np.zeros((height, width, 3), dtype=float)
    colour_buf[:] = np.array([0.94, 0.94, 0.93])
    depth = np.full((height, width), -1e9)
    light = np.array([-0.45, -0.72, 0.53])
    light /= np.linalg.norm(light)

    for verts, facets, base in meshes:
        local = verts - centre
        sx = local @ right * scale + width / 2.0
        sy = height / 2.0 - local @ upv * scale
        sz = local @ forward
        base = np.array(base, dtype=float)
        for tri in facets:
            xs, ys, zs = sx[tri], sy[tri], sz[tri]
            x0, x1 = int(max(0, math.floor(xs.min()))), int(min(width - 1, math.ceil(xs.max())))
            y0, y1 = int(max(0, math.floor(ys.min()))), int(min(height - 1, math.ceil(ys.max())))
            if x1 < x0 or y1 < y0:
                continue
            a = np.array([xs[1] - xs[0], ys[1] - ys[0]])
            b = np.array([xs[2] - xs[0], ys[2] - ys[0]])
            det = a[0] * b[1] - a[1] * b[0]
            if abs(det) < 1e-9:
                continue
            gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5,
                                 np.arange(y0, y1 + 1) + 0.5)
            px, py = gx - xs[0], gy - ys[0]
            u = (px * b[1] - py * b[0]) / det
            v = (py * a[0] - px * a[1]) / det
            inside = (u >= -1e-6) & (v >= -1e-6) & (u + v <= 1 + 1e-6)
            if not inside.any():
                continue
            z = zs[0] + u * (zs[1] - zs[0]) + v * (zs[2] - zs[0])
            e1 = verts[tri[1]] - verts[tri[0]]
            e2 = verts[tri[2]] - verts[tri[0]]
            normal = np.cross(e1, e2)
            norm = np.linalg.norm(normal)
            if norm < 1e-12:
                continue
            normal /= norm
            if normal @ forward < 0:
                normal = -normal
            shade = 0.32 + 0.68 * max(0.0, float(normal @ light))
            patch = depth[y0:y1 + 1, x0:x1 + 1]
            mask = inside & (z > patch)
            if not mask.any():
                continue
            patch[mask] = z[mask]
            colour_buf[y0:y1 + 1, x0:x1 + 1][mask] = base * shade

    image = Image.fromarray((np.clip(colour_buf, 0, 1) * 255).astype(np.uint8))
    if path:
        image.save(path)
    return image


def main(doc=None):
    doc = doc or App.openDocument(str(DOCUMENT))
    meshes = triangles(doc)
    for name, view in VIEWS.items():
        options = dict(view)
        size = options.pop("size")
        render(meshes, options.pop("eye"), options.pop("up"), size,
               path=str(OUT / (name + ".png")), **options)
        print("wrote", name)


if __name__ == "__main__":
    main()
