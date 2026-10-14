"""Reuse the nineteen existing body guides; diagnose only current leg ends.

The old interface register says OPEN for guides added by later scoped proofs.
This inventory does NOT accept new restraints, stock or complete W5. No CAD
recompute, routing or historical source overwrite is performed.
"""
import json,math,time
from pathlib import Path
from plan_current_harness_interfaces import ROOT,OUT,SHA


def data_aliases(data,rows):
    aliases={}
    for station,move in data['physical_port_reassignment'].items():
        assert station.startswith('D_') and move['ports_2_3_4']=='unchanged'
        old=station+'.'+move['historical_bridge_port'];new=station+'.'+move['current_bridge_port']
        assert new not in {role for row in rows.values() for role in row['roles']},'New same-rail cavity already occupied'
        aliases[old]=new
    return aliases


def run():
    tick=time.monotonic();pins={};cache={}
    def read(name):
        path=OUT/(name+'.json');pins[path.relative_to(ROOT).as_posix()]=SHA(path)
        if name not in cache:cache[name]=json.loads(path.read_text())
        return cache[name]
    register=read('harness-interfaces-plan');datums=read('current-leg-receiver-datums')
    rows={r['id']:r for r in register['body_conductors']};guides={}
    sources=[('ground-tree',('W001','W025','W036','W060','W061','W062','W063')),
             ('main-pi',('W077','W078')),('data-bridges',('W007','W011','W012')),
             ('positive-source',('W075','W066')),('BUS-routes',('W002','W003'))]
    for tag,names in sources:
        plan=read(tag+'-plan')
        for name in names:
            route=plan['routes'][name]
            guides[name]=dict(recipe_file=tag+'-plan.json',segments=[route])
    plan=read('s0-in-extension-plan')
    guides['W076']=dict(recipe_file='s0-in-extension-plan.json',
        segments=[plan['routes']['W076_FACTORY'],plan['routes']['W076_EXTENSION']],
        inline_joint=plan.get('post_F0'),segments_not_blindly_joined=True)
    common=read('u1-common-wiring-plan')
    for name,route in common['changed_MAIN_pair'].items():
        guides[name]=dict(recipe_file='u1-common-wiring-plan.json',segments=[route],
            qualification='Selected E1 module, not obsolete MAIN-Pi curve')
    assert set(guides)==set(register['open_body_guides']) and len(guides)==19
    data=read('data-bridges-plan');gate=read('data-bridges-checks')
    assert gate['status']=='THREE_DATA_BRIDGES_SAMPLED_CLEAR_NATIVE_OPEN' and not gate['contacts'] and not gate['errors']
    data_path=(OUT/'data-bridges-plan.json').relative_to(ROOT).as_posix()
    assert gate['source_sha256'][data_path]==SHA(OUT/'data-bridges-plan.json')
    aliases=data_aliases(data,rows)
    checks=[];stale=[]
    for name,guide in guides.items():
        endpoints=[p for s in guide['segments'] for p in (s['parts'][0]['start'],s['parts'][-1]['end'])]
        guide['electrical_roles']=rows[name]['roles']
        guide['centreline_sum_mm']=sum(p['length_mm'] for s in guide['segments'] for p in s['parts'])
        guide['source_endpoints_mm']=endpoints
        for role in rows[name]['roles']:
            if role not in datums['ports']:continue
            physical_role=aliases.get(role,role)
            point=datums['ports'][physical_role]['point_mm'];gap=min(math.dist(point,p) for p in endpoints)
            check=dict(wire=name,role=role,current_same_rail_role=physical_role,current_project_datum_mm=point,gap_to_existing_guide_endpoint_mm=gap)
            checks.append(check)
            if gap>1e-6:stale.append(check)
    result=dict(status='RETAINED19GUIDE_INVENTORY_CURRENT_STATION_ENDS_MATCH_RESTRAINTS_OPEN' if not stale else 'RETAINED19GUIDE_INVENTORY_CHANGED_STATION_ENDS_OPEN',
        guides=guides,station_endpoint_checks=checks,stale_station_ends=stale,same_DATA_rail_aliases=aliases,
        interpretation='Nineteen guides already exist in the current snapshot; old OPEN register is not evidence to route them again. Matching current leg-station ends only; other interfaces inherit their existing scoped proof and must be bound in final current package.',
        scope='Recipe inventory/current-station endpoint reconciliation only. No new material/contact/native/retention/stock acceptance.',
        source_sha256={**pins,Path(__file__).relative_to(ROOT).as_posix():SHA(Path(__file__))},
        worker_seconds=round(time.monotonic()-tick,3),selected=False,W5_complete=False,physical_pass=False)
    (OUT/'retained-body-guides-inventory.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],guides=len(guides),station_ends=len(checks),stale=len(stale),worker_seconds=result['worker_seconds'])))


if __name__=='__main__':run()
