"""One coupled complete TY receiving corridor; preserve both MTA_RL sides.
Change the whole TY factory output, covered joint, receiving approach and
grip station together. Keep actual servo/load interface as an OPEN moving
continuation: the old insulation station was a project datum, not a pin.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,time,math
import open_prototype_aux_fanout_choice as F
import open_prototype_source_group as B
import open_prototype_rr_receiving_branch as R
import open_prototype_pi_capacity_plan as K
from open_prototype_distribution_allocation import input_recipe
from open_prototype_path_preflight import samples
ROOT=F.ROOT;OUT=F.OUT
PLAN=OUT/'tail-joint-height-plan.json';PROOF=OUT/'tail-corridor-allocated-space.json';REUSE_PROOF=None

def allocate_joint_height(x,y):
    # Bounds from valid transformed saved S1_ring_3 in f1e7665's scene.
    # This is a conservative search obstacle, not supplier geometry. The
    # actual full-radius gate still checks the real ring, shell and all peers.
    bounds=[115.4375,6.437,81.825,124.9625,34.123,88.175]
    required=1.05+1 # insulation radius + explicit project margin
    for i in range(212,260):
        cut=i*.5;start=[x,y,cut-18.25];end=B.add(start,B.mul(B.DOWN,9))
        parts=[B.line(start,end),B.quarter(end,B.DOWN,B.NORTH,12.6)]
        d=min(math.sqrt(K.distance_squared(q,bounds)) for _,q in samples(parts,step=.1))
        # Every curve point is <=.1mm from a sample; distance is1-Lipschitz.
        if d>=required+.1:return cut,d,bounds
    raise AssertionError('No whole joint/approach capacity; change topology')

def build():
    p=F.build()
    h=next(h for h in p['holders'] if h['role']=='F_TY')
    # Allocate complete case BETWEEN HP and S1 operator, not another guessed
    # coordinate. Keep NORTH factory exit below rear bus Y37, then EAST and
    # DOWN beyond its side; the whole covered joint sits below rear Z133.22.
    hp=next(h for h in p['holders'] if h['role']=='F_HP')
    lo=hp['centre_mm'][0]+hp['size_mm'][0]/2+20.25/2+2
    hi=112.2-20.25/2-2
    # The existing HP input turning column is atX96. Reserve >=4mm axis
    # separation there AND2mm case/operator gap; midpoint of the case-only
    # interval wrongly omits that shared input. Its EAST edge satisfies
    # both constraints. Do not launch CAD until the full input screen passes.
    assert lo<hi and hi-96>=4;cx=hi
    end=p['ports'][h['input_target']]['point_mm']
    # Bind the actual current port level142, not the obsolete139mm fanout
    # inlet level; no diagonal straight disguised as a tangent entry.
    h.update(axis=B.NORTH[:],input_mm=[cx,-26,end[2]],output_mm=[cx,25,end[2]],
        centre_mm=[cx,-.5,end[2]+1],size_mm=[20.25,51,22],
        shared_case_corridor_x_mm=[lo,hi],corridor_basis='HP whole case +2mm and S1 operator XMin112.2 -2mm; rear YMin37 constrains both output bends together')
    anchor=[cx,end[1]+6,end[2]]
    inlet=B.line(h['input_mm'],anchor);inlet_turn=B.quarter(anchor,B.SOUTH,B.EAST,6)
    h['input_segments']=[inlet,inlet_turn,B.line(inlet_turn['end'],end)]
    h['input_blank_mm']=B.check_path(h['input_segments'],h['input_mm'],end,6)+11
    assert h['input_blank_mm']<=84.5
    first=B.line(h['output_mm'],B.add(h['output_mm'],B.mul(B.NORTH,3)))
    side_turn=B.quarter(first['end'],B.NORTH,B.EAST,6)
    side=B.line(side_turn['end'],B.add(side_turn['end'],B.mul(B.EAST,3)))
    factory_turn=B.quarter(side['end'],B.EAST,B.DOWN,6)
    cut_z,ring_budget_distance,ring_bounds=allocate_joint_height(factory_turn['end'][0],factory_turn['end'][1])
    cut=[factory_turn['end'][0],factory_turn['end'][1],cut_z]
    assert factory_turn['end'][2]-cut_z>=9, 'Factory insulation grip straight'
    h['output_segments']=[first,side_turn,side,factory_turn,B.line(factory_turn['end'],cut)]
    h['output_prefix_mm']=B.check_path(h['output_segments'],h['output_mm'],cut,6)
    assert h['output_prefix_mm']<=h['factory_minimum_mm']
    h.update(sleeve_start_mm=B.sub(cut,B.mul(B.DOWN,17.25)),
        sleeve_end_mm=B.add(cut,B.mul(B.DOWN,9.25)),
        new_insulation_end_mm=B.add(cut,B.mul(B.DOWN,18.25)),
        joint_height_allocation=dict(obstacle='S1_ring_3 transformed saved material bounds',
            bounds_mm=ring_bounds,minimum_sampled_distance_mm=ring_budget_distance,
            insulation_radius_mm=1.05,project_margin_mm=1,sampling_allowance_mm=.1,
            entire_covered_joint_and_receiving_approach_recomputed=True))
    start=h['new_insulation_end_mm']
    a=B.add(start,B.mul(B.DOWN,9));q=B.quarter(a,B.DOWN,B.NORTH,12.6)
    bottom=B.add(q['end'],B.mul(B.NORTH,9));turn=B.quarter(bottom,B.NORTH,B.UP,12.6)
    end=[start[0],turn['end'][1],130]
    parts=[B.line(start,a),q,B.line(q['end'],bottom),turn,B.line(turn['end'],end)]
    full=[B.line(h['output_segments'][-1]['end'],start)]+parts
    length=B.check_path(full,full[0]['start'],end,12.6)
    B.check_path(h['output_segments']+full,h['output_mm'],end)
    row=dict(wire='XB32',holder='F_TY',leg='TY',side='output',target='',segments=full,
        OD_mm=2.1,min_radius_mm=12.6,extension_centreline_mm=length,
        station_mm=end,terminal_straight_mm=B.segment_geometry(parts[-1])[0],
        covered_joint_is_existing_recipe=True,stock_selected=False,
        old_project_insulation_station_mm=[68,-45,116.78756443470179],
        new_station_is_not_a_changed_servo_pin=True,
        changed_factory_output_and_covered_joint_together=True,
        independent_grips_open=True,moving_continuation_not_qualified=True)
    p['tails'].append(row);p['protected_receiving_rows'].append(row)
    p.update(changed_case_names=['F_TY'],changed_path_names=['XB32','F_TY/input','F_TY/output','F_TY/sleeve','F_TY/new_insulation'],
        s1_geometry_changed=False,status='RL_BOTH_SIDES_AND_TAIL_GALLERY_NOT_NATIVE_ACCEPTANCE')
    return p

def compact():
    p=build();report=F.F.proximity(p)
    space=B.read(OUT/'routing-space-map.json')['samples'];outside=[]
    for r in p['tails']:
        if r['wire'] not in p['changed_path_names']:continue
        for i,q in samples(r['segments'],step=2):
            spans=min(space,key=lambda v:(v['x_mm']-q[0])**2+(v['y_mm']-q[1])**2)['torso_z_intervals_mm']
            if not spans or q[2]<min(v[0] for v in spans)+r['OD_mm']/2+.5 or q[2]>max(v[1] for v in spans)-r['OD_mm']/2-.5:
                outside.append(dict(wire=r['wire'],segment=i,point=q));break
    failures=[r for r in report['near_pairs'] if r['status']=='REJECT_PLANNING_PROXIMITY']
    boxes=[(r['role'],K.bounds(r['centre_mm'],r['size_mm'])) for r in p['stations']+p['mta']+p['holders']]
    boxes += [(r['name'],r['bounds_mm']) for r in B.read(OUT/'obstacle-map-current.json')['objects']
        if r['basis'].startswith('Canonical whole-component/reference envelope') or r['name']=='U1UnknownModuleReservation']
    boxes += [('S1/operator',[112.2,-14,126,140.2,14,160])]
    h=next(h for h in p['holders'] if h['role']=='F_TY')
    profiles=[('input',h['input_segments'],2),('output',h['output_segments'],2),
        ('sleeve',[B.line(h['sleeve_start_mm'],h['sleeve_end_mm'])],3),
        ('new_insulation',[B.line(h['output_segments'][-1]['end'],h['new_insulation_end_mm'])],1.05),
        ('XB32',next(r['segments'] for r in p['protected_receiving_rows'] if r['wire']=='XB32'),1.05)]
    budgets=[]
    for name,parts,radius in profiles:
        for case,bb in boxes:
            for i,q in samples(parts,step=.5):
                if case=='F_TY' and name in ('input','output') and math.dist(q,parts[0]['start'])<=radius+1e-5:continue
                if case=='P_AUX' and name=='input' and math.dist(q,parts[-1]['end'])<=radius+1e-5:continue
                if K.distance_squared(q,bb)<radius**2-1e-8:
                    budgets.append(dict(profile=name,budget=case,segment=i,point_mm=q));break
    files=[Path(__file__),Path(F.__file__),F.PLAN,F.PROOF,OUT/'source-fanouts-plan.json',OUT/'routing-space-map.json']
    return dict(status='REQUIRES_SHARED_CHANGE_BEFORE_CAD' if failures or outside or budgets else 'RL_TAIL_SHARED_PLAN_REQUIRES_ONE_ACTUAL_GATE',
        family=p,geometry_digest=R.geometry_digest(p),mutual_preflight=report,
        known_mutual_failures=failures,conservative_boundary_exclusions=outside,
        diameter_budget_exclusions=budgets,sampled_full_radius_boxes_not_actual_material_clearance=True,
        old_servo_load_interface_not_claimed_changed=True,moving_continuation_to_existing_tail_still_open=True,
        old_project_insulation_station_replaced=True,legacy_source920mm_open=True,
        source_sha256={f.relative_to(ROOT).as_posix():B.sha(f) for f in files},
        selected=False,stage_completed=False,physical_pass=False)

if __name__=='__main__':
    if PLAN.exists():
        old=B.read(PLAN)
        if old['status']!='REQUIRES_SHARED_CHANGE_BEFORE_CAD':
            prior=B.read(OUT/'tail-receiving-whole-space.json')
            assert prior['status']=='REJECTED_COUPLED_SPACE_OR_INPUT_WITNESS' and not prior['errors']
            assert prior['source_sha256'][PLAN.relative_to(ROOT).as_posix()]==B.sha(PLAN)
        assert old['source_sha256'][Path(__file__).relative_to(ROOT).as_posix()]!=B.sha(Path(__file__)), 'No unchanged retry'
    tick=time.monotonic();data=compact()
    data.update(worker_seconds=round(time.monotonic()-tick,6),finished_utc=datetime.now(timezone.utc).isoformat())
    data['prior_failed_upper_gallery_preserved_in_git']='e139dd8 upper151mm boundary failure and01ea2d7 downstream drop/W042 crossing retained. Current whole TY factory output/joint/downstream station changes together; no third free-wire offset.'
    PLAN.write_text(json.dumps(data,separators=(',',':'))+'\n',encoding='utf-8')
    print(json.dumps(dict(status=data['status'],blanks=[(r['wire'],r['required_blank_mm']) for r in data['family']['tails'] if r['wire'] in ('W044','W045')],
        conflicts=data['known_mutual_failures'],outside=data['conservative_boundary_exclusions'],seconds=data['worker_seconds'])),flush=True)
