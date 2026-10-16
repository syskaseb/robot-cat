"""Two changed causes, retaining all current wires and29 received domains."""
import copy
import json
import math
from pathlib import Path
from plan_current_harness_interfaces import OUT,ROOT,SHA


def apply_layout(plan):
    p=copy.deepcopy(plan);groups={g['id']:g for g in p['groups']}
    bankfile=OUT/'bank-input-plan.json';mainfile=OUT/'main-source-plan.json'
    bank=json.loads(bankfile.read_text());main=json.loads(mainfile.read_text())
    g=groups['W027/single/end'];line=bank['routes']['W027']['parts'][g['part_index']]
    assert line['kind']=='line' and line['length_mm']>=10 and g['axis']==[0,0,1]
    # Full wire land remains >10mm. Place the actual3mm lacing cradle on
    # its upstream end, BEFORE actual Foundation bottom65.99, and root DOWN.
    g['centre_world_mm']=[a+u*2.5 for a,u in zip(line['start'],g['axis'])]
    assert g['centre_world_mm'][2]+1.5<65.99
    g['foot_sign']=-1
    g['allocation_change']='Before existing Foundation passage; downward root foot. Not a changed wire, enlarged hole or removed P0 material.'
    pair=[groups[n] for n in ('W044/custom/end','W052/custom/end')]
    lines=[main['routes'][wid+'_CUSTOM']['parts'][g['part_index']] for wid,g in zip(('W044','W052'),pair)]
    assert all(r['kind']=='line' and r['start'][:2]==r['end'][:2] for r in lines)
    lo=max(min(r['start'][2],r['end'][2]) for r in lines)
    hi=min(max(r['start'][2],r['end'][2]) for r in lines)
    assert hi-lo>=9
    dx=lines[1]['start'][0]-lines[0]['start'][0]
    dy=lines[1]['start'][1]-lines[0]['start'][1]
    d=math.hypot(dx,dy);assert all(g['project_radius_mm']==2.1 for g in pair)
    normal=[dy/d,-dx/d,0]
    common=dict(id='P_REAR_TWO_EQUAL_FEEDS',ends=[e for g in pair for e in g['ends']],
        architecture='One common loop on two equal-radius parallel feed jackets; no band squeezed between them',
        common_axis=[0,0,-1],normal_candidates=[normal,[-a for a in normal]],
        centre_world_mm=[sum(r['start'][0] for r in lines)/2,sum(r['start'][1] for r in lines)/2,(lo+hi)/2],
        project_radius_mm=2.1,land_mm=9,lateral_half_span_mm=d/2+2.1,
        available_common_straight_mm=hi-lo,qualified=False,root=None,normal=None,
        allocation_change='Shared current parallel segment midpoint, not separate wraps at first short rail returns. Full current W044/W052 guides remain unchanged.')
    revised=[]
    for g in p['groups']:
        if g['id']=='W044/custom/end':revised.append(common)
        elif g['id']!='W052/custom/end':revised.append(g)
    p['groups']=revised
    # Allocate the entire lower four-port fan together: equal thin triplets
    # stay atZ24, the larger input loop goes atZ26.5 on its existing straight.
    # At one level even the best west-facing fat loop overlaps the thin loop.
    changed_feeds=[]
    for wid,leg in [('W026','FL'),('W037','FR'),('W045','RL'),('W053','RR')]:
        g=next(g for g in revised if g['id']==wid+'/custom/end')
        e=next(e for e in p['ends'] if e['id']==g['id'])
        assert e['role']==leg+'_P.1'
        file=OUT/e['recipe_file'];r=json.loads(file.read_text())['routes'][e['recipe_key']]
        line=r['parts'][g['part_index']]
        assert line['kind']=='line' and line['start'][:2]==line['end'][:2]
        assert line['length_mm']>=9
        assert min(line['start'][2],line['end'][2])+1.5<=26.5<=max(line['start'][2],line['end'][2])-1.5
        g['centre_world_mm']=[line['start'][0],line['start'][1],26.5]
        branch=next(q for q in revised if q['id']==leg+'_P_BRANCH3')
        outward=1 if g['centre_world_mm'][0]>branch['centre_world_mm'][0] else -1
        g['normal_candidates']=[[outward,0,0],[0,1,0],[0,-1,0]]
        g['allocation_change']='Larger incoming feed3mm cradle atZ26.5, equal branch triplet atZ24; whole original>=9mm straight/wire/port retained. Levels fit even the shortest current9mm stem; not a centred9mm contact pad claim.'
        changed_feeds.append(g['id'])
    assert len(revised)==54
    bound=[e for g in revised for e in g['ends']]
    assert len(bound)==len(set(bound))==63
    p['layout_change']=dict(changed_groups=['W027/single/end','W044/custom/end','W052/custom/end']+changed_feeds,
        rejected_receipt_commit='640b9ef',wire_routes_changed=0,
        W027_actual_wire_to_Foundation_mm=3.2,W027_old_cradle_conflict_mm3=32.415651236654114,
        W027_old_band_conflict_mm3=5.844833146918047,
        P_REAR_equal_wire_centre_spacing_mm=d,
        lower_power_branch_and_feed_levels_mm=[24,26.5],
        rejected_same_level_FL_loop_overlap_mm3=.5209312415999816,
        basis='W027 passage already exists: diagnostic did not change curve clearance. Its former cradle was inside actual plate. P_REAR two equal feeds need one shared loop, not scalar offsets of individual loops.',
        physical_pass=False)
    pins={f.relative_to(ROOT).as_posix():SHA(f) for f in (Path(__file__),bankfile,mainfile)}
    return p,pins
