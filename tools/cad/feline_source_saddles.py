"""Nine millimetres of an existing line/arc; open flat PETG plus selectedT18I.

No extra wire length, rigid cylindrical clamp, reduced bend or hidden head.
Nominal fit/pull/creep and tightening remain delivered-prototype gates.
"""
import numpy as np
import FreeCAD as A
import Part
from receive_feline_positive_service_deck import open_grip


def segment(row):
    a,b=A.Vector(*row['start']),A.Vector(*row['end'])
    return Part.makeLine(a,b) if row['kind']=='line' else Part.Arc(a,A.Vector(*row['mid']),b).toShape()


def build(row,start,side,band_at,channel_band=False):
    edge=segment(row);stop=start+9.;assert start>=0 and stop<=edge.Length+1e-6
    param=lambda s:edge.FirstParameter+(edge.LastParameter-edge.FirstParameter)*s/edge.Length
    p=edge.valueAt(param(start));t=edge.tangentAt(param(start));side=A.Vector(*side);side.normalize()
    assert abs(t.dot(side))<1e-6
    cross=t.cross(side);assert abs(cross.Length-1)<1e-6
    trim=edge.Curve.toShape(param(start),param(stop));path=Part.Wire([trim])
    corners=[p+side*y+cross*z for y,z in ((2.5,-2.3),(4.5,-2.3),(4.5,2.3),(2.5,2.3),(2.5,-2.3))]
    pad=path.makePipeShell([Part.Wire(Part.makePolygon(corners).Edges)],True,False)
    q=edge.valueAt(param(band_at));axis=edge.tangentAt(param(band_at))
    kit=open_grip(np.array(list(q-axis*4.5)),np.array(list(axis)),np.array(list(side)),4.5)
    if channel_band:
        # A rectangular tie is tangent, whereas this pad follows an arc.
        # Model its actual printed passage; never accept positive overlap.
        channel=kit['band'].makeOffsetShape(.2,1e-6)
        assert channel.isValid() and channel.Solids
        pad=pad.cut(channel)
    kit['pad']=pad
    for n,s in kit.items():assert s.isValid() and len(s.Solids)==1,n
    for k in ('band','head'):
        overlap=pad.common(kit[k]);assert overlap.isNull() or overlap.isValid()
        assert overlap.Volume<1e-5,(k,overlap.Volume)
    nylon=kit['band'].fuse(kit['head']);assert nylon.isValid() and len(nylon.Solids)==1
    assert abs(kit['head'].Volume-5*4.3*5.3)<1e-5
    proof=dict(full_jacket_grip_arclength_mm=[start,stop],band_centre_arclength_mm=band_at,
        extra_wire_length_mm=0,open_flat_saddle_not_bore=True,nominal_pad_wall_mm=2,
        selected_T18I_section_mm=[2.5,1.2],full_selected_head_mm=[5,4.3,5.3],
        delivered_wire_fit_tightening_pull_and_PETG_creep_gate=True)
    if channel_band:proof['printed_band_channel_mm']=.2
    return kit,proof
