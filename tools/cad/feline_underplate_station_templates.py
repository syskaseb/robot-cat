"""Constructive under-platform common AFTER-arc combs, not native details.

All occupied mouths are one rigid source case, no new pinout or connector.
3mm transition is a project routing assumption; full9mm grip follows the
actual constant-R arc. Cases, every wire, split-comb exterior, whole strap
and6mm head are material geometry, not an inflated case-only promise.
"""
import math
import numpy as np
import FreeCAD as A
import Part
from feline_flat_station_templates import build
from receive_feline_global_case_candidates import placement


def box(lo,hi,pose=None):
    s=Part.makeBox(*(np.asarray(hi)-lo),A.Vector(*lo))
    if pose:s.Placement=pose*s.Placement
    return s


def build_underplate(station,slot,bend_side=1,head_side=1):
    assert slot['pose_family']=='UNDER_PLATFORM_SHARED_REMOVABLE_COMBS'
    assert not station['fixed_identity_pose'] and bend_side in (-1,1) and head_side in (-1,1)
    centre=np.array(slot['centre_mm']);side=-1 if centre[1]<0 else 1
    if slot['profile']=='standard':
        rot=np.array([[0.,1.,0.],[0.,0.,side],[side,0.,0.]])
        departure=-side;d=np.array([0.,0.,-1.]);b=np.array([0.,bend_side,0.]);sweep=90.
    else:
        rot=np.array([[0.,-1.,0.],[1.,0.,0.],[0.,0.,1.]])
        departure=-side;d=np.array([0.,-side,0.]);b=np.array([0.,0.,-1.]);sweep=45.
    assert abs(np.linalg.det(rot)-1)<1e-8
    base=build(dict(station,row_families=['inner','outer']),'outer',1,departure)
    old=np.array(base['centre_mm']);qmap=lambda q:rot@(np.array(q)-old)+centre
    dims=np.array(slot['dimensions_mm']);case=box(centre-dims/2,centre+dims/2)
    sourcevol=station['source_part_record']['volume_mm3'];assert abs(case.Volume-sourcevol)<1e-5
    parts={'case':case};wires=[];after=[];angles=np.linspace(0,math.radians(sweep),math.ceil(station['shared_fan_R_mm']*math.radians(sweep))+1)
    theta=math.radians(sweep);t=math.cos(theta)*d+math.sin(theta)*b;u=np.array([1.,0.,0.]);n=np.cross(t,u)
    for source in base['wires']:
        q=qmap(source['point_mm']);R=station['shared_fan_R_mm'];r=source['radius'];a=q+d*3
        arc=a+R*np.sin(angles)[:,None]*d+R*(1-np.cos(angles))[:,None]*b;end=arc[-1]
        mid=a+d*(R*math.sin(theta/2))+b*(R*(1-math.cos(theta/2)))
        path=Part.Wire([Part.makeLine(A.Vector(*q),A.Vector(*a)),Part.Arc(A.Vector(*a),A.Vector(*mid),A.Vector(*end)).toShape(),Part.makeLine(A.Vector(*end),A.Vector(*(end+t*9)))])
        wire=path.makePipeShell([Part.Wire([Part.makeCircle(r,A.Vector(*q),A.Vector(*d))])],True,False)
        assert wire.isValid() and len(wire.Solids)==1
        name='wire:'+source['endpoint'];parts[name]=wire;after.append(end)
        wires.append(dict(endpoint=source['endpoint'],wire=source['wire'],point_mm=q.tolist(),departure_axis=d.tolist(),bend_unit=b.tolist(),
            R_mm=R,radius_mm=r,first_mm=3,sweep_degrees=sweep,grip_start_mm=end.tolist(),grip_axis=t.tolist(),grip_length_mm=9,
            points_mm=np.vstack((np.linspace(q,a,4),arc,np.linspace(end,end+t*9,10))).tolist()))
    origin=np.mean(after,axis=0);basis=np.column_stack((u,n,t));pose=placement(basis,origin)
    local=np.array(after)-origin;xx=local@u;rmax=max(w['radius_mm'] for w in wires)
    xmin=min(x-w['radius_mm'] for x,w in zip(xx,wires))-2;xmax=max(x+w['radius_mm'] for x,w in zip(xx,wires))+2
    nn=rmax+2;cap=box(np.array([xmin,-nn,0.]),np.array([xmax,nn,9.]),pose)
    for w in wires:
        cap=cap.cut(Part.makeCylinder(w['radius_mm']+.15,11,A.Vector(*(np.array(w['grip_start_mm'])-t)),A.Vector(*t)))
    assert cap.isValid() and len(cap.Solids)==1;parts['split_common_comb']=cap
    strips=[([xmin-1.2,-nn-1.2,3.25],[xmin,nn+1.2,5.75]),([xmax,-nn-1.2,3.25],[xmax+1.2,nn+1.2,5.75]),
            ([xmin,-nn-1.2,3.25],[xmax,-nn,5.75]),([xmin,nn,3.25],[xmax,nn+1.2,5.75])]
    parts['band_budget']=Part.makeCompound([box(np.array(lo),np.array(hi),pose) for lo,hi in strips])
    hc=np.array([(xmin+xmax)/2,head_side*(nn+1.2+3),4.5]);parts['head_budget']=box(hc-3,hc+3,pose)
    return dict(ref=station['ref'],slot=slot,parts=parts,wires=wires,bend_side=bend_side,head_side=head_side,
        source_case_rotation_rows=rot.tolist(),grip_length_mm=9,transition3_is_project_not_manufacturer=True,
        assembly_split_plane='Through ALL parallel jacket axes; removable upper comb before tying. Not a one-piece closed threading requirement.',
        roots_and_exact_whole_world_not_qualified=True,nylon_loop_upper_bound_mm=2*(xmax-xmin+2*nn)+10)
