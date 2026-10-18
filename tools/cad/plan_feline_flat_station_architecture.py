"""One WHOLE20-station architecture, not another isolated DFL/S1 pose.

Read source case geometry and all86occupied ports first. Produce compact
shared pose/fan domains with source frames, tools, roots and holds explicit.
This is not a placement, native model or N01 approval.
"""
import hashlib
import json
import math
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure'


def dot(a,b):return sum(x*y for x,y in zip(a,b))
def sub(a,b):return [x-y for x,y in zip(a,b)]
def unit(v):
    n=math.sqrt(dot(v,v));assert n>1e-10
    return [x/n for x in v]
def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def build():
    tick=time.monotonic()
    files={k:OUT/n for k,n in dict(ports='n01-twenty-wago-port-contract.json',
        map='n01-whole-constraint-map.json',profiles='n01-rev3-whole-profiles.json',
        overrides='n01-dedicated-fuse-bays.json',lands='n01-all-current-first-lands.json',
        packet='n01-current-endpoint-packet-r3.json',fore='n01-fore-intrinsic.json',
        ownership='n01-reservation-ownership-plan.json').items()}
    data={k:json.loads(p.read_text()) for k,p in files.items()}
    profiles={**data['profiles']['recipes'],**data['overrides']['station_profile_recipes']}
    land={r['id']:r for r in data['lands']['land_recipes']}
    stations=[];power={'W064','W065','W067','W068'}
    for source in data['ports']['stations']:
        record=next((r for r in data['map']['parts'] if r['owner']==source['current_group']),None)
        if source['ref']=='P_SYS':record=next(r for r in data['map']['parts'] if r['name']=='Ref_Material_P_SYS_new_0_0')
        assert record is not None
        lo,hi=record['world_bounds_mm'];centre=[(a+b)/2 for a,b in zip(lo,hi)]
        p=unit(source['prototype']['port_pitch_vector_mm']);d=unit(source['prototype']['departure_axis'])
        assert abs(dot(p,d))<1e-8 and abs(p[2])+abs(d[2])<1e-6
        width=lambda v:sum(abs(v[i])*(hi[i]-lo[i]) for i in range(3))
        depth,pitch,thickness=width(d),width(p),hi[2]-lo[2]
        assert any(max(abs(a-b) for a,b in zip((thickness,depth,pitch),s))<1e-5 for s in ((9,19,30),(11,22,37)))
        first=source['prototype']['first_port_mm']
        assert abs(dot(sub(first,centre),d)-depth/2)<1e-5,'Mouth and source case pose must agree before transforming'
        ports=[]
        for e in source['occupied_ports']:
            key='REV3Station:'+e['endpoint'];r=profiles.get(key)
            if r:radius=r['radius_mm'];R=r['R_mm'];basis=r['source_profile']
            else:
                ids=[r['id'] for r in data['packet']['endpoints'] if r['wire']==e['wire'] and r['role']==e['endpoint']]
                matches=[land[n] for n in ids if n in land]
                radius=matches[0]['radius_mm'] if matches else 2.1
                R=25.2 if source['ref']=='P_SYS' else 12.4
                basis=dict(method='Retained current land recipe' if matches else 'Explicit conservative project radius, not vendor data')
            if e['wire'] in power:R=max(R,25.2);radius=max(radius,2.1)
            q=e['point_mm'];local=sub(q,centre)
            assert abs(dot(local,d)-depth/2)<1e-5
            ports.append(dict(endpoint=e['endpoint'],wire=e['wire'],physical_port=e['physical_port'],
                schematic_port=e['schematic_port'],local_pitch_departure_thickness_mm=[dot(local,p),dot(local,d),local[2]],
                radius_mm=radius,minimum_project_R_mm=R,source_basis=basis,
                protected_whole_route_reuse=(source['ref']=='P_SYS' and e['wire']=='W043')))
        stations.append(dict(ref=source['ref'],case_name=record['name'],source_world_centre_mm=centre,
            source_part_record=record['source_record'],source_pitch_axis=p,source_departure_axis=d,
            flat_dimensions_pitch_departure_thickness_mm=[pitch,depth,thickness],
            preserve_closed_lever_UP=True,ports=ports,unused_ports=source['unused_ports'],
            fixed_identity_pose=(source['ref']=='P_SYS'),
            row_families=['inner'] if thickness>10 else ['inner','outer'],
            shared_fan_R_mm=max(12.4,max(r['minimum_project_R_mm'] for r in ports)),
            changed_case_all_owned_ports_and_grip_as_ONE_group=True))
    assert len(stations)==20 and sum(len(r['ports']) for r in stations)==86
    assert sum(s['flat_dimensions_pitch_departure_thickness_mm'][2]>10 for s in stations)==4
    return dict(status='WHOLE20_FLAT_ARCHITECTURE_DOMAINS_REQUIRED_NOT_CHOSEN',selected=False,N01_complete=False,physical_pass=False,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (*files.values(),Path(__file__),
            ROOT/'hardware/reference/parent-fuse-extensions-2026-10-03/facts.json')},
        station_count=20,occupied_ports=86,small_415_count=16,large_615_count=4,
        stations=stations,
        source_bound_receipt=dict(P_REAR_current_mouth_X_mm=-119,departure=[-1,0,0],first_mm=3,R_mm=25.2,radius_mm=2.1,
            required_fore_extent_before90turn_mm=-149.3,hard_fore_bound_mm=-141.5,
            current_P_REAR_orientation_cannot_be_frozen=True,not_actual_collision_or_global_infeasibility=True),
        row_domains=dict(inner=dict(centre_Y_mm=[-19.5,19.5],bottom_Z_mm=44.77,
            fan='OUTWARD_Y below bank bed; use each group common_R >= all actual project minima',
            case_height_mm='SOURCE9or11, not universal9',
            preserve_P_SYS_exact_identity_pose=True),
            outer=dict(centre_Y_mm=[-62.5,62.5],top_Z_mm=50.75,
            fan='UP_Z in source bank case gaps, not outward through wall or down through folding knees',
            small_415_only=True,source_bank_gap_X_controls_case_X_domains=True)),
        pose_domains=dict(departure_X_signs=[-1,1],pitch_Y_sign_equals_departure_X_sign=True,
            rule='Rotate complete source kit aboutZ to flat UP; target centre from shared row and bank-gap domains, not isolated scalar offsets',
            X_continuous_ranges_require_actual_fixed_material_and_all36motion_before_choice=True,
            use_no_more_than_two_whole_hypotheses_before_reassessing_cause=True),
        full_fan=dict(first_mm=3,after_arc_grip_mm=9,
            first3_is_existing_unclamped_source_exit_not_a_3mm_grip=True,
            whole_station_grip_domains=['BEFORE: first9 with one common multichannel cap before arc',
                'AFTER: first3 then full9 after arc, only if whole cap and closure fit'],
            outer_default='BEFORE: do not force whole clamps/heads into9mm inter-fuse columns',
            shared_head_or_bolted_cap_not_five_overlapping_6mm_heads=True,
            radius_rule='Whole station common_R at least every named source minimum; four HELU ends at least25.2',
            seat_mm=2,band_width_mm=2.5,band_thickness_mm=1.2,head_cube_mm=6,
            channel_all_neighbouring_jackets_before_common_PETG_union=True,
            no_filled_collision_boxes_instead_of_real_multichannel_grips=True,
            closure_heads_and_attachment_entry_must_be_in_same_domain=True),
        shared_frame=dict(status='JOINT_REPLACEMENT_REQUIRED_NOT_REMOVED_PARTS_PASS',
            provisional_inner_case_maxY_mm=38,outer_small_case_minY_mm=47.5,
            possible_between_row_rail_centre_absY_mm=42.75,
            P0_side_top_mm=38.52,provisional_airgap_base_Z_mm=39.77,
            root_owners='Actual existing rail clamps x0/90 and all current fastener/4MTA/battery owners must be reconciled once',
            all_changed_scaffolding_list='n01-reservation-ownership-plan.json plus positivePost-69_1/LowerRail1',
            preserve_retained_MAIN_cut_channel=True,
            member_thickness_contact_bolt_access_load_paths_NOT_qualified=True,
            outer_low_seat_transition_is_not_solved_by_the_rail_centre_number=True),
        preserve=['All selected purchased SKUs/counts/nets/cavities','12R47 bank cases and24source ends',
            'Both sides of4MTA and their retained source families','P_SYScase/F_PI/W043/W077/W078 where source identity permits',
            'P0/E6/15drives/replaceableMG92B/325x200x160/max200/256cube margin/Ola appearance'],
        installation_sequence=['Foundation and low supports before boards and station wiring',
            'Install/terminate flat stations and all independent grips before bank obstructs lever service',
            'Fit complete bank as retained kit, then modules/head/tail wires and removable panels',
            'RoutineATO withdrawal remains outward above low stations; prove all12 actual tool paths',
            'Deep WAGO repair may reverse assembly; do not invent quick service but account real disconnections'],
        required_before_N01=['Joint whole20 case/all86fullfans/closureheads/frame loadpath proposal',
            'WholeS1body/control/4ring axes and all8HELU ends in freed common space, no old-sourceclock retry',
            'All3FHAC fulltails, fore collar/panelpartner, rear tails and4MTA interfaces',
            'All123physical portions/246ends and dynamic12looms throughout adopted motion, no historical15degree shortcut',
            'Complete end/grip/root/tool/assembly coverage and nominal lengths/stock',
            'One exact whole changed-geometry reception before native detailed features'],
        new_scope_count=0,new_scope_total=10,
        measured_seconds=round(time.monotonic()-tick,6))


def main():
    dest=OUT/'n01-flat-station-architecture.json';assert not dest.exists()
    r=build();dest.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:r[k] for k in ('status','station_count','occupied_ports','small_415_count','large_615_count','measured_seconds')}))


if __name__=='__main__':main()
