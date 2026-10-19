"""One source-to-body three-wire allocation around bridge and S0 side.

Nominal existing1.05 jackets, source full9, R12.4/nested turns; one shared
vertical-to-flat transition, outside-side drop and concentric inboard S.
No production carrier, native replacement or supplier OD claim.
"""
import math
import numpy as np
import FreeCAD as A
import Part
from scipy.interpolate import make_interp_spline
from receive_feline_positive_service_deck import circle_arc,pipe
from feline_cubic_curvature import extrema
from receive_feline_shared_corridor_space import transition_separation_bound


def whole_axis_samples(edges,step=.05):
    """Closed coverage bound, including all spline parameter spans."""
    from scipy.interpolate import BSpline
    points=[];error=0.
    for e in edges:
        if type(e.Curve).__name__=='BSplineCurve':
            c=e.Curve;assert not c.isRational()
            t=np.repeat(c.getKnots(),c.getMultiplicities());p=np.array([list(v) for v in c.getPoles()])
            spline=BSpline(t,p,c.Degree);speed=float(np.linalg.norm(spline.derivative().c,axis=1).max())
            lo,hi=e.FirstParameter,e.LastParameter;N=max(1,int(math.ceil(speed*(hi-lo)/step)))
            points.append(spline(np.linspace(lo,hi,N+1)));error=max(error,speed*(hi-lo)/(2*N))
        else:
            N=max(1,int(math.ceil(e.Length/step)))
            points.append(np.array([list(e.valueAt(v)) for v in np.linspace(e.FirstParameter,e.LastParameter,N+1)]))
            error=max(error,e.Length/(2*N))
    return np.vstack(points),error


