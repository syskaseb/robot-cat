"""Resolve shared planning failures against actual shapes before changing CAD."""
import itertools
import json
import time
from pathlib import Path
import FreeCAD as A
import build_complete_source_carriers as B
from loom_land_port import build

P=B.P


def transform(axes,code,h,k,stage):
    t=A.Placement()
    for name,angle in (('Hip',h),('Knee',k)):
        ax=next(r for r in axes if r['code']==code and r['stage']==name)
        p=A.Vector(*ax['pivot_mm']);r=A.Rotation(A.Vector(*ax['axis']),angle)
        t=t*A.Placement(p-r.multVec(p),r)
        if name==stage:break
    return t


def moved(s,t):
    q=s.copy();q.Placement=t*q.Placement;return q


def run():
    tick=time.monotonic()
    files=[P.OUT/n for n in ('remaining-loom-support-paths.json','remaining-retention-rest.json',
        'remaining-loom-roots-plan.json','front-fixed-port-clearance-native.json','leg-source-near-member-plan.json')]
    paths,rest,roots,native,family=[json.loads(f.read_text()) for f in files]
    af=P.ROOT/'hardware/simulation/p0/e6-leg-compatibility.json';axes=json.loads(af.read_text())['axes']
    reader=B.H.P.SavedShapes();targets,wires,archive,sf,hw=B.current_scene(reader)
    model=P.ROOT/native['native'];assert P.SHA(model)==native['native_sha256']
    for name in reader.doc(model):
        if name.endswith('SourceCarrier') or name.startswith('Ref_'):targets[name.removeprefix('Ref_')]=reader.shape(model,name)
    fixed=[];rear=[];wire_rows=[]
    for group in paths['groups']:
        failed=[r for r in group['paths'] if not r['points_mm']]
        if not failed:continue
        x,y,z=group['root_world_mm'];seed=P.box([x-2,y-3,z-2,x+2,y+3,z+2])
        contract=next(g for g in roots['groups'] if g['id']==group['id'])
        if group['id'].endswith('FixedCarrier'):
            name=failed[0]['start_blocker'].split('/',1)[1];other=targets[name]
            fixed.append(dict(group=group['id'],target=name,actual_seed_gap_mm=seed.distToShape(other)[0],
                actual_seed_intersection_mm3=seed.common(other).Volume,
                seed_outside_parent_mm3=seed.cut(targets[contract['preserved_owner']]).Volume,
                root_choice=group['root_choice']))
        elif group['id'].endswith('HipExtension'):
            code=contract['owner_stage'].split('_')[1];parent=targets[contract['preserved_owner']]
            # The forced-clear seed can be trapped solely by conservative
            # reservations around unchanged parent material. Check six actual
            # connected departures, not arbitrary replacement cap positions.
            for axis,sign in itertools.product(range(3),(-1,1)):
                c=[x,y,z];c[axis]+=sign*4
                q=P.box([min(c[0],x)-2,min(c[1],y)-3,min(c[2],z)-2,
                         max(c[0],x)+2,max(c[1],y)+3,max(c[2],z)+2])
                added=q.cut(parent);hits=[]
                for name,t in targets.items():
                    if name==contract['preserved_owner'] or not q.BoundBox.intersect(t.BoundBox):continue
                    volume=q.common(t).Volume
                    if volume>1e-5:hits.append(dict(target=name,volume_mm3=volume))
                rear.append(dict(group=group['id'],axis=axis,sign=sign,end=c,
                    added_to_parent_mm3=added.Volume,rest_contacts=hits))
        else:
            selected=next(g for g in rest['groups'] if g['id']==group['id'])
            for failure in failed:
                port=next(p for p in selected['ports'] if p['land_id']==failure['land_id'])
                land=next(p for p in contract['lands'] if p['id']==failure['land_id'])
                target=failure['goal_blocker'].split('/',1)[1]
                route=next(r for r in family['routes'] if r['loom']==target)
                shapes=build(land,port['arrival_normal'],port['recipe']['band_axial_offset_mm'])
                a,b,c=port['arrival_world_mm'];shapes['seed']=P.box([a-2,b-3,c-2,a+2,b+3,c+2])
                code=contract['owner_stage'].split('_')[1]
                for h,k in itertools.product((-15,0,15),repeat=2):
                    t=transform(axes,code,h,k,'Knee')
                    wire=P.wire(B.parts_for_loom(family,target,h,k,axes)+B.moved_parts(route['source_parts'],route['source'],h,k,axes))
                    wire_rows.append(dict(land=land['id'],target=target,hip=h,knee=k,
                        gaps_to_wire_centre_mm={n:moved(shapes[n],t).distToShape(wire)[0] for n in ('seed','body','band')},
                        wire_radius_project_mm=3,planning_wire_radius_including_margin_and_sampling_mm=4))
    result=dict(status='ACTUAL_ENDPOINT_DIAGNOSIS_NOT_LAYOUT_APPROVAL',fixed_roots=fixed,rear_root_departures=rear,
        blocked_wire_ports=wire_rows,physical_pass=False,selected=False,
        source_sha256={f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in files+[af,archive,sf,hw,model,Path(__file__)]},
        worker_seconds=round(time.monotonic()-tick,3))
    (P.OUT/'remaining-support-endpoint-diagnosis.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result),flush=True)


if __name__=='__main__':run()
