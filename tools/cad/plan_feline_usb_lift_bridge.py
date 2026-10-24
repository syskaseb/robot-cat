"""Bridge existing USB start and lifted end; not a swept-clearance certificate."""
import math
import numpy as np
import FreeCAD as A
import Part
from scipy.interpolate import make_interp_spline
from feline_cubic_curvature import extrema
from receive_feline_positive_service_deck import circle_arc


def path(lift):
    if not 0 <= lift <= 10:
        raise ValueError('Only the agreed 0..10mm lift')
    q=np.array([110.,28.85810963471377,98.7+lift])
    first=q+[15,0,0]; radius=31.5; drop=9.7+lift
    u=np.linspace(0,1,241); blend=lift/10
    h3=3*u*u-2*u**3; h5=10*u**3-15*u**4+6*u**5
    h=(1-blend)*h3+blend*h5
    p=np.column_stack([first[0]+radius*np.sin(np.pi*u),
                       first[1]+radius*(1-np.cos(np.pi*u)),first[2]-drop*h])
    spline=make_interp_spline(u,p,k=3,
        bc_type=([(1,[radius*np.pi,0,0])],[(1,[-radius*np.pi,0,0])]))
    proof=extrema(spline.t,spline.c)
    knots,mults=np.unique(spline.t,return_counts=True)
    curve=Part.BSplineCurve()
    curve.buildFromPolesMultsKnots([A.Vector(*v) for v in spline.c],
        mults.tolist(),knots.tolist(),False,3)
    turn=curve.toShape(); target=np.array([86.,46.,89.])
    angle=math.acos(1-(target[1]-q[1])/60); dx=60*math.sin(angle)
    main=(452-(15+turn.Length+math.pi*radius+60*angle+target[0]-first[0]-dx))/2
    a=np.array(list(curve.value(1))); b=a+[-main,0,0]; start=b+[0,-2*radius,0]
    mid=start+[30*math.sin(angle),30*(1-math.cos(angle)),0]
    end=start+[dx,target[1]-q[1],0]
    edges={'first':Part.makeLine(A.Vector(*q),A.Vector(*first)),'turn':turn,
        'main':Part.makeLine(A.Vector(*a),A.Vector(*b)),
        'U':circle_arc(b,[-1,0,0],[0,-1,0],radius,math.pi),
        'S1':circle_arc(start,[1,0,0],[0,1,0],30,angle),
        'S2':circle_arc(mid,[math.cos(angle),math.sin(angle),0],
                        [math.sin(angle),-math.cos(angle),0],30,angle),
        'final':Part.makeLine(A.Vector(*end),A.Vector(*target))}
    length=sum(e.Length for e in edges.values())
    assert abs(length-452)<1e-5 and main>0
    return edges,dict(lift_mm=lift,jacket_length_mm=length,
        turn_regular=proof['regular'],minimum_turn_R_mm=proof['minimum_radius_mm'],
        main_straight_mm=main,continuous_motion_received=False,
        sampled_pose_only=True,N01_complete=False,physical_pass=False)
