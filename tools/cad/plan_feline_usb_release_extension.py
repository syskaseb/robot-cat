"""Final3mm of existing USB withdrawal; fixed452mm jacket, unchanged bend radii."""
import FreeCAD as A
import Part
from plan_feline_usb_release_grip import release_path
from receive_feline_pi_split_service_space import independent


def path(stroke):
    if not 12 <= stroke <= 15:
        raise ValueError('Only the remaining12..15mm stroke')
    edges,_=release_path(12);delta=stroke-12;shift=A.Vector(-delta/2,0,0)
    start=edges['first'].Vertexes[0].Point+A.Vector(delta,0,0)
    end=edges['first'].Vertexes[-1].Point
    if (end-start).Length>1e-8:edges['first']=Part.makeLine(start,end)
    else:del edges['first']
    for name in ['U','S1','S2']:
        edges[name]=independent(edges[name]);edges[name].translate(shift)
    edges['main']=Part.makeLine(edges['main'].Vertexes[0].Point,
                                edges['main'].Vertexes[-1].Point+shift)
    edges['final']=Part.makeLine(edges['final'].Vertexes[0].Point+shift,
                                 edges['final'].Vertexes[-1].Point)
    length=sum(e.Length for e in edges.values());assert abs(length-452)<1e-5
    return edges,dict(stroke_mm=stroke,jacket_length_mm=length,
        BUS_end_fixed=True,Pi_not_lifted=True,first_straight_mm=15-stroke,
        zero_straight_at15_is_tangent_join_not_zero_edge=True,
        continuous_collision_received=False,N01_complete=False,physical_pass=False)


def front_loop_path(stroke):
    """Different service topology: keep rear U/S fixed, advance front turn.

    Losing stroke/2 from the first straight is exactly compensated by adding
    stroke/2 to the main return. No extra cable or altered stationary wire.
    """
    if not 0 <= stroke <= 15:
        raise ValueError('Only the reserved0..15mm stroke')
    edges,_=release_path(0);shift=A.Vector(stroke/2,0,0)
    first=edges['first']
    edges['first']=Part.makeLine(first.Vertexes[0].Point+A.Vector(stroke,0,0),
                                first.Vertexes[-1].Point+shift)
    edges['fixed_turn']=independent(edges['fixed_turn'])
    edges['fixed_turn'].translate(shift)
    main=edges['main']
    edges['main']=Part.makeLine(main.Vertexes[0].Point+shift,main.Vertexes[-1].Point)
    length=sum(e.Length for e in edges.values());assert abs(length-452)<1e-5
    return edges,dict(stroke_mm=stroke,jacket_length_mm=length,
        front_turn_translation_mm=stroke/2,rear_U_and_S_unchanged=True,
        first_straight_mm=15-stroke/2,Pi_not_lifted=True,
        continuous_collision_received=False,N01_complete=False,physical_pass=False)


def side_bow_path(stroke):
    """Keep BOTH turns fixed; the long side straight takes the released length."""
    import numpy as np
    from scipy.interpolate import make_interp_spline
    from scipy.optimize import brentq
    from feline_cubic_curvature import extrema
    if not 0 <= stroke <= 15:
        raise ValueError('Only the reserved0..15mm stroke')
    edges,_=release_path(0)
    if stroke==0:return edges,dict(stroke_mm=0,jacket_length_mm=452,amplitude_mm=0)
    first=edges['first'];start=first.Vertexes[0].Point+A.Vector(stroke,0,0)
    if stroke<15:edges['first']=Part.makeLine(start,first.Vertexes[-1].Point)
    else:del edges['first']
    a=np.array(list(edges['main'].Vertexes[0].Point))
    b=np.array(list(edges['main'].Vertexes[-1].Point));direction=b-a
    length=edges['main'].Length;u=np.linspace(0,1,241)
    def curve(amplitude):
        p=a+u[:,None]*direction;p[:,2]-=amplitude*np.sin(np.pi*u)**2
        spline=make_interp_spline(u,p,k=3,bc_type=([(1,direction)],[(1,direction)]))
        knots,mults=np.unique(spline.t,return_counts=True);c=Part.BSplineCurve()
        c.buildFromPolesMultsKnots([A.Vector(*v) for v in spline.c],
                                  mults.tolist(),knots.tolist(),False,3)
        return c.toShape(),spline
    amplitude=brentq(lambda amp:curve(amp)[0].Length-length-stroke,0,60,xtol=1e-9)
    edge,spline=curve(amplitude);proof=extrema(spline.t,spline.c);edges['main']=edge
    total=sum(e.Length for e in edges.values());assert abs(total-452)<1e-5
    return edges,dict(stroke_mm=stroke,jacket_length_mm=total,amplitude_mm=amplitude,
        minimum_bow_R_mm=proof['minimum_radius_mm'],regular=proof['regular'],
        both_turns_and_BUS_end_unchanged=True,Pi_not_lifted=True,
        continuous_collision_received=False,N01_complete=False,physical_pass=False)


def side_bow_family_bound(max_amplitude):
    """B-spline derivative convex-hull bound for every amplitude0..maximum."""
    import numpy as np
    from scipy.interpolate import make_interp_spline
    edges,_=release_path(0);edge=edges['main']
    a=np.array(list(edge.Vertexes[0].Point));b=np.array(list(edge.Vertexes[-1].Point))
    direction=b-a;u=np.linspace(0,1,241)
    p=a+u[:,None]*direction;p[:,2]-=np.sin(np.pi*u)**2
    spline=make_interp_spline(u,p,k=3,bc_type=([(1,direction)],[(1,direction)]))
    d1=spline.derivative();d2=spline.derivative(2)
    c1=d1.c[:len(d1.t)-d1.k-1];c2=d2.c[:len(d2.t)-d2.k-1]
    assert max_amplitude>=0 and np.all(c1[:,0]<0)
    assert np.max(np.abs(c1[:,1]))<1e-8 and np.max(np.abs(c2[:,1]))<1e-7
    lower_speed=np.min(np.abs(c1[:,0]));upper_xp=np.max(np.abs(c1[:,0]))
    upper_zp=max_amplitude*np.max(np.abs(c1[:,2]))
    upper_zpp=max_amplitude*np.max(np.abs(c2[:,2]))
    upper_xpp=np.max(np.abs(c2[:,0]))
    cross_bound=upper_xp*upper_zpp+upper_zp*upper_xpp
    return dict(max_amplitude_mm=max_amplitude,speed_lower_bound=lower_speed,
        minimum_R_lower_bound_mm=lower_speed**3/cross_bound if cross_bound else float('inf'),
        method='B-spline derivative control convex hull; x derivative constant-sign; amplitude scales z only',
        covers_all_amplitudes_from_zero=True)
