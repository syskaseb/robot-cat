"""Read-only actual shared module/prefix/service preflight before native details.

Scopes are explicit: incomplete prefixes, tools and full cable lengths cannot
be reported as a whole wiring or physical PASS. No CAD document is saved.
"""
import json
import time
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,SavedShapes,sha
from plan_feline_layout import MODEL,BASE,OUT,STAGES
from build_feline_interior_candidate import transform,bb
from check_feline_leg_body import placement
from plan_feline_endpoints import owner


def tube_prefix(point,direction,radius,bend,R):
    p=A.Vector(*point);d=A.Vector(*direction);d.normalize()
    b=A.Vector(*bend);b=b-d*b.dot(d);b.normalize()
    q=p+d*9
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
    motion=json.loads((OUT/'motion-layout.json').read_text())
    groups={g['role']:g for g in plan['groups']};parts={};roles={};by_group={}
    report=dict(status='SHARED_SPACE_CHECK_RUNNING',selected=False,physical_pass=False,
        scope='48rigid groups, known9mm+quarter-bend prefixes, twoleg poses and provisional sideATO/12mmrail service. No fullcables/skin/mounts/continuousmotion approval.',
        pairs=0,contacts=[],errors=[],prefixes=[],prefixes_open=[],service_budgets=[],source_sha256={})
    destination=OUT/'shared-space-checks.json';cache={}
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
                if not t.isIdentity():s.Placement=t*s.Placement
            if not s.isValid() or not s.Solids:report['errors'].append(dict(object=n,error='Invalid/non-solid source'))
            parts[n]=s;roles[n]=role;by_group[role][n]=s
    print('Saved physical parts loaded',len(parts),flush=True);save()
    for a,b in plan['potential_group_pairs_NOT_collisions']:
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
    lands=json.loads(landfile.read_text())['ends'];prefixes={};prefix_roles={}
    for row in lands:
        role=owner(row['role'],groups)
        if role not in groups:continue
        land=row['land'];point=np.array(row['point_world_mm']);centre=np.array(land['centre_world_mm'])
        if land['intervening_guide_mm']>1e-6 or abs(np.linalg.norm(centre-point)-4.5)>.05:
            report['prefixes_open'].append(dict(id=row['id'],reason='Existing land is downstream; first departure needs actual currentport reconstruction'))
            continue
        g=groups[role];rot=np.array(g['rotation_rows']);d=rot@(centre-point)/4.5;p=rot@point+g['translation_mm']
        if role=='Bank12Oprawek24Koncow':bend=[1,0,0]
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
    for row in json.loads(endfile.read_text())['body_fixed_boundary_ends']:
        role=owner(row['role'],groups)
        if role!='Bank12Oprawek24Koncow':continue
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
            for bn,b in current.items():check(an,a,bn,b,f'retained_pose{index}')
        print('Pose',index,'pairs',report['pairs'],'contacts',len(report['contacts']),flush=True);save()
    # Provisional tool grip on distal6mm of each ATO, followed by60mm withdrawal.
    # Actual tool grip, rail-mountedcompletecable service remain OPEN.
    service=dict(parts)
    for n,s in service.items():
        if roles[n].startswith('WAGO:') and abs(s.BoundBox.Center.y+50)<.1 and s.BoundBox.ZMin< -40:
            q=s.copy();q.translate(A.Vector(0,0,-12));service[n]=q
    for n,s in by_group['Bank12Oprawek24Koncow'].items():
        if '_ATO_' not in n:continue
        b=s.BoundBox;c=b.Center
        tool=Part.makeBox(25,66,12,A.Vector(c.x-12.5,b.YMin-60,c.z-6))
        probe='Tool:'+n;report['service_budgets'].append(dict(id=probe,width25_height12_mm=True,withdrawal_mm=60,rail_drop_mm=12,actual_tool_verified=False))
        for bn,bs in {**service,**retained}.items():
            if bn==n:continue
            check(probe,tool,bn,bs,'provisional_ATO_tool_rail_down_rest')
    report.update(status='SHARED_SPACE_REJECTED' if report['contacts'] or report['errors'] else 'CHECKED_SHARED_SUBSCOPES_CLEAR_REMAINING_PREFIXES_WIRES_SKIN_OPEN',
        source_sha256={**reader.hashes,planfile.relative_to(ROOT).as_posix():sha(planfile),
            landfile.relative_to(ROOT).as_posix():sha(landfile),endfile.relative_to(ROOT).as_posix():sha(endfile),
            Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},full_conductors_complete=False,
        native_details_allowed=False,remaining='Unreconstructedprefixes/allW1W3W4/continuouslooms andlengths/newgriproots/skin/jointtravel')
    save();print(json.dumps(dict(status=report['status'],pairs=report['pairs'],contacts=len(report['contacts']),errors=len(report['errors']),prefixes=len(prefixes),seconds=report['worker_seconds'])),flush=True)


if __name__=='__main__':main()
