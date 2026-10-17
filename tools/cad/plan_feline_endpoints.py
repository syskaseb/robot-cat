"""Transfer identities, not clearance claims, to the shared packaging plan.

Moved distribution/source modules invalidate their old complete wire paths.
Every old end remains accounted for, including currently unallocated parts.
"""
import json
import time
from collections import Counter
import numpy as np
from check_main_p0_placement import ROOT, sha
from plan_feline_layout import BASE, OUT


def owner(role,roles):
    base=role.split('.')[0]
    if base in roles:return base
    # These legacy body-net roles terminate at the XT60, not at the pack.
    # The pack-to-XT60 factory portion remains an independently accounted hold.
    if base.startswith('BAT'):return 'XT60' if 'XT60' in roles else None
    if base=='BUS':return 'BUS'
    if base.startswith('MAIN'):return 'MAIN'
    if base=='PI_USB_C':return 'Pi4'
    if base in ('S0','S1','F_PI'):return base
    for code,bank,offset in [('FL','L',0),('FR','R',0),('RL','L',3),('RR','R',3)]:
        if base=='F_'+code:return 'MTA_'+code
        if base in ['F_'+code+str(i) for i in (1,2,3)]:
            return ('BankLeft6Oprawek12Koncow' if bank=='L' else 'BankRight6Oprawek12Koncow')
    aliases={'P_FRONT':'P_FRONT_new','P_SYS':'P_SYS_new','G1':'G1_CP2','G2':'G2_CP2',
        'G_AUX':'W3Ref_G_AUX_case','P_AUX':'P_AUX_CP2'}
    key='WAGO:'+aliases.get(base,base)
    return key if key in roles else None


def source_port_frames(plan):
    """Reconcile explicit CURRENT nominal port frames with saved snapshot cases.

    A historical guide point is not necessarily in the saved assembly frame.
    Only a same-orientation, equal-size case translation is inferred here;
    no hole location, supplier pinout or electrical qualification is invented.
    """
    source=BASE/'body-harness-checkpoint/leg-stations-plan.json'
    stations=json.loads(source.read_text())['stations']
    groups={g['role']:g for g in plan['groups']};frames={}
    for role,station in stations.items():
        group=owner(role,groups)
        assert group in groups,('Missing physical station',role)
        bounds=np.array(groups[group]['current_bounds_mm'])
        nominal=np.array(station['casing_mm']).reshape(2,3)
        assert np.max(abs((bounds[1]-bounds[0])-(nominal[1]-nominal[0])))<.03,role
        shift=bounds[0]-nominal[0]
        frames[group]=dict(source=source.relative_to(ROOT).as_posix(),
            source_nominal_bounds_mm=nominal.tolist(),snapshot_bounds_mm=bounds.tolist(),
            nominal_to_snapshot_translation_mm=shift.tolist(),
            nominal_outward_axis=station['entry_axis'],ports=station['ports'],
            logical_to_physical_common_rail_cavity=station['logical_to_physical_common_rail_cavity'],
            basis='Explicit current nominal station recipe; equal-size same-orientation saved casing translation. Not new manufacturer data.')
    return frames


def transfer_port(plan,role,point,direction=None,frames=None):
    groups={g['role']:g for g in plan['groups']};group=owner(role,groups)
    if group not in groups:return group,None,None
    p=np.array(point,dtype=float);d=None if direction is None else np.array(direction,dtype=float)
    frames=source_port_frames(plan) if frames is None else frames
    if group in frames:
        f=frames[group];port=role.split('.')[1]
        assert port in f['ports'],('Unknown nominal cavity',role)
        # All routes are being redesigned: use the explicit local port, not
        # a later historical guide endpoint that may belong to another frame.
        p=np.array(f['ports'][port],dtype=float)+f['nominal_to_snapshot_translation_mm']
        if d is not None:d=np.array(f['nominal_outward_axis'],dtype=float)
    override_name=plan.get('role_pose_overrides',{}).get(role)
    if override_name:
        ov=plan['part_pose_overrides'][override_name];rr=np.array(ov['rotation_rows'])
        p=rr@p+ov['translation_mm']
        if d is not None:d=rr@d
    g=groups[group];rr=np.array(g['rotation_rows'])
    return group,rr@p+g['translation_mm'],None if d is None else rr@d


