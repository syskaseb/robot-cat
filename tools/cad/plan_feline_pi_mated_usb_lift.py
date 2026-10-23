"""Necessary service pose: lift Pi with USB mated, then unplug above BUS.

Fixed bought cable length, no selected stationary geometry changes. An end
pose is not a proof of its transition or of full assembly/disassembly.
"""
import math
import time
import numpy as np
import FreeCAD as A
import Part
from scipy.interpolate import make_interp_spline
from feline_cubic_curvature import extrema
from plan_feline_usb_release_grip import release_path
from receive_feline_positive_service_deck import circle_arc
from feline_atomic_save import save_json
from plan_feline_layout import OUT
from feline_solid_distance import bbox_lower_bound


def path(lift=10):
    q=np.array([110.,28.85810963471377,98.7+lift])
    first=q+[15,0,0]; R=31.5; drop=9.7+lift
    u=np.linspace(0,1,241)
    p=np.column_stack([first[0]+R*np.sin(np.pi*u),
                      first[1]+R*(1-np.cos(np.pi*u)),
                      first[2]-drop*(10*u**3-15*u**4+6*u**5)])
    spline=make_interp_spline(u,p,k=3,
        bc_type=([(1,[R*np.pi,0,0])],[(1,[-R*np.pi,0,0])]))
    proof=extrema(spline.t,spline.c)
    assert proof['regular'] and proof['minimum_radius_mm']>=30
    knots,mults=np.unique(spline.t,return_counts=True)
    curve=Part.BSplineCurve()
    curve.buildFromPolesMultsKnots([A.Vector(*v) for v in spline.c],
        mults.tolist(),knots.tolist(),False,3)
    turn=curve.toShape(); target=np.array([86.,46.,89.])
    angle=math.acos(1-(target[1]-q[1])/60); dx=60*math.sin(angle)
    main=(452-(15+turn.Length+math.pi*R+60*angle+target[0]-first[0]-dx))/2
    a=np.array(list(curve.value(1))); b=a+[-main,0,0]; start=b+[0,-2*R,0]
    mid=start+[30*math.sin(angle),30*(1-math.cos(angle)),0]
    end=start+[dx,target[1]-q[1],0]
    t=[math.cos(angle),math.sin(angle),0]; n=[math.sin(angle),-math.cos(angle),0]
    edges={'first':Part.makeLine(A.Vector(*q),A.Vector(*first)), 'turn':turn,
           'main':Part.makeLine(A.Vector(*a),A.Vector(*b)),
           'U':circle_arc(b,[-1,0,0],[0,-1,0],R,math.pi),
           'S1':circle_arc(start,[1,0,0],[0,1,0],30,angle),
           'S2':circle_arc(mid,t,n,30,angle),
           'final':Part.makeLine(A.Vector(*end),A.Vector(*target))}
    length=sum(e.Length for e in edges.values()); assert abs(length-452)<1e-5
    return edges,dict(lift_mm=lift,jacket_length_mm=length,
        minimum_turn_R_mm=proof['minimum_radius_mm'],
        curvature_method=proof['method'],main_straight_mm=main,
        BUS_endpoint_unchanged=True,service_transition_not_qualified=True)


def probe(scene,core):
    tick=time.monotonic(); dest=OUT/'n01-Pi-mated-USB-lift-service-sample.json'
    assert not dest.exists()
    edges,recipe=path()
    excluded={r['name'] for r in core['geometry'] if r.get('role','').startswith('Pi')}
    excluded.update(core['recipe'].get('fixed_replaced_names',[]))
    excluded.update({'USB500:whole','SharedPi:Carrier','USBGrip:Pi:pad',
                     'USBGrip:Pi:band','USBGrip:Pi:head'})
    # The last straight and BUS grip stay collinear, shortened at their far end.
    # Do not recheck unchanged own mates as foreign obstacles.
    old,_=release_path(0)
    changed=dict(edges); changed.pop('final')
    checks={};errors={}
    for ename,edge in changed.items():
        for name,target in scene.items():
            if name in excluded or not target.Solids: continue
            if bbox_lower_bound(edge.BoundBox,target.BoundBox)>=3.75+1e-6:continue
            key=ename+'|'+name
            try:
                assert target.isValid()
                # Boundary distance minus2.5 is a necessary swept-radius bound.
                # A centreline inside target is separately rejected.
                inside=any(s.isInside(edge.Vertexes[0].Point,1e-7,True) for s in target.Solids)
                gap=edge.distToShape(target)[0]-2.5
                checks[key]=dict(gap_lower_bound_mm=gap,minimum_mm=1.25,
                                 inside=inside,ok=not inside and gap>=1.25-1e-6)
            except Exception as exc:errors[key]=str(exc)
    failures=[k for k,r in checks.items() if not r['ok']]
    result=dict(status='MATED_USB_LIFT_SAMPLE_HOLD' if failures or errors else
                'MATED_USB_LIFT_SUBSET_CLEAR_NOT_SERVICE_RECEIVED',
        recipe=recipe,checks=checks,errors=errors,failures=failures,
        excluded=sorted(excluded),curves_and_missing_actors_not_checked=True,
        moving_Pi_own_interface_not_checked=True,continuous_motion_not_checked=True,
        N01_complete=False,physical_pass=False,
        worker_seconds=round(time.monotonic()-tick,3))
    save_json(dest,result)
    print(result['status'],failures,errors,result['worker_seconds'],flush=True)
    return result,edges
