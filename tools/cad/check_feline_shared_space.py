"""Read-only actual shared module/prefix/service preflight before native details.

Scopes are explicit: incomplete prefixes, tools and full cable lengths cannot
be reported as a whole wiring or physical PASS. No CAD document is saved.
"""
import json
import time
import sys
import subprocess
import hashlib
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,SavedShapes,sha
from plan_feline_layout import MODEL,BASE,OUT,STAGES
from build_feline_interior_candidate import transform,bb
from check_feline_leg_body import placement
from plan_feline_endpoints import owner


def tube_prefix(point,direction,radius,bend,R,straight_mm=9):
    p=A.Vector(*point);d=A.Vector(*direction);d.normalize()
    b=A.Vector(*bend);b=b-d*b.dot(d);b.normalize()
    q=p+d*straight_mm
    mid=q+d*(R/2**.5)+b*(R*(1-1/2**.5))
    end=q+d*R+b*R
    spine=Part.Wire([Part.makeLine(p,q),Part.Arc(q,mid,end).toShape()])
    profile=Part.Wire([Part.makeCircle(radius,p,d)])
    result=spine.makePipeShell([profile],True,False)
    assert result.isValid() and len(result.Solids)==1
    return result


def main():
    tick=time.monotonic();reader=SavedShapes()
    planfile=OUT/'module-layout.json';plan=json.loads(planfile.read_text())
    parts_only='--parts-only' in sys.argv
    motion=json.loads((OUT/'motion-layout.json').read_text())
    groups={g['role']:g for g in plan['groups']};parts={};roles={};by_group={}
    changed=None;parent=None
    if '--reuse-git' in sys.argv:
        commit=sys.argv[sys.argv.index('--reuse-git')+1]
        def gitjson(relative):
            raw=subprocess.run(['git','show',commit+':'+relative],cwd=ROOT,check=True,capture_output=True).stdout
            return json.loads(raw)
        parent=gitjson((OUT/'shared-parts-checks.json').relative_to(ROOT).as_posix())
        oldplan=gitjson(planfile.relative_to(ROOT).as_posix())
        assert parent['status']=='SHARED_PARTS_REJECTED' and not parent['errors'] and parts_only
        oldgroups={g['role']:g for g in oldplan['groups']};assert set(oldgroups)==set(groups)
        keys=('objects','rotation_rows','translation_mm')
        changed={role for role in groups if any(groups[role][k]!=oldgroups[role][k] for k in keys)}
        assert changed and plan['geometry_source_sha256']==oldplan['geometry_source_sha256']
        for key in ('part_pose_overrides','reference_substitutions'):assert plan[key]==oldplan[key]
        for n,h in parent['source_sha256'].items():
            if n.endswith('.FCStd'):assert sha(ROOT/n)==h,n
        oldmotion=subprocess.run(['git','show',commit+':'+(OUT/'motion-layout.json').relative_to(ROOT).as_posix()],cwd=ROOT,check=True,capture_output=True).stdout
        assert json.loads(oldmotion)==motion,'Kinematic data changed; do not reuse'
        affected={n for role in changed for n in groups[role]['objects']}
        assert all(c['a'] in affected or c['b'] in affected for c in parent['contacts'])
    report=dict(status='SHARED_SPACE_CHECK_RUNNING',selected=False,physical_pass=False,
        scope='48rigid groups, known9mm+quarter-bend prefixes, twoleg poses and provisional sideATO/12mmrail service. No fullcables/skin/mounts/continuousmotion approval.',
        pairs=0,contacts=[],errors=[],prefixes=[],prefixes_open=[],service_budgets=[],source_sha256={})
    if parent is not None:report['unchanged_scope_reuse']=dict(parent_commit=commit,parent_pairs=parent['pairs'],
        changed_roles=sorted(changed),unchanged_rigid_recipes_verified=len(groups)-len(changed),
        scope='All unchanged material and twolegposes reused by exactsourcepins/poses/overrides. Parentpairtotal is not falsely called number ofreusedpairs.',
        parent_geometry_validation_reused=True)
    if parent is not None:report['unchanged_scope_reuse']['kinematic_JSON_values_identical']=True
    destination=OUT/('shared-parts-checks.json' if parts_only else 'shared-space-checks.json');cache={}
    def save():
        report['worker_seconds']=round(time.monotonic()-tick,3)
        destination.write_text(json.dumps(report,indent=2)+'\n')
    def check(an,a,bn,b,scope):
        for n,s in ((an,a),(bn,b)):
            if (n,scope) not in cache:cache[n,scope]=s.BoundBox
        if not cache[an,scope].intersect(cache[bn,scope]):return
        report['pairs']+=1
        try:
            c=a.common(b)
            if not c.isNull() and not c.isValid():raise ValueError('Invalid intersection')
            if c.Volume>1e-5:report['contacts'].append(dict(a=an,b=bn,scope=scope,volume_mm3=c.Volume,witness_bounds_mm=bb(c)))
        except Exception as e:report['errors'].append(dict(a=an,b=bn,scope=scope,error=str(e)))
    for role,g in groups.items():
        t=transform(g);by_group[role]={}
        for n in g['objects']:
            replacement=plan['reference_substitutions'].get(n)
            if replacement:
                s=reader.shape(ROOT/replacement['source'],replacement['object'])
                s.Placement=t*A.Placement(A.Vector(*replacement['world_shift_before_head_drop_mm']),A.Rotation())*s.Placement
            else:
                s=reader.shape(MODEL,n)
                override=plan.get('part_pose_overrides',{}).get(n)
                if override:s.Placement=transform(override)*s.Placement
                if not t.isIdentity():
                    if t.Rotation.isIdentity():s.translate(t.Base)
                    else:s.Placement=t*s.Placement
            if (changed is None or role in changed) and (not s.isValid() or not s.Solids):
                report['errors'].append(dict(object=n,error='Invalid/non-solid source'))
            parts[n]=s;roles[n]=role;by_group[role][n]=s
    print('Saved physical parts loaded',len(parts),flush=True);save()
    for a,b in plan['potential_group_pairs_NOT_collisions']:
        if changed is not None and not changed.intersection((a,b)):continue
        for an,aa in by_group[a].items():
            for bn,bs in by_group[b].items():check(an,aa,bn,bs,'rigid_groups')
    print('Common groups',report['pairs'],'contacts',len(report['contacts']),flush=True);save()
    retained={}
    for r in motion['inventory']:
        n=r['object']
        if n in parts or r['kind']!='surface':continue
        if r['label'].startswith(('P0_','tail/')) or n.startswith(('Print_P0_','Print_CP2_TailRiser','Battery')):
            retained[n]=reader.shape(MODEL,n)
    old_envelope=OUT/'FelineLayoutEnvelope.FCStd'
    for i in range(1,5):
        n=f'BellyPadReservation{i}';retained[n]=reader.shape(old_envelope,n)
    landfile=BASE/'body-harness-checkpoint/remaining25-interface-allocation.json'
    lands=[] if parts_only else json.loads(landfile.read_text())['ends'];prefixes={};prefix_roles={}
    for row in lands:
        role=owner(row['role'],groups)
        if role not in groups:continue
        land=row['land'];point=np.array(row['point_world_mm']);centre=np.array(land['centre_world_mm'])
        if land['intervening_guide_mm']>1e-6 or abs(np.linalg.norm(centre-point)-4.5)>.05:
            report['prefixes_open'].append(dict(id=row['id'],reason='Existing land is downstream; first departure needs actual currentport reconstruction'))
            continue
        g=groups[role];rot=np.array(g['rotation_rows'])
        override_name=plan.get('role_pose_overrides',{}).get(row['role'])
        if override_name:
            ov=plan['part_pose_overrides'][override_name];rr=np.array(ov['rotation_rows']);tt=np.array(ov['translation_mm'])
            point=rr@point+tt;centre=rr@centre+tt
        d=rot@(centre-point)/4.5;p=rot@point+g['translation_mm']
        if role.startswith('Bank'):bend=[1,0,0]
        elif role.startswith('MTA_'):bend=[0,-np.sign(p[1]),0]
        else:bend=[1,0,0] if abs(d[0])<.5 else [0,1,0]
        radius=row['project_radius_mm'];R=max(12.4,5*2*radius)
        n='Prefix:'+row['id'];prefixes[n]=tube_prefix(p,d,radius,bend,R);prefix_roles[n]=role
        report['prefixes'].append(dict(id=n,owner=role,start_mm=p.tolist(),direction=d.tolist(),
            radius_mm=radius,straight_mm=9,bend_R_mm=R,bend=bend,
            basis='Exact source role/point/adjacent land; project radius, not delivered manufacturer guarantee'))
    # Bodyfanout power ends use the retained common TE OUT family at its saved
    # lowerZ mouth. Project2mm OD/R10 is a nominal design budget, not delivery.
    endfile=BASE/'body-harness-checkpoint/w5-current-end-coverage.json'
    for row in ([] if parts_only else json.loads(endfile.read_text())['body_fixed_boundary_ends']):
        role=owner(row['role'],groups)
        if not role or not role.startswith('Bank'):continue
        g=groups[role];rot=np.array(g['rotation_rows']);p=rot@row['point_world_mm']+g['translation_mm'];d=rot@[0,0,-1]
        n='Prefix:'+row['id'];prefixes[n]=tube_prefix(p,d,1,[1,0,0],10);prefix_roles[n]=role
        report['prefixes'].append(dict(id=n,owner=role,start_mm=p.tolist(),direction=d.tolist(),
            radius_mm=1,straight_mm=9,bend_R_mm=10,bend=[1,0,0],basis='Retained TEOUT lowerZ mouth family, nominal bodyfanout OD2/R10 budget'))
    for an,a in prefixes.items():
        for bn,b in parts.items():check(an,a,bn,b,'prefix_modules')
    for i,(an,a) in enumerate(prefixes.items()):
        for bn,b in list(prefixes.items())[i+1:]:check(an,a,bn,b,'prefix_prefix')
    print('Prefixes',len(prefixes),'pairs',report['pairs'],'contacts',len(report['contacts']),flush=True);save()
    axes=json.loads((ROOT/'hardware/simulation/p0/e6-leg-compatibility.json').read_text())['axes']
    stage_of={n for g in motion['membership'].values() for ns in g.values() for n in ns}
    for index in (0,35):
        pose=motion['poses'][index];current={n:s for n,s in retained.items() if n not in stage_of}
        for code,g in motion['membership'].items():
            aa=[next(a for a in axes if a['code']==code and a['stage']==stage) for stage in STAGES]
            tf=placement(aa,pose['legs'][code]['angles_delta_degrees'])
            for stage,ns in g.items():
                for n in ns:
                    s=retained[n].copy();s.Placement=tf[stage]*s.Placement;current[n]=s
        for an,a in {**parts,**prefixes}.items():
            if changed is not None and roles.get(an) not in changed:continue
            for bn,b in current.items():check(an,a,bn,b,f'retained_pose{index}')
        print('Pose',index,'pairs',report['pairs'],'contacts',len(report['contacts']),flush=True);save()
    # Provisional tool grip on distal6mm of each ATO, followed by60mm withdrawal.
    # Actual tool grip, rail-mountedcompletecable service remain OPEN.
    service=dict(parts)
    for n,s in service.items():
        if roles[n].startswith('WAGO:') and abs(s.BoundBox.Center.y+50)<.1 and s.BoundBox.ZMin< -40:
            q=s.copy();q.translate(A.Vector(0,0,-12));service[n]=q
    service_bank={} if parts_only else {n:s for role,g in by_group.items() if role.startswith('Bank') for n,s in g.items()}
    for n,s in service_bank.items():
        if '_ATO_' not in n:continue
        b=s.BoundBox;c=b.Center
        tool=Part.makeBox(25,66,12,A.Vector(c.x-12.5,b.YMin-60,c.z-6))
        probe='Tool:'+n;report['service_budgets'].append(dict(id=probe,width25_height12_mm=True,withdrawal_mm=60,rail_drop_mm=12,actual_tool_verified=False))
        for bn,bs in {**service,**retained}.items():
            if bn==n:continue
            check(probe,tool,bn,bs,'provisional_ATO_tool_rail_down_rest')
    report.update(status=('SHARED_PARTS_REJECTED' if parts_only else 'SHARED_SPACE_REJECTED') if report['contacts'] or report['errors'] else ('COMMON_PARTS_TWO_POSES_CLEAR_PREFIXES_WIRES_SKIN_OPEN' if parts_only else 'CHECKED_SHARED_SUBSCOPES_CLEAR_REMAINING_PREFIXES_WIRES_SKIN_OPEN'),
        source_sha256={**reader.hashes,planfile.relative_to(ROOT).as_posix():sha(planfile),
            landfile.relative_to(ROOT).as_posix():sha(landfile),endfile.relative_to(ROOT).as_posix():sha(endfile),
            Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},full_conductors_complete=False,
        native_details_allowed=False,remaining='Unreconstructedprefixes/allW1W3W4/continuouslooms andlengths/newgriproots/skin/jointtravel')
    save();print(json.dumps(dict(status=report['status'],pairs=report['pairs'],contacts=len(report['contacts']),errors=len(report['errors']),prefixes=len(prefixes),seconds=report['worker_seconds'])),flush=True)


if __name__=='__main__':main()