def candidates():
    result=[];transitions=[];Y=-38.320513724211
    for name,x,R,k in (('XB22',-238.6,14.94,0),('XB23',-241.14,17.48,1),('XS23',-236.06,12.4,-1)):
        start=np.array([x,Y,-10.]);land=start+[0,-12,0]
        e1=circle_arc(land,[0,-1,0],[0,0,1],12.4,math.pi/2)
        p=land+[0,-12.4,12.4]
        e2=circle_arc(p,[0,0,1],[1,0,0],R,math.pi/2)
        end=p+[R,0,R];assert np.allclose(end,[-223.66,Y-24.4,17.34+k*2.54])
        es=[Part.makeLine(A.Vector(*start),A.Vector(*land)),e1,e2]
        # Shared transition is allocated before selecting either existing
        # source tie orientation. It clears the side of the yaw bridge first.
        v=np.linspace(0,1,241);h=10*v**3-15*v**4+6*v**5;theta=math.pi/2*h
        radius=2.54+(3.4-2.54)*h
        centre=np.column_stack([-223.66+66*v,np.full(len(v),Y-24.4)+(-35-(Y-24.4))*h,
            17.34+(53.5-17.34)*h])
        dh=30*v**2-60*v**3+30*v**4
        tangent=np.column_stack([np.ones(len(v)),(-35-(Y-24.4))*dh/66,(53.5-17.34)*dh/66])
        tangent/=np.linalg.norm(tangent,axis=1)[:,None]
        lateral=np.tile([0.,1,0],(len(v),1))-tangent*tangent[:,1,None]
        lateral/=np.linalg.norm(lateral,axis=1)[:,None]
        vertical=np.cross(tangent,lateral)
        # A world-Z translation compresses spacing on the rising shared
        # centre curve. Rotate a true normal cross-section, not that offset.
        pts=centre+k*radius[:,None]*(np.sin(theta[:,None])*lateral+np.cos(theta[:,None])*vertical)
        s=make_interp_spline(66*v,pts,k=3,bc_type=([(1,[1.,0,0])],[(1,[1.,0,0])]))
        proof=extrema(s.t,s.c);assert proof['regular'] and proof['minimum_radius_mm']>=12.4,(name,proof['minimum_radius_mm'])
        knots,mults=np.unique(s.t,return_counts=True);curve=Part.BSplineCurve()
        curve.buildFromPolesMultsKnots([A.Vector(*p) for p in s.c],mults.tolist(),knots.tolist(),False,3)
        es.append(curve.toShape())
        transitions.append(dict(name=name,knots=s.t.tolist(),poles_mm=s.c.tolist(),radius_mm=1.05))
        point=pts[-1];t=np.array([1.,0,0]);normal=np.array([0.,0,-1.]);H=11.75;rr=17.
        alpha=math.acos(1-H/(2*rr))
        es.append(circle_arc(point,t,normal,rr,alpha))
        point=point+rr*math.sin(alpha)*t+rr*(1-math.cos(alpha))*normal
        t2=math.cos(alpha)*t+math.sin(alpha)*normal;op=math.sin(alpha)*t-math.cos(alpha)*normal
        es.append(circle_arc(point,t2,op,rr,alpha))
        point=point+rr*math.sin(alpha)*t2+rr*(1-math.cos(alpha))*op
        assert abs(point[2]-41.75)<1e-8
        # Concentric offsets retain the actual3.4mm pitch throughout the
        # horizontal S, rather than translating three crossing tight turns.
        centre=point-np.array([0.,k*3.4,0]);t=np.array([1.,0,0]);n=np.array([0.,1,0]);off=k*3.4
        angle=math.acos(1-17/(2*17.))
        e=circle_arc(point,t,n,17-off,angle);es.append(e)
        centre2=centre+17*math.sin(angle)*t+17*(1-math.cos(angle))*n
        t2=math.cos(angle)*t+math.sin(angle)*n;n2=-math.sin(angle)*t+math.cos(angle)*n
        point2=centre2+off*n2
        assert (e.Vertexes[-1].Point-A.Vector(*point2)).Length<1e-7
        es.append(circle_arc(point2,t2,-n2,17+off,angle))
        end=centre+np.array([34*math.sin(angle),17,0])+np.array([0.,off,0])
        assert (es[-1].Vertexes[-1].Point-A.Vector(*end)).Length<1e-7
        finish=np.array([-35.,-18.+off,41.75]);assert finish[0]>end[0]
        es.append(Part.makeLine(A.Vector(*end),A.Vector(*finish)))
        body,path=pipe(es,1.05)
        result.append(dict(name='HP_integrated:'+name,kind='head_actual_source_nominal_jacket',wire=name,shape=body,
            start_mm=start.tolist(),end_mm=finish.tolist(),radius_mm=1.05,path_length_mm=path.Length,
            analytic_expected_volume_mm3=math.pi*1.05**2*path.Length,minimum_wire_R_mm=12.4,
            source_full9_mm=[(start+[0,-3,0]).tolist(),land.tolist()],transition_curvature=proof,
            final_flat_pitch_mm=3.4,nominal_source_OD_unchanged=True))
    bounds=[]
    for i,a in enumerate(transitions):
        for b in transitions[i+1:]:
            bound=transition_separation_bound(a,b);assert bound['ok'],bound;bounds.append(bound)
    return result,bounds


