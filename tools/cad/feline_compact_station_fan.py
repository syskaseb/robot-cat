"""Low common typed-radius30deg fan at the SAME received WAGO mouths.

Retain the entire case/first9/full cap/band/head. Only five following wire
arcs change. A source minimumR is not the old template's larger commonR.
"""
import math
import numpy as np
import FreeCAD as A
import Part
from feline_station_zone_domains import materialise
from feline_zone_station_templates import zone_build
from feline_zone_station_templates import vertical_build
from feline_underplate_station_templates import build_underplate
from feline_flat_station_templates import build


def unit(st,choice):
    slot=choice['slot'];recipe=choice['base_recipe']
    assert recipe['family']=='FLAT' and not st['fixed_identity_pose']
    parts,kinds=materialise(st,slot,recipe);model=zone_build(st,slot,recipe['departure'],recipe['bend_mode'])
    minimum={p['endpoint']:p['minimum_project_R_mm'] for p in st['ports']}
    wires=[];theta=math.radians(30);b=np.array([0.,0.,1.])
    for w in model['wires']:
        q=np.asarray(w['point_mm']);d=np.asarray(w['departure_axis']);radius=w['radius']
        R=max(12.4,minimum[w['endpoint']]);a=q+9*d
        point=lambda t:a+R*math.sin(t)*d+R*(1-math.cos(t))*b
        end=point(theta);axis=math.cos(theta)*d+math.sin(theta)*b;tip=end+9*axis
        edges=[Part.makeLine(A.Vector(*q),A.Vector(*a)),
               Part.Arc(A.Vector(*a),A.Vector(*point(theta/2)),A.Vector(*end)).toShape(),
               Part.makeLine(A.Vector(*end),A.Vector(*tip))]
        path=Part.Wire(edges);s=path.makePipeShell([Part.Wire([Part.makeCircle(radius,A.Vector(*q),A.Vector(*d))])],True,False)
        assert s.isValid() and len(s.Solids)==1
        parts['wire:'+w['endpoint']]=s
        wires.append(dict(endpoint=w['endpoint'],wire=w['wire'],point_mm=q.tolist(),departure_axis=d.tolist(),
            radius=radius,R_mm=R,minimum_R_mm=minimum[w['endpoint']],first_mm=9,
            grip_length_mm=9,before_arc_grip_line_mm=[q.tolist(),a.tolist()],
            sweep_degrees=30,bend_unit=b.tolist(),after_arc_end_mm=tip.tolist(),after_arc_exit_axis=axis.tolist()))
    assert len(wires)==len(st['ports'])
    return dict(parts=parts,kinds=kinds,wires=wires,reused_jacket_lands=[],
                case_first9_full_cap_band_head_unchanged=True,roots_and_full_length_capacity_open=True)


def legacy_unit(st,choice):
    """Shared rule for the6 existing fan-bearing stations, not local offsets.

    Keep actual case/all4or5 mouths/first9/full stock and protected W043.
    Remove the arbitrary mandatory90degree sweep for custom wire prefixes.
    """
    slot=choice['slot'];r=choice['base_recipe'];parts,kinds=materialise(st,slot,r)
    if r['family']=='UNDER_PLATFORM_SHARED_REMOVABLE_COMBS':model=build_underplate(st,slot,r['bend_side'],r['head_side'])
    elif st['fixed_identity_pose']:model=build(st,'inner',1,-1)
    elif r['family']=='VERTICAL_DEPARTURE_TWO_SIDE_TIERS':model=vertical_build(st,slot,r['departure_z'],r['lever_sign'],r['head_side'])
    else:model=zone_build(st,slot,r['departure'],r['bend_mode'])
    minimum={p['endpoint']:p['minimum_project_R_mm'] for p in st['ports']};theta=math.radians(30);wires=[]
    for w in model['wires']:
        q=np.asarray(w['point_mm']);d=np.asarray(w['departure_axis']);b=np.asarray(w['bend_unit']);radius=w['radius']
        assert abs(d@b)<1e-6
        R=max(12.4,minimum[w['endpoint']]);a=q+9*d
        point=lambda t:a+R*math.sin(t)*d+R*(1-math.cos(t))*b
        end=point(theta);axis=math.cos(theta)*d+math.sin(theta)*b;tip=end+9*axis
        path=Part.Wire([Part.makeLine(A.Vector(*q),A.Vector(*a)),
            Part.Arc(A.Vector(*a),A.Vector(*point(theta/2)),A.Vector(*end)).toShape(),Part.makeLine(A.Vector(*end),A.Vector(*tip))])
        s=path.makePipeShell([Part.Wire([Part.makeCircle(radius,A.Vector(*q),A.Vector(*d))])],True,False)
        assert s.isValid() and len(s.Solids)==1
        parts['wire:'+w['endpoint']]=s
        wires.append(dict(endpoint=w['endpoint'],wire=w['wire'],point_mm=q.tolist(),departure_axis=d.tolist(),
            radius=radius,R_mm=R,minimum_R_mm=minimum[w['endpoint']],first_mm=9,grip_length_mm=9,
            before_arc_grip_line_mm=[q.tolist(),a.tolist()],after_arc_end_mm=tip.tolist(),sweep_degrees=30,
            after_arc_exit_axis=axis.tolist(),bend_unit=b.tolist()))
    for w in wires:
        for n,t in parts.items():
            if n.startswith('wire:'):continue
            common=parts['wire:'+w['endpoint']].copy().common(t.copy());assert common.isNull() or common.isValid()
            assert common.Volume<1e-7,(st['ref'],w['endpoint'],n,common.Volume)
    return dict(parts=parts,kinds=kinds,wires=wires,reused_jacket_lands=model['reused_jacket_lands'],
                all_case_first9_cap_band_head_and_protected_factory_unchanged=True,
                roots_and_full_length_capacity_open=True)
