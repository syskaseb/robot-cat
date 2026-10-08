"""Pi's same protected pair outside the holder's ATO opening, not over it.

Keep one8mm splice. One extra horizontal turn replaces the old over-holder
return; the rise is3mm, preserving the guaranteed84.5mm factory blank.
"""
import math
from open_prototype_wiring_endpoints import BASE, read


def pi_service_route(A,Part):
    prior=read(BASE/'wiring-checkpoint/source-output-plan.json')
    pad=A.Vector(*prior['MAIN']['pad_mm'])
    X,Y,Z=A.Vector(1,0,0),A.Vector(0,1,0),A.Vector(0,0,1)
    def line(a,b):
        assert (b-a).Length>1e-7
        return Part.makeLine(a,b)
    def bend(a,u,v):
        centre=a+v*6;end=a+(u+v)*6
        return Part.Arc(a,centre+(u-v)*(6/math.sqrt(2)),end).toShape(),end
    def sweep(edges,diameter,axis):
        w=Part.Wire(edges)
        s=w.makePipeShell([Part.Wire(Part.makeCircle(diameter/2,edges[0].Vertexes[0].Point,axis))],True,False)
        assert s.isValid() and len(s.Solids)==1
        return s,w.Length
    start=A.Vector(-22.5,56.75,100.99)
    a=start+X*9;c1,b=bend(a,X,Z)
    c=b+Z*3;c2,d=bend(c,Z,Y)
    e=d+Y*5.5;c3,f=bend(e,Y,-X)
    j=A.Vector(pad.x-5,f.y,f.z)
    factory_edges=[line(start,a),c1,line(b,c),c2,line(d,e),c3,line(f,j)]
    factory,fl=sweep(factory_edges,4,X)
    assert fl+8<=84.5
    ss=j-X*8
    descent=-99.3
    # Do NOT descend at jointY74.25 beside lower-row WAGO. Turn inward
    # above the upper row, then descend in the retained clearY56.75 corridor.
    a=ss-X*(ss.x-descent-6);c1,b=bend(a,-X,-Y)
    c=b-Y*5.5;c0,bd=bend(c,-Y,-Z)
    z=pad.z+20
    c=A.Vector(bd.x,bd.y,z+6);c2,d=bend(c,-Z,X)
    e=A.Vector(pad.x-6,d.y,d.z);c3,f=bend(e,X,-Y)
    g=A.Vector(f.x,pad.y+6,f.z);c4,h=bend(g,-Y,-Z)
    neck=pad+Z*5
    assert abs((h-neck).Length-9)<1e-7
    middle=A.Vector(descent,62.75,j.z)
    extension_edges=[line(ss,a),c1,line(b,middle),c0,line(bd,c),c2,line(d,e),c3,line(f,g),c4,line(h,neck)]
    extension,el=sweep(extension_edges,2.6,-X)
    assert el+16<240
    sleeve=Part.makeCylinder(2.1,20,j+X*6,-X)
    objects={'W077_RouteReference':factory,'W078_RouteReference':extension,
        'PiJointShrinkAllowance_RouteReference':sleeve}
    record=dict(status='PI_SERVICE_ROUTE_NOMINAL_GEOMETRY; context checked in fixture proof',
        new_connector_or_splice_count=0, bare_overlap_mm=8, sleeve_mm=20,
        intact_overlap_each_side_mm=6, splice_boundary_mm=list(j),
        rise_straight_mm=3, joint_y_mm=74.25, input_route_unchanged=True,
        descent_y_mm=56.75, return_inward_above_WAGO=True,
        W077=dict(required_blank_mm=fl+8, nominal_fit_blank_mm=84, factory_minimum_mm=84.5),
        W078=dict(required_blank_mm=el+16,nominal_fit_blank_mm=240),
        grip_centres_mm=[[j.x+10.5,j.y,j.z],[ss.x-10.5,ss.y,ss.z]],
        wire_OD_R6_and_pull_creep_gate=True, selected=False,physical_pass=False)
    record['centreline_edges']={n:[dict(start_mm=list(e.Vertexes[0].Point),
        end_mm=list(e.Vertexes[-1].Point), length_mm=e.Length,
        centre_mm=list(e.Curve.Center) if hasattr(e.Curve,'Center') else None) for e in edges]
        for n,edges in [('W077',factory_edges),('W078',extension_edges)]}
    return objects,record
