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
    if base.startswith('BAT'):return 'RetainedBattery'
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


def main():
    tick=time.monotonic()
    source=BASE/'body-harness-checkpoint/w5-current-end-coverage.json'
    model=OUT/'module-layout.json'
    old=json.loads(source.read_text());plan=json.loads(model.read_text())
    roles={g['role']:g for g in plan['groups']}
    moved=[];open_roles=Counter()
    for row in old['fixed_physical_guide_ends']+old['body_fixed_boundary_ends']:
        group=owner(row['role'],roles)
        point=np.array(row['point_world_mm'])
        if group=='RetainedBattery':candidate=point
        elif group in roles:
            g=roles[group];candidate=np.array(g['rotation_rows'])@point+g['translation_mm']
        else:
            candidate=None;open_roles[row['role'].split('.')[0]]+=1
        moved.append(dict(id=row['id'],wire=row['wire'],role=row['role'],
            original_point_mm=point.tolist(),candidate_group=group,
            transformed_guide_end_mm=None if candidate is None else candidate.tolist(),
            status='IDENTITY_TRANSFER_ONLY_PORT_AND_GRIP_NOT_QUALIFIED' if candidate is not None
                   else 'NEW_ANCHOR_OR_COMPONENT_ALLOCATION_REQUIRED',
            old_owner=row['restraint']['owner'],old_restraint_not_reselected=True))
    # These actual physical cases cannot be dropped merely because they do
    # not match the dimensions of the20 larger distribution connectors.
    inventory=json.loads((OUT/'motion-layout.json').read_text())['inventory']
    unresolved_parts=[r for r in inventory if r['kind']=='surface' and (
        '_Joint/' in r['label'] or r['label'].startswith(('F_AUX_candidate_case/',
            'PostF0Splice_CP2/','JPWM/','XP01/','XP02/','XP03/','XT60','F0_CP2/')))]
    report=dict(status='WHOLE_END_ACCOUNTING_ROUTING_NOT_COMPLETE',selected=False,
        endpoints=moved,endpoint_records=len(moved),logical_nets=80,
        mapped_identity_only=sum(r['candidate_group'] is not None for r in moved),
        unallocated_role_counts=dict(open_roles),
        additional_actual_parts_requiring_allocation=unresolved_parts,
        full_paths_complete=False,actual_port_axes_verified=False,
        moving36_boundary_anchors_need_new_compact_motion_plan=True,
        old_source920mm_not_automatically_retained=True,
        assembly_order=['Frame/battery and load-bearing belly supports',
            'Lower distribution tray and independent wire restraints, bench wiring',
            'Lower boards and new compact neck root',
            'Inverted complete bank and upper boards/source cases',
            'Both exits of4MTA plus8real inline extension joints',
            'Continuous moving leg/head looms with calibrated motion/lengths',
            'Split removable skin with bottom ATO service apertures'],
        open=['Actual placement of additional listed cases',
            'All new port/9mm insulation grip/bend transitions together',
            '80continuous nets and moving sections, materials and assembly',
            'Skin/module containment and complete motion'],
        source_sha256={source.relative_to(ROOT).as_posix():sha(source),
            model.relative_to(ROOT).as_posix():sha(model),
            __file__.replace('\\','/').split(str(ROOT).replace('\\','/')+'/')[-1]:sha(__import__('pathlib').Path(__file__))},
        physical_pass=False,worker_seconds=round(time.monotonic()-tick,3))
    (OUT/'endpoint-layout.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ('status','endpoint_records','mapped_identity_only','unallocated_role_counts','worker_seconds')}),flush=True)


if __name__=='__main__':main()
