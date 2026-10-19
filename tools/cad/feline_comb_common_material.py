"""Reject a whole functional slot only through shared ACTUAL cap material.

One tiny common bottom-wall witness replaces label permutations when the
same fixed owner blocks the unchanged PETG wall. Bounds only propose a
solid; cut(subset, every actual cap) proves containment before use.
"""
import numpy as np
import FreeCAD as A
import Part
from feline_t18i_two_lane import unit


def common_bottom_wall(stations, slot, lane):
    models = [unit(st, slot, lane) for st in stations]
    caps = [m['parts']['split_common_comb'] for m in models]
    bounds = [s.BoundBox for s in caps]
    lo = np.array([max(b.XMin for b in bounds), max(b.YMin for b in bounds),
                   max(b.ZMin for b in bounds)])
    hi = np.array([min(b.XMax for b in bounds), min(b.YMax for b in bounds),
                   min(w['point_mm'][2]-w['radius_mm']-.15
                       for m in models for w in m['wires'])])
    assert np.all(hi-lo > 1e-5), (lo, hi)
    witness = Part.makeBox(*(hi-lo), A.Vector(*lo))
    receipts = []
    for st, cap in zip(stations, caps):
        outside = witness.copy().cut(cap.copy())
        assert outside.isNull() or outside.isValid()
        assert outside.Volume < 1e-7, (st['ref'], outside.Volume)
        receipts.append(dict(ref=st['ref'], outside_mm3=outside.Volume))
    return witness, receipts
