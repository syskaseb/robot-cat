"""Recover the 17 named Pi planning reserves in the current PCB frame.

The earlier screw stacks have different axial lengths: screw centres of mass
are not registration datums. Use three labelled axes intersected with the PCB
midplane, plus the board centre. These are project occupied-space reservations,
not exact manufacturer component material. No document or source is modified.
"""
import hashlib
import json
import zipfile

import FreeCAD as A
import Part
import numpy as np

from receive_feline_global_case_candidates import placement
from plan_feline_underframe_jacket_retention import isolated


def construct(root, out, current):
    source = json.loads((out / 'n01-common-fore-layout.json').read_text())
    rows = {r['name']: r for r in source['parts']}
    names = [n for n in rows if n.startswith('PiBudget:')]
    assert len(names) == 17
    board_name = 'Ref_Material_Pi4NominalPCB_0_0'
    axes = ['Ref_Material_Pi410Screw_0_0', 'Ref_Material_Pi49Screw_0_0',
            'Ref_Material_Pi411Screw_0_0']
    archive = root / source['bundle']
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == source['bundle_sha256']
    loaded = {}
    with zipfile.ZipFile(archive) as z:
        for n in names + [board_name] + axes:
            raw = z.read(rows[n]['entry'])
            assert hashlib.sha256(raw).hexdigest() == rows[n]['sha256']
            s = Part.Shape()
            s.importBrepFromString(raw.decode())
            loaded[n] = s

    def axis_on_board(screw, board):
        face = max((f for f in board.Faces if isinstance(f.Surface, Part.Plane)),
                   key=lambda f: f.Area)
        normal = face.normalAt(0, 0)
        normal.normalize()
        cylinder = min((f for f in screw.Faces
                        if isinstance(f.Surface, Part.Cylinder)),
                       key=lambda f: f.Surface.Radius).Surface
        point, axis = cylinder.Center, cylinder.Axis
        assert abs(axis.dot(normal)) > .99
        return point + axis * ((board.Solids[0].CenterOfMass - point).dot(normal)
                               / axis.dot(normal))

    def witnesses(scene):
        board = scene[board_name]
        return np.array([list(board.Solids[0].CenterOfMass)]
                        + [list(axis_on_board(scene[n], board)) for n in axes])

    src, dst = witnesses(loaded), witnesses(current)
    sc, dc = src.mean(0), dst.mean(0)
    u, _, vt = np.linalg.svd((src - sc).T @ (dst - dc))
    rotation = vt.T @ u.T
    if np.linalg.det(rotation) < 0:
        vt[-1] *= -1
        rotation = vt.T @ u.T
    translation = dc - rotation @ sc
    residuals = np.linalg.norm(src @ rotation.T + translation - dst, axis=1)
    assert max(residuals) < 1e-6
    pose = placement(rotation, translation)
    mapped = isolated(loaded[board_name])
    mapped.Placement = pose * mapped.Placement
    differences = [isolated(mapped).cut(isolated(current[board_name])).Volume,
                   isolated(current[board_name]).cut(isolated(mapped)).Volume]
    assert max(differences) < 1e-5
    result = {}
    for n in names:
        s = isolated(loaded[n])
        s.Placement = pose * s.Placement
        s.check(True)
        assert s.isValid() and len(s.Solids) == 1
        result[n] = s
    return result, dict(source_bundle=source['bundle'],
                        source_bundle_sha256=source['bundle_sha256'],
                        board_bidirectional_difference_mm3=differences,
                        labelled_mount_axes=axes, residuals_mm=residuals.tolist(),
                        pose_matrix=list(pose.toMatrix().A),
                        exact_manufacturer_geometry=False)
