"""Four open PETG saddles on existing first arcs; no extra wire length.

Construct the whole pad/band/head/root before a scene check. Parameters are
project allowances, not delivered tie-fit or PETG strength guarantees.
"""
import math
import numpy as np
import FreeCAD as A
import Part
from receive_feline_early_curved_rrp import sector
from receive_feline_global_case_candidates import placement
from receive_feline_positive_service_deck import open_grip


def at(arc,s,d,n):
    radius=arc['radius_mm'];theta=s/radius
    point=np.asarray(arc['start'])+radius*math.sin(theta)*d+radius*(1-math.cos(theta))*n
    return point,math.cos(theta)*d+math.sin(theta)*n


def interval(arc,a,b,r0,r1,z0,z1,d,n):
    """Annular strip extruded vertically, using actual arc not bbox fit."""
    R=arc['radius_mm'];centre=np.asarray(arc['start'])+R*n
    b0=np.cross(d,n);rot=np.column_stack((b0,-d,-n));assert np.linalg.det(rot)>1-1e-9
    # Local X is vertical but changes sign for mirrored first-arc frames.
    x0=min((z0-centre[2])/b0[2],(z1-centre[2])/b0[2])
    raw=sector([x0,0,0],r0,r1,(b-a)/R,z1-z0)
    spin=A.Placement(A.Vector(),A.Rotation(A.Vector(1,0,0),math.degrees(a/R)))
    raw.Placement=placement(rot,centre)*spin*raw.Placement
    return raw


def construct(recipe):
    arc=recipe['parts'][1];R=arc['radius_mm'];assert abs(R-25.2)<1e-6
    d=np.asarray(recipe['axis'],float);p=np.asarray(arc['start']);q=np.asarray(arc['end'])
    theta=arc['length_mm']/R
    n=(q-p-R*math.sin(theta)*d)/(R*(1-math.cos(theta)))
    assert abs(np.linalg.norm(n)-1)<1e-6 and abs(n[2])<1e-6
    # Full10mm interval and a2mm root before the whole head interval.
    a,b=1.25,11.25;assert b<arc['length_mm']
    pad=interval(arc,a,b,R-2.4,R+2.4,p[2]-4.5,p[2]-2.5,d,n)
    point,tangent=at(arc,8,d,n)
    kit=open_grip(point-8*tangent,tangent,[0,0,-1],8)
    kit['pad']=pad
    root=interval(arc,2.5,4.5,R-2.4,R+2.4,-43.3,p[2]-3.5,d,n)
    joined=pad.fuse(root);assert joined.isValid() and len(joined.Solids)==1
    kit['pad']=joined
    for s in kit.values():assert s.isValid() and len(s.Solids)==1
    for suffix in ('band','head'):
        c=joined.common(kit[suffix]);assert (c.isNull() or c.isValid()) and c.Volume<1e-5,(suffix,c.Volume)
    bandhead=kit['band'].fuse(kit['head']);assert bandhead.isValid() and len(bandhead.Solids)==1
    assert abs(kit['head'].Volume-5*4.3*5.3)<1e-5
    return kit,dict(full_grip_arclength_mm=[a,b],independent_wire=True,wire_length_added_mm=0,
        first_arc_R_mm=R,root_arclength_mm=[2.5,4.5],band_centre_arclength_mm=8,
        pad_thickness_mm=2,root_bottom_mm=-43.3,root_pad_common_mm3=pad.common(root).Volume,
        nominal_T18I_head_volume_mm3=kit['head'].Volume,assembly='Install PETG floor/pad; lay jacket; pass separate tie through floor slot; tighten without conductor crush; cut tie for removal.',
        root_parent_and_full_scene_and_pull_test_OPEN=True)
