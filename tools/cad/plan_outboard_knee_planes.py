"""Allocate whole Knee cable/grip planes from shared moving reservations.

The inherited arch itself keeps its validated length/tangents/R31. Translate
both anchors and every curve along the real joint axis, where rotation
commutes with translation. This is a derived common plane, not another cuff
height guess. Face boxes reserve space; they NEVER prove material collision.
Native grip roots, whole cables and exact material gates remain mandatory.
"""
import copy,itertools,json,math,time,zipfile
from pathlib import Path
import FreeCAD as A
import check_low_hip_loom_layout as P
import plan_current_head_wiring as H
from plan_current_joint_local_looms import scene_parts,expanded_pose


def run():
    tick=time.monotonic();fp=P.OUT/'low-joint-family-plan.json'
    family=json.loads(fp.read_text());assert family['status']=='LOW_JOINT_FAMILY_SAMPLED_SCREEN_CLEAR_MATERIAL_ROOTS_OPEN'
    af=P.ROOT/'hardware/simulation/p0/e6-leg-compatibility.json'
    axes=json.loads(af.read_text())['axes'];zf=P.ROOT/'hardware/simulation/v35/inputs.zip'
    with zipfile.ZipFile(zf) as z:components=json.loads(z.read('geometry.json'))['components']
    membership={r['name']:r['stage'].split('_')[1:] for r in components if r['stage'].startswith('Motion_')}
    targets,old,archive=P.scene();supports,assigned,_=P.allocate(family['hips'],targets)
    reader=H.P.SavedShapes()
    # Conservative retained head family, including the currently selected arm.
    heads={f'head/{yaw}/{pitch}/{n}':s for yaw,pitch in itertools.product((-15,0,15),(-10,0,5))
           for n,s in H.head(reader,yaw,pitch).items()}
    fixed={**targets,**heads,**supports}
    wire_points={n:([p for e in s.Edges for p in e.discretize(Distance=1)],rad) for n,(s,rad) in old.items()}
    faces={};rows=[];allocation=[]
    def transform(ax,angle):
        v=A.Vector(*ax['pivot_mm']);r=A.Rotation(A.Vector(*ax['axis']),angle)
        return A.Placement(v-r.multVec(v),r)
    for leg in ('FrontLeft','FrontRight','RearLeft','RearRight'):
        kk=[r for r in family['knees'] if r['physical_leg']==leg];first=kk[0];code=first['cad_code']
        pivot=A.Vector(*first['pivot_mm']);normal=A.Vector(*first['joint_axis'])
        side=1 if leg.endswith('Left') else -1
        if side*normal.y<0:normal=-normal
        vertical=A.Vector(0,0,1)-normal*normal.z;vertical.normalize()
        outward=A.Vector(-1 if leg.startswith('Front') else 1,0,0)
        footprint=[]
        for r in kk:
            for angle in (-15,0,15):
                curve=P.wire(scene_parts(r,0,angle,axes))
                footprint.extend(p for e in curve.Edges for p in e.discretize(Distance=2))
        vb=[min((p-pivot).dot(vertical) for p in footprint)-5,max((p-pivot).dot(vertical) for p in footprint)+5]
        xb=[min((p-pivot).dot(outward) for p in footprint)-5,max((p-pivot).dot(outward) for p in footprint)+5]
        limits=[]
        def reserve(n,points,rad=0):
            vs=[(p-pivot).dot(vertical) for p in points];xs=[(p-pivot).dot(outward) for p in points]
            if max(vs)+rad<vb[0] or min(vs)-rad>vb[1] or max(xs)+rad<xb[0] or min(xs)-rad>xb[1]:return
            depth=max((p-pivot).dot(normal) for p in points)+rad
            if depth>0:limits.append((depth,n))
        def reserve_samples(n,points,rad):
            # A whole curved wire bbox spans empty space. Only samples in
            # this transverse slab bound the required axial plane;0.5mm
            # added above covers the half-step of1mm discretization.
            points=[p for p in points if vb[0]-rad<=(p-pivot).dot(vertical)<=vb[1]+rad
                    and xb[0]-rad<=(p-pivot).dot(outward)<=xb[1]+rad]
            if points:reserve(n,points,rad)
        hipaxis=next(a for a in axes if a['code']==code and a['stage']=='Hip')
        for hip in (-15,0,15):
            inv=transform(hipaxis,hip).inverse()
            for n,(points,rad) in wire_points.items():reserve_samples(n,[inv.multVec(p) for p in points],rad+.5)
            for r in family['hips']:
                if r['cad_code']!=code:continue
                s=P.wire(P.parts_at(r,hip))
                reserve_samples(r['section'],[inv.multVec(p) for e in s.Edges for p in e.discretize(Distance=1)],4.2+.5)
            for n,s in fixed.items():
                if not s.Solids:continue
                member=membership.get(n[3:]) if n.startswith('P0_') else None
                stage=member[1] if member and member[0]==code else None
                poses=[A.Placement()] if stage=='Hip' or assigned.get(n)==code else [inv]
                if stage in ('Knee','Ankle'):
                    poses=[]
                    for knee,ankle in itertools.product((-15,0,15),repeat=2):
                        kt=transform(next(a for a in axes if a['code']==code and a['stage']=='Knee'),knee)
                        if stage=='Ankle':kt=kt*transform(next(a for a in axes if a['code']==code and a['stage']=='Ankle'),ankle)
                        poses.append(kt)
                b=s.BoundBox
                corners=[A.Vector(*p) for p in itertools.product((b.XMin,b.XMax),(b.YMin,b.YMax),(b.ZMin,b.ZMax))]
                for tr in poses:
                    before=len(limits);reserve(n,[tr.multVec(p) for p in corners])
                    if len(limits)==before:continue
                    limits.pop() # Whole bbox is only a broad candidate selector.
                    if n not in faces:
                        faces[n]=[]
                        for f in s.Faces:
                            b=f.BoundBox
                            faces[n].append([A.Vector(*p) for p in itertools.product((b.XMin,b.XMax),(b.YMin,b.YMax),(b.ZMin,b.ZMax))])
                    for points in faces[n]:reserve(n,[tr.multVec(p) for p in points],.5)
        depth,owner=max(limits)
        current=(A.Vector(*first['fixed_anchor_world_mm'])-pivot).dot(normal)
        plane=max(current,math.ceil((depth+4.2+.5)*2)/2)
        for i,r in enumerate(kk):
            r=copy.deepcopy(r);oldplane=(A.Vector(*r['fixed_anchor_world_mm'])-pivot).dot(normal)
            delta=normal*(plane+10*i-oldplane)
            r['fixed_anchor_world_mm']=list(A.Vector(*r['fixed_anchor_world_mm'])+delta)
            r['moving_anchor_rest_world_mm']=list(A.Vector(*r['moving_anchor_rest_world_mm'])+delta)
            r['poses']=[{k:v for k,v in q.items() if k in ('angle','first_handle_mm','second_handle_mm','length_mm','sampled_minimum_R_mm')} for q in
                (dict(angle=p['angle'],**next(s for s in p['parts'] if s['kind']=='bezier')) for p in r['poses'])]
            r['recipe']='Shared outboard Knee plane derived from all fixed wires/material/retained head and coupled moving reservations,10mm grip lanes'
            r['plane_axis_offset_mm']=plane+10*i;rows.append(r)
            # Translation along the exact rotation axis must preserve all
            # endpoint rotations/lengths/radii, not merely their nominal view.
            for q in r['poses']:
                expanded_pose(r,q['angle'])
                assert q['sampled_minimum_R_mm']>=31 and abs(q['length_mm']-r['flex_guide_mm'])<1e-6
        allocation.append(dict(leg=leg,first_plane_mm=plane,inherited_plane_mm=current,limiting_owner=owner,
            limiting_reservation_mm=depth,grip_half_width_mm=4.2,margin_mm=.5,lane_pitch_mm=10,
            transverse_vertical_mm=vb,transverse_outward_mm=xb,reservations=len(limits)))
        print('whole Knee plane',leg,allocation[-1],flush=True)
    report=dict(status='KNEE_PLANES_RESERVED_EXACT_MATERIAL_AND_NATIVE_ROOTS_OPEN',knees=rows,allocations=allocation,
        math_poses=sum(len(r['poses']) for r in rows),selected=False,W5_complete=False,native_changed=False,physical_pass=False,
        planning_only='Face boxes and sampled wire jackets allocate a shared plane; neither contact nor continuous clearance is proved. Both actual grip roots must be redesigned together.',
        retained_invariants='All8fixed-length outward Knee bows/R31/9mm lands; exact axis translations commute with Knee rotation. No purchased part cut.',
        source_sha256={**reader.hashes,**{p.relative_to(P.ROOT).as_posix():P.SHA(p) for p in (fp,af,zf,archive,Path(__file__),Path(P.__file__))}},
        worker_seconds=round(time.monotonic()-tick,3))
    (P.OUT/'outboard-knee-planes-plan.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ('status','math_poses','worker_seconds')}),flush=True)


if __name__=='__main__':run()
