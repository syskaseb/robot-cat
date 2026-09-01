"""Find cylindrical bores in an STL by fitting circles to face patches.

A bore's wall is the set of faces whose normals are perpendicular to the bore
axis and point at it. Group connected faces, keep the groups that fit a circle,
report centre and diameter.
"""
import sys
import numpy as np
import trimesh
from scipy.optimize import least_squares


def fit_circle(p2):
    c0 = p2.mean(axis=0)
    r0 = np.linalg.norm(p2 - c0, axis=1).mean()

    def res(v):
        return np.linalg.norm(p2 - v[:2], axis=1) - v[2]

    s = least_squares(res, [c0[0], c0[1], r0])
    return s.x, np.abs(s.fun).max()


def bores(mesh, axis, tol=0.08, min_faces=6):
    a = np.asarray(axis, float)
    a /= np.linalg.norm(a)
    u = np.cross(a, [1, 0, 0] if abs(a[0]) < 0.9 else [0, 1, 0])
    u /= np.linalg.norm(u)
    v = np.cross(a, u)
    keep = np.abs(mesh.face_normals @ a) < tol
    idx = np.flatnonzero(keep)
    if len(idx) < min_faces:
        return []
    sub = mesh.submesh([idx], append=True)
    out = []
    for comp in sub.split(only_watertight=False):
        if len(comp.faces) < min_faces:
            continue
        pts = comp.triangles_center
        p2 = np.column_stack([pts @ u, pts @ v])
        (cx, cy, r), err = fit_circle(p2)
        if r < 0.5 or r > 40 or err > 0.25:
            continue
        # inward-facing normals confirm a bore rather than a boss
        n2 = np.column_stack([comp.face_normals @ u, comp.face_normals @ v])
        radial = p2 - [cx, cy]
        inward = (np.sum(n2 * radial, axis=1) < 0).mean()
        along = pts @ a
        out.append(dict(d=round(2 * r, 2), centre=(round(cx, 2), round(cy, 2)),
                        span=(round(along.min(), 2), round(along.max(), 2)),
                        bore=inward > 0.8, err=round(err, 3)))
    return out


if __name__ == '__main__':
    for name in sys.argv[1:]:
        m = trimesh.load(name)
        print(f'\n=== {name} ===  bbox {(m.bounds[1] - m.bounds[0]).round(2)}')
        for ax, lbl in zip(np.eye(3), 'XYZ'):
            found = [b for b in bores(m, ax) if b['bore']]
            if not found:
                continue
            print(f'  bores along {lbl}:')
            for b in sorted(found, key=lambda b: (b['d'], b['centre'])):
                print(f'    O{b["d"]:6.2f} mm  centre {b["centre"]}  '
                      f'depth {b["span"]}  fit±{b["err"]}')
