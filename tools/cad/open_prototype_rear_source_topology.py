"""One jointly planned rear bus/S1/AUX/both MTA receiving topology.

The retained downward rear bus forces the large source bend beneath itself;
the low southern S1 bearing plane faces D_RR. Change both causes as a unit:
WEST-facing rear bus, complete S1 plane above D_RR, both MTA source tails and
AUX input rebound. Preserve the already prepared SYS/Pi/FHAC family.
No terminal-only shifts, no native CAD variants, no supplier claim.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,time
import open_prototype_s1_grip_capacity as H
from open_prototype_distribution_allocation import input_recipe
B=H.B;G=H.G;ROOT=H.ROOT;OUT=H.OUT
PLAN=OUT/'rear-source-topology.json';PROOF=OUT/'rear-source-space.json';REUSE_PROOF=None

def build_base():
    p=G.F.build();s=next(s for s in p['stations'] if s['role']=='P_REAR')
    s.update(centre_mm=[103,42.5,115.5],size_mm=[22,37,11],rotation='-90')
    for n in range(1,6):
        p['ports'][f'P_REAR.{n}'].update(point_mm=[92,42.5-(n-3)*6.5,115.5],departure=B.WEST[:])
    for row in p['tails']:
        if row['wire'] not in ('W044','W052'):continue
        end=p['ports'][row['target']]['point_mm'];anchor=B.add(end,[-15,-6,0])
        start=next(m['source_exit_mm'] for m in p['mta'] if m['role']=='MTA_'+row['leg'])
        parts=input_recipe(start,anchor,B.NORTH,6)['segments']
        turn=B.quarter(anchor,B.NORTH,B.EAST,6)
        parts += [turn,B.line(turn['end'],end)]
        length=B.check_path(parts,start,end,6)
        row.update(segments=parts,centreline_mm=length,required_blank_mm=length+14)
        assert row['required_blank_mm']<=100,(row['wire'],row['required_blank_mm'])
    aux=next(h for h in p['holders'] if h['role']=='F_AUX')
    end=p['ports'][aux['input_target']]['point_mm']
    assert B.sub(end,aux['input_mm'])==[29,0,0]
    aux.update(input_segments=[B.line(aux['input_mm'],end)],input_blank_mm=43)
    # Coupled lower-loop/S1 level constraint, BEFORE native edits:
    # Monitor top54 +4mm planning clearance gives low58. A24mm sideways
    # reversal needs >=44.33mm vertical separation forR25.2; choose45.
    # Thus the whole terminal plane is103, not the incomplete99mm budget.
    monitor=next(r for r in B.read(OUT/'obstacle-map-current.json')['objects'] if r['name']=='Monitor_CP2')
    low=monitor['bounds_mm'][5]+4
    plane=low+45;lift=plane-85
    spec=p['s1_module'];spec['translation_mm']=B.add(spec['translation_mm'],[0,0,lift])
    for ring in spec['rings']:
        ring['eye_mm']=B.add(ring['eye_mm'],[0,0,lift])
        ring['barrel_mm']=B.add(ring['barrel_mm'],[0,0,lift])
    spec.update(body_bounds_mm=[114.2,-21,89+lift,138.2,21,126+lift],
        operator_bounds_mm=[112.2,-14,126+lift,140.2,14,160+lift],
        lower_gallery_mm=low,
        whole_plane_change='Whole S1 plane103 derives jointly from Monitor54+4 lower-gallery clearance and radius25.2 reversal, not a receiver-only offset.')
    for end in p['body_ends']:end['datum']=p['ports'].get(end['current_role'])
    return p

def connector(start,departure,end,arrival,d1):
    if arrival==B.WEST and end==[-38,33,131]:
        straight=B.line(start,B.add(start,B.mul(departure,d1)))
        turn=B.quarter(straight['end'],B.NORTH,B.WEST,25.2)
        return [straight,turn]+input_recipe(turn['end'],end,B.WEST,25.2)['segments']
    if arrival==B.EAST and end==[92,29.5,115.5]:
        # Rear circuit6 uses the lower gallery SOUTH of the entire AUX case,
        # not the rejected north-to-east biarc through its envelope. Derive
        # the reverse loop from BOTH fixed grip ends and actualR25.2.
        radius=25.2;low=start[2]-45;last=B.sub(end,B.mul(B.EAST,9))
        south_x=last[0]+radius
        lead=B.line(start,B.add(start,B.mul(B.NORTH,9)))
        reverse=B.half_turn(lead['end'],B.NORTH,[south_x-start[0],0,low-start[2]])
        anchor=[south_x,end[1]-radius,low]
        turn=B.quarter(anchor,B.SOUTH,B.WEST,radius)
        assert abs(turn['end'][0]-last[0])<1e-6
        return_to_grip=B.half_turn(turn['end'],B.WEST,[0,2*radius,end[2]-low])
        assert all(abs(a-b)<1e-6 for a,b in zip(return_to_grip['end'],last))
        return [lead,reverse,B.line(reverse['end'],anchor),turn,return_to_grip,B.line(last,end)]
    return G.A.connect(start,departure,end,arrival,d1)

def build():
    d=B.read(PLAN);assert d['family'] is not None
    for n,h in d['source_sha256'].items():assert B.sha(ROOT/n)==h,n
    return d['family']

if __name__=='__main__':
    if PLAN.exists():
        old=B.read(PLAN)
        assert old['family'] is None
        assert old['source_sha256'][Path(__file__).relative_to(ROOT).as_posix()]!=B.sha(Path(__file__))
    tick=time.monotonic();base=build_base()
    choices,counts,reasons=G.search(connector,base,receiving_goals=[(10,-10)],source_budget_allowance=0)
    p=choices[0][1] if choices else None
    if p:
        for r in p['s1_routes']:
            r['source_straight_mm']=B.segment_geometry(r['segments'][0])[0]
            r['end_straight_mm']=B.segment_geometry(r['segments'][-1])[0]
        p.update(changed_case_names=['P_REAR'],s1_geometry_changed=True,
            changed_path_names=['W064','W065','W067','W068','W044','W052','F_AUX/input'],
            status='ONE_REAR_SOURCE_TOPOLOGY_REQUIRES_MATERIAL_RADIUS_AND_NATIVE_GATE')
    files=[Path(__file__),Path(H.__file__),Path(G.__file__),Path(G.A.__file__),Path(G.S.__file__),Path(G.F.__file__),
        G.F.PLAN,G.F.PROOF,OUT/'routing-space-map.json',OUT/'obstacle-map-current.json',Path(input_recipe.__globals__['__file__'])]
    d=dict(status='ONE_SOURCE_FAMILY_REQUIRES_ACTUAL_GATE' if p else 'NO_CONSERVATIVE_JOINT_REAR_TOPOLOGY_NOT_PHYSICAL_IMPOSSIBILITY',
        family=p,planned_receiver=next(s for s in base['stations'] if s['role']=='P_REAR'),
        changed_factory_blanks=[(r['wire'],r['required_blank_mm']) for r in base['tails'] if r['wire'] in ('W044','W052')],
        AUX_input_blank_mm=43,all_current_source_bindings=G.S.source_specs(base),
        counts=counts,conservative_rejections=reasons,mutual_preflight=choices[0][2] if p else None,
        source_sha256={f.relative_to(ROOT).as_posix():B.sha(f) for f in files},
        geometry_digest=G.S.R.geometry_digest(p) if p else None,
        historical_failed_plans_snapshot='01ea2d7; old source target and rejected layouts are not current proofs',
        source_wire_radius_mm=2.1,extra_source_box_allowance_mm=0,
        allowance_note='Extra0.5mm was a conservative planning filter, not a manufacturer minimum. BUS lower-gallery nominal gap0.3mm requires actual BRep/thickness and delivery-fit qualification, not waived collision.',
        selected=False,stage_completed=False,physical_pass=False,
        worker_seconds=round(time.monotonic()-tick,6),finished_utc=datetime.now(timezone.utc).isoformat())
    PLAN.write_text(json.dumps(d,separators=(',',':'))+'\n',encoding='utf-8')
    print(json.dumps({k:d[k] for k in ('status','changed_factory_blanks','counts','conservative_rejections','worker_seconds')}),flush=True)
