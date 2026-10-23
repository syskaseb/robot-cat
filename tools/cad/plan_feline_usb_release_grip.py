"""Move the USB restraint beyond the plug-withdrawal volume, retaining cable.

Constructive N01 geometry only; independent physical pull/print fit remains open.
"""
import math
import numpy as np
import FreeCAD as A
import Part
from scipy.interpolate import make_interp_spline
from scipy.optimize import brentq
from receive_feline_positive_service_deck import pipe,open_grip,circle_arc
from receive_feline_pi_split_service_space import independent


def first_curve():
    first=np.array([125.,28.85810963471377,98.7]);R=31.5;drop=9.7
    at=lambda u:first+np.array([R*math.sin(math.pi*u),R*(1-math.cos(math.pi*u)),-drop*(3*u*u-2*u*u*u)])
    deriv=lambda u:np.array([R*math.pi*math.cos(math.pi*u),R*math.pi*math.sin(math.pi*u),-6*drop*u*(1-u)])
    v=np.linspace(0,1,241);spline=make_interp_spline(v,np.array([at(u) for u in v]),k=3,
        bc_type=([(1,deriv(0))],[(1,deriv(1))]))
    knots,mults=np.unique(spline.t,return_counts=True);curve=Part.BSplineCurve()
    curve.buildFromPolesMultsKnots([A.Vector(*p) for p in spline.c],mults.tolist(),knots.tolist(),False,3)
    return curve


def build(carrier):
    first=np.array([125.,28.85810963471377,98.7]);curve=first_curve()
    param=lambda length:brentq(lambda u:curve.toShape(0,u).Length-length,1e-8,.25)
    u9=param(9);u1=param(3.25);u2=param(5.75);mid=param(4.5)
    edge=curve.toShape(0,u9);outer,_=pipe([edge],4.65);inner,_=pipe([edge],2.65)
    pad=outer.cut(inner).common(Part.makeBox(40,40,30,A.Vector(115,10,98.7)))
    clip=Part.makeBox(40,40,30,A.Vector(115,10,98.7))
    strap_outer,_=pipe([curve.toShape(u1,u2)],5.85);strap_inner,_=pipe([curve.toShape(u1,u2)],4.65)
    lower_outer,_=pipe([curve.toShape(u1,u2)],3.85);lower_inner,_=pipe([curve.toShape(u1,u2)],2.65)
    # Wrap the pad's roof AND the lower jacket, not a loose full-radius ring.
    outer_clip=Part.makeBox(40,40,31.2,A.Vector(115,10,97.5))
    band=strap_outer.common(outer_clip).fuse(lower_outer).cut(strap_inner.common(clip).fuse(lower_inner))
    p=curve.value(mid);t=curve.tangent(mid)[0]
    side=A.Vector(-t.y,t.x,0);side.normalize()
    vertical=A.Vector(0,0,1)-t*t.z;vertical.normalize()
    up=side+vertical;up.normalize()
    across=t.cross(up);mat=A.Matrix()
    for i in range(3):
        for j,col in enumerate((up,across,t)):setattr(mat,f'A{i+1}{j+1}',list(col)[i])
    head=Part.makeBox(4.3,5.3,5,A.Vector(-2.15,-2.65,-2.5))
    head.Placement=A.Placement(p+up*(5.85+2.15),A.Rotation(mat))
    oldpad=open_grip([116,first[1],98.7],[1,0,0],[0,0,1],1.75)['pad']
    oldpost=Part.makeCylinder(1.5,4.2,A.Vector(118.5,first[1],102.9))
    oldpost=oldpost.fuse(Part.makeSphere(1.5,A.Vector(118.5,first[1],102.9)))
    retained=independent(carrier).cut(oldpad.fuse(oldpost)).removeSplitter()
    # Root at the beginning of the grip: the far end is occupied by the
    # received W009 corridor. Keep the old beam short; never move W009.
    after=curve.value(0)
    goal=A.Vector(after.x,after.y,102.9);high=A.Vector(after.x,after.y,107.1);start=A.Vector(118.5,first[1],107.1)
    delta=high-start
    arm=Part.makeCylinder(1.5,delta.Length,start,delta).fuse(Part.makeSphere(1.5,high))
    arm=arm.fuse(Part.makeCylinder(1.5,high.z-goal.z,goal)).fuse(Part.makeSphere(1.5,goal))
    new=retained.fuse(arm).fuse(pad).removeSplitter()
    shapes=dict(carrier=new,pad=pad,band=band,head=head,arm=arm,retained=retained)
    assert all(s.isValid() and len(s.Solids)==1 for s in shapes.values())
    return shapes,dict(grip_length_mm=edge.Length,retained_wire=True,groove_radius_mm=2.65,
        wall_mm=2.,head_mm=[4.3,5.3,5],midpoint_mm=list(p),old_straight_grip_retired=True,
        service_withdrawal_mm=12,nominal_fit_and_pull_not_qualified=True)


def release_path(distance):
    """Same452mm jacket: shorten first straight, extend both return legs equally."""
    assert 0<=distance<=12
    q=np.array([110.+distance,28.85810963471377,98.7]);first=np.array([125.,q[1],q[2]])
    curve=first_curve();edge=curve.toShape();R=31.5;target=np.array([86.,46.,89.])
    angle=math.acos(1-(target[1]-q[1])/60);dx=60*math.sin(angle)
    main=(452-(15-distance+edge.Length+math.pi*R+60*angle+target[0]-first[0]-dx))/2
    a=np.array(list(curve.value(1)));b=a+[-main,0,0];start=b+[0,-2*R,0]
    mid=start+[30*math.sin(angle),30*(1-math.cos(angle)),0]
    t=[math.cos(angle),math.sin(angle),0];n=[math.sin(angle),-math.cos(angle),0]
    end=start+[dx,target[1]-q[1],0]
    edges=dict(first=Part.makeLine(A.Vector(*q),A.Vector(*first)),fixed_turn=edge,
        main=Part.makeLine(A.Vector(*a),A.Vector(*b)),
        U=circle_arc(b,[-1,0,0],[0,-1,0],R,math.pi),
        S1=circle_arc(start,[1,0,0],[0,1,0],30,angle),
        S2=circle_arc(mid,t,n,30,angle),final=Part.makeLine(A.Vector(*end),A.Vector(*target)))
    assert abs(sum(e.Length for e in edges.values())-452)<1e-5
    return edges,dict(distance_mm=distance,jacket_length_mm=sum(e.Length for e in edges.values()),
        moving_arcs_translation_mm=[-distance/2,0,0],BUS_end_unchanged=True,minimum_R_mm=30,
        first_straight_mm=15-distance,grip_released_before_motion=True)
