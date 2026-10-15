"""Physical cavity labels for retained guides, without altering pinned history.

Logical ground labels were permuted before the current view. Datums already
apply that permutation: do not apply it a second time to the coordinates.
"""
import json,math,time
from pathlib import Path
from reconcile_retained_body_guides import ROOT,OUT,SHA


def cavity(role,datum,aliases):
    logical=aliases.get(role,role)
    if logical not in datum:return logical,None
    p=datum[logical];station=logical.rsplit('.',1)[0]
    return station+'.'+str(p['physical_project_cavity']),p['point_mm']


def run():
    tick=time.monotonic();files=[OUT/(n+'.json') for n in
        ('retained-body-guides-inventory','current-leg-receiver-datums','ground-tree-plan',
         'ground-tree-manifest','u1-power-grips-native','BUS-native-checks')]
    inventory,datums,ground,groundreceipt,power,bus=[json.loads(p.read_text()) for p in files]
    for receipt in (inventory,groundreceipt,power,bus):
        for n,h in receipt['source_sha256'].items():assert SHA(ROOT/n)==h,n
    aliases=inventory['same_DATA_rail_aliases'];bindings={};seen={}
    for name,guide in inventory['guides'].items():
        endpoints=[]
        for side,role in enumerate(guide['electrical_roles']):
            physical,point=cavity(role,datums['ports'],aliases)
            if role.startswith('G1.'):
                physical='G1.'+str(ground['G1_same_ground_port_mapping'][name])
                point=ground['G1']['ports'][physical.rsplit('.',1)[1]]
            actual=guide['segments'][0]['parts'][0]['start'] if side==0 else guide['segments'][-1]['parts'][-1]['end']
            gap=math.dist(actual,point) if point is not None else None
            if gap is not None:assert gap<1e-6,(name,role,physical,gap)
            if physical in seen:raise AssertionError((physical,seen[physical],name,'Two retained ends in one physical port'))
            seen[physical]=name
            endpoints.append(dict(logical_historical_role=role,current_physical_role=physical,
                point_world_mm=actual,project_datum_gap_mm=gap,actual_delivered_cavity_verified=False))
        retained=[]
        if name in ('W060','W078','W079','W080'):retained.append('MAIN/USB ends: u1-power-grips-native.json; not the other remote end')
        if name in ('W002','W003'):retained.append('BUS paired source grip: BUS-native-checks.json; not remote WAGO end')
        candidates=[]
        for side,segment in enumerate((guide['segments'][0],guide['segments'][-1])):
            parts=segment['parts'] if side==0 else list(reversed(segment['parts']))
            part=next((p for p in parts if p['kind']=='line' and p['length_mm']>=9),None)
            candidates.append(dict(end_index=side,existing_straight=part,
                nine_mm_lands_are_candidates_not_chosen_restraints=True))
        bindings[name]=dict(ends=endpoints,existing_native_scope=retained,
            land_candidates=candidates,full_retention_complete=False,
            guide_mm=guide['centreline_sum_mm'],actual_cut_mm=None)
    result=dict(status='RETAINED19_PHYSICAL_END_BINDINGS_AND_RETENTION_INPUTS_ONLY',bindings=bindings,
        checked_project_ends=sum(e['project_datum_gap_mm'] is not None for b in bindings.values() for e in b['ends']),
        one_common_retention_plan='Retain MAIN/USB and BUS native grips only in their demonstrated scope. Root other end grips in the owning printed station Frame/Foundation; use actual straight geometry, not adhesive or WAGO levers. Plan all remaining groups before modeling.',
        special_cases=['W075 short BAT/F0 link is one common supported source assembly, not two overlapping9mm clamps.',
                       'S0 nominal lugs/case and power-wire insulation require delivery fit; no invented metal contact.',
                       'Short fixed MAIN land is3mm by existing proof, not silently enlarged to9mm.'],
        source_sha256={p.relative_to(ROOT).as_posix():SHA(p) for p in files+[Path(__file__)]},
        worker_seconds=round(time.monotonic()-tick,3),selected=False,W5_complete=False,physical_pass=False)
    (OUT/'retained19-current-end-bindings.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(guides=len(bindings),checked_ends=result['checked_project_ends'],worker_seconds=result['worker_seconds'])))


if __name__=='__main__':run()
