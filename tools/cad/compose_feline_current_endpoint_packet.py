"""One current178identity/89segment packet before remaining routing.

Never inherit a previous route/stock approval from unchanged identity labels.
No CAD, guessed pinout, selected material or completed-result credit.
"""
import copy
import json
import math
import time
from pathlib import Path
from plan_feline_n01_coupled_pi_bus import ROOT,OUT,sha


def branch_point(point,datum):
    old=datum['old_centre_mm'];new=datum['new_centre_mm']
    return [new[0]+point[1]-old[1],new[1]-point[0]+old[0],new[2]+point[2]-old[2]]


def branch_direction(d):return [d[1],-d[0],d[2]]


def compose():
    tick=time.monotonic()
    files={k:OUT/n for k,n in dict(old='n01-complete-end-allocation.json',
        branches='n01-central-mta-cassette-plan-r3.json',
        axial='n01-axial-branch-root-clear.json',power='n01-central-spine-power-plan-r4.json',
        bank='n01-common-backbone-preflight-r4.json',bus='n01-bus-both-plugs-plan-r3.json').items()}
    p={k:json.loads(path.read_text()) for k,path in files.items()}
    branches=p['branches'];assert len(branches['poses'])==36
    assert all(not branches[k] for k in ('contacts','reservation_contacts','errors','envelope_outside','wall_budget_failures'))
    rows=copy.deepcopy(p['old']['endpoints']);byid={r['id']:r for r in rows}
    assert len(byid)==178
    for r in rows:
        r.update(complete_route_verified=False,stock_selected=False,current_update='Retained reconciled R5 endpoint only; old route not inherited')
    changed=[]
    def update(key,point,direction,source,**extra):
        r=byid[key];r.update(point_mm=list(point),departure_axis=list(direction),
            current_update=source,complete_route_verified=False,stock_selected=False,**extra)
        changed.append(key)
    for b in p['bank']['bend_allocations']:
        R=b['bend_R_mm'];land=b['land_mm']
        d=[(q-a-R*v)/(land+R) for a,q,v in zip(b['start_mm'],b['end_mm'],b['bend'])]
        assert abs(sum(v*v for v in d)-1)<1e-6
        update(b['id'],b['start_mm'],d,'Current flat-bank R4 full9mm/R12.4 first bend',
            boundary_after_first_bend_mm=b['end_mm'],initial_jacket_land_mm=land)
    for e in p['power']['all_unit_ends']:
        update(e['id'],e['point_mm'],e['departure_axis'],'Current full8end source unit R4',
            initial_jacket_land_mm=e['initial_mm'])
    fuse=p['power']['F_PI'];sp=p['power']['splice']
    update('W043/single/start',fuse['input_mm'],[1,0,0],'Current F_PI input/full W043')
    update('W077/retained0/start',fuse['output_mm'],[-1,0,0],'Current F_PI output/full W077')
    update('W077/retained0/end',sp['tip16_mm'],[-1,0,0],'Current8mm solder overlap16AWG, intact grip outside20mm sleeve')
    update('W078/retained0/start',sp['tip18_mm'],[1,0,0],'Current8mm solder overlap18AWG, intact grip outside20mm sleeve')
    wire_branch={w:c for c,d in branches['branch_datums'].items() for w in d['wires']}
    factory_lengths={}
    for route in p['axial']['joint_bay_factory_routes']:
        w=route['wire'];d=branches['branch_datums'][wire_branch[w]]
        a=route['parts'][0]['start'];b=route['parts'][-1]['end'];length=math.dist(a,b)
        aa=branch_point(a,d);bb=branch_point(b,d)
        axis=[(y-x)/length for x,y in zip(aa,bb)]
        update(w+'/factory/start',aa,axis,'Whole central cassette factory side; nominal CAD port',
            initial_jacket_land_mm=9,factory100mm_is_project_assumption=True)
        update(w+'/factory/end',bb,[-v for v in axis],'Whole central cassette factory joint; nominal CAD port',
            initial_jacket_land_mm=9,factory100mm_is_project_assumption=True)
        factory_lengths[w]=dict(guide_mm=length,grip_offsets_from_start_mm=[.25,length-9-.25],
            grip_length_mm=9,between_grips_mm=length-18-.5,factory100mm_is_project_assumption=True)
    for e in p['axial']['all_eight_joint_custom_ends']:
        w=e['id'].split('/')[0];d=branches['branch_datums'][wire_branch[w]]
        update(e['id'],branch_point(e['point_mm'],d),branch_direction(e['departure_axis']),
            'Whole central cassette custom side; nominal CAD port',initial_jacket_land_mm=9)
    for route in p['bus']['routes']:
        if route['wire'] not in ('BUS.D','BUS.G'):continue
        key='W002/retained0/start' if route['wire']=='BUS.D' else 'W003/retained0/start'
        a=route['parts'][0];axis=[-1,0,0]
        update(key,a['start'],axis,'Current nominal H5 mating reservation, NOT supplier pin guarantee',
            boundary_after_first_bend_mm=route['end_mm'],actual_port_verified=False)
    assert len(changed)==len(set(changed))==62
    segments={}
    for r in rows:segments.setdefault(r['id'].rsplit('/',1)[0],[]).append(r)
    assert len(segments)==89 and all(len(es)==2 for es in segments.values())
    distances=[dict(id=k,endpoint_ids=[e['id'] for e in es],
        straight_lower_bound_mm=math.dist(es[0]['point_mm'],es[1]['point_mm']),
        is_not_cut_length=True,full_middle_route_verified=False) for k,es in sorted(segments.items())]
    assert len({r['wire'] for r in rows})==80
    return dict(status='CURRENT178_IDENTITIES_RECONCILED_REMAINING_ROUTING_OPEN',selected=False,
        physical_pass=False,N01_complete=False,endpoints=rows,changed_endpoint_ids=changed,
        physical_segment_lower_bounds=distances,logical_nets=80,physical_segments=89,
        factory_lengths=factory_lengths,current_case_datums=branches['branch_datums'],
        full_route_receipts_only=['W043','W077','W078','Eight20.75mm factory portions'],
        body_bundle_hierarchy=p['old']['body_bundle_hierarchy'],
        head_tail_JR_outside80='Separate current JPWM factory branch remains unchanged; full source/receiver path and lie/head/tail motion still open.',
        USB_outside80=dict(current_BUS_prefix=p['bus']['routes'][-1],Pi_A_mould_and_complete500mm_middle_open=True),
        source_sha256={**{path.relative_to(ROOT).as_posix():sha(path) for path in files.values()},
            Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
        assumptions='Guide points remain nominal project geometry. No external U1/pinout or manufacturer usable lead guarantee invented. No route or stock acceptance transferred by identity.',
        next='Allocate common fixed/moving corridors, all lands/restraints and assembly with these current endpoints; do not route against obsolete transverse joints or old source poses.',
        worker_seconds=round(time.monotonic()-tick,4))


def main():
    target=OUT/'n01-current-endpoint-packet.json';assert not target.exists()
    p=compose();target.write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:p[k] for k in ('status','logical_nets','physical_segments','worker_seconds')}),flush=True)


if __name__=='__main__':main()