def main():
    tick=time.monotonic()
    source=BASE/'body-harness-checkpoint/w5-current-end-coverage.json'
    model=OUT/'module-layout.json'
    old=json.loads(source.read_text());plan=json.loads(model.read_text())
    roles={g['role']:g for g in plan['groups']}
    frames=source_port_frames(plan);moved=[];open_roles=Counter();frame_errors=[]
    for row in old['fixed_physical_guide_ends']+old['body_fixed_boundary_ends']:
        group=owner(row['role'],roles)
        point=np.array(row['point_world_mm'])
        if group=='RetainedBattery':candidate=point
        elif group in roles:
            group,candidate,_=transfer_port(plan,row['role'],point,frames=frames)
        else:
            candidate=None;open_roles[row['role'].split('.')[0]]+=1
        if candidate is not None and group.startswith('WAGO:'):
            lo,hi=np.array(roles[group]['candidate_bounds_mm'])
            distance=float(np.linalg.norm(np.maximum(np.maximum(lo-candidate,candidate-hi),0)))
            if distance>2:frame_errors.append(dict(id=row['id'],role=row['role'],
                outside_case_bbox_mm=distance,reason='Nominal source end not on its current physical casing frame; no automatic port acceptance'))
        moved.append(dict(id=row['id'],wire=row['wire'],role=row['role'],
            original_point_mm=point.tolist(),candidate_group=group,
            transformed_guide_end_mm=None if candidate is None else candidate.tolist(),
            status='IDENTITY_TRANSFER_ONLY_PORT_AND_GRIP_NOT_QUALIFIED' if candidate is not None
                   else 'NEW_ANCHOR_OR_COMPONENT_ALLOCATION_REQUIRED',
            source_nominal_frame_reconciled=group in frames,
            old_owner=row['restraint']['owner'],old_restraint_not_reselected=True))
    # These actual physical cases cannot be dropped merely because they do
    # not match the dimensions of the20 larger distribution connectors.
    inventory=json.loads((OUT/'motion-layout.json').read_text())['inventory']
    unresolved_parts=[r for r in inventory if r['kind']=='surface' and (
        '_Joint/' in r['label'] or r['label'].startswith(('F_AUX_candidate_case/',
            'PostF0Splice_CP2/','JPWM/','XP01/','XP02/','XP03/','XT60','F0_CP2/')))]
    report=dict(status='WHOLE_END_ACCOUNTING_ROUTING_NOT_COMPLETE',selected=False,
        endpoints=moved,source_port_frames=frames,source_frame_errors=frame_errors,endpoint_records=len(moved),logical_nets=80,
        mapped_identity_only=sum(r['candidate_group'] is not None for r in moved),
        unallocated_role_counts=dict(open_roles),
        additional_actual_parts_requiring_allocation=unresolved_parts,
        full_paths_complete=False,actual_port_axes_verified=False,
        moving36_boundary_anchors_need_new_compact_motion_plan=True,
        old_source920mm_not_automatically_retained=True,pack_factory_portion_not_XT60_body_role=True,
        assembly_order=['Frame/battery and load-bearing belly supports',
            'Lower distribution tray and independent wire restraints, bench wiring',
            'Lower boards and new compact neck root',
            'Two tilted six-holder bank rows and upper boards/source cases',
            'Both exits of4MTA plus8real inline extension joints',
            'Continuous moving leg/head looms with calibrated motion/lengths',
            'Split removable skin with side/upward ATO service apertures'],
        open=['Actual placement of additional listed cases',
            'All new port/9mm insulation grip/bend transitions together',
            '80continuous nets and moving sections, materials and assembly',
            'Skin/module containment and complete motion'],
        source_sha256={source.relative_to(ROOT).as_posix():sha(source),
            model.relative_to(ROOT).as_posix():sha(model),
            (BASE/'body-harness-checkpoint/leg-stations-plan.json').relative_to(ROOT).as_posix():sha(BASE/'body-harness-checkpoint/leg-stations-plan.json'),
            __file__.replace('\\','/').split(str(ROOT).replace('\\','/')+'/')[-1]:sha(__import__('pathlib').Path(__file__))},
        physical_pass=False,worker_seconds=round(time.monotonic()-tick,3))
    (OUT/'endpoint-layout.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ('status','endpoint_records','mapped_identity_only','unallocated_role_counts','worker_seconds')}),flush=True)


if __name__=='__main__':main()
