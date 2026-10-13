"""One shared recovery contract from completed actual material evidence.

Identify whole fixed branches to reroute while retaining cable lands and
moving supports. This is an input plan, not a claimed solved path or PASS.
"""
import json,time
from pathlib import Path
import build_remaining_loom_supports as G
P=G.P

def segment_bounds(a,b):
    return [min(x,y)-h for x,y,h in zip(a,b,(2,3,2))]+[max(x,y)+h for x,y,h in zip(a,b,(2,3,2))]

def run():
    tick=time.monotonic()
    files=[P.OUT/n for n in ('remaining-support-material.json','remaining-support-contact-diagnosis.json','remaining-support-final-paths.json')]
    gate,diagnosis,paths=[json.loads(f.read_text()) for f in files]
    assert len(gate['groups'])==12 and gate['status']=='REJECTED_COMBINED_SUPPORT_MATERIAL'
    assert diagnosis['received_gate_sha256']==P.SHA(files[0])
    changes={};unresolved=[]
    for witness in diagnosis['contacts']:
        if not witness['matches_received_added_material_volume']:
            unresolved.append(dict(reason='Full-part witness differs from checked addition',contact=witness['received_contact']));continue
        fixed=[r for r in witness['fragments'] if r['group'].endswith('FixedCarrier')]
        if len(fixed)!=1:
            unresolved.append(dict(reason='Requires different common ownership decision',contact=witness['received_contact']));continue
        affected=fixed[0];name=affected['group'];pg=next(g for g in paths['groups'] if g['id']==name)
        group=changes.setdefault(name,dict(group=name,owner_stage=pg['owner_stage'],branches={},received_conflicts=[]))
        group['received_conflicts'].append(witness['received_contact'])
        for pad in affected['pads']:
            matches=[]
            if pad['name'].startswith('Arm'):
                for path in pg['paths']:
                    if any(all(abs(x-y)<1e-6 for x,y in zip(segment_bounds(a,b),pad['bounds_mm']))
                           for a,b in zip(path['points_mm'],path['points_mm'][1:])):matches.append(path)
            if not matches:
                unresolved.append(dict(reason='Conflict is not attributable solely to an arm segment',group=name,pad=pad));continue
            for path in matches:
                group['branches'][path['land_id']]=dict(land_id=path['land_id'],
                    preserved_start_mm=path['points_mm'][0],preserved_arrival_mm=path['points_mm'][-1],
                    prior_points_mm=path['points_mm'],decision='Reroute WHOLE branch against frozen moving support poses; no scalar-offset search')
    non_support=[r for r in gate['contacts'] if not r['target'].startswith('NewSupport_')]
    unresolved.extend(dict(reason='Retained part/wire contact needs separate actual witness',contact=r) for r in non_support)
    for group in changes.values():group['branches']=list(group['branches'].values())
    result=dict(status='SHARED_SUPPORT_RECOVERY_CONTRACT_NOT_SOLVED',changed_fixed_groups=list(changes.values()),
        unresolved=unresolved,freeze=['All cable paths, sleeve positions,9mm jacket lands and independent bands',
            'All received native parent geometry and mounting interfaces',
            'All unchanged Hip/Knee support candidates as explicit moving obstacles, NOT accepted parts'],
        planning_rules=['Insert complete new supports into owner-relative planning obstacles before searching the failed fixed branches',
            'For fixed branches reserve all9Hip/Knee and27childAnkle sampled poses; preserve existing coupled-motion rules',
            'Retain all existing body/head shapes and wire radius+0.5mm; mesh/bounds are reservations only',
            'New paths must end on the unchanged physical root and whole port approach, not floating endpoints',
            'After one joint plan, rebuild only changed fixed bodies; check actual added material against complete assembly and each other',
            'Reuse exact unchanged pair results; native/editability/parameter/reopen/STL only after complete accepted gate'],
        inherited_phase1_percent=60,accepted=False,native_build_allowed=False,geometry_changed=False,physical_pass=False,
        source_sha256={f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in files+[Path(__file__)]},
        worker_seconds=round(time.monotonic()-tick,3))
    (P.OUT/'remaining-support-shared-recovery-plan.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(groups=len(changes),branches=sum(len(r['branches']) for r in changes.values()),unresolved=len(unresolved),worker_seconds=result['worker_seconds'])),flush=True)
if __name__=='__main__':run()
