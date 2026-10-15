"""Current36-core contract: retain20 routes; bind12 changed Hip1 breakouts.

All receiver identities stay fixed. Factory reserve/donor stock is inherited
once; changing a guide does not buy another cable or guess copper/pin order.
"""
import copy,hashlib,json,math,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/body-harness-checkpoint'
SHA=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()


def build():
    tick=time.monotonic();files=[OUT/n for n in ('body-receiver-relief-layout.json','body-axial-layout-chosen.json',
        'leg-source-near-member-plan.json','axial-source-receiver-integration.json','receiver-relief-approach-plan.json')]
    body,source,family,proof,receivers=[json.loads(f.read_text()) for f in files]
    assert body['status']=='BODY20_ROUTES_AND_RECEIVER_GRIPS_EXACT_CHANGED_WIRE_CLEAR_ROOT_ARMS_NATIVE_OPEN'
    assert proof['status']=='FOUR_SOURCES_TWELVE_BREAKOUTS_TWENTY_RECEIVER_GRIPS_SAMPLED_CLEAR_ROOT_ARMS_OPEN'
    assert len(proof['completed_fans'])==12 and not proof['contacts'] and not proof['errors']
    for name,digest in proof['source_sha256'].items():assert SHA(ROOT/name)==digest,name
    rows=copy.deepcopy(body['rows']);new_sources={r['loom']:r for r in source['hips']}
    old_sources={r['loom']:r for r in family['routes']}
    changed=[]
    for row in rows:
        if row['loom'] not in new_sources:continue
        assert row['wire'] not in body['routes'],'Changed source would invalidate a retained route'
        hip=new_sources[row['loom']];core=next(r for r in hip['source_fans'] if r['core']==row['core'])
        mapping=hip['source']['electrical'][row['core']]
        assert (mapping['wire'],mapping['body_end'])==(row['wire'],row['receiver_role'])
        assert row['source_extension_candidate'] is None,'Do not silently recalculate donor stock'
        old_guide=old_sources[row['loom']]['guide_to_body_grip_mm']
        new_guide=hip['guide_mm']+hip['factory_guide_mm']
        inherited_total=row['capacity_before_terminal_mm']+old_guide
        assert abs(inherited_total-850)<1e-6,'Existing900minus50reserve contract changed'
        capacity=inherited_total-new_guide
        row.update(bundle_root_world_mm=hip['fixed_anchor_world_mm'],
            bodyward_bundle_tangent=[-v for v in hip['fixed_tangent_world']],
            start=core['parts'][0]['start'],free_start=core['parts'][-1]['end'],
            source_land=core['parts'][0],source_parts=core['parts'],source_free_axis=hip['source_fan_direction'],
            source_after_jacket_first5_mm=core['after_5mm'],
            capacity_before_terminal_mm=capacity,source_guide_to_body_mm=new_guide,
            factory850_usable_is_project_assumption=True,
            inherited_factory_reserve_mm=50,extra_cable_purchased_mm=0,
            actual_core_start=None,actual_route=None,receiving_restraint=None,actual_cut_mm=None)
        changed.append(row['wire'])
    assert len(rows)==36 and len({r['wire'] for r in rows})==36 and len(changed)==12
    remaining=[r['wire'] for r in rows if r['wire'] not in body['routes']]
    assert len(remaining)==16
    return dict(status='CURRENT36CORE_CONTRACT_20ROUTES_RETAINED_16OPEN',rows=rows,
        inherited_routes=body['routes'],inherited_receiver_grips=receivers['grips'],
        changed_source_core_ids=changed,remaining_wire_ids=remaining,
        unchanged_routes=20,planned_receiver_grips=20,total_receiver_grips_required=36,
        constraints=['Plan remaining16receiver prefixes/fullgrips jointly with existing20 BEFORE native detail.',
            'Source8rootedarms must be checked with all36receiver reservations before final selection.',
            'Rear Hip1bodyward axis is-X, notUP. Keep actual source fan direction/C1; do not force old router assertion by falsifying datums.',
            'Existing first5mm source jacket exclusion may end inside the fan arc; use source_after_jacket_first5_mm, not blindly drop firstline.',
            'No imaginary factory extension, supplier copper/pinout/radius or physicalPASS.'],
        source_sha256={f.relative_to(ROOT).as_posix():SHA(f) for f in files+[Path(__file__)]},
        worker_seconds=round(time.monotonic()-tick,3),selected=False,W5_complete=False,physical_pass=False)


if __name__=='__main__':
    result=build();(OUT/'body36-current-contract.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','changed_source_core_ids','remaining_wire_ids','worker_seconds')}))
