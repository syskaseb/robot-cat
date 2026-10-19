"""Two opposed whole-bank exit planes instead of intersecting quarter fans.

All real terminal mouths/first9/full BEFORE grips and bought parts retained.
Each side turns30deg towards its own Z-plane at the retained minimum-safe R.
N01 only constructive geometry; complete world/mutual/length/root gates open.
"""
import copy
import math
import numpy as np
import FreeCAD as A
import Part
from feline_remaining_kits import materialise as original_material


def candidates(groups):
    result={}
    for group,options in groups.items():
        if not group.startswith('Bank:'):continue
        heads={}
        for r in options:
            if r.get('grip_site')=='AFTER_BEND':continue
            h=r.get('complete_band_head_degrees',r.get('head_degrees'))
            assert h is not None
            heads.setdefault(h,r)
        result[group]=[dict(base_recipe=copy.deepcopy(r),shared_exit_lanes='TWO_OPPOSED_Z30') for r in heads.values()]
    assert len(result)==24 and all(result.values())
    return result


def materialise(group,recipe):
    r=recipe['base_recipe'];assert recipe['shared_exit_lanes']=='TWO_OPPOSED_Z30'
    assert r.get('grip_site')!='AFTER_BEND' and r['first_mm']==9
    parts,kinds=original_material(group,r)
    q=np.asarray(r['point_mm']);d=np.asarray(r['departure_axis']);b=np.array([0.,0.,1. if q[1]>0 else -1.])
    assert abs(d@b)<1e-6
    radius=r.get('radius_mm',r.get('radius'));R=r['R_mm'];theta=math.radians(30);a=q+9*d
    point=lambda t:a+R*math.sin(t)*d+R*(1-math.cos(t))*b
    end=point(theta);axis=math.cos(theta)*d+math.sin(theta)*b;tip=end+9*axis
    path=Part.Wire([Part.makeLine(A.Vector(*q),A.Vector(*a)),
        Part.Arc(A.Vector(*a),A.Vector(*point(theta/2)),A.Vector(*end)).toShape(),Part.makeLine(A.Vector(*end),A.Vector(*tip))])
    wire=path.makePipeShell([Part.Wire([Part.makeCircle(radius,A.Vector(*q),A.Vector(*d))])],True,False)
    assert wire.isValid() and len(wire.Solids)==1
    wires=[n for n in parts if kinds[n]=='proposal_wire'];assert len(wires)==1
    parts[wires[0]]=wire
    return parts,kinds


def under_key_candidates(groups):
    return {g:[dict(r,shared_exit_lanes='UNDER_S0_KEY_THREE_PLANES') for r in rows] for g,rows in candidates(groups).items()}


def under_key_materialise(group,recipe):
    """Allocate all24 BELOW the S0 key, respecting the bank's stagger.

    Left goes down; right IN bends towards+X, right OUT towards-X. Those
    horizontal directions separate each nearest2mm-staggered opposing pair.
    No source case, first9, full clamp or minimumR is changed.
    """
    r=recipe['base_recipe'];assert recipe['shared_exit_lanes']=='UNDER_S0_KEY_THREE_PLANES'
    assert r.get('grip_site')!='AFTER_BEND' and r['first_mm']==9
    parts,kinds=original_material(group,r);q=np.asarray(r['point_mm']);d=np.asarray(r['departure_axis'])
    if q[1]>0:b=np.array([0.,0.,-1.])
    else:
        assert '_IN_' in r['terminal_name'] or '_OUT_' in r['terminal_name']
        b=np.array([1. if '_IN_' in r['terminal_name'] else -1.,0.,0.])
    assert abs(d@b)<1e-6
    radius=r.get('radius_mm',r.get('radius'));R=r['R_mm'];theta=math.radians(30);a=q+9*d
    point=lambda t:a+R*math.sin(t)*d+R*(1-math.cos(t))*b
    end=point(theta);axis=math.cos(theta)*d+math.sin(theta)*b;tip=end+9*axis
    path=Part.Wire([Part.makeLine(A.Vector(*q),A.Vector(*a)),
        Part.Arc(A.Vector(*a),A.Vector(*point(theta/2)),A.Vector(*end)).toShape(),Part.makeLine(A.Vector(*end),A.Vector(*tip))])
    wire=path.makePipeShell([Part.Wire([Part.makeCircle(radius,A.Vector(*q),A.Vector(*d))])],True,False)
    assert wire.isValid() and len(wire.Solids)==1
    wires=[n for n in parts if kinds[n]=='proposal_wire'];assert len(wires)==1
    parts[wires[0]]=wire
    return parts,kinds