def positive_channel_candidates(rooted=False):
    """Whole shared lower-head return, rise on free positive side, top trunk.

    Retains the factory yaw loop; does not attempt to pass through it on the
    negative side. Top-trunk Y33/Z103 is proposed by the existing signed map.
    """
    rows=[];proof_rows=[];Y=-38.320513724211
    for name,x,R,k in (('XB22',-238.6,14.94,0),('XB23',-241.14,17.48,1),('XS23',-236.06,12.4,-1)):
        start=np.array([x,Y,-10.]);p=start+[0,-12,0]
        es=[Part.makeLine(A.Vector(*start),A.Vector(*p))]
        es.append(circle_arc(p,[0,-1,0],[0,0,-1],12.4,math.pi/2));p=p+[0,-12.4,-12.4]
        es.append(circle_arc(p,[0,0,-1],[0,1,0],12.4,math.pi/2));p=p+[0,12.4,-12.4]
        rise_y=50. if rooted else 45.4
        q=np.array([x,rise_y-12.4,-34.8]);es.append(Part.makeLine(A.Vector(*p),A.Vector(*q)));p=q
        es.append(circle_arc(p,[0,1,0],[0,0,1],12.4,math.pi/2));p=p+[0,12.4,12.4]
        q=np.array([x,rise_y,85.5]);es.append(Part.makeLine(A.Vector(*p),A.Vector(*q)));p=q
        es.append(circle_arc(p,[0,0,1],[1,0,0],R,math.pi/2));p=p+[R,0,R]
        assert np.allclose(p,[-223.66,rise_y,100.44+k*2.54])
        v=np.linspace(0,1,241);h=10*v**3-15*v**4+6*v**5;theta=math.pi/2*h
        radius=2.54+(3.4-2.54)*h
        L1,L2=(60.,46.) if rooted else (66.,40.)
        first=np.column_stack([-223.66+L1*v,rise_y+k*radius*np.sin(theta),100.44+k*radius*np.cos(theta)])
        second=np.column_stack([-223.66+L1+L2*v,rise_y+(33-rise_y)*h+k*3.4,100.44+(103-100.44)*h])
        minR=math.inf
        for index,pts in enumerate((first,second)):
            L=L1 if index==0 else L2
            spline=make_interp_spline(L*v,pts,k=3,bc_type=([(1,[1.,0,0])],[(1,[1.,0,0])]))
            proof=extrema(spline.t,spline.c);assert proof['regular'] and proof['minimum_radius_mm']>=12.4
            minR=min(minR,proof['minimum_radius_mm'])
            knots,mults=np.unique(spline.t,return_counts=True);curve=Part.BSplineCurve()
            curve.buildFromPolesMultsKnots([A.Vector(*p) for p in spline.c],mults.tolist(),knots.tolist(),False,3)
            # Exact central straight uses an analytic line: a241pole
            # collinear cubic after seven arcs triggers an OCC pipe failure.
            es.append(Part.makeLine(A.Vector(*pts[0]),A.Vector(*pts[-1])) if index==0 and k==0 else curve.toShape())
            proof_rows.append(dict(name=name+':'+str(index),wire=name,segment=index,knots=spline.t.tolist(),poles_mm=spline.c.tolist(),radius_mm=1.05))
        finish=np.array([-35.,33+k*3.4,103.]);es.append(Part.makeLine(A.Vector(*second[-1]),A.Vector(*finish)))
        body,path=pipe(es,1.05)
        rows.append(dict(name='HP_positive_channel:'+name,kind='head_actual_source_nominal_jacket',wire=name,shape=body,
            start_mm=start.tolist(),end_mm=finish.tolist(),radius_mm=1.05,path_length_mm=path.Length,
            analytic_expected_volume_mm3=math.pi*1.05**2*path.Length,minimum_wire_R_mm=12.4,
            source_full9_mm=[(start+[0,-3,0]).tolist(),(start+[0,-12,0]).tolist()],transition_curvature=dict(minimum_radius_mm=minR),
            final_flat_pitch_mm=3.4,nominal_source_OD_unchanged=True,
            swept_piece_bounds_mm=[[[e.BoundBox.XMin-1.05001,e.BoundBox.YMin-1.05001,e.BoundBox.ZMin-1.05001],
                                   [e.BoundBox.XMax+1.05001,e.BoundBox.YMax+1.05001,e.BoundBox.ZMax+1.05001]] for e in es]))
        if rooted:rows[-1]['_axis_samples'],rows[-1]['axis_coverage_error_mm']=whole_axis_samples(es)
    bounds=[]
    for index in (0,1):
        rr=[r for r in proof_rows if r['segment']==index]
        for i,a in enumerate(rr):
            for b in rr[i+1:]:
                bound=transition_separation_bound(a,b);assert bound['ok'],bound;bounds.append(bound)
    if rooted:
        from scipy.spatial import cKDTree
        for i,a in enumerate(rows):
            for b in rows[i+1:]:
                gap=float(cKDTree(a['_axis_samples']).query(b['_axis_samples'])[0].min())
                error=a['axis_coverage_error_mm']+b['axis_coverage_error_mm'];lower=gap-error-2.1
                proof=dict(a=a['name'],b=b['name'],scope='whole_wire',gap_lower_bound_mm=lower,minimum_mm=.2,
                    ok=bool(lower>=.2),sample_axis_gap_mm=gap,coverage_error_mm=error,
                    method='All analytic arc-length intervals and BSpline derivative convex-hull coverage; global nearest pair')
                assert proof['ok'],proof;bounds.append(proof)
    return rows,bounds
