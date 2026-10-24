"""Valid additive cover of the received carrier before its subtractive cuts.

Not a repaired carrier or a replacement printable part. Positive separation
from every cover constituent suffices; overlap is unresolved, never collision.
Recipe follows feline_gallery_tail_support.build; R2 only removes material.
"""
import numpy as np
import FreeCAD as A
import Part
from receive_feline_global_case_candidates import placement


def cover(old_tail, originals, recipe):
    parts={}
    def bound(name, shape):
        b=shape.BoundBox
        parts[name]=Part.makeBox(b.XLength,b.YLength,b.ZLength,A.Vector(b.XMin,b.YMin,b.ZMin))
    def rod(name, a, b):
        a=A.Vector(*a);b=A.Vector(*b);d=b-a
        parts[name]=Part.makeCylinder(2,d.Length,a,d)
        parts[name+':round']=Part.makeSphere(2,b)
    bound('old_tail',old_tail)
    anchor=[140.231079691734,8.178061652152161,58.89181240855591]
    parts['anchor']=Part.makeSphere(2.5,A.Vector(*anchor))
    rails=[originals[n] for n in recipe['BUS_carrier_edge_rails']]
    front,rear=recipe['BUS_carrier_rail_centre_Y_mm']
    z=(rails[0].BoundBox.ZMin+rails[0].BoundBox.ZMax)/2
    edge=rails[0].BoundBox.XMax-.5;root=[145.5,13.5,61.5];post=[145.5,13.5,z]
    rod('root',anchor,root);rod('front_post',root,post)
    rod('front_elbow',post,[145.5,front,z])
    rod('front_arm',[145.5,front,z],[edge,front,z])
    rod('low_crossbar',[145.5,13.5,88.75],[145.5,rear,88.75])
    rod('rear_post',[145.5,rear,88.75],[145.5,rear,z])
    rod('rear_arm',[145.5,rear,z],[edge,rear,z])
    for n,s in originals.items():
        bound(n,s)
        if 'Standoff' in n:
            b=s.BoundBox;c=b.Center
            parts[n+':overlap']=Part.makeCylinder(3,.26,A.Vector(c.x,c.y,b.ZMax-.01))
    for row in recipe['new_BUS_DG_full_ends']:
        tag=row['name'].rsplit('.',1)[-1]
        end,tip=map(lambda p:np.array(p,float),row['full9_mm']);t=(tip-end)/9
        tf=placement(np.column_stack([t,[0.,0,1],np.cross(t,[0.,0,1])]),end)
        body=Part.makeBox(9,8,8,A.Vector(0,-4,-4));body.Placement=tf*body.Placement
        parts[tag+':uncut_saddle']=body
        p=end+7.75*t;target=[p[0],p[1],58.]
        if tag=='D':rod('D_arm',anchor,target)
        else:
            rod('G_side',root,[145.5,p[1],58.])
            rod('G_arm',[145.5,p[1],58.],target)
    for s in parts.values():
        assert s.isValid() and len(s.Solids)==1
        s.check(True)
    return parts
