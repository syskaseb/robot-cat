"""Full source rings and jacket/grip/head candidates for the shared24-node plan.

No acceptance from clouds. Eye/body/stud intentional mating and root/tool
space require the subsequent exact receiver; source and opposite ends stay pinned.
"""
import hashlib
import itertools
import json
import math
import zipfile
import numpy as np
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_current_candidate_scene import current
from plan_feline_joint_fore_domains import cloud
from plan_feline_fore_service_macro import rigid_tf
from feline_flat_station_templates import box_points


def candidates():
    scene,meta,_,pins,*_=current()
    srcfile=OUT/'n01-s1-current-source-datums.json';source=json.loads(srcfile.read_text())
    pins[srcfile.relative_to(ROOT).as_posix()]=sha(srcfile)
    pins[__import__('pathlib').Path(__file__).relative_to(ROOT).as_posix()]=sha(__import__('pathlib').Path(__file__))
    body=scene['Ref_Material_current_S1_body_CP2_0_0'];tf=rigid_tf(body.BoundBox.Center,[15,0,0],180)
    result={}
    for receipt in source['receipts']:
        endpoint=receipt['endpoint'];ringname=receipt['matching_nominal_source_planes'][0]['part']
        number=int(ringname.split('_ring_')[1].split('_')[0])
        screw=scene[f'Ref_Material_current_S1_screw_{number}_0_0']
        qold=A.Vector(*receipt['source_point_mm']);dold=A.Vector(*receipt['source_departure'])
        eye=A.Vector(screw.BoundBox.Center.x,qold.y,screw.BoundBox.Center.z)
        assert abs((qold-eye).Length-22.123)<1e-5
        ring=scene[ringname];assert ring.isValid() and ring.Solids
        assert any(type(f.Surface).__name__=='Cylinder' and abs(f.Surface.Axis.y)>.999
            and (eye-f.Surface.Center).cross(f.Surface.Axis).Length<1e-5 for f in ring.Faces)
        original=cloud(ring);e=np.array(list(tf.multVec(eye)));rows=[]
        for angle in range(0,360,30):
            d=np.array([math.cos(math.radians(angle)),0,math.sin(math.radians(angle))])
            target=tf.Rotation.inverted().multVec(A.Vector(*d))
            delta=math.degrees(math.atan2(dold.z,dold.x)-math.atan2(target.z,target.x))
            rot=A.Rotation(A.Vector(0,1,0),delta);assert rot.multVec(dold).isEqual(target,1e-7)
            clock=A.Placement(eye-rot.multVec(eye),rot);ct=tf*clock
            rc=np.array([list(ct.multVec(A.Vector(*v))) for v in original]);q=e+22.123*d
            u=np.array([0,1,0]);v=np.cross(d,u)
            for first in (9,18):
                for ba in range(0,360,45):
                    b=u*math.cos(math.radians(ba))+v*math.sin(math.radians(ba));R=25.2
                    a=q+first*d;angles=np.linspace(0,math.pi/2,41)
                    arc=a+R*np.sin(angles)[:,None]*d+R*(1-np.cos(angles))[:,None]*b
                    line=np.linspace(q,q+9*d,10)
                    wp=np.vstack((np.linspace(q,a,first+1),arc,np.linspace(arc[-1],arc[-1]+9*b,10)))
                    # Whole insulating two-mm clamp exterior on a straight,
                    # one full6cube head; not a bare wire-only proposal.
                    grip_r=5.3 #2.1jacket+2mm insulating cap+1.2mm complete band budget
                    ringaxes=np.linspace(0,2*math.pi,17)[:-1]
                    grip=np.vstack([p+grip_r*(np.cos(t)*u+np.sin(t)*v) for p in line for t in ringaxes])
                    h=q+4.5*d-8.3*u;head=box_points(h-3,h+3)
                    points=np.vstack((rc,wp,grip,head));radii=np.r_[np.zeros(len(rc)),np.full(len(wp),2.1),np.zeros(len(grip)+len(head))]
                    types=np.r_[np.full(len(rc),9),np.ones(len(wp),int),np.full(len(grip)+len(head),2)]
                    rows.append(dict(ref=endpoint,source_ring=True,ring_name=ringname,
                        wire=receipt.get('wire',endpoint.split('/')[0]),point_mm=q.tolist(),
                        departure_axis=d.tolist(),bend_unit=b.tolist(),R_mm=R,first_mm=first,
                        clock_target_degrees=angle,bend_degrees=ba,
                        clock_tf_translation_mm=list(clock.Base),clock_tf_rotation_quaternion=list(clock.Rotation.Q),
                        points=points,radii=radii,types=types,
                        bounds=np.array([(points-radii[:,None]).min(0),(points+radii[:,None]).max(0)]),
                        boxes=[],wires=[],source_ring_eye_body_mate_exact_OPEN=True,
                        complete_grip_and6cube_head_included=True,clamp_root_and_tools_OPEN=True))
        result[endpoint]=rows
    assert len(result)==4
    return result,pins


def source_pair_compatible(a,b):
    from scipy.spatial import cKDTree
    g,ix=cKDTree(b['points']).query(a['points'],workers=1)
    return float(np.min(g-a['radii']-b['radii'][ix]))>=.2-1e-5
