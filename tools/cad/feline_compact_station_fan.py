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
