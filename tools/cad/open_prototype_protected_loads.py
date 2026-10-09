"""Bind moved FHAC outputs to existing local insulation stations together.

Only intact straight subsets of old HY/HP/TY cores are reused. New source
approaches are exact tangent arcs, not reuse of stale FHAC coordinates.
AUX padmap and MAIN route stay explicit gates, not guessed terminals.
"""
from pathlib import Path
from datetime import datetime, timezone
import copy,json,math,time
import open_prototype_source_group as B
import open_prototype_rr_receiving_branch as R
from open_prototype_distribution_allocation import input_recipe
from open_prototype_path_preflight import screen

OUT=B.OUT;ROOT=B.ROOT
PLAN=OUT/'protected-loads-receiving-plan.json'

def build():
    p=R.build()
    old=B.read(OUT/'source-fanouts-plan.json')
    rows=[]
    for role,ident in [('F_HY','XB12'),('F_HP','XB22')]:
        h=next(h for h in p['holders'] if h['role']==role)
        core=copy.deepcopy(next(r['core_segments'] for r in old['rows'] if r['wire']==ident))
        start=h['new_insulation_end_mm']
        if ident in ('XB12','XB22'):
            # Allocate complete approach length from bend diameter and grip.
            # The retained straight is a subset, never moved into new space.
            mouth=core[0]['start'][:]
            mouth[0]=min(mouth[0],start[0]-(2*12.6+3+9+2))
            assert mouth[0]>core[0]['end'][0],'No residual straight: change topology'
            core[0]['start']=mouth
            approach=input_recipe(start,mouth,B.WEST,12.6)['segments']
            retained_basis='Old HY/HP core with first straight shortened in-place; last station unchanged'
        else:
            # Remove obsolete tail-mouth reversal. Feed retained final EAST
            # seat from one shared south-side turn and descent instead.
            approach=B.compose(start,[('line',B.add(start,[-9,0,0])),
                ('quarter',B.WEST,B.SOUTH,12.6),
                ('line',[start[0]-9-12.6,-45+12.6,start[2]]),
                ('quarter',B.SOUTH,B.EAST,12.6)])
            core=[core[-1]]
            approach+=input_recipe(approach[-1]['end'],core[0]['start'],B.EAST,12.6)['segments']
            retained_basis='Only old last22.745mm EAST tail insulation station; upstream loop discarded'
        prefix=[B.line(h['output_segments'][-1]['end'],start)]
        extension=prefix+approach+core
        length=B.check_path(extension,end=core[-1]['end'],min_radius=12.6)
        full=h['output_segments']+extension
        B.check_path(full,h['output_mm'],core[-1]['end'])
        rows.append(dict(wire=ident,holder=role,segments=extension,
            factory_prefix=h['output_segments'],full_body_feed_segments=full,
            station_mm=core[-1]['end'],extension_centreline_mm=length,
            retained_basis=retained_basis,OD_mm=2.1,min_radius_mm=12.6,
            sleeve_start_mm=h['sleeve_start_mm'],sleeve_end_mm=h['sleeve_end_mm'],
            new_insulation_after_sleeve_mm=9,covered_overlap_mm=8,
            nominal_cut_mm=None,stock_selected=False,native_grips_open=True,
            local_moving_continuation_not_qualified=True))
    # Include all existing source paths in the same cheap crossing screen.
    # Factory prefixes already occur once under their holder role.
    q=copy.deepcopy(p)
    q['tails']+=rows
    preflight=screen(q)
    # One conductor crosses its own covered solder lap. This is not a
    # second electrical wire; keep the named connection exempt explicitly.
    joins={(r['wire'],r['holder']+'/output') for r in rows}
    preflight['declared_covered_same_conductor_joins']=[r for r in preflight['near_pairs'] if (r['a'],r['b']) in joins or (r['b'],r['a']) in joins]
    preflight['near_pairs']=[r for r in preflight['near_pairs'] if (r['a'],r['b']) not in joins and (r['b'],r['a']) not in joins]
    preflight['status']='MUTUAL_ROUTE_ALLOCATION_REQUIRES_CHANGE' if any(r['status']=='REJECT_PLANNING_PROXIMITY' for r in preflight['near_pairs']) else 'PROXIMITY_SCREEN_ONLY_RETAINED_MATERIAL_OPEN'
    rejected=B.read(OUT/'protected-loads-plan.json')
    tail_witness=next(r for r in rejected['mutual_path_preflight']['near_pairs'] if {r['a'],r['b']}=={'W045','XB32'})
    return dict(status='TWO_PROTECTED_BODY_FEEDS_PLANNED_TAIL_RECEIVING_STATION_BLOCKED',
        rows=rows,mutual_path_preflight=preflight,
        remaining=[dict(wire='PI_VIN',physical_aliases=['W077','W078'],
            target='MAIN.VIN',target_mm=next(e['point_mm'] for w in B.read(OUT/'endpoint-plan.json')['body_conductors']
                if w['id']=='W078' for e in w['ends'] if e['role']=='MAIN.VIN'),
            full_current_route_open=True,no_extra_parallel_wire=True),
            dict(wire='XA02',target='AUX.VIN',target_pin_mm=None,
                delivered_padmap_required=True,protected_park_only_until_identified=True),
            dict(wire='XB32',target='Existing tail insulation station',
                exact_station_mm=[68,-45,116.78756443470179],
                blocker='W045 reserved route overlaps required receiving station itself; changing upstream tail approach cannot fix this. Reallocate W045 with complete tail receiving family, not another tail-only scalar shift.',
                planning_witness=tail_witness,actual_BRep_collision_not_claimed=True)],
        selected=False,stage_completed=False,W5_complete=False,physical_pass=False,
        current_geometry_reference='rr-receiving-branch-plan.json; source group still open',
        new_connectors=0,new_native_parts=0,
        source_sha256={f.relative_to(ROOT).as_posix():B.sha(f) for f in
            (Path(__file__),Path(R.__file__),OUT/'rr-receiving-branch-plan.json',
             OUT/'source-fanouts-plan.json',OUT/'endpoint-plan.json',OUT/'protected-loads-plan.json')})

def expanded_gate_plan():
    p=R.build();compact=build()
    for r in compact['rows']:
        row=copy.deepcopy(r)
        row.update(leg=r['holder'],target='',side='output')
        p['tails'].append(row)
    p.update(changed_path_names=[r['wire'] for r in compact['rows']],changed_case_names=[],
        mutual_path_preflight=compact['mutual_path_preflight'])
    return p

if __name__=='__main__':
    assert not PLAN.exists(),'No unchanged trial or historical overwrite'
    tick=time.monotonic();p=build()
    p.update(worker_seconds=round(time.monotonic()-tick,6),finished_utc=datetime.now(timezone.utc).isoformat())
    PLAN.write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=p['status'],lengths=[(r['wire'],r['extension_centreline_mm']) for r in p['rows']],
        conflicts=[{k:r[k] for k in ('a','b','sampled_distance_mm')} for r in p['mutual_path_preflight']['near_pairs']
            if r['status']=='REJECT_PLANNING_PROXIMITY'],seconds=p['worker_seconds'])),flush=True)
