"""Coupled reallocation against all new motion states, reusing static domains.

No module positions or old immutable receipts are overwritten. Test8complete
factory pieces first; only old statically passing prefix options can survive
additional motion/skin/added-foot obstacles. Full80nets/12looms remain OPEN.
"""
import json,time,math,copy,sys
from pathlib import Path
import FreeCAD as A
import Part
import numpy as np
from datetime import datetime as task_datetime,timezone as task_timezone
from check_main_p0_placement import ROOT,SavedShapes,sha
from plan_feline_layout import OUT,STAGES
from check_feline_leg_body import placement
from check_feline_shared_space import tube_prefix
from plan_feline_interior import inside_shared


def main():
    tick=time.monotonic();reader=SavedShapes();oldfile=OUT/'prefix-allocation.json';old=json.loads(oldfile.read_text())
    assert old['status']=='COUPLED_KNOWN_PREFIXES_CLEAR_FULL_WIRING_OPEN'
    factoryfile=OUT/'factory-routes.json';factory=json.loads(factoryfile.read_text())
    meta=json.loads((OUT/'interior-native-checks.json').read_text());native=ROOT/meta['native'];assert sha(native)==meta['native_sha256']
    for p in (oldfile,factoryfile):assert meta['reused_qualified_interface_receipts'][p.relative_to(ROOT).as_posix()]==sha(p)
    planfile=OUT/'module-layout.json';plan=json.loads(planfile.read_text());motionfile=OUT/'motion-layout.json';motion=json.loads(motionfile.read_text())
    scenario=None;parent_native=native;changed_roles={};affected=set();specifications=copy.deepcopy(old['specifications'])
    if '--receiver-scenario' in sys.argv:
        scenariofile=OUT/'motion-receivers-checks.json';scenario=json.loads(scenariofile.read_text())
        assert scenario['status']=='RECEIVING_CORRIDOR_STATIC_FACTORY_AND36LEGPOSES_CLEAR_PREFIXES_HEAD_OPEN' and scenario['native_built']
        assert scenario['old_native_sha256']==sha(parent_native)
        native=ROOT/scenario['native'];assert sha(native)==scenario['native_sha256']
        planfile=ROOT/scenario['module_plan'];plan=json.loads(planfile.read_text());changed_roles=plan['motion_receiving_changes']
        factory={'routes':scenario['factory_routes']}
        for spec in specifications:
            if spec['role'] not in changed_roles:continue
            change=changed_roles[spec['role']];rotation=np.array(change['rotation_rows']);shift=np.array(change['translation_mm'])
            spec['point']=(rotation@np.array(spec['point'])+shift).tolist();spec['direction']=(rotation@np.array(spec['direction'])).tolist();affected.add(spec['id'])
    skinfile=OUT/'shared-skin-exact.json';skin=json.loads(skinfile.read_text());assert skin['status']=='SAMPLED_SHARED_SKIN_CLEAR_COWLS_MOUNTS_WIRING_OPEN'
    skinnative=ROOT/skin['native'];assert sha(skinnative)==skin['native_sha256']
    feetfile=OUT/'belly-feet-native.json';feet=json.loads(feetfile.read_text());feetnative=ROOT/feet['native'];assert sha(feetnative)==feet['native_sha256']
    report=dict(status='MOTION_COUPLED_PREFIX_ALLOCATION_RUNNING',selected=False,physical_pass=False,
        old_static_domain_receipt_sha256=sha(oldfile),module_positions_changed=False,
        specifications=specifications,domains={},domain_rejections={},allocation=None,
        pairs=0,wire_pairs=0,factory_motion_contacts=[],errors=[],nodes=0,
        intermediate_leg_poses=34,additional_head_poses=8,full_wiring_complete=False,moving12looms_complete=False,
        static_domain_rejections_reused=True,unchanged_static_domains_not_retested=True,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (oldfile,factoryfile,native,planfile,motionfile,skinfile,skinnative,feetfile,feetnative,Path(__file__))})
    if scenario:
        report.update(module_positions_changed=True,changed_roles=list(changed_roles),relocated_approaches=sorted(affected),
            receiving_scenario= scenariofile.relative_to(ROOT).as_posix(),unchanged6factory_motion_reuse_commit='5b9ab49')
        report['source_sha256'][scenariofile.relative_to(ROOT).as_posix()]=sha(scenariofile)
    dest=OUT/'prefix-motion-allocation.json';deadline=task_datetime.fromisoformat('2026-10-17T07:30:00+00:00')
    def save():
        report['worker_seconds']=round(time.monotonic()-tick,3);dest.write_text(json.dumps(report,indent=2)+'\n')
    def gate():
        if task_datetime.now(task_timezone.utc)>=deadline or time.monotonic()-tick>480:
            report.update(status='MOTION_PREFIX_ALLOCATION_TIME_BOUNDED_PARTIAL');save();raise TimeoutError('Deadline or480s budget')
    axes=json.loads((ROOT/'hardware/simulation/p0/e6-leg-compatibility.json').read_text())['axes']
    sources={n:reader.shape(native,n) for g in motion['membership'].values() for ns in g.values() for n in ns}
    moving={}
    endpoint_motion={}
    for index in range(36):
        gate();pose=motion['poses'][index]
        for code,g in motion['membership'].items():
            aa=[next(a for a in axes if a['code']==code and a['stage']==stage) for stage in STAGES];tf=placement(aa,pose['legs'][code]['angles_delta_degrees'])
            for stage,ns in g.items():
                for n in ns:
                    s=sources[n].copy();s.Placement=tf[stage]*s.Placement
                    (endpoint_motion if index in (0,35) else moving)[f'Leg{index}:{n}']=s
    head=next(g['objects'] for g in plan['groups'] if g['role']=='HeadMechanism');headsource={n:reader.shape(native,n) for n in head}
    for pitch in (-10,0,5):
        for yaw in (-15,0,15):
            if pitch==yaw==0:continue
            for n,raw in headsource.items():
                s=raw.copy()
                if pitch:s.rotate(A.Vector(*plan['head_pitch_axis_mm']),A.Vector(0,1,0),pitch)
                if yaw:s.rotate(A.Vector(*plan['head_yaw_axis_mm']),A.Vector(0,0,1),yaw)
                moving[f'Head{pitch},{yaw}:{n}']=s
    full_static={};new_cases={};groups={g['role']:g for g in plan['groups']}
    if scenario:
        for role,g in groups.items():
            for n in g['objects']:
                s=reader.shape(native,n);full_static[n]=s
                if role in changed_roles:new_cases[n]=s
        moving_names=set(sources)
        for n in reader.doc(native):
            if n in full_static or n in moving_names:continue
            if n.startswith(('Print_P0_','Print_CP2_TailRiser','Battery','Ref_Material_P0_','Ref_Material_tail_','BellyFoot','FrameHardwareNew')):full_static[n]=reader.shape(native,n)
    added={r['object']:reader.shape(skinnative,r['object']) for r in json.loads((OUT/'skin-access-native.json').read_text())['parts']}
    for row in feet['parts']:
        n=row['object'];s=reader.shape(feetnative,n);oldpad=reader.shape(OUT/'FelineLayoutEnvelope.FCStd','BellyPadReservation'+n[-1]);added[n]=s.cut(oldpad)
    for row in feet['hardware']:
        n=row['object'];added[n]=reader.shape(feetnative,n).cut(reader.shape(OUT.parent/'phase1-whole-assembly/RobotCatPhase1Current.FCStd',row['replaces']))
    bounds={n:s.BoundBox for n,s in {**moving,**endpoint_motion,**added,**full_static,**new_cases}.items()}
    def near(a,b,gap):
        return sum(max(0,x-y,z-w)**2 for x,y,z,w in [(a.XMin,b.XMax,b.XMin,a.XMax),(a.YMin,b.YMax,b.YMin,a.YMax),(a.ZMin,b.ZMax,b.ZMin,a.ZMax)])<=gap*gap
    def obstruction(s,obstacles,root_names=(),trimmed=None,factory_obstacle=False):
        b=s.BoundBox
        for n,other in obstacles.items():
            gate()
            gap=.2 if factory_obstacle else 1.25
            if not near(b,bounds[n],gap):continue
            report['pairs']+=1
            try:
                if n in root_names:
                    c=s.common(other)
                    if not c.isNull() and not c.isValid():raise ValueError('Invalid own-mate intersection')
                    if c.Volume>1e-5:return dict(object=n,volume_mm3=c.Volume,kind='own_mate_penetration')
                distance=(trimmed if n in root_names else s).distToShape(other)[0]
                if distance<gap-1e-5:return dict(object=n,gap_mm=distance,required_mm=gap)
            except Exception as exc:
                report['errors'].append(dict(object=n,error=str(exc)));return dict(object=n,error=str(exc))
        return None
    factory_shapes={}
    head_motion={n:s for n,s in moving.items() if n.startswith('Head')}
    for row in factory['routes']:
        edges=[]
        for e in row['parts']:
            a,b=A.Vector(*e['start']),A.Vector(*e['end']);edges.append(Part.makeLine(a,b) if e['kind']=='line' else Part.Arc(a,A.Vector(*e['mid']),b).toShape())
        w=Part.Wire(edges);e=w.Edges[0];p=e.valueAt(e.FirstParameter);t=e.tangentAt(e.FirstParameter)
        s=w.makePipeShell([Part.Wire([Part.makeCircle(row['radius_mm'],p,t)])],True,False)
        factory_shapes['FactoryRoute:'+row['wire']]=s;bounds['FactoryRoute:'+row['wire']]=s.BoundBox
        # Scenario already proves changed2 factory links at all36legposes;
        # unchanged6 have the identical immutable all-new-motion proof5b9ab49.
        if scenario:
            original=next(r for r in json.loads(factoryfile.read_text())['routes'] if r['wire']==row['wire'])
            if row['wire'] not in ('W044','W052'):assert row['parts']==original['parts']
            hit=obstruction(s,head_motion) if row['wire'] in ('W044','W052') else None
        else:hit=obstruction(s,moving)
        if hit:report['factory_motion_contacts'].append(dict(wire=row['wire'],**hit))
        save();print('Factory new motion',row['wire'],'blocked',bool(hit),flush=True)
    if report['factory_motion_contacts'] or report['errors']:
        report['status']='FACTORY_MOTION_REJECTED_DO_NOT_ALLOCATE_DEPENDENT_PREFIXES';save();return
    if scenario:
        for n,s in new_cases.items():
            hit=obstruction(s,head_motion)
            if hit:report['factory_motion_contacts'].append(dict(changed_case=n,**hit))
        if report['factory_motion_contacts'] or report['errors']:
            report['status']='NEW_RECEIVING_CASE_HEAD_MOTION_REJECTED';save();return
    shapes={}
    for spec in specifications:
        gate();sid=spec['id'];p,d,r=spec['point'],spec['direction'],spec['radius'];domain=[];rejected=[]
        candidates=old['domains'][sid]
        if sid in affected:
            d=np.array(d);d/=np.linalg.norm(d);p=np.array(p)
            u=np.array([1.,0,0]) if abs(d[0])<.9 else np.array([0.,1,0]);u-=d*np.dot(u,d);u/=np.linalg.norm(u);v=np.cross(d,u)
            candidates=[dict(option=k,bend=(np.cos(k*np.pi/4)*u+np.sin(k*np.pi/4)*v).tolist()) for k in range(8)]
        for candidate in candidates:
            option=candidate['option'];s=tube_prefix(p,d,r,candidate['bend'],12.4)
            hit=None
            if sid in affected:
                bend=np.array(candidate['bend']);q=p+d*9;t=np.linspace(0,np.pi/2,25)
                samples=np.r_[np.array([p+d*l for l in np.linspace(0,9,6)]),q+12.4*(np.sin(t)[:,None]*d+(1-np.cos(t))[:,None]*bend)]
                if not inside_shared(samples,margin=2+r).all():
                    rejected.append(dict(option=option,kind='outside_shared_reservation'));continue
                root_names=set(groups[spec['role']]['objects']);trimmed=tube_prefix(p+2.5*d,d,r,bend,12.4,straight_mm=6.5)
                # New endpoints need FULL retained feet, not only the added
                # bridge delta used when reusing an unchanged endpoint proof.
                hit=obstruction(s,{**added,**full_static},root_names,trimmed)
                if not hit:hit=obstruction(s,endpoint_motion)
            elif scenario:hit=obstruction(s,new_cases)
            if not hit:hit=obstruction(s,moving)
            # Original selected approaches have the exact current skin/feet
            # proof. Only newly selected geometry needs those added obstacles.
            if not hit and sid not in affected and option!=old['allocation'][sid]:hit=obstruction(s,added)
            if not hit and scenario:hit=obstruction(s,factory_shapes,factory_obstacle=True)
            if hit:rejected.append(dict(option=option,kind='new_motion_or_added_material',**hit));continue
            domain.append(candidate);shapes[(sid,option)]=s
        report['domains'][sid]=domain;report['domain_rejections'][sid]=rejected
        save();print('Motion prefix',sid,'remaining',len(domain),'pairs',report['pairs'],flush=True)
    compatible_cache={}
    def compatible(a,b):
        key=tuple(sorted((a,b)))
        if key in compatible_cache:return compatible_cache[key]
        if a[0] not in affected and b[0] not in affected and a[1]==old['allocation'][a[0]] and b[1]==old['allocation'][b[0]]:ok=True
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
        changed_approaches=[] if answer is None else [n for n,k in answer.items() if n in affected or k!=old['allocation'][n]],
        factory_motion_clear=True)
    report['source_sha256'].update(reader.hashes);save()
    print(json.dumps({k:report[k] for k in ('status','empty_domains','changed_approaches','nodes','pairs','wire_pairs','worker_seconds')}),flush=True)


if __name__=='__main__':
    try:main()
    except TimeoutError as exc:print(str(exc)+'; partial saved, no new candidates',flush=True)
