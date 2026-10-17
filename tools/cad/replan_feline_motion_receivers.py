"""One coordinated protected receiving corridor, not per-wire offsets.

Rear input joints move toX-42/Y+/-32/Z-34; two large low distribution
stations face inward; AUX shifts fore30mm to free all9mm inward lands.
Retain4MTA/other6joints/boards/skin/P0. Preflight all changed interfaces and
whole36pose motion BEFORE emitting a derived native assembly.
"""
import json,time,math,copy,sys,zipfile,hashlib
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from datetime import datetime as task_datetime,timezone as task_timezone
from check_main_p0_placement import ROOT,SavedShapes,sha,prop
from plan_feline_layout import OUT,STAGES
from check_feline_leg_body import placement
from plan_feline_factory_links import routes


def main():
    tick=time.monotonic();reader=SavedShapes();oldplanfile=OUT/'module-layout.json';old=json.loads(oldplanfile.read_text())
    meta=json.loads((OUT/'interior-native-checks.json').read_text());native=ROOT/meta['native'];assert sha(native)==meta['native_sha256']
    oldfactoryfile=OUT/'factory-routes.json';oldfactory=json.loads(oldfactoryfile.read_text())
    reportfile=OUT/'motion-receivers-checks.json';planfile=OUT/'module-motion-layout.json'
    previous=json.loads(reportfile.read_text()) if reportfile.exists() else None
    previous_plan=json.loads(planfile.read_text()) if planfile.exists() else None
    plan=copy.deepcopy(old);groups={g['role']:g for g in plan['groups']};changes={}
    def translate(role,delta):
        g=groups[role];g['translation_mm']=(np.array(g['translation_mm'])+delta).tolist()
        g['candidate_bounds_mm']=(np.array(g['candidate_bounds_mm'])+delta).tolist()
        changes[role]=dict(rotation_rows=np.eye(3).tolist(),translation_mm=list(delta),objects=g['objects'])
    translate('W044_Joint',[-25,-25,0]);translate('W052_Joint',[-25,25,0]);translate('AUX4092',[-30,0,0])
    rr=np.diag([-1,-1,1])
    for role in ('WAGO:P_SYS_new','WAGO:P_REAR'):
        g=groups[role];c=np.mean(g['candidate_bounds_mm'],axis=0);shift=c-rr@c
        extra=np.array([3.25 if role=='WAGO:P_REAR' else 0,-6.5 if role=='WAGO:P_SYS_new' else 6.5,0])
        shift+=extra;g['candidate_bounds_mm']=(np.array(g['candidate_bounds_mm'])+extra).tolist()
        g['rotation_rows']=(rr@np.array(g['rotation_rows'])).tolist();g['translation_mm']=(rr@np.array(g['translation_mm'])+shift).tolist()
        changes[role]=dict(rotation_rows=rr.tolist(),translation_mm=shift.tolist(),objects=g['objects'])
    plan.update(status='ONE_PROTECTED_RECEIVING_CORRIDOR_PREFLIGHT',selected=False,
        motion_receiving_changes=changes,parent_module_layout_sha256=sha(oldplanfile),
        physical_pass=False,new_mounts_complete=False,
        receiving_strategy='Rear input pairX-42/Y32/Z-34; large low rails centredY+/-34 face inward with negative rail staggered half-portpitch3.25mm; AUXfore30 frees all9mm inward lands. No4MTA/outputjoint/head/P0 relocation.',
        receiving_pair_budget={'casing_outer_y_mm':45,'port_face_abs_y_mm':23,'straight_land_mm':9,'bend_R_mm':12.4,
            'opposite_down_bend_end_y_separation_mm':3.2,'half_port_pitch_x_stagger_mm':3.25,
            'opposite_down_bend_end_center_distance_mm':math.hypot(3.2,3.25),'worst_jacket_center_requirement_mm':4.4,
            'budget_is_geometry_plan_not_actual_coupled_wire_pass':True})
    delta_roles=set(changes);reuse_until=-1
    if previous:
        assert previous['status']=='RECEIVING_CORRIDOR_MOTION_REJECTED_NO_REPEAT_POSES'
        assert previous['old_native_sha256']==sha(native) and not previous['errors'] and not previous['clearance_failures']
        prior_groups={g['role']:g for g in previous_plan['groups']}
        delta_roles={role for role in changes if any(groups[role][key]!=prior_groups[role][key] for key in ('rotation_rows','translation_mm'))}
        assert delta_roles=={'WAGO:P_SYS_new','WAGO:P_REAR'}
        delta_names={n for role in delta_roles for n in groups[role]['objects']}
        assert all(r['a'] in delta_names and r['scope']=='changed_cases_leg' for r in previous['contacts'])
        reuse_until=previous['leg_poses'][-1]['index']
    planfile.write_text(json.dumps(plan,indent=2)+'\n')
    rows=routes(plan);oldrows={r['wire']:r for r in oldfactory['routes']};changed_wires={'W044','W052'}
    assert all(r['parts']==oldrows[r['wire']]['parts'] for r in rows if r['wire'] not in changed_wires)
    groups_old={g['role']:g for g in old['groups']};scene={};changed={}
    for g in old['groups']:
        for n in g['objects']:
            s=reader.shape(native,n)
            if g['role'] in changes:
                t=changes[g['role']]
                if g['role'].startswith('WAGO:'):
                    rot=A.Rotation(A.Vector(0,0,1),180);s.Placement=A.Placement(A.Vector(*t['translation_mm']),rot)*s.Placement
                else:s.translate(A.Vector(*t['translation_mm']))
                changed[n]=s
            scene[n]=s
    motionfile=OUT/'motion-layout.json';motion=json.loads(motionfile.read_text());moving_names={n for g in motion['membership'].values() for ns in g.values() for n in ns}
    for n in reader.doc(native):
        if n in scene or n in moving_names:continue
        if n.startswith(('Print_P0_','Print_CP2_TailRiser','Battery','Ref_Material_P0_','Ref_Material_tail_','BellyFoot','FrameHardwareNew')):scene[n]=reader.shape(native,n)
    sk=json.loads((OUT/'skin-access-native.json').read_text());skinfile=OUT/'shared-skin-exact.json';skin=json.loads(skinfile.read_text())
    assert skin['native_sha256']==sk['native_sha256']==sha(ROOT/sk['native'])
    for r in sk['parts']:scene['Skin:'+r['object']]=reader.shape(ROOT/sk['native'],r['object'])
    report=dict(status='RECEIVING_CORRIDOR_PREFLIGHT_RUNNING',selected=False,physical_pass=False,
        changed_roles=list(changes),changed_parts=len(changed),factory_changed_wires=sorted(changed_wires),
        contacts=[],clearance_failures=[],errors=[],pairs=0,leg_poses=[],native_built=False,
        module_plan=planfile.relative_to(ROOT).as_posix(),factory_routes=rows,
        old_native_sha256=sha(native),source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (native,oldplanfile,planfile,oldfactoryfile,motionfile,skinfile,Path(__file__))})
    delta_names={n for role in delta_roles for n in groups[role]['objects']}
    if previous:
        report['unchanged_receiver_scope_reused']={'prior_status':previous['status'],'previous_source_sha256':previous['source_sha256'],
            'delta_roles':sorted(delta_roles),'unchanged_factory_and_cases_leg_poses_reused_through':reuse_until,
            'previous_contacts_not_waived':previous['contacts']}
        assert all(r['parts']==next(p for p in previous['factory_routes'] if p['wire']==r['wire'])['parts'] for r in rows)
    deadline=task_datetime.fromisoformat('2026-10-17T07:30:00+00:00')
    def save():
        report['worker_seconds']=round(time.monotonic()-tick,3);reportfile.write_text(json.dumps(report,indent=2)+'\n')
    def gate():
        if task_datetime.now(task_timezone.utc)>=deadline or time.monotonic()-tick>520:
            report.update(status='RECEIVING_CORRIDOR_TIME_BOUNDED_PARTIAL');save();raise TimeoutError('Deadline or520s budget')
    bounds={n:s.BoundBox for n,s in scene.items()}
    def near(a,b,gap=0):
        return sum(max(0,x-y,z-w)**2 for x,y,z,w in [(a.XMin,b.XMax,b.XMin,a.XMax),(a.YMin,b.YMax,b.YMin,a.YMax),(a.ZMin,b.ZMax,b.ZMin,a.ZMax)])<=gap*gap
    def check(an,a,bn,b,scope,pose=None,gap=0):
        gate()
        if not near(a.BoundBox,b.BoundBox,gap):return
        report['pairs']+=1
        try:
            c=a.common(b)
            if not c.isNull() and not c.isValid():raise ValueError('Invalid exact intersection')
            if c.Volume>1e-5:
                pts,_=c.tessellate(.2);v=[list(p) for p in pts]
                report['contacts'].append(dict(a=an,b=bn,scope=scope,pose=pose,volume_mm3=c.Volume,
                    witness_mesh_bounds_mm=[[min(p[i] for p in v) for i in range(3)],[max(p[i] for p in v) for i in range(3)]] if v else None))
            elif gap:
                distance=a.distToShape(b)[0]
                if distance<gap-1e-5:report['clearance_failures'].append(dict(a=an,b=bn,scope=scope,pose=pose,gap_mm=distance,required_mm=gap))
        except Exception as exc:report['errors'].append(dict(a=an,b=bn,scope=scope,error=str(exc)))
    save()
    for n,s in changed.items():
        if n not in delta_names:continue
        for bn,b in scene.items():
            if bn==n or (bn in changed and bn<n):continue
            if bn in changes.get(next((role for role,c in changes.items() if n in c['objects']),''),{}).get('objects',[]):continue
            check(n,s,bn,b,'changed_material')
    save();print('Receiving changed material',len(report['contacts']),'errors',len(report['errors']),flush=True)
    if report['contacts'] or report['errors']:
        report['status']='RECEIVING_CORRIDOR_STATIC_REJECTED_BEFORE_MOTION';save();return
    def pipe(parts,r):
        edges=[]
        for e in parts:
            a,b=A.Vector(*e['start']),A.Vector(*e['end']);edges.append(Part.makeLine(a,b) if e['kind']=='line' else Part.Arc(a,A.Vector(*e['mid']),b).toShape())
        w=Part.Wire(edges);e=w.Edges[0];p=e.valueAt(e.FirstParameter);t=e.tangentAt(e.FirstParameter)
        result=w.makePipeShell([Part.Wire([Part.makeCircle(r,p,t)])],True,False);assert result.isValid();return result
    pipes={r['wire']:pipe(r['parts'],r['radius_mm']) for r in rows}
    for row in rows:
        wid=row['wire'];s=pipes[wid]
        if wid in changed_wires and not previous:
            trimmed=copy.deepcopy(row['parts'])
            for index,first in ((0,True),(-1,False)):
                e=trimmed[index];a,b=np.array(e['start']),np.array(e['end']);d=(b-a)/np.linalg.norm(b-a)
                if first:e['start']=(a+2.5*d).tolist()
                else:e['end']=(b-2.5*d).tolist()
            short=pipe(trimmed,row['radius_mm']);mates=set(groups[row['source_group']]['objects']+groups[row['joint_group']]['objects'])
            for n,other in scene.items():check(wid,short if n in mates else s,n,other,'changed_factory_static',gap=1.25)
        else:
            for n,other in changed.items():
                if n in delta_names:check(wid,s,n,other,'unchanged_factory_new_cases',gap=1.25)
    for wid in (changed_wires if not previous else ()):
        for other,s in pipes.items():
            if other==wid or (other in changed_wires and other<wid):continue
            check(wid,pipes[wid],other,s,'factory_mutual',gap=.2)
    save();print('Receiving factory static',len(report['contacts']),'gaps',len(report['clearance_failures']),flush=True)
    if any(report[k] for k in ('contacts','clearance_failures','errors')):
        report['status']='RECEIVING_CORRIDOR_FACTORY_REJECTED_BEFORE_MOTION';save();return
    axes=json.loads((ROOT/'hardware/simulation/p0/e6-leg-compatibility.json').read_text())['axes'];leg={n:reader.shape(native,n) for n in moving_names}
    for index,pose in enumerate(motion['poses'][:36]):
        start=report['pairs']
        for code,g in motion['membership'].items():
            aa=[next(a for a in axes if a['code']==code and a['stage']==stage) for stage in STAGES];tf=placement(aa,pose['legs'][code]['angles_delta_degrees'])
            for stage,ns in g.items():
                for n in ns:
                    s=leg[n].copy();s.Placement=tf[stage]*s.Placement
                    for cn,c in changed.items():
                        if cn in delta_names or index>reuse_until:check(cn,c,n,s,'changed_cases_leg',index)
                    if index>reuse_until:
                        for wid in changed_wires:check(wid,pipes[wid],n,s,'changed_factory_leg',index,1.25)
        report['leg_poses'].append(dict(index=index,pairs=report['pairs']-start));save()
        print('Receiving leg',index,'hits',len(report['contacts']),'gaps',len(report['clearance_failures']),flush=True)
        if any(report[k] for k in ('contacts','clearance_failures','errors')):
            report['status']='RECEIVING_CORRIDOR_MOTION_REJECTED_NO_REPEAT_POSES';save();return
    report.update(status='RECEIVING_CORRIDOR_STATIC_FACTORY_AND36LEGPOSES_CLEAR_PREFIXES_HEAD_OPEN',
        factory_lengths_mm={r['wire']:r['guide_mm'] for r in rows if r['wire'] in changed_wires})
    report['source_sha256'].update(reader.hashes);save()
    if '--build-native-if-clear' not in sys.argv:return
    target=OUT/'FelineInteriorMotion.FCStd';assert not target.exists(),'Receive existing derived assembly before rebuild'
    doc=A.openDocument(str(native));doc_name=doc.Name
    try:
        doc.saveAs(str(target))
        for role,c in changes.items():
            for n in c['objects']:
                ob=doc.getObject(n)
                if role.startswith('WAGO:'):
                    transform=A.Placement(A.Vector(*c['translation_mm']),A.Rotation(A.Vector(0,0,1),180))
                    ob.Placement=transform*ob.Placement
                else:ob.Placement.Base=ob.Placement.Base+A.Vector(*c['translation_mm'])
        doc.recompute()
        for n,s in changed.items():
            actual=doc.getObject(n).Shape;assert actual.isValid() and abs(actual.Volume-s.Volume)<1e-4,n
            assert (actual.CenterOfMass-s.CenterOfMass).Length<1e-5,n
        doc.save();A.closeDocument(doc_name);doc=None
        after=SavedShapes();oldxml=reader.doc(native);newxml=after.doc(target);assert set(oldxml)==set(newxml)
        unchanged=[]
        for n in oldxml:
            if n in changed:continue
            assert reader.placement(oldxml[n]).isSame(after.placement(newxml[n]),1e-7),n
            if prop(oldxml[n],'LinkPlacement') is not None:assert reader.placement(oldxml[n],'LinkPlacement').isSame(after.placement(newxml[n],'LinkPlacement'),1e-7),n
            unchanged.append(n)
        d=A.openDocument(str(target))
        try:
            for n,s in changed.items():
                actual=d.getObject(n).Shape;assert actual.isValid() and abs(actual.Volume-s.Volume)<1e-4 and (actual.CenterOfMass-s.CenterOfMass).Length<1e-5,n
        finally:A.closeDocument(d.Name)
        report.update(native_built=True,native=target.relative_to(ROOT).as_posix(),native_sha256=sha(target),
            changed_native_parts_verified=len(changed),unchanged_saved_node_placements_verified=len(unchanged),
            fresh_reopen=True,full_unchanged_geometry_reaudit_performed=False)
        save();print(json.dumps({k:report[k] for k in ('status','native_built','changed_native_parts_verified','worker_seconds')}),flush=True)
    finally:
        if doc and doc.Name in A.listDocuments():A.closeDocument(doc.Name)


if __name__=='__main__':
    try:main()
    except TimeoutError as exc:print(str(exc)+'; partial saved, no new work',flush=True)
