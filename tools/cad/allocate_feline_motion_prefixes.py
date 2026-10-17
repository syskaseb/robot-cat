"""Coupled reallocation against all new motion states, reusing static domains.

No module positions or old immutable receipts are overwritten. Test8complete
factory pieces first; only old statically passing prefix options can survive
additional motion/skin/added-foot obstacles. Full80nets/12looms remain OPEN.
"""
import json,time,math
from pathlib import Path
import FreeCAD as A
import Part
from datetime import datetime as task_datetime,timezone as task_timezone
from check_main_p0_placement import ROOT,SavedShapes,sha
from plan_feline_layout import OUT,STAGES
from check_feline_leg_body import placement
from check_feline_shared_space import tube_prefix


def main():
    tick=time.monotonic();reader=SavedShapes();oldfile=OUT/'prefix-allocation.json';old=json.loads(oldfile.read_text())
    assert old['status']=='COUPLED_KNOWN_PREFIXES_CLEAR_FULL_WIRING_OPEN'
    factoryfile=OUT/'factory-routes.json';factory=json.loads(factoryfile.read_text())
    meta=json.loads((OUT/'interior-native-checks.json').read_text());native=ROOT/meta['native'];assert sha(native)==meta['native_sha256']
    for p in (oldfile,factoryfile):assert meta['reused_qualified_interface_receipts'][p.relative_to(ROOT).as_posix()]==sha(p)
    planfile=OUT/'module-layout.json';plan=json.loads(planfile.read_text());motionfile=OUT/'motion-layout.json';motion=json.loads(motionfile.read_text())
    skinfile=OUT/'shared-skin-exact.json';skin=json.loads(skinfile.read_text());assert skin['status']=='SAMPLED_SHARED_SKIN_CLEAR_COWLS_MOUNTS_WIRING_OPEN'
    skinnative=ROOT/skin['native'];assert sha(skinnative)==skin['native_sha256']
    feetfile=OUT/'belly-feet-native.json';feet=json.loads(feetfile.read_text());feetnative=ROOT/feet['native'];assert sha(feetnative)==feet['native_sha256']
    report=dict(status='MOTION_COUPLED_PREFIX_ALLOCATION_RUNNING',selected=False,physical_pass=False,
        old_static_domain_receipt_sha256=sha(oldfile),module_positions_changed=False,
        specifications=old['specifications'],domains={},domain_rejections={},allocation=None,
        pairs=0,wire_pairs=0,factory_motion_contacts=[],errors=[],nodes=0,
        intermediate_leg_poses=34,additional_head_poses=8,full_wiring_complete=False,moving12looms_complete=False,
        static_domain_rejections_reused=True,unchanged_static_domains_not_retested=True,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (oldfile,factoryfile,native,planfile,motionfile,skinfile,skinnative,feetfile,feetnative,Path(__file__))})
    dest=OUT/'prefix-motion-allocation.json';deadline=task_datetime.fromisoformat('2026-10-17T07:30:00+00:00')
    def save():
        report['worker_seconds']=round(time.monotonic()-tick,3);dest.write_text(json.dumps(report,indent=2)+'\n')
    def gate():
        if task_datetime.now(task_timezone.utc)>=deadline or time.monotonic()-tick>480:
            report.update(status='MOTION_PREFIX_ALLOCATION_TIME_BOUNDED_PARTIAL');save();raise TimeoutError('Deadline or480s budget')
    axes=json.loads((ROOT/'hardware/simulation/p0/e6-leg-compatibility.json').read_text())['axes']
    sources={n:reader.shape(native,n) for g in motion['membership'].values() for ns in g.values() for n in ns}
    moving={}
    for index in range(1,35):
        gate();pose=motion['poses'][index]
        for code,g in motion['membership'].items():
            aa=[next(a for a in axes if a['code']==code and a['stage']==stage) for stage in STAGES];tf=placement(aa,pose['legs'][code]['angles_delta_degrees'])
            for stage,ns in g.items():
                for n in ns:
                    s=sources[n].copy();s.Placement=tf[stage]*s.Placement;moving[f'Leg{index}:{n}']=s
    head=next(g['objects'] for g in plan['groups'] if g['role']=='HeadMechanism');headsource={n:reader.shape(native,n) for n in head}
    for pitch in (-10,0,5):
        for yaw in (-15,0,15):
            if pitch==yaw==0:continue
            for n,raw in headsource.items():
                s=raw.copy()
                if pitch:s.rotate(A.Vector(*plan['head_pitch_axis_mm']),A.Vector(0,1,0),pitch)
                if yaw:s.rotate(A.Vector(*plan['head_yaw_axis_mm']),A.Vector(0,0,1),yaw)
                moving[f'Head{pitch},{yaw}:{n}']=s
    added={r['object']:reader.shape(skinnative,r['object']) for r in json.loads((OUT/'skin-access-native.json').read_text())['parts']}
    for row in feet['parts']:
        n=row['object'];s=reader.shape(feetnative,n);oldpad=reader.shape(OUT/'FelineLayoutEnvelope.FCStd','BellyPadReservation'+n[-1]);added[n]=s.cut(oldpad)
    for row in feet['hardware']:
        n=row['object'];added[n]=reader.shape(feetnative,n).cut(reader.shape(OUT.parent/'phase1-whole-assembly/RobotCatPhase1Current.FCStd',row['replaces']))
    bounds={n:s.BoundBox for n,s in {**moving,**added}.items()}
    def near(a,b,gap):
        return sum(max(0,x-y,z-w)**2 for x,y,z,w in [(a.XMin,b.XMax,b.XMin,a.XMax),(a.YMin,b.YMax,b.YMin,a.YMax),(a.ZMin,b.ZMax,b.ZMin,a.ZMax)])<=gap*gap
    def obstruction(s,obstacles):
        b=s.BoundBox
        for n,other in obstacles.items():
            gate()
            if not near(b,bounds[n],1.25):continue
            report['pairs']+=1
            try:
                distance=s.distToShape(other)[0]
                if distance<1.25-1e-5:return dict(object=n,gap_mm=distance,required_mm=1.25)
            except Exception as exc:
                report['errors'].append(dict(object=n,error=str(exc)));return dict(object=n,error=str(exc))
        return None
    for row in factory['routes']:
        edges=[]
        for e in row['parts']:
            a,b=A.Vector(*e['start']),A.Vector(*e['end']);edges.append(Part.makeLine(a,b) if e['kind']=='line' else Part.Arc(a,A.Vector(*e['mid']),b).toShape())
        w=Part.Wire(edges);e=w.Edges[0];p=e.valueAt(e.FirstParameter);t=e.tangentAt(e.FirstParameter)
        s=w.makePipeShell([Part.Wire([Part.makeCircle(row['radius_mm'],p,t)])],True,False)
        hit=obstruction(s,moving)
        if hit:report['factory_motion_contacts'].append(dict(wire=row['wire'],**hit))
        save();print('Factory new motion',row['wire'],'blocked',bool(hit),flush=True)
    if report['factory_motion_contacts'] or report['errors']:
        report['status']='FACTORY_MOTION_REJECTED_DO_NOT_ALLOCATE_DEPENDENT_PREFIXES';save();return
    shapes={}
    for spec in old['specifications']:
        gate();sid=spec['id'];p,d,r=spec['point'],spec['direction'],spec['radius'];domain=[];rejected=[]
        for candidate in old['domains'][sid]:
            option=candidate['option'];s=tube_prefix(p,d,r,candidate['bend'],12.4)
            hit=obstruction(s,moving)
            # Original selected approaches have the exact current skin/feet
            # proof. Only newly selected geometry needs those added obstacles.
            if not hit and option!=old['allocation'][sid]:hit=obstruction(s,added)
            if hit:rejected.append(dict(option=option,kind='new_motion_or_added_material',**hit));continue
            domain.append(candidate);shapes[(sid,option)]=s
        report['domains'][sid]=domain;report['domain_rejections'][sid]=rejected
        save();print('Motion prefix',sid,'remaining',len(domain),'pairs',report['pairs'],flush=True)
    compatible_cache={}
    def compatible(a,b):
        key=tuple(sorted((a,b)))
        if key in compatible_cache:return compatible_cache[key]
        if a[1]==old['allocation'][a[0]] and b[1]==old['allocation'][b[0]]:ok=True
        else:
            sa,sb=shapes[a],shapes[b]
            if not near(sa.BoundBox,sb.BoundBox,.2):ok=True
            else:
                gate();report['wire_pairs']+=1;ok=sa.distToShape(sb)[0]>=.2-1e-5
        compatible_cache[key]=ok;return ok
    domains={sid:[(sid,c['option']) for c in domain] for sid,domain in report['domains'].items()}
    def solve(remaining,chosen):
        gate();report['nodes']+=1
        if not remaining:return chosen
        sid=min(remaining,key=lambda n:len(remaining[n]))
        choices=sorted(remaining[sid],key=lambda c:c[1]!=old['allocation'][sid])
        for a in choices:
            new={n:[b for b in choices if compatible(a,b)] for n,choices in remaining.items() if n!=sid}
            if any(not v for v in new.values()):continue
            answer=solve(new,{**chosen,sid:a[1]})
            if answer is not None:return answer
        return None
    answer=None if any(not v for v in domains.values()) else solve(domains,{})
    report.update(status='COUPLED_PREFIXES_ALL_NEW_MOTION_CLEAR_FULL_LOOMS_OPEN' if answer else 'MOTION_PREFIX_ALLOCATION_REJECTED_EMPTY_OR_COUPLED_DOMAINS',
        allocation=answer,empty_domains=[n for n,v in domains.items() if not v],
        changed_approaches=[] if answer is None else [n for n,k in answer.items() if k!=old['allocation'][n]],
        factory_motion_clear=True)
    report['source_sha256'].update(reader.hashes);save()
    print(json.dumps({k:report[k] for k in ('status','empty_domains','changed_approaches','nodes','pairs','wire_pairs','worker_seconds')}),flush=True)


if __name__=='__main__':
    try:main()
    except TimeoutError as exc:print(str(exc)+'; partial saved, no new candidates',flush=True)
